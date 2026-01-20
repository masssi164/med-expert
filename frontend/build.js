/**
 * Simple build script to bundle the compiled JS into the www directory
 */
const fs = require('fs');
const path = require('path');

const distDir = path.join(__dirname, 'dist');
const wwwDir = path.join(__dirname, '..', 'custom_components', 'med_expert', 'www');

// Ensure www directory exists
if (!fs.existsSync(wwwDir)) {
  fs.mkdirSync(wwwDir, { recursive: true });
}

// Read all JS files from dist and combine them
const files = fs.readdirSync(distDir).filter(f => f.endsWith('.js'));

let bundle = '';
for (const file of files) {
  const content = fs.readFileSync(path.join(distDir, file), 'utf8');
  bundle += content + '\n';
}

// Write to www directory
const outputPath = path.join(wwwDir, 'med-expert-panel.js');
fs.writeFileSync(outputPath, bundle);

console.log(`Built ${outputPath}`);
