const https = require('https');
const http = require('http');
const fs = require('fs');

const imagePaths = [
  'C:/Users/Administrador/Desktop/facturas/pdf_pages/page1_img0.jpg',
  'C:/Users/Administrador/Desktop/facturas/pdf_pages/page2_img1.jpg',
  'C:/Users/Administrador/Desktop/facturas/pdf_pages/page3_img2.jpg'
];

function upload0x0(filePath) {
  return new Promise((resolve, reject) => {
    const imageData = fs.readFileSync(filePath);
    const boundary = '----FormBoundary' + Math.random().toString(36).slice(2);
    const filename = filePath.split('/').pop();
    
    const header = 
      '--' + boundary + '\r\n' +
      'Content-Disposition: form-data; name="file"; filename="' + filename + '"\r\n' +
      'Content-Type: image/jpeg\r\n\r\n';
    
    const footer = '\r\n--' + boundary + '--\r\n';
    
    const body = Buffer.concat([
      Buffer.from(header, 'utf8'),
      imageData,
      Buffer.from(footer, 'utf8')
    ]);
    
    const options = {
      hostname: '0x0.st',
      path: '/',
      method: 'POST',
      headers: {
        'Content-Type': 'multipart/form-data; boundary=' + boundary,
        'Content-Length': body.length
      }
    };
    
    const req = https.request(options, res => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => {
        const url = data.trim();
        if (url.startsWith('http')) {
          console.log('Uploaded:', url);
          resolve(url);
        } else {
          console.log('0x0 error:', data);
          reject(new Error(data));
        }
      });
    });
    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

function callOCRByURL(imageUrl) {
  return new Promise((resolve) => {
    const postData = JSON.stringify({ url: imageUrl, language: 'spa', isOverlayRequired: false });
    const options = {
      hostname: 'api.ocr.space',
      path: '/parse/image',
      method: 'POST',
      headers: {
        'apikey': 'helloworld',
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(postData)
      }
    };
    const req = https.request(options, res => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => {
        try {
          const json = JSON.parse(data);
          if (json.ParsedResults && json.ParsedResults[0]) {
            resolve(json.ParsedResults[0].ParsedText);
          } else {
            console.log('OCR error:', JSON.stringify(json).substring(0, 200));
            resolve('');
          }
        } catch(e) {
          resolve('');
        }
      });
    });
    req.on('error', () => resolve(''));
    req.write(postData);
    req.end();
  });
}

(async () => {
  const allResults = [];
  for (const p of imagePaths) {
    try {
      console.log('Uploading:', p.split('/').pop());
      const url = await upload0x0(p);
      await new Promise(r => setTimeout(r, 2000));
      console.log('Calling OCR...');
      const text = await callOCRByURL(url);
      const pageNum = p.match(/page(\d+)/)[1];
      allResults.push({ page: pageNum, text, url });
      console.log('Text length:', text.length);
    } catch(e) {
      console.error('Error:', e.message);
    }
  }
  
  const allText = allResults.map(r => 
    `=== PAGE ${r.page} ===\nURL: ${r.url}\n${r.text}`
  ).join('\n\n');
  fs.writeFileSync('C:/Users/Administrador/Desktop/facturas/ocr_result.txt', allText, 'utf8');
  
  // Also log to console
  console.log('\n========== OCR RESULTS ==========');
  allResults.forEach(r => {
    console.log(`\n=== PAGE ${r.page} ===`);
    console.log(r.text);
  });
  console.log('\n=================================');
  console.log('Done! Saved to ocr_result.txt');
})();