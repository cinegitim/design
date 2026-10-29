// Offline recovery of AES-256-GCM Brandstudio backup snapshots.
// Run: node decrypt.mjs <encrypted-snapshot.json> <recovery-key.txt> <output.json>
// Never sends the recovery key or plaintext to a network endpoint.
import fs from 'node:fs/promises';
import {webcrypto} from 'node:crypto';
const [input,keyFile,output]=process.argv.slice(2);
if(!input||!keyFile||!output)throw new Error('Usage: node decrypt.mjs <snapshot> <recovery-key.txt> <output.json>');
const blob=JSON.parse(await fs.readFile(input,'utf8'));
if(blob.format!=='brandstudio-aes256gcm-v1'||!blob.product||!blob.revision)throw new Error('Unknown backup format');
const text=await fs.readFile(keyFile,'utf8');
const match=text.match(/Key \(hex\): ([a-f0-9]{64})/);
if(!match)throw new Error('Missing 256-bit recovery key');
const key=await webcrypto.subtle.importKey('raw',Buffer.from(match[1],'hex'),{name:'AES-GCM'},false,['decrypt']);
const dec=x=>Buffer.from(x.replace(/-/g,'+').replace(/_/g,'/'),'base64');
const plain=await webcrypto.subtle.decrypt({name:'AES-GCM',iv:dec(blob.nonce),additionalData:new TextEncoder().encode('brandstudio-backup:v1:'+blob.product)},key,dec(blob.ciphertext));
const document=JSON.parse(new TextDecoder().decode(plain));
if(document.sha!==blob.revision||document.document?.product!==blob.product)throw new Error('Restored document identity did not match backup manifest');
await fs.writeFile(output,JSON.stringify(document,null,2)+'\n',{flag:'wx',mode:0o600});
console.log('Brandstudio recovery verified and saved to local file:',output);
