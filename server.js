const http = require('http');
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const { DatabaseSync } = require('node:sqlite');

const PORT = 8765;
const ROOT = __dirname;
const DB_PATH = path.join(ROOT, 'facturas.db');
const BACKUP_DIR = path.join(ROOT, 'backups');
const OPENAI_MODEL = process.env.OPENAI_MODEL || 'gpt-4.1-mini';
const AI_CONFIG_PATH = path.join(ROOT, 'ai_config.json');

const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.webmanifest': 'application/manifest+json; charset=utf-8',
  '.svg': 'image/svg+xml; charset=utf-8',
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

function readAiConfig() {
  let config = {};
  if (fs.existsSync(AI_CONFIG_PATH)) {
    config = JSON.parse(fs.readFileSync(AI_CONFIG_PATH, 'utf8'));
  }
  const keyPath = path.join(ROOT, 'openai_key.txt');
  return {
    provider: process.env.AI_PROVIDER || config.provider || 'openai',
    apiKey: process.env.AI_API_KEY || process.env.OPENAI_API_KEY || config.apiKey || (fs.existsSync(keyPath) ? fs.readFileSync(keyPath, 'utf8').trim() : ''),
    baseUrl: process.env.AI_BASE_URL || config.baseUrl || 'https://api.openai.com/v1',
    model: process.env.AI_MODEL || process.env.OPENAI_MODEL || config.model || OPENAI_MODEL
  };
}

function invoiceJsonSchema() {
  const fields = {
    type: { type: 'string', enum: ['expense', 'income', 'abono', 'sale'] },
    num: { type: 'string' },
    date: { type: 'string', description: 'YYYY-MM-DD or empty string' },
    due: { type: 'string', description: 'YYYY-MM-DD or empty string' },
    supplier: { type: 'string' },
    client: { type: 'string' },
    nif: { type: 'string' },
    description: { type: 'string' },
    base: { type: 'number' },
    iva_rate: { type: 'number' },
    iva_amount: { type: 'number' },
    irpf_rate: { type: 'number' },
    irpf_amount: { type: 'number' },
    total: { type: 'number' },
    pay_method: { type: 'string' },
    pay_date: { type: 'string', description: 'YYYY-MM-DD or empty string' },
    bank_amount: { type: 'number' },
    cash_amount: { type: 'number' },
    notes: { type: 'string' },
    confidence: { type: 'number' },
    needs_review: { type: 'boolean' }
  };
  return {
    type: 'object',
    additionalProperties: false,
    properties: fields,
    required: Object.keys(fields)
  };
}

function normalizeAiInvoice(data, fileName) {
  const out = data || {};
  const numeric = ['base', 'iva_rate', 'iva_amount', 'irpf_rate', 'irpf_amount', 'total', 'bank_amount', 'cash_amount', 'confidence'];
  numeric.forEach((key) => { out[key] = Number(out[key] || 0); });
  ['num', 'date', 'due', 'supplier', 'client', 'nif', 'description', 'pay_method', 'pay_date', 'notes'].forEach((key) => {
    out[key] = String(out[key] || '').trim();
  });
  out.type = ['expense', 'income', 'abono', 'sale'].includes(out.type) ? out.type : 'expense';
  if (!out.num) out.num = path.basename(fileName || 'invoice', path.extname(fileName || ''));
  if ((!out.iva_rate || out.iva_rate <= 1) && out.base && out.iva_amount) {
    out.iva_rate = Math.round((out.iva_amount / out.base) * 10000) / 100;
  }
  if (!out.iva_rate) out.iva_rate = 21;
  if (!out.iva_amount && out.base) out.iva_amount = Math.round(out.base * out.iva_rate) / 100;
  if (!out.total && out.base) out.total = Math.round((out.base + out.iva_amount - out.irpf_amount) * 100) / 100;
  out.needs_review = Boolean(out.needs_review || out.confidence < 0.85);
  return out;
}

async function parseInvoiceWithOpenAI(payload) {
  const ai = readAiConfig();
  if (!ai.apiKey) throw new Error('Missing AI key. Add ai_config.json or openai_key.txt');
  const fileName = payload.fileName || 'invoice';
  const mimeType = payload.mimeType || 'application/octet-stream';
  const base64 = String(payload.base64 || '').replace(/^data:[^,]+,/, '');
  const ocrText = String(payload.ocrText || '').slice(0, 12000);
  if (!base64) throw new Error('Missing file data');

  const content = [{
    type: 'input_text',
    text:
      'Extract this Spanish invoice into JSON. Return only fields from the schema. ' +
      'Use decimal numbers, ISO dates YYYY-MM-DD, and empty strings for unknown dates/text. ' +
      'Do not guess totals when unreadable; set needs_review=true. ' +
      `Filename: ${fileName}\nOCR text, may contain errors:\n${ocrText}`
  }];

  if (mimeType === 'application/pdf' || fileName.toLowerCase().endsWith('.pdf')) {
    content.push({
      type: 'input_file',
      filename: fileName,
      file_data: `data:${mimeType};base64,${base64}`
    });
  } else {
    content.push({
      type: 'input_image',
      image_url: `data:${mimeType};base64,${base64}`,
      detail: 'high'
    });
  }

  if (ai.provider !== 'openai') {
    return parseInvoiceWithChatCompletions(payload, ai, base64, ocrText);
  }

  const response = await fetch(`${ai.baseUrl.replace(/\/$/, '')}/responses`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${ai.apiKey}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      model: ai.model,
      input: [{ role: 'user', content }],
      text: {
        format: {
          type: 'json_schema',
          name: 'invoice_extraction',
          strict: true,
          schema: invoiceJsonSchema()
        }
      }
    })
  });

  const json = await response.json();
  if (!response.ok) throw new Error(json.error ? json.error.message : `OpenAI HTTP ${response.status}`);
  let text = json.output_text;
  if (!text && Array.isArray(json.output)) {
    text = json.output.flatMap((item) => item.content || []).map((part) => part.text || '').join('');
  }
  if (!text) throw new Error('OpenAI returned no structured text');
  return normalizeAiInvoice(JSON.parse(text), fileName);
}

async function parseInvoiceWithChatCompletions(payload, ai, base64, ocrText) {
  const fileName = payload.fileName || 'invoice';
  const mimeType = payload.mimeType || 'application/octet-stream';
  const isPdf = mimeType === 'application/pdf' || fileName.toLowerCase().endsWith('.pdf');
  if (isPdf) {
    throw new Error('当前免费AI接口不直接支持PDF。请在网页选择PDF，页面会先转成图片再识别；如果仍失败，请把PDF第一页截图成JPG/PNG再上传。');
  }
  const prompt =
    'Look at the attached image and extract only clearly visible Spanish invoice fields into strict JSON with these exact keys: ' +
    Object.keys(invoiceJsonSchema().properties).join(', ') + '. ' +
    'Never invent company names, invoice numbers, dates, tax ids, or amounts. ' +
    'If the image is blank, unreadable, not an invoice, or a field is uncertain, use empty string for text, 0 for numbers, confidence 0, and needs_review true. ' +
    'Use numbers for amounts and ISO date YYYY-MM-DD or empty string. Return JSON only. ' +
    `Filename: ${fileName}\nOCR text, may contain errors:\n${ocrText}`;

  const userContent = [{ type: 'text', text: prompt }];
  if (!isPdf) {
    userContent.push({
      type: 'image_url',
      image_url: { url: `data:${mimeType};base64,${base64}` }
    });
  }

  const response = await fetch(`${ai.baseUrl.replace(/\/$/, '')}/chat/completions`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${ai.apiKey}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      model: ai.model,
      messages: [
        { role: 'system', content: 'You extract invoice data from visible evidence only. Return valid JSON only, no markdown. Do not guess or fabricate.' },
        { role: 'user', content: userContent }
      ],
      response_format: { type: 'json_object' },
      max_tokens: 1200,
      temperature: 0
    })
  });

  const json = await response.json();
  if (!response.ok) {
    const detail = json.error ? JSON.stringify(json.error) : JSON.stringify(json).slice(0, 600);
    throw new Error(`AI HTTP ${response.status}: ${detail}`);
  }
  const text = json.choices && json.choices[0] && json.choices[0].message ? json.choices[0].message.content : '';
  if (!text) throw new Error('AI returned no text');
  return normalizeAiInvoice(JSON.parse(text), fileName);
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
    if (url.pathname === '/api/ai-parse' && req.method === 'POST') {
      const body = JSON.parse(await readBody(req));
      const parsed = await parseInvoiceWithOpenAI(body);
      sendJson(res, 200, { ok: true, parsed });
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
