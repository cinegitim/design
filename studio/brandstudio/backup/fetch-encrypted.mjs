// Export encrypted Cloudflare snapshots from the verified GitHub Actions workflow.
// This script never fetches or writes plaintext design documents.
import fs from 'node:fs/promises';
import path from 'node:path';
const API='https://studio.asyadaegitim.com/internal/backup';
const AUD='brandstudio-backup-v1';
const TOKEN_URL=process.env.ACTIONS_ID_TOKEN_REQUEST_URL;
const TOKEN_AUTH=process.env.ACTIONS_ID_TOKEN_REQUEST_TOKEN;
const RUNNER_TEMP=process.env.RUNNER_TEMP;
if(!TOKEN_URL||!TOKEN_AUTH||!RUNNER_TEMP)throw new Error('GitHub Actions OIDC environment missing');
const oidc=new URL(TOKEN_URL);
oidc.searchParams.set('audience',AUD);
const tokenResp=await fetch(oidc,{headers:{Authorization:'Bearer '+TOKEN_AUTH}});
if(!tokenResp.ok)throw new Error('GitHub OIDC token issuance failed: '+tokenResp.status);
const token=(await tokenResp.json()).value;
if(!token)throw new Error('GitHub OIDC token missing');
const catalog=JSON.parse(await fs.readFile('docs/visual-editor/browser/catalog.json','utf8'));
const ids=[...new Set(catalog.map(x=>x.id).filter(x=>typeof x==='string'&&/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(x)))].sort();
if(ids.length===0||ids.length>1000)throw new Error('Invalid catalog');
const out=path.join(RUNNER_TEMP,'brandstudio-export');
await fs.mkdir(out,{recursive:true});
let active=0,empty=0;
for(const id of ids){
 const response=await fetch(API+'?product='+encodeURIComponent(id),{
  headers:{Authorization:'Bearer '+token,Accept:'application/json'},
  redirect:'error',signal:AbortSignal.timeout(30000)
 });
 if(response.status===204){empty++;continue}
 if(response.status!==200)throw new Error('Encrypted backup failed for '+id+' (HTTP '+response.status+')');
 const data=await response.json();
 if(data.format!=='brandstudio-aes256gcm-v1'||data.product!==id||!data.revision||
    !/^[A-Za-z0-9_-]+$/.test(data.nonce||'')||!/^[A-Za-z0-9_-]+$/.test(data.ciphertext||''))
  throw new Error('Invalid encrypted backup payload for '+id);
 await fs.writeFile(path.join(out,id+'.enc.json'),JSON.stringify(data,null,2)+'\n',{mode:0o600});
 active++;
}
if(active===0)throw new Error('No active design found; refusing to replace backup files');
console.log('Encrypted backup export complete:',active,'active designs,',empty,'empty catalog entries. No plaintext or keys transferred.');
