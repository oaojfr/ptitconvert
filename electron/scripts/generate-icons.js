/*
  Generate platform icons from assets/icon.svg using sharp.
*/
const fs = require('fs');
const path = require('path');
const sharp = require('sharp');

const svgPath = path.resolve(__dirname, '..', 'assets', 'icon.svg');
const outDir = path.resolve(__dirname, '..', 'assets');

async function ensureDir(p) {
  await fs.promises.mkdir(p, { recursive: true });
}

async function generatePngs() {
  const sizes = [16, 24, 32, 48, 64, 128, 256, 512, 1024];
  await ensureDir(outDir);
  await Promise.all(
    sizes.map(async (size) => {
      const out = path.join(outDir, `icon-${size}.png`);
      await sharp(svgPath).resize(size, size).png({ compressionLevel: 9 }).toFile(out);
    })
  );

  // Extra Linux-friendly filenames expected by electron-builder when icon is a directory
  // Reference: electron-builder looks for 256x256.png, 512x512.png or icon.png (512x512)
  const png256 = path.join(outDir, 'icon-256.png');
  const png512 = path.join(outDir, 'icon-512.png');
  const named256 = path.join(outDir, '256x256.png');
  const named512 = path.join(outDir, '512x512.png');
  const iconPng = path.join(outDir, 'icon.png'); // 512x512
  try {
    if (fs.existsSync(png256)) await fs.promises.copyFile(png256, named256);
    if (fs.existsSync(png512)) {
      await fs.promises.copyFile(png512, named512);
      await fs.promises.copyFile(png512, iconPng);
    }
  } catch (e) {
    console.warn('Warning while creating Linux icon aliases:', e);
  }
}

async function generateIco() {
  const png2icons = require('png2icons');
  const base = fs.readFileSync(path.join(outDir, 'icon-256.png'));
  const icoBuf = png2icons.createICO(base, png2icons.BICUBIC, /*icoCompression=*/0, /*sizes=*/[16,24,32,48,64,128,256]);
  if (!icoBuf) throw new Error('Failed to generate ICO');
  await fs.promises.writeFile(path.join(outDir, 'icon.ico'), icoBuf);
}

async function generateIcns() {
  const png2icons = require('png2icons');
  // Use the 1024 base PNG for best quality
  const base = fs.readFileSync(path.join(outDir, 'icon-1024.png'));
  const icnsBuf = png2icons.createICNS(base, png2icons.BICUBIC, /*icnsCompression=*/0);
  if (!icnsBuf) throw new Error('Failed to generate ICNS');
  await fs.promises.writeFile(path.join(outDir, 'icon.icns'), icnsBuf);
}

async function main() {
  if (!fs.existsSync(svgPath)) throw new Error('Missing assets/icon.svg');
  await generatePngs();
  await generateIco();
  await generateIcns();
  console.log('Icons generated in assets/.');
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
