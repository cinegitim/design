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

test('English-only review uses real Jost 550 outlines and unmodified approved seal',()=>{
 for(const layout of [{stem:'h-en-02-horizontal',parent:'h-02-primary-horizontal'},{stem:'p-en-01-stacked',parent:'p-01-primary-stacked'}]){
  for(const tone of ['light','dark','monochrome']){
   const name=layout.stem+'-'+tone+'.svg';
   const proposal=read('brands/asyada-egitim/assets/english-only-candidates/'+name);
   const publicFile=read('docs/identity/english-only/assets/'+name);
   const canonical=read('brands/asyada-egitim/assets/lockups/'+layout.parent+'-'+tone+'.svg');
   const seal=svg=>{const begin=svg.indexOf('<svg viewBox="0 0 400 370"');return svg.slice(begin,svg.indexOf('</svg>',begin)+6);};
   assert.equal(proposal,publicFile);
   assert.equal(seal(proposal),seal(canonical));
   assert.match(proposal,/true-jost-550-english-review/);
   assert.match(proposal,/"fontWeight":550/);
   assert.match(proposal,/REVIEW_ONLY_HUMAN_APPROVAL_PENDING/);
   assert.ok(!/stroke-width="2.8"/.test(proposal));
   assert.ok(!proposal.includes('<text'));
   assert.equal([...proposal.matchAll(/data-glyph="([A-Z])"/g)].map(x=>x[1]).join(''),'EDUCATIONINASIA');
  }
 }
});

test('English v4 wordmark centers lower line with smaller IN, dominant ASIA and exact approved SVG seal',()=>{
 const variants=['h-en-02-horizontal','p-en-01-stacked'];
 const tones=['light','dark','monochrome'];
 for(const stem of variants)for(const tone of tones){
  const svg=read('brands/asyada-egitim/assets/english-only-candidates/'+stem+'-'+tone+'.svg');
  const match=svg.match(/<metadata>([\s\S]*?)<\/metadata>/);
  assert.ok(match,'metadata required');
  const m=JSON.parse(match[1]);
  assert.equal(m.version,'v4.2-optical-kerning');
  assert.equal(m.letterSpacing.ASIA,20);
  assert.ok(m.ASIAScale>1.95 && m.ASIAScale<2.05);
  assert.equal(m.fontWeight,550);
  assert.deepEqual(m.bottom,['IN','ASIA']);
  assert.ok(m.INScale < 1);
  assert.ok(m.ASIAScale > 1.6 && m.ASIAScale < 2.1);
  assert.ok(Math.abs((m.layoutMetrics.EDUCATION-m.layoutMetrics.lowerTotal)/2-m.layoutMetrics.centerOffset)<0.001);
  assert.equal(m.canonicalSealSha256,'8f5d46f0302c4cc7e3765d3bfce9445f842dbd92f1e0f8fbe99f9f509c77e11a');
  for(const [line,count] of [['EDUCATION',9],['IN',2],['ASIA',4]]){
   const segment=svg.match(new RegExp('<g data-line="'+line+'"[^>]*>([\\s\\S]*?)<\\/g>'));
   assert.ok(segment,'Missing line '+line);
   assert.equal((segment[1].match(/data-glyph=/g)||[]).length,count);
  }
  assert.ok(svg.includes('data-outline-source="locked-Jost550-path"'));
  assert.ok(svg.includes('data-outline-source="original-JostVF-wght550"'));
  assert.ok(!svg.includes('<image'));
  assert.ok(!svg.includes('<text'));
 }
});

// V4.1 kerning correction: SVG path outlines and canonical seal remain untouched;
// only ASIA glyph positions, its uniform scale and vertical baseline may differ.
test('English V4.2 ASIA characters are closer without altering Jost 550 geometry',()=>{
  const m=JSON.parse(read('brands/asyada-egitim/assets/english-only-candidates/review-manifest.json'));
  assert.equal(m.version,'v4.2-optical-kerning');
  assert.equal(m.layout.tracking.ASIA,20);
  assert.ok(Math.abs((m.layout.width.EDUCATION-m.layout.width.lowerTotal)/2-m.layout.width.centerOffset)<0.001);
  for(const layout of ['h-en-02-horizontal','p-en-01-stacked'])for(const tone of ['light','dark','monochrome']){
    const svg=read('brands/asyada-egitim/assets/english-only-candidates/'+layout+'-'+tone+'.svg');
    const mstart=svg.indexOf('<metadata>')+10, mend=svg.indexOf('</metadata>');
    const meta=JSON.parse(svg.slice(mstart,mend));
    assert.equal(meta.version,'v4.2-optical-kerning');
    assert.equal(meta.letterSpacing.ASIA,20);
    assert.equal(meta.fontWeight,550);
    assert.equal(meta.status,'REVIEW_ONLY_HUMAN_APPROVAL_PENDING');
    assert.match(svg,/<g data-line="ASIA"/);
  }
});

test('English V4.2 optical kerning keeps equal minimum gaps, unchanged outlines and whole-line centering',()=>{
 const source=json('brands/asyada-egitim/assets/english-only-candidates/review-manifest.json');
 assert.equal(source.version,'v4.2-optical-kerning');
 assert.deepEqual(source.layout.opticalKerning.pairOffsetsNative,{AS:-28,SI:-12,IA:-14});
 const gaps=Object.values(source.layout.opticalKerning.minimumGapNative);
 assert.ok(Math.max(...gaps)-Math.min(...gaps)<0.3);
 for(const stem of ['h-en-02-horizontal','p-en-01-stacked'])for(const tone of ['light','dark','monochrome']){
  const s=read('brands/asyada-egitim/assets/english-only-candidates/'+stem+'-'+tone+'.svg');
  const meta=JSON.parse(s.split('<metadata>')[1].split('</metadata>')[0]);
  const opt=meta.opticalKerning;
  assert.equal(meta.fontWeight,550);
  assert.equal(meta.version,'v4.2-optical-kerning');
  assert.equal(opt.scaleUnchanged,true);
  assert.equal(opt.sealUnchanged,true);
  assert.equal(opt.recenteredTogether,true);
  assert.ok(meta.layoutMetrics.lowerWidthRatio>0.90&&meta.layoutMetrics.lowerWidthRatio<0.92);
  assert.ok(Math.abs(meta.layoutMetrics.centerOffset-(meta.layoutMetrics.EDUCATION-meta.layoutMetrics.lowerTotal)/2)<0.001);
  const xs=[...s.matchAll(/<g data-line="ASIA"[^>]*>([\s\S]*?)<\/g>/g)];
  assert.equal(xs.length,1);
  const positions=[...xs[0][1].matchAll(/transform="translate\(([-\d.]+) 0\)"/g)].map(x=>+x[1]);
  assert.equal(positions.length,4);
  assert.ok(Math.abs(positions[1]-131.500244)<0.001);
  assert.ok(Math.abs(positions[2]-242.136208)<0.001);
  assert.ok(Math.abs(positions[3]-274.536207)<0.001);
 }
});
