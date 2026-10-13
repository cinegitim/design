/* Render six editable SVG slides with Playwright/Chromium and measure geometry.

   Reports Jost loading, per-text bounding boxes, pairwise text collisions,
   text/canonical-lockup collisions, Chinese-mark collisions, icon/label
   collisions and out-of-frame bounds. Any reported issue throws unless
   DRAFT_RENDER is set, so a slide cannot be shipped unreviewed. */
import { createRequire } from 'node:module'
import { dirname, resolve } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'
import { writeFileSync, mkdirSync } from 'node:fs'

const here = dirname(fileURLToPath(import.meta.url))
const require = createRequire(import.meta.url)
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright-core')
const IDS = ['01-cover', '02-fields', '03-atlas', '04-masters', '05-doctorate', '06-dossier']

const browser = await chromium.launch({
  headless: true,
  executablePath: process.env.CHROME_PATH || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  args: ['--allow-file-access-from-files', '--font-render-hinting=none'],
})
const report = {}
try {
  for (const id of IDS) {
    const page = await browser.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 1 })
    await page.goto(pathToFileURL(resolve(here, 'source', id + '.html')).href, { waitUntil: 'networkidle' })
    await page.evaluate(() => document.fonts.ready)
    const info = await page.evaluate(() => {
      const canvas = document.createElement('canvas'), ctx = canvas.getContext('2d')
      const texts = [...document.querySelectorAll('#editable-campaign-copy text')].map(el => {
        const b = el.getBBox(), style = getComputedStyle(el)
        ctx.font = `${style.fontWeight} ${style.fontSize} ${style.fontFamily}`
        const ink = ctx.measureText(el.textContent)
        const baseline = Number(el.getAttribute('y'))
        return {
          copy: el.textContent,
          x: +b.x.toFixed(2), y: +(baseline - ink.actualBoundingBoxAscent).toFixed(2),
          width: +b.width.toFixed(2),
          height: +(ink.actualBoundingBoxAscent + ink.actualBoundingBoxDescent).toFixed(2),
          weight: style.fontWeight, family: style.fontFamily, fontSize: style.fontSize,
        }
      })
      const cjk = [...document.querySelectorAll('#chinese-cultural-marks text')].map(el => {
        const b = el.getBBox()
        return { copy: el.textContent, x: +b.x.toFixed(2), y: +b.y.toFixed(2),
                 width: +b.width.toFixed(2), height: +b.height.toFixed(2) }
      })
      const mark = document.querySelector('#canonical-lockup')
      const r = mark.getBBox()
      return {
        jostLoaded: document.fonts.check('600 96px Jost'),
        cjkLoaded: document.fonts.check('400 24px SongCJK', '\u6e05'),
        textBounds: texts, cjkBounds: cjk,
        logoBounds: { x: +r.x.toFixed(2), y: +r.y.toFixed(2), width: +r.width.toFixed(2), height: +r.height.toFixed(2) },
        viewport: [innerWidth, innerHeight],
      }
    })
    const issues = []
    const SAFE = { x0: 40, y0: 40, x1: 1040, y1: 1310 }
    if (!info.jostLoaded) issues.push(id + ': Jost not loaded')
    if (info.cjkBounds.length && !info.cjkLoaded) issues.push(id + ': SongCJK not loaded')
    for (const b of info.textBounds) {
      if (b.x < SAFE.x0 || b.y < SAFE.y0 || b.x + b.width > SAFE.x1 || b.y + b.height > SAFE.y1)
        issues.push(`${id}: unsafe text bounds ${JSON.stringify(b)}`)
    }
    for (let i = 0; i < info.textBounds.length; i++)
      for (let j = i + 1; j < info.textBounds.length; j++) {
        const a = info.textBounds[i], b = info.textBounds[j]
        if (a.x < b.x + b.width && a.x + a.width > b.x && a.y < b.y + b.height && a.y + a.height > b.y)
          issues.push(`${id}: text collision "${a.copy}" / "${b.copy}"`)
      }
    // Chinese cultural marks must never collide with Turkish copy or the lockup
    for (const c of info.cjkBounds) {
      if (c.x < SAFE.x0 || c.y < SAFE.y0 || c.x + c.width > SAFE.x1 || c.y + c.height > SAFE.y1)
        issues.push(`${id}: unsafe Chinese mark bounds ${JSON.stringify(c)}`)
      for (const b of info.textBounds)
        if (c.x < b.x + b.width && c.x + c.width > b.x && c.y < b.y + b.height && c.y + c.height > b.y)
          issues.push(`${id}: Chinese mark collides with copy "${b.copy}"`)
    }
    const l = info.logoBounds
    if (l.x < SAFE.x0 || l.y < SAFE.y0 || l.x + l.width > SAFE.x1 || l.y + l.height > SAFE.y1)
      issues.push(id + ': unsafe lockup bounds')
    for (const b of info.textBounds)
      if (b.x < l.x + l.width && b.x + b.width > l.x && b.y < l.y + l.height && b.y + b.height > l.y)
        issues.push(`${id}: copy intersects lockup clearspace: "${b.copy}"`)
    for (const c of info.cjkBounds)
      if (c.x < l.x + l.width && c.x + c.width > l.x && c.y < l.y + l.height && c.y + c.height > l.y)
        issues.push(`${id}: Chinese mark intersects lockup: "${c.copy}"`)
    // icon/label geometry (slide 06)
    const icons = await page.evaluate(() =>
      [...document.querySelectorAll('#dossier-icons g')].map(g => {
        const b = g.getBBox()
        return { x: +b.x.toFixed(2), y: +b.y.toFixed(2), width: +b.width.toFixed(2), height: +b.height.toFixed(2) }
      }))
    for (let i = 0; i < icons.length; i++)
      for (const b of info.textBounds)
        if (icons[i].x < b.x + b.width && icons[i].x + icons[i].width > b.x &&
            icons[i].y < b.y + b.height && icons[i].y + icons[i].height > b.y)
          issues.push(`${id}: icon ${i} collides with label "${b.copy}"`)
    info.issues = issues
    info.iconBounds = icons
    if (issues.length && !process.env.DRAFT_RENDER) throw Error(issues.join('\n'))
    mkdirSync(resolve(here, 'final'), { recursive: true })
    mkdirSync(resolve(here, 'originals'), { recursive: true })
    await page.screenshot({ path: resolve(here, 'final', id + '.png'), type: 'png', fullPage: false })
    report[id] = info
    console.log('Rendered', id, issues.length ? issues : 'PASS — Jost loaded, no collisions')
    await page.close()
  }
} finally { await browser.close() }
writeFileSync(resolve(here, 'render-validation.json'), JSON.stringify(report, null, 2))
