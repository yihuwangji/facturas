const https = require('https');
const fs = require('fs');

const imgbbKey = 'bd16f87df6msh0a4d5e9f0b1c2d3e4f5'; // free tier demo key
const imagePaths = [
  'C:/Users/Administrador/Desktop/facturas/pdf_pages/page1_img0.jpg',
  'C:/Users/Administrador/Desktop/facturas/pdf_pages/page2_img1.jpg',
  'C:/Users/Administrador/Desktop/facturas/pdf_pages/page3_img2.jpg'
];

function uploadImgBB(filePath) {
  return new Promise((resolve, reject) => {
    const imageData = fs.readFileSync(filePath);
    const base64 = imageData.toString('base64');
    const postData = 'key=' + encodeURIComponent(imgbbKey) + '&image=' + encodeURIComponent(base64);
    const boundary = Math.random().toString(36).slice(2);
    
    const body = 
      '--' + boundary + '\r\n' +
      'Content-Disposition: form-data; name="image"\r\n\r\n' +
      base64 + '\r\n' +
      '--' + boundary + '--\r\n';
    
    const options = {
      hostname: 'api.imgbb.com',
      path: '/1/upload?key=' + imgbbKey,
      method: 'POST',
      headers: {
        'Content-Type': 'multipart/form-data; boundary=' + boundary,
        'Content-Length': Buffer.byteLength(body)
      }
    };
    
    const req = https.request(options, res => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => {
        try {
          const json = JSON.parse(data);
          if (json.data && json.data.url) {
            console.log('Uploaded:', json.data.url);
            resolve(json.data.url);
          } else {
            console.log('imgbb error:', data.substring(0, 300));
            reject(new Error('imgbb failed'));
          }
        } catch(e) {
          reject(e);
        }
      });
    });
    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

function callOCRByURL(imageUrl) {
  return new Promise((resolve, reject) => {
    const postData = JSON.stringify({ url: imageUrl, language: 'spa' });
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
    req.on('error', e => resolve(''));
    req.write(postData);
    req.end();
  });
}

(async () => {
  const allResults = [];
  for (const p of imagePaths) {
    try {
      console.log('\nUploading:', p);
      const url = await uploadImgBB(p);
      console.log('Calling OCR for:', url.substring(0, 80));
      const text = await callOCRByURL(url);
      const pageNum = p.match(/page(\d+)/)[1];
      allResults.push({ page: pageNum, text, url });
      console.log('Text length:', text.length);
    } catch(e) {
      console.error('Error:', e.message);
    }
  }
  
  const allText = allResults.map(r => 
    `=== PAGE ${r.page} ===\n${r.text}`
  ).join('\n\n');
  fs.writeFileSync('C:/Users/Administrador/Desktop/facturas/ocr_result.txt', allText, 'utf8');
  console.log('\nDone! Saved to ocr_result.txt');
})();