const https = require('https');
const fs = require('fs');

const apiKey = 'helloworld';
const imagePaths = [
  'C:/Users/Administrador/Desktop/facturas/pdf_pages/page1_img0.jpg',
  'C:/Users/Administrador/Desktop/facturas/pdf_pages/page2_img1.jpg',
  'C:/Users/Administrador/Desktop/facturas/pdf_pages/page3_img2.jpg'
];

function callOCR(imagePath) {
  return new Promise((resolve, reject) => {
    const imageData = fs.readFileSync(imagePath);
    const base64 = imageData.toString('base64');
    const boundary = '----WebKitFormBoundary' + Math.random().toString(36).slice(2);
    
    const body = 
      `--${boundary}\r\n` +
      `Content-Disposition: form-data; name="base64Image"\r\n\r\n` +
      base64 + `\r\n` +
      `--${boundary}\r\n` +
      `Content-Disposition: form-data; name="language"\r\n\r\n` +
      `spa\r\n` +
      `--${boundary}--\r\n`;
    
    const options = {
      hostname: 'api.ocr.space',
      path: '/parse/image?language=spa&detectOrientation=true',
      method: 'POST',
      headers: {
        'apikey': apiKey,
        'Content-Type': 'multipart/form-data; boundary=' + boundary,
        'Content-Length': Buffer.byteLength(body)
      }
    };
    
    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const json = JSON.parse(data);
          if (json.ParsedResults && json.ParsedResults[0]) {
            console.log('Page', imagePath.match(/page(\d+)/)[1], 'OK');
            resolve(json.ParsedResults[0].ParsedText);
          } else {
            console.log('OCR failed:', JSON.stringify(json).substring(0, 500));
            resolve('');
          }
        } catch(e) {
          console.error('Parse error:', e.message);
          resolve('');
        }
      });
    });
    req.on('error', e => { console.error(e); resolve(''); });
    req.write(body);
    req.end();
  });
}

(async () => {
  const results = [];
  for (let i = 0; i < imagePaths.length; i++) {
    const text = await callOCR(imagePaths[i]);
    results.push({ page: i+1, text });
  }
  const allText = results.map(r => `=== PAGE ${r.page} ===\n${r.text}`).join('\n\n');
  fs.writeFileSync('C:/Users/Administrador/Desktop/facturas/ocr_result.txt', allText, 'utf8');
  console.log('\nAll results saved to ocr_result.txt');
})();