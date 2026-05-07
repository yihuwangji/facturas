const fs = require('fs');
const c = fs.readFileSync('C:\\Users\\Administrador\\Desktop\\facturas\\data.js', 'utf8');
const lines = c.split('\n');
for (let i = 0; i < lines.length; i++) {
  const l = lines[i].trim();
  // Find lines with double quotes like: "value"",
  if (l.match(/"[^"]*""[,\s]/)) {
    console.log((i+1) + ': ' + l.substring(0, 120));
  }
}
