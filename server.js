const http = require('http');
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const { DatabaseSync } = require('node:sqlite');

const PORT = 8765;
const ROOT = __dirname;
const DB_PATH = path.join(ROOT, 'facturas.db');
const BACKUP_DIR = path.join(ROOT, 'backups');

const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.pdf': 'application/pdf',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.txt': 'text/plain; charset=utf-8'
};

fs.mkdirSync(BACKUP_DIR, { recursive: true });

const db = new DatabaseSync(DB_PATH);
db.exec(`
  PRAGMA journal_mode = WAL;
  PRAGMA synchronous = FULL;
  CREATE TABLE IF NOT EXISTS invoices (
    id INTEGER PRIMARY KEY,
    num TEXT NOT NULL,
    type TEXT,
    date TEXT,
    supplier TEXT,
    client TEXT,
    total REAL,
    data TEXT NOT NULL,
    deleted_at TEXT,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
  );
  DROP INDEX IF EXISTS idx_invoice_identity;
  CREATE INDEX IF NOT EXISTS idx_invoice_identity
    ON invoices(num, date, supplier, client, total);
  CREATE TABLE IF NOT EXISTS meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
  );
`);

function loadSeed() {
  const dataPath = path.join(ROOT, 'data.js');
  const script = fs.readFileSync(dataPath, 'utf8');
  const context = { window: {} };
  vm.createContext(context);
  vm.runInContext(script, context);
  return context.window.SEED_DATA || context.SEED_DATA;
}

function getAllInvoices(includeDeleted = false) {
  const stmt = db.prepare(`
    SELECT data
    FROM invoices
    ${includeDeleted ? '' : 'WHERE deleted_at IS NULL'}
    ORDER BY id
  `);
  return stmt.all().map((row) => JSON.parse(row.data));
}

function getNextId() {
  const row = db.prepare('SELECT MAX(id) AS maxId FROM invoices').get();
  return Math.max(Number(row.maxId || 0) + 1, Number(getMeta('nextId') || 1));
}

function getMeta(key) {
  const row = db.prepare('SELECT value FROM meta WHERE key = ?').get(key);
  return row ? row.value : null;
}

function setMeta(key, value) {
  db.prepare(`
    INSERT INTO meta(key, value)
    VALUES (?, ?)
    ON CONFLICT(key) DO UPDATE SET value = excluded.value
  `).run(key, String(value));
}

function upsertInvoice(inv) {
  const id = Number(inv.id);
  if (!id) throw new Error('Invoice is missing id');
  db.prepare(`
    INSERT INTO invoices(id, num, type, date, supplier, client, total, data, deleted_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, NULL, CURRENT_TIMESTAMP)
    ON CONFLICT(id) DO UPDATE SET
      num = excluded.num,
      type = excluded.type,
      date = excluded.date,
      supplier = excluded.supplier,
      client = excluded.client,
      total = excluded.total,
      data = excluded.data,
      deleted_at = NULL,
      updated_at = CURRENT_TIMESTAMP
  `).run(
    id,
    inv.num || '',
    inv.type || '',
    inv.date || '',
    inv.supplier || '',
    inv.client || '',
    Number(inv.total || 0),
    JSON.stringify(inv)
  );
}

function replaceActiveInvoices(snapshot) {
  const incomingIds = new Set(snapshot.invoices.map((inv) => Number(inv.id)));
  const currentIds = db.prepare('SELECT id FROM invoices WHERE deleted_at IS NULL').all().map((row) => Number(row.id));
  db.exec('BEGIN IMMEDIATE');
  try {
    snapshot.invoices.forEach(upsertInvoice);
    currentIds.forEach((id) => {
      if (!incomingIds.has(id)) {
        db.prepare('UPDATE invoices SET deleted_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP WHERE id = ?').run(id);
      }
    });
    setMeta('version', snapshot.version || new Date().toISOString());
    setMeta('nextId', snapshot.nextId || getNextId());
    setMeta('updatedAt', new Date().toISOString());
    db.exec('COMMIT');
  } catch (err) {
    db.exec('ROLLBACK');
    throw err;
  }
}

function seedDatabaseIfNeeded() {
  const count = db.prepare('SELECT COUNT(*) AS count FROM invoices').get().count;
  const seed = loadSeed();
  if (count === 0 && seed && Array.isArray(seed.invoices)) {
    replaceActiveInvoices({
      version: seed.version,
      nextId: seed.nextId,
      invoices: seed.invoices
    });
  }
}

function snapshot() {
  const invoices = getAllInvoices(false);
  const maxId = invoices.reduce((max, inv) => Math.max(max, Number(inv.id || 0)), 0);
  return {
    version: getMeta('version') || 'sqlite',
    nextId: Math.max(Number(getMeta('nextId') || 1), maxId + 1),
    invoices,
    source: 'sqlite',
    savedAt: getMeta('updatedAt') || new Date().toISOString()
  };
}

function backupSnapshot(reason) {
  const stamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
  const file = path.join(BACKUP_DIR, `sqlite_${reason}_${stamp}.json`);
  fs.writeFileSync(file, JSON.stringify(snapshot(), null, 2), 'utf8');
  const backups = fs.readdirSync(BACKUP_DIR)
    .filter((name) => name.startsWith('sqlite_') && name.endsWith('.json'))
    .map((name) => ({ name, time: fs.statSync(path.join(BACKUP_DIR, name)).mtimeMs }))
    .sort((a, b) => b.time - a.time);
  backups.slice(30).forEach((entry) => fs.rmSync(path.join(BACKUP_DIR, entry.name), { force: true }));
}

seedDatabaseIfNeeded();
backupSnapshot('startup');

function sendJson(res, status, body) {
  const text = JSON.stringify(body);
  res.writeHead(status, {
    'Content-Type': 'application/json; charset=utf-8',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type'
  });
  res.end(text);
}

function readBody(req) {
  return new Promise((resolve, reject) => {
    let body = '';
    req.on('data', (chunk) => {
      body += chunk;
      if (body.length > 25 * 1024 * 1024) {
        reject(new Error('Request body too large'));
        req.destroy();
      }
    });
    req.on('end', () => resolve(body));
    req.on('error', reject);
  });
}

function serveStatic(req, res) {
  const url = new URL(req.url, `http://localhost:${PORT}`);
  let pathname = decodeURIComponent(url.pathname);
  if (pathname === '/') pathname = '/index.html';
  const filePath = path.normalize(path.join(ROOT, pathname));
  if (!filePath.startsWith(ROOT)) {
    res.writeHead(403);
    res.end('Forbidden');
    return;
  }
  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
      res.end('Not found');
      return;
    }
    res.writeHead(200, { 'Content-Type': MIME_TYPES[path.extname(filePath).toLowerCase()] || 'application/octet-stream' });
    res.end(data);
  });
}

const server = http.createServer(async (req, res) => {
  if (req.method === 'OPTIONS') {
    sendJson(res, 204, {});
    return;
  }

  try {
    const url = new URL(req.url, `http://localhost:${PORT}`);
    if (url.pathname === '/api/health') {
      sendJson(res, 200, { ok: true, db: DB_PATH, count: snapshot().invoices.length });
      return;
    }
    if (url.pathname === '/api/data' && req.method === 'GET') {
      sendJson(res, 200, snapshot());
      return;
    }
    if (url.pathname === '/api/save' && req.method === 'POST') {
      const body = JSON.parse(await readBody(req));
      if (!body || !Array.isArray(body.invoices)) throw new Error('Invalid invoice snapshot');
      backupSnapshot('before_save');
      replaceActiveInvoices(body);
      sendJson(res, 200, snapshot());
      return;
    }
    if (url.pathname === '/api/export' && req.method === 'GET') {
      sendJson(res, 200, snapshot());
      return;
    }
    serveStatic(req, res);
  } catch (err) {
    sendJson(res, 500, { ok: false, error: err.message });
  }
});

server.listen(PORT, () => {
  console.log(`Facturas local server: http://localhost:${PORT}/`);
  console.log(`SQLite database: ${DB_PATH}`);
});
