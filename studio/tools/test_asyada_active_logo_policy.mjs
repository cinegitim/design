import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';

const root=path.resolve(import.meta.dirname,'../..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8');
const json=p=>JSON.parse(read(p));
const fileSha=p=>createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const manifestPath='brands/asyada-egitim/assets/lockups/canonical-lockups.json';
const manifest=json(manifestPath);
const brand=json('brands/asyada-egitim/brand.json');
const approved=['H-02','P-01','F-05'];
const active=manifest.records.filter(x=>x.status==='APPROVED / CANONICAL');
const retired=manifest.records.filter(x=>x.status==='RETIRED / HISTORY ONLY');
const ids=new Set(active.map(x=>x.variant_id));

test('only H-02, P-01 and F-05 are active; original SVG hashes are unchanged',()=>{
 assert.deepEqual([...ids].sort(),[...approved].sort());
 assert.equal(manifest.records.length,15);
 assert.equal(active.length,9);
 assert.equal(retired.length,6);
 assert.deepEqual(new Set(retired.map(x=>x.variant_id)),new Set(['C-03','D-04']));
 assert.deepEqual(brand.canonicalLockups.approvedVariants,approved);
 assert.equal(brand.canonicalLockups.defaultVariant,'H-02');
 assert.deepEqual(manifest.current_variant_ids,approved);
 assert.equal(manifest.default_variant_id,'H-02');
 assert.equal(brand.canonicalLockups.records.length,9);
 assert.equal(brand.canonicalLockups.manifestSha256,fileSha(manifestPath));
 for(const r of manifest.records)assert.equal(fileSha(r.canonical_file_path),r.sha256);
 assert.deepEqual(new Set(manifest.retired_variants.map(x=>x.id)),new Set(['C-03','D-04']));
});
test('H-02 compact display keeps the complete canonical artwork',()=>{
 const h=active.filter(x=>x.variant_id==='H-02');
 assert.equal(h.length,3);
 for(const r of h){
  assert.equal(r.minimum_supported_display_size.screen_width_px,528);
  assert.equal(r.small_digital_minimum_px,320);
  assert.deepEqual(r.recommended_screen_width_px,[360,480]);
  assert.equal(r.minimum_supported_display_size.print_width_mm,110);
  assert.match(r.usage_rules.join(' '),/proportionally/i);
 }
 assert.equal(brand.canonicalLockups.smallDigital.variant,'H-02');
 assert.equal(brand.canonicalLockups.smallDigital.minWidthPx,320);
 assert.match(manifest.small_digital_rule,/V-01/);
});
test('active galleries remove C-03 and D-04 cards and display H-02 compact examples',()=>{
 const page=read('docs/workspaces/asyada-egitim/logos-and-covers/index.html');
 const englishStart=page.indexOf('<section class="section" id="english-logo">');
 const logo=page.slice(page.indexOf('<section class="section" id="logos">'),englishStart>=0?englishStart:page.indexOf('<section class="section" id="profile">'));
 assert.ok(logo.includes('H-02 · Temel yatay imza'));
 assert.ok(logo.includes('id="logos"'));
 assert.ok(logo.includes('id="profile"')===false);
 assert.ok(logo.includes('H-02/light')===false); // same original asset, no new synthetic lockup id
 assert.ok(logo.includes('h-02-primary-horizontal-light.svg'));
 assert.ok(logo.includes('h-02-primary-horizontal-dark.svg'));
 assert.ok(!/src="[^"]*(c-03|d-04)/i.test(logo));
 assert.equal((logo.match(/class="card(?: feature)?"/g)||[]).length,3);
 if(englishStart>=0){
  const review=page.slice(englishStart,page.indexOf('<section class="section" id="profile">'));
  assert.match(review,/Görsel onay bekliyor/);
  assert.match(review,/H-EN-02/);
  assert.match(review,/P-EN-01/);
 }
 const identity=read('docs/identity/index.html');
 const englishIdentityStart=identity.indexOf('<section id="english-logo">');
 const active=identity.slice(identity.indexOf('<section id="lockups">'),englishIdentityStart>=0?englishIdentityStart:identity.indexOf('<section id="rules">'));
 assert.ok(active.includes('id="small-digital"'));
 assert.ok(!active.includes('id="C-03"')&&!active.includes('id="D-04"'));
 assert.ok(identity.includes('320px'));
 if(englishIdentityStart>=0){
  const review=identity.slice(englishIdentityStart,identity.indexOf('<section id="rules">'));
  assert.match(review,/henüz üretim için onaylı kimlik değildir/);
  assert.match(review,/english-only\/assets\/h-en-02-horizontal-light.svg/);
 }
});
test('retired artwork remains for past deliverables but is prohibited in future production',()=>{
 assert.ok(fs.existsSync(path.join(root,'brands/asyada-egitim/assets/lockups/c-03-compact-light.svg')));
 assert.ok(fs.existsSync(path.join(root,'brands/asyada-egitim/assets/lockups/d-04-small-use-digital-light.svg')));
 assert.match(read('AGENTS.md'),/C-03 and D-04 are retired/);
 assert.match(read('studio/production/chatgpt/EXECUTION.md'),/Eski C-03 ve D-04/);
 assert.match(read('brands/asyada-egitim/decisions/2026-10-30-h02-small-use-retire-c03-d04.md'),/Arşiv ayrımı/);
 const verification=json('brands/asyada-egitim/assets/lockups/verification-result.json');
 assert.equal(verification.checked_records,15);
 assert.equal(verification.active_records,9);
 assert.equal(verification.retired_records,6);
 assert.equal(verification.manifest_sha256,fileSha(manifestPath));
 assert.equal(verification.records.length,15);
 assert.deepEqual(json('docs/asyada-seal/canonical-lockups/assets/canonical-lockups.json').records,manifest.records);
});


test('English V6 canonical alignment, lighter main and five-country subtitle: source seal, vectors, mirrors and dot alignment',()=>{
 const review=json('brands/asyada-egitim/assets/english-only-candidates/review-manifest.json');
 assert.equal(review.version,'v7.1-even-optical-tracking');
 assert.equal(review.english_headline_weight,450);
 assert.equal(review.country_line_font_weight,350);
 assert.equal(review.country_separator_count,4);
 assert.deepEqual(review.country_labels,['China','Hong Kong','Japan','Singapore','South Korea']);
 assert.equal(review.approved_for_production,false);
 assert.equal(review.canonical_registration,false);
 for(const layout of [{stem:'h-en-02-horizontal',parent:'h-02-primary-horizontal'},{stem:'p-en-01-stacked',parent:'p-01-primary-stacked'}]){
  for(const tone of ['light','dark','monochrome']){
   const name=layout.stem+'-'+tone+'.svg';
   const file='brands/asyada-egitim/assets/english-only-candidates/'+name;
   const svg=read(file),publicFile=read('docs/identity/english-only/assets/'+name);
   const source=read('brands/asyada-egitim/assets/lockups/'+layout.parent+'-'+tone+'.svg');
   const seal=x=>{const i=x.indexOf('<svg viewBox="0 0 400 370"');return x.slice(i,x.indexOf('</svg>',i)+6);};
   assert.equal(svg,publicFile);
   assert.equal(seal(svg),seal(source));
   const meta=JSON.parse(svg.split('<metadata>')[1].split('</metadata>')[0]);
   assert.equal(meta.version,'v7.1-even-optical-tracking');
   assert.equal(meta.status,'REVIEW_ONLY_HUMAN_APPROVAL_PENDING');
   assert.equal(meta.mainWeight,450);
   assert.equal(meta.taglineWeight,350);
   assert.equal(meta.sourceCanonicalLockup,layout.parent+'-'+tone+'.svg');
   assert.ok(meta.metrics.tagWidth<=meta.metrics.topWidth);
   assert.ok(meta.metrics.lowerWidth<meta.metrics.topWidth);
   assert.ok(Math.abs(meta.metrics.asiaScale-1.10)<0.00001);
   assert.ok(Math.abs(meta.metrics.inScale-0.88)<0.00001);
   assert.equal(meta.metrics.lowerBaseline,409);
   assert.equal(meta.metrics.countryBaseline,495);
   assert.ok(Math.abs(meta.metrics.rootCanvasHeight-(layout.stem.startsWith('h-')?587.56787109:1003.79998779))<0.0001);
   assert.ok(meta.metrics.line2VisualTop>meta.metrics.line1VisualBottom);
   assert.ok(meta.metrics.countryVisualTop>meta.metrics.line2VisualBottom);
   assert.match(svg,/data-wordmark="english-v5-jost-450"/);
   assert.deepEqual([...svg.matchAll(/data-country="([^"]+)"/g)].map(x=>x[1]),['CHINA','HONG KONG','JAPAN','SINGAPORE','SOUTH KOREA']);
   const bullets=[...svg.matchAll(/<circle data-country-dot="\d"[^>]*>/g)].map(x=>x[0]);
   assert.equal(bullets.length,4);
   assert.ok(bullets.every(x=>x.includes('cy="-12.3"')));
   assert.ok(bullets.every(x=>x.includes('fill="'+(tone==='monochrome'?'#1D2027':'#BD2120')+'"')));
   assert.ok(!svg.includes('<text'));
   assert.ok(!svg.includes('<image'));
  }
 }
});


test('English V6 uses canonical Turkish lockup canvas heights and baselines without changing the glyph outlines',()=>{
 const manifest=json('brands/asyada-egitim/assets/english-only-candidates/review-manifest.json');
 assert.equal(manifest.version,'v7.1-even-optical-tracking');
 assert.equal(manifest.alignment.targetMainLineBaseline,209);
 assert.equal(manifest.alignment.targetSecondLineBaseline,409);
 assert.equal(manifest.alignment.targetCountryBaseline,495);
 for(const stem of ['h-en-02-horizontal','p-en-01-stacked']){
  for(const tone of ['light','dark','monochrome']){
   const s=read('brands/asyada-egitim/assets/english-only-candidates/'+stem+'-'+tone+'.svg');
   const m=JSON.parse(s.split('<metadata>')[1].split('</metadata>')[0]);
   assert.equal(m.version,'v7.1-even-optical-tracking');
   assert.ok(m.metrics.asiaScale<=1.10);
   assert.ok(m.metrics.inScale<=0.88);
   assert.ok(m.metrics.countryVisualBottom<=502.05);
   assert.ok(m.metrics.line2VisualBottom<=412);
   const tag=s.match(/<g data-line="COUNTRIES"[^>]*>/)?.[0];
   const asia=s.match(/<g data-line="ASIA"[^>]*>/)?.[0];
   assert.match(tag,/ 495\)/);
   assert.match(asia,/ 409\)/);
  }
 }
});


test('English V7.1 balances the second line with symmetric strokes but never changes approved seal geometry',()=>{
 const manifest=json('brands/asyada-egitim/assets/english-only-candidates/review-manifest.json');
 assert.equal(manifest.version,'v7.1-even-optical-tracking');
 assert.equal(manifest.alignment.secondaryRowBalance.rules,2);
 for(const stem of ['h-en-02-horizontal','p-en-01-stacked'])for(const tone of ['light','dark','monochrome']){
   const file=stem+'-'+tone+'.svg',svg=read('brands/asyada-egitim/assets/english-only-candidates/'+file);
   const info=JSON.parse(svg.split('<metadata>')[1].split('</metadata>')[0]);
   assert.equal(info.version,'v7.1-even-optical-tracking');
   assert.equal(info.mainWeight,450);
   assert.equal(info.taglineWeight,350);
   assert.equal(info.metrics.asiaScale,1.10);
   assert.equal(info.metrics.inScale,.88);
   assert.equal(info.metrics.lowerBaseline,409);
   assert.equal(info.metrics.countryBaseline,495);
   const rules=info.metrics.secondaryRowRules;
   assert.equal(rules.y,325);
   assert.equal(rules.strokeWidth,2.8);
   assert.ok(Math.abs(rules.lengthLeft-rules.lengthRight)<.002);
   assert.ok(rules.lengthLeft>100);
   assert.equal(rules.stroke,tone==='monochrome'?'#1D2027':'#BD2120');
   assert.equal((svg.match(/data-rule=/g)||[]).length,2);
   assert.equal((svg.match(/data-country-dot=/g)||[]).length,4);
   assert.ok(svg.includes('data-secondary-line-balance="flanking-rules"'));
   assert.ok(!svg.includes('<text'));
   assert.ok(!svg.includes('<image'));
 }
});


test('English V7.1 matches equal optical clearances without stretching fonts or asymmetric rules',()=>{
 const m=json('brands/asyada-egitim/assets/english-only-candidates/review-manifest.json');
 assert.equal(m.version,'v7.1-even-optical-tracking');
 assert.equal(m.alignment.opticalSpacing.targetRenderedClearance,19);
 assert.equal(m.alignment.opticalSpacing.interWordGap,38);
 for(const stem of ['h-en-02-horizontal','p-en-01-stacked'])for(const tone of ['light','dark','monochrome']){
  const text=read('brands/asyada-egitim/assets/english-only-candidates/'+stem+'-'+tone+'.svg');
  const meta=JSON.parse(text.split('<metadata>')[1].split('</metadata>')[0]);
  assert.equal(meta.version,'v7.1-even-optical-tracking');
  assert.equal(meta.opticalSpacing.targetRenderedClearance,19);
  assert.equal(meta.opticalSpacing.wordGapRendered,38);
  assert.equal(meta.opticalSpacing.glyphPathDataUnchanged,true);
  assert.equal(meta.mainWeight,450);
  assert.equal(meta.taglineWeight,350);
  assert.ok(meta.metrics.lowerWidth>640&&meta.metrics.lowerWidth<647);
  assert.ok(Math.abs(meta.metrics.secondaryRowRules.lengthLeft-meta.metrics.secondaryRowRules.lengthRight)<.002);
  assert.equal((text.match(/data-rule=/g)||[]).length,2);
  assert.equal((text.match(/data-country-dot=/g)||[]).length,4);
  assert.ok(!text.includes('<image')&&!text.includes('<text'));
 }
});
