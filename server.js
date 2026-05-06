const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 8765;
const baseDir = 'C:/Users/Administrador/Desktop/facturas/pdf_pages';

const mimeTypes = {
  '.html': 'text/html',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.png': 'image/png'
};

const server = http.createServer((req, res) => {
  const urlPath = req.url === '/' ? '/index.html' : req.url;
  const filePath = path.join(baseDir, urlPath);
  
  if (fs.existsSync(filePath) && fs.statSync(filePath).isFile()) {
    const ext = path.extname(filePath);
    const ct = mimeTypes[ext] || 'application/octet-stream';
    res.writeHead(200, {'Content-Type': ct, 'Access-Control-Allow-Origin': '*'});
    fs.createReadStream(filePath).pipe(res);
  } else {
    // List directory
    const files = fs.readdirSync(baseDir);
    const html = `<!DOCTYPE html><html><head><meta charset="utf-8"><title>Invoice Images</title></head><body>` +
      files.map(f => `<p><img src="/${f}" style="max-width:100%"/><br>${f}</p>`).join('') +
      `</body></html>`;
    res.writeHead(200, {'Content-Type': 'text/html; charset=utf-8'});
    res.end(html);
  }
});

server.listen(PORT, () => {
  console.log('Server running on http://localhost:' + PORT);
});