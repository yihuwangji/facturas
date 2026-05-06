const https = require('https');
const fs = require('fs');
const path = require('path');

const apiKey = 'bd16f87df6msh0a'; // imgbb free tier
const imagePaths = [
  'C:/Users/Administrador/Desktop/facturas/pdf_pages/page1_img0.jpg',
  'C:/Users/Administrador/Desktop/facturas/pdf_pages/page2_img1.jpg',
  'C:/Users/Administrador/Desktop/facturas/pdf_pages/page3_img2.jpg'
];

function uploadImage(filePath) {
  return new Promise((resolve, reject) => {
    const imageData = fs.readFileSync(filePath);
    const base64 = imageData.toString('base64');
    const boundary = '----FormBoundary' + Math.random().toString(36).slice(2);
    
    const body = `--${boundary}\r\n`
      + 'Content-Disposition: form-data; name="image"; filename="invoice.jpg"\r\n'
      + 'Content-Type: image/jpeg\r\n\r\n';
    
    const postData = Buffer.concat([
      Buffer.from(body, 'utf8'),
      Buffer.from(base64, 'base64'),
      Buffer.from(`\r\n--${boundary}--\r\n`, 'utf8')
    ]);
    
    const options = {
      hostname: 'api.imgbb.com',
      path: '/1/upload?key=' + apiKey,
      method: 'POST',
      headers: {
        'Content-Type': 'multipart/form-data; boundary=' + boundary,
        'Content-Length': postData.length
      }
    };
    
    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const json = JSON.parse(data);
          if (json.data && json.data.url) {
            console.log('Uploaded:', path.basename(filePath), '->', json.data.url);
            resolve(json.data.url);
          } else {
            console.log('Upload failed:', data);
            reject(new Error('Upload failed'));
          }
        } catch(e) {
          reject(e);
        }
      });
    });
    req.on('error', reject);
    req.write(postData);
    req.end();
  });
}

(async () => {
  const urls = [];
  for (const p of imagePaths) {
    if (fs.existsSync(p)) {
      try {
        const url = await uploadImage(p);
        urls.push(url);
      } catch(e) {
        console.error('Error uploading', p, e.message);
      }
    } else {
      console.log('File not found:', p);
    }
  }
  console.log('\nAll URLs:', urls);
})();