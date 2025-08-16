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
}

async function generateIco() {
  const toIco = (await import('to-ico')).default;
  const pngs = [16, 24, 32, 48, 64, 128, 256].map((s) => fs.readFileSync(path.join(outDir, `icon-${s}.png`)));
  const buf = await toIco(pngs);
  await fs.promises.writeFile(path.join(outDir, 'icon.ico'), buf);
}

async function generateIcns() {
  // Build minimal ICNS from 256/512/1024 PNGs
  const icns = require('icns-builder');
  const sources = [256, 512, 1024]
    .map((s) => ({ size: s, filePath: path.join(outDir, `icon-${s}.png`) }));
  const buf = await icns(sources);
  await fs.promises.writeFile(path.join(outDir, 'icon.icns'), buf);
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
