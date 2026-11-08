import fs from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL, fileURLToPath } from 'node:url';
import { execFileSync } from 'node:child_process';

const root = path.dirname(fileURLToPath(import.meta.url));
const source = path.join(root, 'source');
const png = path.join(root, 'png');
const out = path.join(root, 'assets');
const common = await fs.readFile(path.join(out,'carousel.css'),'utf8');
const pw = await import(process.env.PLAYWRIGHT_MODULE || 'playwright');
const launchOptions={headless:true};
if(process.env.CHROME_EXECUTABLE) launchOptions.executablePath=process.env.CHROME_EXECUTABLE;
const browser = await pw.chromium.launch(launchOptions);
const page = await browser.newPage({viewport:{width:1080,height:1350},deviceScaleFactor:1,colorScheme:'light'});
const esc = s => s.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');

const slides = [
  {
    id:'01-cover', label:'KAPAK', lockup:'P-01/light', logo:'p-01-light.svg', w:390,
    html:`<div class="topline"><span>ÜNİVERSİTE ATLASI · 2027</span><span>01 / 07</span></div>
      <img class="logo" src="../assets/p-01-light.svg" style="left:72px;top:52px;width:390px">
      <div class="cover-title"><span>TSINGHUA</span><i>ÜNİVERSİTESİ</i></div>
      <div class="cover-sub">Pekin’de küresel ölçekte<br>bir akademik ekosistem.</div>
      <div class="cover-rank"><strong>14</strong><span>QS WORLD UNIVERSITY<br>RANKINGS 2027</span></div>
      <div class="hero-photo"><img src="../assets/tsinghua-main-building.jpg"><b>PEKİN · HAIDIAN</b></div>
      <div class="cover-bottom"><span>ARAŞTIRMA · EĞİTİM · YENİLİK</span></div>`
  },
  {
    id:'02-rankings', label:'KÜRESEL SIRALAMALAR', lockup:'D-04/light', logo:'d-04-light.svg', w:250,
    html:`<div class="topline"><span>01 — KÜRESEL BAKIŞ</span><span>02 / 07</span></div>
      <h1 class="rank-title">Bir kampüs.<br><em>Üç küresel ölçüt.</em></h1>
      <div class="rank-hero"><strong>#14</strong><div><b>QS</b><span>World University Rankings<br>2027</span></div><small>QS’de 2026’ya göre<br>3 sıra yükseliş</small></div>
      <div class="rank-pair"><article><b>#11</b><span>THE World University<br>Rankings · 2027</span></article><article><b>#6</b><span>U.S. News Best Global<br>Universities · 2026–2027</span></article></div>
      <p class="micro">Sıralamalar farklı metodolojiler kullanır; doğrudan birbirinin yerine geçmez.</p>
      <img class="logo" src="../assets/d-04-light.svg" style="left:72px;bottom:57px;width:250px">`
  },
  {
    id:'03-subjects', label:'ALANLAR', lockup:'D-04/light', logo:'d-04-light.svg', w:250,
    html:`<div class="topline"><span>02 — QS SUBJECT RANKINGS · 2026</span><span>03 / 07</span></div>
      <h1 class="subjects-title">Altı alanda<br><em>ilk 10’da.</em></h1>
      <div class="subject-grid">
        <article><b>07</b><span>Çevre<br>Bilimleri</span></article><article><b>08</b><span>İnşaat ve Yapı<br>Mühendisliği</span></article>
        <article><b>09</b><span>Mimarlık ve Yapılı<br>Çevre</span></article><article><b>09</b><span>Malzeme<br>Bilimleri</span></article>
        <article><b>10</b><span>Veri Bilimi ve<br>Yapay Zekâ</span></article><article><b>10</b><span>Kimya<br>Mühendisliği</span></article>
      </div>
      <p class="micro">QS World University Rankings by Subject 2026 · Dünya sıralaması</p>
      <img class="logo" src="../assets/d-04-light.svg" style="left:72px;bottom:52px;width:250px">`
  },
  {
    id:'04-academic-breadth', label:'AKADEMİK GENİŞLİK', lockup:'D-04/light', logo:'d-04-light.svg', w:250,
    html:`<div class="topline"><span>03 — BİR ÜNİVERSİTEDEN FAZLASI</span><span>04 / 07</span></div>
      <h1 class="breadth-title">Meraktan<br><em>uzmanlığa.</em></h1>
      <div class="campus-photo"><img src="../assets/tsinghua-old-library.jpg"><span>ESKİ KÜTÜPHANE · TSINGHUA ÜNİVERSİTESİ</span></div>
      <div class="breadth-stats"><div><b>93</b><span>lisans<br>ana dalı</span></div><div><b>45</b><span>yan dal</span></div><div><b>12</b><span>disiplin<br>kategorisi</span></div></div>
      <p class="micro">Fen ve mühendislikten beşerî bilimler, hukuka ve disiplinlerarasına.</p>
      <img class="logo" src="../assets/d-04-light.svg" style="left:72px;bottom:48px;width:250px">`
  },
  {
    id:'05-english-programs', label:'İNGİLİZCE PROGRAMLAR', lockup:'D-04/light', logo:'d-04-light.svg', w:250,
    html:`<div class="topline"><span>04 — 2027 LİSANS KABULÜ</span><span>05 / 07</span></div>
      <div class="language-mark"><span>EN</span><i>·</i><b>03</b></div>
      <h1 class="language-title">İngilizce<br><em>öğrenim.</em></h1>
      <p class="language-lead">2027 için duyurulan, tamamen İngilizce yürütülen üç lisans programından örnekler:</p>
      <div class="program-list"><article><b>01</b><span>Global Talents in<br>Science and Engineering</span></article><article><b>02</b><span>Urban Regeneration<br>and Design</span></article><article><b>03</b><span>Politics, Economics and Sociology<br>for Global Leaders in Smart Society</span></article></div>
      <div class="language-note"><strong>Önemli:</strong> Bunlar belirli programlardır; Tsinghua’daki tüm lisans eğitiminin İngilizce olduğu anlamına gelmez.</div>
      <img class="logo" src="../assets/d-04-light.svg" style="left:72px;bottom:43px;width:250px">`
  },
  {
    id:'06-fees-aid', label:'ÜCRETLER & BURSLAR', lockup:'D-04/light', logo:'d-04-light.svg', w:250,
    html:`<div class="topline"><span>05 — MALİYETİ ÖNCEDEN GÖR</span><span>06 / 07</span></div>
      <h1 class="fees-title">Rakamlar<br><em>programa göre.</em></h1>
      <div class="fee-panels"><article><span>SEÇİLİ ÇİNCE–İNGİLİZCE<br>PROGRAMLAR</span><b>¥30.000</b><small>/ yıl · öğrenim ücreti</small></article><article class="dark-panel"><span>GLOBAL TALENTS IN<br>SCIENCE & ENGINEERING</span><b>¥100.000</b><small>/ yıl · öğrenim ücreti</small></article></div>
      <div class="scholarship"><div class="scholar-number">~45<sup>%</sup></div><div><b>2026’da uluslararası lisans birinci sınıf öğrencilerinin yaklaşık %45’i</b><p>Tsinghua International Undergraduate Freshmen Scholarship aldı. Başvuru/ödül koşulları geçerlidir; oran burs garantisi değildir.</p></div></div>
      <p class="micro">Başvuru ücreti: ¥800 · Sağlık sigortası: ¥800/yıl · RMB</p>
      <img class="logo" src="../assets/d-04-light.svg" style="left:72px;bottom:35px;width:250px">`
  },
  {
    id:'07-deadlines', label:'BAŞVURU TAKVİMİ', lockup:'D-04/dark', logo:'d-04-dark.svg', w:250,
    html:`<div class="topline light-top"><span>06 — 2027 GİRİŞİ</span><span>07 / 07</span></div>
      <h1 class="deadline-title">Takvimini<br><i>işaretle.</i></h1>
      <div class="deadline-line"><div class="deadline-item"><span>1. TUR · KAPANIŞ</span><b>20</b><strong>KASIM 2026</strong><small>17.00 · Pekin saati</small></div><div class="timeline"></div><div class="deadline-item"><span>2. TUR · KAPANIŞ</span><b>28</b><strong>ŞUBAT 2027</strong><small>17.00 · Pekin saati</small></div></div>
      <p class="deadline-note">Başvurular 30 Eylül 2026’da açıldı. İkinci tur 21 Kasım 2026’da başlıyor. Bazı programların tur kısıtları olabilir; resmî takvimi ve program kılavuzunu kontrol et.</p>
      <a class="apply" href="https://apply.join-tsinghua.edu.cn/international">RESMÎ BAŞVURU SİSTEMİ ↗</a>
      <img class="logo" src="../assets/d-04-dark.svg" style="left:72px;bottom:48px;width:250px">`
  }
];

const coverFix = `.cover-title{top:465px;font-size:118px}.cover-title i{font-size:88px}.cover-sub{top:665px;font-size:29px}.cover-rank{top:806px;width:395px;height:196px}.cover-rank strong{font-size:154px}.cover-rank span{font-size:18px}.hero-photo{width:500px;height:700px}`;

await fs.mkdir(source,{recursive:true});
await fs.mkdir(png,{recursive:true});
for (const [i,s] of slides.entries()) {
  const html=`<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Tsinghua Atlası — ${esc(s.id)}</title><style>${common}${coverFix}</style></head><body><main class="slide" data-slide="${s.id}">${s.html}</main></body></html>`;
  const file=path.join(source,`${String(i+1).padStart(2,'0')}.html`);
  await fs.writeFile(file,html);
  await page.goto(pathToFileURL(file).href,{waitUntil:'networkidle'});
  await page.evaluate(()=>document.fonts.ready);
  await page.screenshot({path:path.join(png,`${String(i+1).padStart(2,'0')}.png`),type:'png'});
}

const cards=slides.map((s,i)=>`<article><img src="png/${String(i+1).padStart(2,'0')}.png"><b>${String(i+1).padStart(2,'0')} · ${s.label}</b></article>`).join('');
const sheet=`<!doctype html><meta charset="utf-8"><style>*{box-sizing:border-box}body{margin:0;background:#D8D2C7;font:14px Arial,sans-serif}.sheet{width:1360px;margin:auto;padding:28px;display:grid;grid-template-columns:repeat(3,1fr);gap:20px}article{background:#F7F3E9;padding:10px;box-shadow:0 4px 18px #1D202722}img{width:100%;display:block}b{display:block;padding:9px 2px 0;color:#1D2027;letter-spacing:.07em}</style><main class="sheet">${cards}</main>`;
await fs.writeFile(path.join(root,'contact-sheet.html'),sheet);
execFileSync('rsvg-convert',['-w','1360','-o',path.join(root,'contact-sheet.png'),path.join(root,'contact-sheet.svg')]);
await browser.close();
console.log(`Rendered ${slides.length} 1080x1350 slides.`);
