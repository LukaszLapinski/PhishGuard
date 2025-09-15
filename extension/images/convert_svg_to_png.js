// SVG to PNG conversion script
// This requires Node.js with sharp package installed

const fs = require('fs');
const path = require('path');
const sharp = require('sharp');

// SVG files to convert
const svgFiles = [
  'icon16.svg',
  'icon48.svg',
  'icon128.svg',
  'icon16_danger.svg',
  'icon48_danger.svg',
  'icon128_danger.svg'
];

// Path to this directory
const dir = __dirname;

// Convert each SVG file to PNG
async function convertAll() {
  console.log('Converting SVG files to PNG...');
  
  for (const svgFile of svgFiles) {
    const pngFile = svgFile.replace('.svg', '.png');
    const svgPath = path.join(dir, svgFile);
    const pngPath = path.join(dir, pngFile);
    
    // Skip if SVG file doesn't exist
    if (!fs.existsSync(svgPath)) {
      console.log(`File not found: ${svgPath}`);
      continue;
    }
    
    try {
      const svg = fs.readFileSync(svgPath);
      const size = parseInt(pngFile.match(/\d+/)[0], 10);
      
      await sharp(svg)
        .resize(size, size)
        .png()
        .toFile(pngPath);
      
      console.log(`Converted ${svgFile} to ${pngFile}`);
    } catch (err) {
      console.error(`Error converting ${svgFile}:`, err.message);
    }
  }
  
  console.log('Conversion complete!');
}

convertAll(); 