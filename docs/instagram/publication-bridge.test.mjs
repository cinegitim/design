import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const code=fs.readFileSync(new URL('./publication-bridge.js',import.meta.url),'utf8');
const root={URL,AbortSignal,fetch:async()=>({ok:true,json:async()=>({posts:[
 {platform:'instagram',group_id:'instagram-known',product_id:null,match_status:'family_verified',permalink:'https://www.instagram.com/p/ABC123/',published_at:'2026-10-30T00:00:00Z'},
 {platform:'instagram',group_id:'instagram-known',product_id:null,match_status:'family_candidate',permalink:'https://www.instagram.com/p/INVALID/',published_at:'2026-10-30T00:00:00Z'},
 {platform:'instagram',group_id:'instagram-unknown',product_id:null,match_status:'family_verified',permalink:'https://www.instagram.com/p/UNKNOWN/',published_at:'2026-10-30T00:00:00Z'},
 {platform:'instagram',group_id:'instagram-known',product_id:null,match_status:'family_verified',permalink:'https://bad.example/p/BAD/',published_at:'2026-10-30T00:00:00Z'}
 ]})})};
vm.runInNewContext(code,root);
const registry={groups:[{id:'instagram-known'}],socialPublication:{posts:[]}};
test('only valid official unique caption proofs overlay the catalog',async()=>{
 const out=await root.BrandstudioPublicationBridge.merged(registry);
 assert.equal(out.length,1);
 assert.equal(out[0].url,'https://www.instagram.com/p/ABC123/');
 assert.equal(out[0].productId,null);
});
test('existing human-confirmed revision posts are not replaced by API family records',async()=>{
 const out=await root.BrandstudioPublicationBridge.merged({...registry,socialPublication:{posts:[{url:'https://www.instagram.com/asyadaegitim/p/ABC123/',productId:'a-verified-revision'}]}});
 assert.equal(out.length,1);
 assert.equal(out[0].productId,'a-verified-revision');
});
test('unavailable API preserves original registry proof only',async()=>{
 const stale=root.fetch;root.fetch=async()=>{throw Error('offline')};
 const out=await root.BrandstudioPublicationBridge.merged({...registry,socialPublication:{posts:[{url:'https://www.instagram.com/p/ORIGINAL/',verified:true}]}});
 assert.equal(out.length,1);root.fetch=stale;
});
