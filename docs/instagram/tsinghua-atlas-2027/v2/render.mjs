import { createRequire } from 'node:module';
import { copyFile, mkdir, writeFile } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const ROOT = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = resolve(ROOT, '../../../../');
const require = createRequire(join(REPO_ROOT, 'studio/cloud/package.json'));
const { chromium } = require('playwright-core');
const IDS = [
  '01-cover', '02-subject-rankings', '03-global-rankings', '04-english-hsk',
  '05-deadlines', '06-tuition-scholarships', '07-cta',
];
const saveOriginals = process.argv.includes('--preserve-originals');
const renderOnly = process.argv.includes('--slides-only');
const issues = {};

await mkdir(join(ROOT, 'png'), { recursive: true });
await mkdir(join(ROOT, 'originals'), { recursive: true });
await mkdir(join(ROOT, 'mobile-324'), { recursive: true });
await mkdir(join(ROOT, 'mobile-375'), { recursive: true });

const browser = await chromium.launch({ headless: true });
try {
  const browserVersion = browser.version();
  for (let index = 1; index <= IDS.length; index++) {
    const n = String(index).padStart(2, '0');
    const id = IDS[index - 1];
    const page = await browser.newPage({
      viewport: { width: 1080, height: 1350 },
      deviceScaleFactor: 1,
      colorScheme: 'light',
      reducedMotion: 'reduce',
    });
    const pageIssues = [];
    page.on('pageerror', error => pageIssues.push(`pageerror: ${error.message}`));
    page.on('console', message => {
      if (message.type() === 'error') pageIssues.push(`console: ${message.text()}`);
    });
    const sourceHTML = join(ROOT, 'source', `${n}.html`);
    await page.goto(pathToFileURL(sourceHTML).href, { waitUntil: 'load' });
    const readiness = await page.evaluate(async () => {
      await document.fonts.ready;
      const images = [...document.querySelectorAll('svg image')];
      const decoded = await Promise.all(images.map(async element => {
        const image = new Image();
        image.src = new URL(element.getAttribute('href'), document.baseURI).href;
        try {
          await image.decode();
          return { src: element.getAttribute('href'), width: image.naturalWidth, height: image.naturalHeight };
        } catch {
          return { src: element.getAttribute('href'), width: 0, height: 0 };
        }
      }));
      const svg = document.querySelector('svg');
      const boxes = [...svg.querySelectorAll('#editable-campaign-copy text')].map(element => {
        const box = element.getBBox();
        return {
          text: element.textContent,
          x: Number(box.x.toFixed(2)),
          y: Number(box.y.toFixed(2)),
          right: Number((box.x + box.width).toFixed(2)),
          bottom: Number((box.y + box.height).toFixed(2)),
        };
      });
      const datePairs = [['20', 'KASIM'], ['28', 'ŞUBAT']];
      const dateOverlaps = datePairs.filter(([leftText, rightText]) => {
        const left = boxes.find(box => box.text === leftText);
        const right = boxes.find(box => box.text === rightText);
        return left && right && left.x < right.right && left.right > right.x
          && left.y < right.bottom && left.bottom > right.y;
      });
      return {
        jostLoaded: document.fonts.check('600 24px Jost'),
        svgWidth: Number(svg.getAttribute('width')),
        svgHeight: Number(svg.getAttribute('height')),
        images: decoded,
        textOverflows: boxes.filter(box => box.x < 0 || box.y < 0 || box.right > 1080 || box.bottom > 1350),
        dateOverlaps,
      };
    });
    if (!readiness.jostLoaded) pageIssues.push('Jost font did not load');
    if (readiness.svgWidth !== 1080 || readiness.svgHeight !== 1350) pageIssues.push('SVG artboard is not 1080x1350');
    if (readiness.textOverflows.length) pageIssues.push(`${readiness.textOverflows.length} editable text line(s) overflow the artboard`);
    if (readiness.dateOverlaps.length) pageIssues.push('day/month date text overlaps');
    for (const image of readiness.images) {
      if (!image.width || !image.height) pageIssues.push(`image failed to decode: ${image.src}`);
    }
    const finalFile = join(ROOT, 'png', `${n}.png`);
    await page.screenshot({ path: finalFile, type: 'png', animations: 'disabled', caret: 'hide' });
    const originalFile = join(ROOT, 'originals', `${n}.png`);
    if (saveOriginals && !existsSync(originalFile)) await copyFile(finalFile, originalFile);

    for (const [size, folder] of [[324, 'mobile-324'], [375, 'mobile-375']]) {
      const height = Math.round(size * 1.25);
      await page.setViewportSize({ width: size, height });
      await page.evaluate(({ width, height }) => {
        document.documentElement.style.cssText = `width:${width}px;height:${height}px;overflow:hidden;margin:0`;
        document.body.style.cssText = `width:${width}px;height:${height}px;overflow:hidden;margin:0`;
        const svg = document.querySelector('svg');
        svg.style.width = `${width}px`;
        svg.style.height = `${height}px`;
      }, { width: size, height });
      await page.screenshot({
        path: join(ROOT, folder, `${n}.png`), type: 'png', animations: 'disabled', caret: 'hide',
      });
    }
    issues[id] = {
      jostLoaded: readiness.jostLoaded,
      issues: pageIssues,
      browser: `Chromium ${browserVersion}`,
      images: readiness.images,
      textOverflows: readiness.textOverflows,
      dateOverlaps: readiness.dateOverlaps,
    };
    await page.close();
  }

  await writeFile(join(ROOT, 'render-validation.json'), `${JSON.stringify(issues, null, 2)}\n`);
  if (!renderOnly) {
    const pages = [
      ['contact-sheet.html', 'contact-sheet.png', 1600, 1200],
      ['source-vs-final-contact-sheet.html', 'source-vs-final-contact-sheet.png', 1440, 1300],
      ['revision-comparison.html', 'revision-comparison.png', 1440, 2200],
      ['mobile-324-contact-sheet.html', 'mobile-324-contact-sheet.png', 1440, 1000],
      ['feed-cover-preview.html', 'feed-cover-preview.png', 1240, 1000],
      ['mobile-preview.html', 'mobile-feed-preview.png', 520, 1120],
    ];
    for (const [htmlName, pngName, width, height] of pages) {
      const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: 1, colorScheme: 'light' });
      const pageIssues = [];
      page.on('pageerror', error => pageIssues.push(`pageerror: ${error.message}`));
      await page.goto(pathToFileURL(join(ROOT, htmlName)).href, { waitUntil: 'load' });
      await page.evaluate(() => document.fonts.ready);
      await page.screenshot({ path: join(ROOT, pngName), type: 'png', fullPage: true, animations: 'disabled' });
      if (pageIssues.length) console.warn(`${htmlName}: ${pageIssues.join('; ')}`);
      await page.close();
    }
  }
  console.log(JSON.stringify({ status: Object.values(issues).every(r => r.issues.length === 0) ? 'PASS' : 'FAIL', slides: IDS.length, browser: `Chromium ${browserVersion}`, preserved_originals: saveOriginals }, null, 2));
  if (Object.values(issues).some(r => r.issues.length)) process.exitCode = 1;
} finally {
  await browser.close();
}
