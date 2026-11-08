// Install encrypted snapshots into the dedicated GitHub history branch.
// Do not add plaintext snapshots to the public repository.
import fs from 'node:fs/promises';
import path from 'node:path';
const [source,worktree]=process.argv.slice(2);
if(!source||!worktree)throw new Error('Expected export and backup worktree paths');
const target=path.join(worktree,'docs/visual-editor/browser/cloud-offsite-encrypted');
await fs.mkdir(target,{recursive:true});
let changed=0,unchanged=0;
for(const item of await fs.readdir(source)){
 if(!/^[a-z0-9-]+\.enc\.json$/.test(item))throw new Error('Unexpected source filename');
 const next=JSON.parse(await fs.readFile(path.join(source,item),'utf8'));
 const dest=path.join(target,item);
 try{
  const before=JSON.parse(await fs.readFile(dest,'utf8'));
  if(before.revision===next.revision){unchanged++;continue}
 }catch(e){if(e.code!=='ENOENT')throw e}
 await fs.writeFile(dest,JSON.stringify(next,null,2)+'\n');
 changed++
}
console.log('Encrypted offsite backup revisions:',changed,'updated;',unchanged,'already archived.');
