const fs = require('fs');
const path = require('path');

// pdfjs-dist setup
const pdfjsLib = require('pdfjs-dist/legacy/build/pdf.js');

async function extractText(pdfPath) {
  try {
    const data = new Uint8Array(fs.readFileSync(pdfPath));
    const pdf = await pdfjsLib.getDocument({ data, cMapUrl: 'https://unpkg.com/pdfjs-dist@3.11.174/cmaps/', cMapPacked: true }).promise;
    
    let fullText = '';
    for (let i = 1; i <= pdf.numPages; i++) {
      const page = await pdf.getPage(i);
      const textContent = await page.getTextContent();
      const pageText = textContent.items.map(item => item.str).join(' ');
      fullText += `--- Page ${i} ---\n${pageText}\n\n`;
    }
    
    console.log(fullText);
  } catch (err) {
    console.error('Error:', err.message);
  }
}

const pdfPath = process.argv[2];
if (!pdfPath) {
  console.error('Usage: node extract.js <pdf-path>');
  process.exit(1);
}
extractText(pdfPath);