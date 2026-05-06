const https = require('https');
const http = require('http');
const fs = require('fs');

const imagePaths = [
  'C:/Users/Administrador/Desktop/facturas/pdf_pages/page1_img0.jpg',
  'C:/Users/Administrador/Desktop/facturas/pdf_pages/page2_img1.jpg',
  'C:/Users/Administrador/Desktop/facturas/pdf_pages/page3_img2.jpg'
];

function uploadTransferSH(filePath) {
  return new Promise((resolve, reject) => {
    const imageData = fs.readFileSync(filePath);
    const filename = filePath.split('/').pop();
    
    const options = {
      hostname: 'transfer.sh',
      path: '/' + encodeURIComponent(filename),
      method: 'PUT',
      headers: {
        'Content-Type': 'application/octet-stream',
        'Content-Length': imageData.length
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
          console.log('transfer.sh error:', data.substring(0, 200));
          reject(new Error(data));
        }
      });
    });
    req.on('error', reject);
    req.write(imageData);
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
      const url = await uploadTransferSH(p);
      await new Promise(r => setTimeout(r, 3000));
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
    `=== PAGE ${r.page} ===\n${r.text}`
  ).join('\n\n');
  fs.writeFileSync('C:/Users/Administrador/Desktop/facturas/ocr_result.txt', allText, 'utf8');
  
  console.log('\n========== OCR RESULTS ==========');
  allResults.forEach(r => {
    console.log(`\n=== PAGE ${r.page} ===`);
    console.log(r.text);
  });
  console.log('\n=================================');
})();