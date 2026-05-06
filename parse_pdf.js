const pdf = require('pdf-parse');
const fs = require('fs');
const buf = fs.readFileSync('C:/Users/Administrador/.qclaw/media/inbound/FacturaVenta_FVV26010340---7c0af5f0-3a64-4493-8767-403014f0b9fc.pdf');
pdf(buf).then(d => {
    console.log(d.text);
}).catch(e => {
    console.log('err:' + e.message);
});
