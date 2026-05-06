const https = require('https');
const fs = require('fs');

const imagePaths = [
  'C:/Users/Administrador/Desktop/facturas/pdf_pages/page1_img0.jpg',
  'C:/Users/Administrador/Desktop/facturas/pdf_pages/page2_img1.jpg',
  'C:/Users/Administrador/Desktop/facturas/pdf_pages/page3_img2.jpg'
];

function callOCRBase64(imagePath) {
  return new Promise((resolve) => {
    const imageData = fs.readFileSync(imagePath);
    const base64 = imageData.toString('base64');
    const pageNum = imagePath.match(/page(\d+)/)[1];
    
    // Use URL form encoding for OCR.space
    const postData = 'base64Image=data:image/jpeg;base64,' + encodeURIComponent(base64) + '&language=spa&detectOrientation=true';
    
    const options = {
      hostname: 'api.ocr.space',
      path: '/parse/image',
      method: 'POST',
      headers: {
        'apikey': 'helloworld',
        'Content-Type': 'application/x-www-form-urlencoded',
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
            console.log('Page', pageNum, '- OK, chars:', json.ParsedResults[0].ParsedText.length);
            resolve(json.ParsedResults[0].ParsedText);
          } else {
            console.log('Page', pageNum, '- Error:', JSON.stringify(json).substring(0, 200));
            resolve('');
          }
        } catch(e) {
          console.error('Page', pageNum, '- Parse error:', e.message);
          resolve('');
        }
      });
    });
    req.on('error', e => { console.error('Page', pageNum, '- Request error:', e.message); resolve(''); });
    req.write(postData);
    req.end();
  });
}

(async () => {
  const allResults = [];
  for (const p of imagePaths) {
    console.log('Processing:', p.split('/').pop());
    const text = await callOCRBase64(p);
    allResults.push({ page: p.match(/page(\d+)/)[1], text });
    await new Promise(r => setTimeout(r, 2000));
  }
  
  const allText = allResults.map(r => `=== PAGE ${r.page} ===\n${r.text}`).join('\n\n');
  fs.writeFileSync('C:/Users/Administrador/Desktop/facturas/ocr_result.txt', allText, 'utf8');
  
  console.log('\n========== ALL OCR RESULTS ==========');
  allResults.forEach(r => {
    console.log(`\n=== PAGE ${r.page} ===`);
    console.log(r.text);
  });
  console.log('\n======================================');
})();