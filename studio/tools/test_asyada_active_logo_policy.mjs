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
  assert.match(review,/APPROVED \/ CANONICAL/);
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
  assert.match(review,/approved canonical signature/);
  assert.match(review,/canonical-lockups\/assets\/h-en-02-horizontal-light.svg/);
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



const englishManifestPath='brands/asyada-egitim/assets/lockups/canonical-english-lockups.json';
const englishManifest=json(englishManifestPath);
const englishActive=englishManifest.records.filter(r=>r.status==='APPROVED / CANONICAL');
const englishSeal=x=>{const i=x.indexOf('<svg viewBox="0 0 400 370"');return x.slice(i,x.indexOf('</svg>',i)+6);};

test('English V9 is human-approved as a separate canonical language family, same brand root',()=>{
 assert.equal(englishManifest.status,'APPROVED / CANONICAL');
 assert.equal(englishManifest.human_approval_date,'2026-11-04');
 assert.equal(englishManifest.language,'en');
 assert.equal(englishManifest.design_version,'v9-equal-in-asia-size');
 assert.equal(englishManifest.default_variant_id,'H-EN-02');
 assert.deepEqual(englishManifest.current_variant_ids,['H-EN-02','P-EN-01']);
 assert.equal(englishManifest.canonical_seal_sha256,manifest.canonical_seal_sha256);
 assert.equal(englishManifest.turkish_canonical_manifest,manifestPath);
 assert.equal(englishManifest.shared_assets_directory,'brands/asyada-egitim/assets/lockups/');
 assert.equal(englishActive.length,6);
 assert.equal(brand.canonicalLockups.byLanguage.tr.manifest,manifestPath);
 assert.equal(brand.canonicalLockups.byLanguage.en.manifest,englishManifestPath);
 assert.equal(brand.canonicalLockups.byLanguage.tr.manifestSha256,fileSha(manifestPath));
 assert.equal(brand.canonicalLockups.byLanguage.en.manifestSha256,fileSha(englishManifestPath));
 assert.equal(brand.canonicalLockups.languageSelectionDefault,'tr');
 assert.equal(read('brands/asyada-egitim/assets/lockups/canonical-english-lockups.sha256').trim().split(/\s+/)[0],fileSha(englishManifestPath));
 assert.equal(read('docs/asyada-seal/canonical-lockups/assets/canonical-english-lockups.json'),read(englishManifestPath));
 assert.equal(read('docs/asyada-seal/canonical-lockups/assets/canonical-english-lockups.sha256'),read('brands/asyada-egitim/assets/lockups/canonical-english-lockups.sha256'));
 assert.deepEqual(new Set(englishActive.map(x=>x.variant_id)),new Set(['H-EN-02','P-EN-01']));
 assert.deepEqual(new Set(englishActive.map(x=>x.color_variant)),new Set(['light','dark','monochrome']));
 assert.ok(new Set([...active.map(x=>x.canonical_lockup_id),...englishActive.map(x=>x.canonical_lockup_id)]).size===15);
});

test('Six approved English SVGs preserve the exact Turkish V-01 seal, SHA, letter geometry and mirrors',()=>{
 for(const record of englishActive){
  const f=record.canonical_file_path,mirror=record.public_mirror_path,svg=read(f);
  const color=record.color_variant;
  const canonical=(record.variant_id==='H-EN-02'?'h-02-primary-horizontal':'p-01-primary-stacked')+'-'+color+'.svg';
  const tr=read('brands/asyada-egitim/assets/lockups/'+canonical);
  assert.equal(fileSha(f),record.sha256);
  assert.equal(fileSha(mirror),record.sha256);
  assert.equal(svg,read(mirror));
  assert.equal(englishSeal(svg),englishSeal(tr));
  assert.equal(record.canonical_seal_sha256,englishManifest.canonical_seal_sha256);
  const metadata=JSON.parse(svg.split('<metadata>')[1].split('</metadata>')[0]);
  assert.equal(metadata.status,'APPROVED / CANONICAL');
  assert.equal(metadata.approvedOn,'2026-11-04');
  assert.equal(metadata.designVersion,'v9-equal-in-asia-size');
  assert.equal(metadata.canonicalLockupId,record.canonical_lockup_id);
  assert.equal(metadata.canonicalFilePath,f);
  assert.equal(metadata.mainWeight,450);
  assert.equal(metadata.taglineWeight,350);
  assert.equal(metadata.metrics.inScale,1.1);
  assert.equal(metadata.metrics.asiaScale,1.1);
  assert.equal(metadata.metrics.inBaseline,409);
  assert.equal(metadata.metrics.lowerBaseline,409);
  assert.ok(Math.abs(metadata.metrics.lowerWidth/metadata.metrics.topWidth-.9901653478)<.00001);
  const inTag=svg.match(/<g data-line="IN"[^>]*>/)?.[0]||'';
  const asiaTag=svg.match(/<g data-line="ASIA"[^>]*>/)?.[0]||'';
  assert.match(inTag,/ 409\) scale\(1\.10000000\)/);
  assert.match(asiaTag,/ 409\) scale\(1\.10000000\)/);
  assert.deepEqual([...svg.matchAll(/data-country="([^"]+)"/g)].map(x=>x[1]),['CHINA','HONG KONG','JAPAN','SINGAPORE','SOUTH KOREA']);
  assert.equal((svg.match(/data-country-dot=/g)||[]).length,4);
  assert.ok(!svg.includes('data-rule='));
  assert.ok(!svg.includes('<image'));
  assert.ok(!svg.includes('<text'));
  assert.ok(!svg.includes('REVIEW_ONLY_HUMAN_APPROVAL_PENDING'));
  assert.match(svg,/approved canonical English logo/);
 }
});

test('Public Brandstudio separates Türkçe / English headings while removing previous English review SVGs',()=>{
 const identity=read('docs/identity/index.html');
 const studio=read('docs/workspaces/asyada-egitim/logos-and-covers/index.html');
 assert.match(identity,/<h2>Türkçe logo<\/h2>/);
 assert.match(identity,/<h2>English logo<\/h2>/);
 assert.match(studio,/<h2>Türkçe logo<\/h2>/);
 assert.match(studio,/<h2>English logo<\/h2>/);
 assert.match(identity,/href="#lockups"/);
 assert.match(identity,/href="#english-logo"/);
 assert.match(studio,/href="#logos"/);
 assert.match(studio,/href="#english-logo"/);
 assert.match(identity,/H-EN-02/);
 assert.match(identity,/P-EN-01/);
 assert.match(studio,/APPROVED \/ CANONICAL/);
 assert.ok(!identity.includes('english-only/assets/'));
 assert.ok(!studio.includes('identity/english-only/assets/'));
 assert.ok(!identity.includes('henüz üretim için onaylı kimlik değildir'));
 assert.ok(!studio.includes('Görsel onay bekliyor'));
 const redirect=read('docs/identity/english-only/index.html');
 assert.match(redirect,/\.\.\/#english-logo/);
 const obsolete=['brands/asyada-egitim/assets/english-only-candidates/review-manifest.json'];
 for(const stem of ['h-en-02-horizontal','p-en-01-stacked'])for(const tone of ['light','dark','monochrome']){
  const file=stem+'-'+tone+'.svg';
  obsolete.push('brands/asyada-egitim/assets/english-only-candidates/'+file);
  obsolete.push('docs/identity/english-only/assets/'+file);
 }
 for(const rev of ['v6','v7','v71','v8'])obsolete.push('docs/identity/english-only/history/'+rev+'-horizontal-light.svg');
 for(const old of obsolete)assert.ok(!fs.existsSync(path.join(root,old)),'Obsolete English review SVG remains: '+old);
});
