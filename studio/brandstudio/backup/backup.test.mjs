import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {webcrypto,randomBytes} from 'node:crypto';
import {spawnSync} from 'node:child_process';
const root=path.resolve(import.meta.dirname,'../../..');
const base=path.join(root,'studio/brandstudio/backup');
const edge=fs.readFileSync(path.join(root,'studio/cloudflare-brandstudio/asya-gateway/worker.mjs'),'utf8');
const workflow=fs.readFileSync(path.join(root,'.github/workflows/brandstudio-offsite-backup.yml'),'utf8');

test('backup API is gated to a signed GitHub Actions OIDC identity and encrypts before export',()=>{
 assert.match(edge,/const GITHUB_BACKUP_AUD='brandstudio-backup-v1'/);
 assert.match(edge,/claims\.repository!=='cinegitim\/design'/);
 assert.match(edge,/claims\.workflow_ref!==GITHUB_BACKUP_WORKFLOW/);
 assert.match(edge,/String\(claims\.repository_id\)!=='1401886207'/);
 assert.match(edge,/claims\.ref!=='refs\/heads\/main'/);
 assert.match(edge,/crypto\.subtle\.verify\('RSASSA-PKCS1-v1_5'/);
 assert.match(edge,/crypto\.subtle\.encrypt\(\{name:'AES-GCM'/);
 assert.match(edge,/if\(!\(await backupIdentity\(request\)\)\)/);
 assert.match(edge,/BRANDSTUDIO_BACKUP_KEY/);
 assert.doesNotMatch(edge,/9dd8bba943453d1625b87ebcc7ac3879fe9f6376218f3e116f90d3c50afea163/);
 assert.match(edge,/url\.pathname==='\/internal\/backup'/);
});
test('workflows use short-lived OIDC rather than storing admin passwords or Cloudflare API tokens',()=>{
 assert.match(workflow,/id-token: write/);
 assert.match(workflow,/contents: write/);
 assert.match(workflow,/17 5,17 \* \* \*/);
 assert.match(workflow,/brandstudio-editor-history/);
 assert.match(workflow,/fetch-encrypted\.mjs/);
 assert.doesNotMatch(workflow,/adminasya|1a2b3c4d5e\.|ADMIN_PBKDF2_HASH/);
});
test('an AES-256-GCM encrypted snapshot can be recovered offline with user key file',async()=>{
 const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'bs-offsite-test-'));
 try{
  const key=randomBytes(32),iv=randomBytes(12),product='test-product';
  const payload={sha:'revision-1',document:{product,history:[{kind:'save',note:'Private design content'}]}};
  const imported=await webcrypto.subtle.importKey('raw',key,'AES-GCM',false,['encrypt']);
  const encrypted=await webcrypto.subtle.encrypt({name:'AES-GCM',iv,additionalData:new TextEncoder().encode('brandstudio-backup:v1:'+product)},imported,new TextEncoder().encode(JSON.stringify(payload)));
  const snapshot={format:'brandstudio-aes256gcm-v1',product,revision:payload.sha,nonce:iv.toString('base64url'),ciphertext:Buffer.from(encrypted).toString('base64url')};
  const input=path.join(tmp,'input.json'),recovery=path.join(tmp,'recovery.txt'),output=path.join(tmp,'result.json');
  fs.writeFileSync(input,JSON.stringify(snapshot));
  fs.writeFileSync(recovery,'Key (hex): '+key.toString('hex')+'\n');
  const result=spawnSync(process.execPath,[path.join(base,'decrypt.mjs'),input,recovery,output],{encoding:'utf8'});
  assert.equal(result.status,0,result.stderr);
  assert.deepEqual(JSON.parse(fs.readFileSync(output,'utf8')),payload);
  const tampered={...snapshot,product:'wrong-product'};fs.writeFileSync(input,JSON.stringify(tampered));
  const second=spawnSync(process.execPath,[path.join(base,'decrypt.mjs'),input,recovery,path.join(tmp,'bad.json')],{encoding:'utf8'});
  assert.notEqual(second.status,0);
 }finally{fs.rmSync(tmp,{recursive:true,force:true})}
});
