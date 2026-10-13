/* Render the copy-free art-direction plates used as recorded originals. */
import { createRequire } from 'node:module'
import { dirname, resolve } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'
import { mkdirSync } from 'node:fs'

const here = dirname(fileURLToPath(import.meta.url))
const require = createRequire(import.meta.url)
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright-core')
const IDS = ['01-cover', '02-fields', '03-atlas', '04-masters', '05-doctorate', '06-dossier']

const browser = await chromium.launch({
  headless: true,
  executablePath: process.env.CHROME_PATH || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  args: ['--allow-file-access-from-files', '--font-render-hinting=none'],
})
try {
  for (const id of IDS) {
    const page = await browser.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 1 })
    await page.goto(pathToFileURL(resolve(here, 'source', id + '-plate.html')).href, { waitUntil: 'networkidle' })
    await page.evaluate(() => document.fonts.ready)
    mkdirSync(resolve(here, 'originals'), { recursive: true })
    await page.screenshot({ path: resolve(here, 'originals', id + '.png'), type: 'png', fullPage: false })
    console.log('Plate', id)
    await page.close()
  }
} finally { await browser.close() }
