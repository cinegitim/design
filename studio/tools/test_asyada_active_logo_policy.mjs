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
  assert.equal(r.minimum_supported_display_size.screen_width_px,320);
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
 const logo=page.slice(page.indexOf('<section class="section" id="logos">'),page.indexOf('<section class="section" id="profile">'));
 assert.ok(logo.includes('H-02 · Temel yatay imza'));
 assert.ok(logo.includes('id="logos"'));
 assert.ok(logo.includes('id="profile"')===false);
 assert.ok(logo.includes('H-02/light')===false); // same original asset, no new synthetic lockup id
 assert.ok(logo.includes('h-02-primary-horizontal-light.svg'));
 assert.ok(logo.includes('h-02-primary-horizontal-dark.svg'));
 assert.ok(!/src="[^"]*(c-03|d-04)/i.test(logo));
 assert.equal((logo.match(/class="card(?: feature)?"/g)||[]).length,3);
 const identity=read('docs/identity/index.html');
 const active=identity.slice(identity.indexOf('<section id="lockups">'),identity.indexOf('<section id="rules">'));
 assert.ok(active.includes('id="small-digital"'));
 assert.ok(!active.includes('id="C-03"')&&!active.includes('id="D-04"'));
 assert.ok(identity.includes('320px'));
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
