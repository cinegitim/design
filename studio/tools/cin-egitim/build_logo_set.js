#!/usr/bin/env node
/**
 * Deterministic Logo Set Builder for Çin Eğitim (brands/cin-egitim)
 *
 * Conforms to:
 * - Canonical Symbol SHA-256 lock: 1cc1808947d8f7f759ebb9956a715d535bb4fcc985d3f85194d4eaf1a85c7381
 * - Approved Typographic Direction: Option 1 (Source Serif 4 SemiBold 600)
 * - Variants: P-01 (Primary Horizontal), H-02 (Stacked Centered), C-03 (Compact Inline), D-04 (Avatar / Favicon)
 * - Color variations: light, dark, mono-black, mono-white
 * - Outlines: pure vector SVG path data with zero external runtime font dependency.
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const opentype = require('./node_modules/opentype.js');

const ROOT = path.resolve(__dirname, '../../../');
const SYMBOL_PATH = path.join(ROOT, 'brands/cin-egitim/assets/symbol.svg');
const FONT_PATH = path.join(__dirname, 'fonts/SourceSerif4-SemiBold.ttf');
const ASSETS_OUT = path.join(ROOT, 'brands/cin-egitim/assets/lockups');
const DOCS_OUT = path.join(ROOT, 'docs/cin-egitim/assets/lockups');

const CANONICAL_SHA = '1cc1808947d8f7f759ebb9956a715d535bb4fcc985d3f85194d4eaf1a85c7381';

// 1. Verify Canonical Symbol
const symbolContent = fs.readFileSync(SYMBOL_PATH, 'utf8');
const symbolSha = crypto.createHash('sha256').update(symbolContent).digest('hex');
if (symbolSha !== CANONICAL_SHA) {
  console.error(`FATAL: Canonical symbol SHA-256 mismatch!\nExpected: ${CANONICAL_SHA}\nGot:      ${symbolSha}`);
  process.exit(1);
}
console.log(`✓ Canonical symbol integrity verified: ${symbolSha}`);

// Extract symbol paths
const brushMatch = symbolContent.match(/<g[^>]*id="brush-ring"[^>]*>[\s\S]*?<path\s+d="([^"]+)"/);
const pagodaMatch = symbolContent.match(/<g[^>]*id="pagoda-and-ink-ground"[^>]*>[\s\S]*?<path\s+d="([^"]+)"/);

if (!brushMatch || !pagodaMatch) {
  console.error('FATAL: Could not extract path data from canonical symbol.svg');
  process.exit(1);
}

const BRUSH_PATH = brushMatch[1];
const PAGODA_PATH = pagodaMatch[1];

// 2. Load Font
const fontBuf = fs.readFileSync(FONT_PATH);
const font = opentype.parse(fontBuf.buffer.slice(fontBuf.byteOffset, fontBuf.byteOffset + fontBuf.byteLength));
console.log('✓ Font loaded successfully: Source Serif 4 SemiBold');

// Helper to render symbol SVG group
function renderSymbol(theme, x, y, width, height) {
  let brushColor = '#BF0C1A';
  let pagodaColor = '#202020';

  if (theme === 'dark') {
    brushColor = '#BF0C1A';
    pagodaColor = '#FFFFFF';
  } else if (theme === 'mono-black') {
    brushColor = '#111111';
    pagodaColor = '#111111';
  } else if (theme === 'mono-white') {
    brushColor = '#FFFFFF';
    pagodaColor = '#FFFFFF';
  }

  return `  <svg viewBox="0 0 916 924" x="${x.toFixed(2)}" y="${y.toFixed(2)}" width="${width.toFixed(2)}" height="${height.toFixed(2)}" role="img" aria-label="Çin Eğitim Kanonik Sembol">
    <g transform="translate(0,924) scale(0.01,-0.01)" fill="${brushColor}">
      <path d="${BRUSH_PATH}" />
    </g>
    <g transform="translate(0,924) scale(0.01,-0.01)" fill="${pagodaColor}">
      <path d="${PAGODA_PATH}" />
    </g>
  </svg>`;
}

// Helper to get text color
function getTextColor(theme) {
  if (theme === 'dark' || theme === 'mono-white') {
    return '#FFFFFF';
  }
  return '#111111';
}

function pathToSvg(path) {
  let d = '';
  for (const cmd of path.commands) {
    if (cmd.type === 'M') d += 'M' + cmd.x.toFixed(2) + ' ' + cmd.y.toFixed(2);
    else if (cmd.type === 'L') d += 'L' + cmd.x.toFixed(2) + ' ' + cmd.y.toFixed(2);
    else if (cmd.type === 'C') d += 'C' + cmd.x1.toFixed(2) + ' ' + cmd.y1.toFixed(2) + ' ' + cmd.x2.toFixed(2) + ' ' + cmd.y2.toFixed(2) + ' ' + cmd.x.toFixed(2) + ' ' + cmd.y.toFixed(2);
    else if (cmd.type === 'Q') d += 'Q' + cmd.x1.toFixed(2) + ' ' + cmd.y1.toFixed(2) + ' ' + cmd.x.toFixed(2) + ' ' + cmd.y.toFixed(2);
    else if (cmd.type === 'Z') d += 'Z';
  }
  return d;
}

// 3. Build Lockups

const lockupRecords = [];

function saveSvg(filename, svgContent, record) {
  fs.mkdirSync(ASSETS_OUT, { recursive: true });
  fs.mkdirSync(DOCS_OUT, { recursive: true });

  const p1 = path.join(ASSETS_OUT, filename);
  const p2 = path.join(DOCS_OUT, filename);

  fs.writeFileSync(p1, svgContent, 'utf8');
  fs.writeFileSync(p2, svgContent, 'utf8');

  const sha = crypto.createHash('sha256').update(svgContent).digest('hex');
  record.file_name = filename;
  record.path = `brands/cin-egitim/assets/lockups/${filename}`;
  record.sha256 = sha;
  lockupRecords.push(record);
  console.log(`  ✓ Generated ${filename} (${sha.substring(0, 8)})`);
}

// THEMES
const themes = [
  { id: 'light', name: 'Açık Zemin (Light / Kurumsal Renkli)' },
  { id: 'dark', name: 'Koyu Zemin (Dark / Ters Kontrast)' },
  { id: 'mono-black', name: 'Monokrom Siyah (Mono Black)' },
  { id: 'mono-white', name: 'Monokrom Beyaz (Mono White / Negatif)' }
];

// VARIANT 1: P-01 Primary Horizontal (Yatay Ana Logo - 2 Satır)
// Symbol: 118.96 x 120 (ratio 916:924)
// Wordmark: Line 1 "Çin", Line 2 "Eğitim"
console.log('\n--- Building P-01 Primary Horizontal Lockups ---');
for (const t of themes) {
  const textColor = getTextColor(t.id);
  const pathCin = pathToSvg(font.getPath('Çin', 145, 50, 50, { letterSpacing: -0.03 }));
  const pathEgitim = pathToSvg(font.getPath('Eğitim', 145, 98, 48, { letterSpacing: -0.03 }));

  const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 120" width="300" height="120" role="img" aria-label="Çin Eğitim — P-01 Yatay Ana Logo (${t.name})">
  <title>Çin Eğitim — P-01 Yatay Ana Logo (${t.name})</title>
${renderSymbol(t.id, 0, 0, 118.96, 120)}
  <g id="wordmark-p01" fill="${textColor}">
    <path id="wm-cin" d="${pathCin}" />
    <path id="wm-egitim" d="${pathEgitim}" />
  </g>
</svg>
`;
  saveSvg(`p-01-horizontal-${t.id}.svg`, svg, {
    variant_id: 'P-01',
    variant_name: 'Primary Horizontal (Yatay Ana Logo)',
    arrangement: 'horizontal, 2-line wordmark',
    theme: t.id,
    dimensions: { width: 300, height: 120, viewBox: '0 0 300 120' },
    typography: { primary: 'Source Serif 4 SemiBold 600', lines: ['Çin', 'Eğitim'] }
  });
}

// VARIANT 2: H-02 Stacked Centered (Dikey / Merkezi Logo)
// Symbol centered on top, "Çin Eğitim" centered below
console.log('\n--- Building H-02 Stacked Centered Lockups ---');
for (const t of themes) {
  const textColor = getTextColor(t.id);
  // Wordmark width for "Çin Eğitim" at 34px is ~172px. Center in 200px box -> X = 14
  const pathFull = pathToSvg(font.getPath('Çin Eğitim', 14, 154, 34, { letterSpacing: -0.02 }));

  const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 174" width="200" height="174" role="img" aria-label="Çin Eğitim — H-02 Dikey / Merkezi Logo (${t.name})">
  <title>Çin Eğitim — H-02 Dikey / Merkezi Logo (${t.name})</title>
${renderSymbol(t.id, 40.52, 0, 118.96, 120)}
  <g id="wordmark-h02" fill="${textColor}">
    <path id="wm-cin-egitim" d="${pathFull}" />
  </g>
</svg>
`;
  saveSvg(`h-02-stacked-${t.id}.svg`, svg, {
    variant_id: 'H-02',
    variant_name: 'Stacked Centered (Dikey / Merkezi Logo)',
    arrangement: 'stacked centered, 1-line wordmark below',
    theme: t.id,
    dimensions: { width: 200, height: 174, viewBox: '0 0 200 174' },
    typography: { primary: 'Source Serif 4 SemiBold 600', lines: ['Çin Eğitim'] }
  });
}

// VARIANT 3: C-03 Compact Inline (Kompakt Tek Satır Yatay)
// Symbol: 59.48 x 60. Wordmark single line next to symbol
console.log('\n--- Building C-03 Compact Inline Lockups ---');
for (const t of themes) {
  const textColor = getTextColor(t.id);
  // "Çin Eğitim" at 30px, X = 74, baseline = 40.5
  const pathFull = pathToSvg(font.getPath('Çin Eğitim', 74, 40.5, 30, { letterSpacing: -0.02 }));

  const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 235 60" width="235" height="60" role="img" aria-label="Çin Eğitim — C-03 Kompakt Tek Satır Logo (${t.name})">
  <title>Çin Eğitim — C-03 Kompakt Tek Satır Logo (${t.name})</title>
${renderSymbol(t.id, 0, 0, 59.48, 60)}
  <g id="wordmark-c03" fill="${textColor}">
    <path id="wm-cin-egitim-compact" d="${pathFull}" />
  </g>
</svg>
`;
  saveSvg(`c-03-inline-${t.id}.svg`, svg, {
    variant_id: 'C-03',
    variant_name: 'Compact Inline (Kompakt Tek Satır Logo)',
    arrangement: 'horizontal, 1-line wordmark',
    theme: t.id,
    dimensions: { width: 235, height: 60, viewBox: '0 0 235 60' },
    typography: { primary: 'Source Serif 4 SemiBold 600', lines: ['Çin Eğitim'] }
  });
}

// VARIANT 4: D-04 Digital Avatars & Favicon
console.log('\n--- Building D-04 Digital Avatars & Favicon ---');
// D-04 Square Light
const avatarSqLight = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512" role="img" aria-label="Çin Eğitim — D-04 Kare Avatar (Light)">
  <title>Çin Eğitim — D-04 Kare Avatar (Light)</title>
  <rect width="512" height="512" rx="64" fill="#FAF7F2" />
${renderSymbol('light', 81, 78, 350, 353.05)}
</svg>
`;
saveSvg('d-04-avatar-square-light.svg', avatarSqLight, {
  variant_id: 'D-04/square-light',
  variant_name: 'Square Avatar Light',
  arrangement: '1:1 square icon',
  theme: 'light',
  dimensions: { width: 512, height: 512, viewBox: '0 0 512 512' }
});

// D-04 Square Dark
const avatarSqDark = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512" role="img" aria-label="Çin Eğitim — D-04 Kare Avatar (Dark)">
  <title>Çin Eğitim — D-04 Kare Avatar (Dark)</title>
  <rect width="512" height="512" rx="64" fill="#141414" />
${renderSymbol('dark', 81, 78, 350, 353.05)}
</svg>
`;
saveSvg('d-04-avatar-square-dark.svg', avatarSqDark, {
  variant_id: 'D-04/square-dark',
  variant_name: 'Square Avatar Dark',
  arrangement: '1:1 square icon',
  theme: 'dark',
  dimensions: { width: 512, height: 512, viewBox: '0 0 512 512' }
});

// D-04 Circle Light (Social Media Profile Picture)
const avatarCirLight = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512" role="img" aria-label="Çin Eğitim — D-04 Dairesel Avatar (Light)">
  <title>Çin Eğitim — D-04 Dairesel Avatar (Light)</title>
  <circle cx="256" cy="256" r="256" fill="#FAF7F2" />
${renderSymbol('light', 96, 93, 320, 322.8)}
</svg>
`;
saveSvg('d-04-avatar-circle-light.svg', avatarCirLight, {
  variant_id: 'D-04/circle-light',
  variant_name: 'Circular Profile Picture Light',
  arrangement: '1:1 circular social media avatar',
  theme: 'light',
  dimensions: { width: 512, height: 512, viewBox: '0 0 512 512' }
});

// D-04 Circle Dark (Social Media Profile Picture)
const avatarCirDark = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512" role="img" aria-label="Çin Eğitim — D-04 Dairesel Avatar (Dark)">
  <title>Çin Eğitim — D-04 Dairesel Avatar (Dark)</title>
  <circle cx="256" cy="256" r="256" fill="#141414" />
${renderSymbol('dark', 96, 93, 320, 322.8)}
</svg>
`;
saveSvg('d-04-avatar-circle-dark.svg', avatarCirDark, {
  variant_id: 'D-04/circle-dark',
  variant_name: 'Circular Profile Picture Dark',
  arrangement: '1:1 circular social media avatar',
  theme: 'dark',
  dimensions: { width: 512, height: 512, viewBox: '0 0 512 512' }
});

// D-04 Favicon (64x64)
const favicon = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64" role="img" aria-label="Çin Eğitim — Favicon">
  <title>Çin Eğitim — Favicon</title>
${renderSymbol('light', 4.2, 4, 55.45, 56)}
</svg>
`;
saveSvg('d-04-favicon.svg', favicon, {
  variant_id: 'D-04/favicon',
  variant_name: 'Digital Favicon',
  arrangement: '1:1 browser favicon',
  theme: 'light',
  dimensions: { width: 64, height: 64, viewBox: '0 0 64 64' }
});

// 4. Write Manifest: canonical-lockups.json
const manifest = {
  brand_id: 'cin-egitim',
  name: 'Çin Eğitim',
  status: 'PRODUCED / CANONICAL LOCKUP FAMILY',
  human_selection: {
    typography_choice: 'Option 1 (Yön A: Modern Editoryal)',
    primary_font: 'Source Serif 4 (SemiBold 600)',
    support_font: 'Manrope (Medium / Regular)',
    canonical_symbol_sha256: CANONICAL_SHA,
    generation_date: '2026-10-14'
  },
  guidelines: {
    clear_space: {
      unit: 'X = Height of capital Ç or half of symbol radius',
      minimum_margin: '0.75X to 1X exclusion zone on all 4 sides'
    },
    minimum_sizes: {
      'P-01': { digital: '36px height', print: '18mm height' },
      'H-02': { digital: '64px height', print: '25mm height' },
      'C-03': { digital: '26px height', print: '12mm height' },
      'D-04': { digital: '24px height', print: '8mm height' }
    },
    colors: {
      vermilion_red: '#BF0C1A',
      deep_ink_black: '#202020',
      text_dark: '#111111',
      paper_ivory: '#FAF7F2',
      dark_surface: '#121212',
      pure_white: '#FFFFFF'
    }
  },
  total_lockups: lockupRecords.length,
  records: lockupRecords
};

const manifestPathAssets = path.join(ASSETS_OUT, 'canonical-lockups.json');
const manifestPathDocs = path.join(DOCS_OUT, 'canonical-lockups.json');

fs.writeFileSync(manifestPathAssets, JSON.stringify(manifest, null, 2), 'utf8');
fs.writeFileSync(manifestPathDocs, JSON.stringify(manifest, null, 2), 'utf8');

console.log(`\n✓ Successfully generated ${lockupRecords.length} lockup SVGs and manifest!`);
