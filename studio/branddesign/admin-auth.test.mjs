import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
const root=path.resolve(import.meta.dirname,'../..');
const gateway=fs.readFileSync(path.join(root,'studio/cloudflare-brandstudio/asya-gateway/worker.mjs'),'utf8');
const auth=fs.readFileSync(path.join(root,'studio/branddesign/admin-auth/worker.mjs'),'utf8');
const config=JSON.parse(fs.readFileSync(path.join(root,'studio/cloudflare-brandstudio/asya-gateway/wrangler.json'),'utf8'));
const authConfig=JSON.parse(fs.readFileSync(path.join(root,'studio/branddesign/admin-auth/wrangler.json'),'utf8'));

test('no password or verifier ever committed in public code',()=>{
 assert.doesNotMatch(gateway,/1a2b3c4d5e\./);
 assert.doesNotMatch(auth,/1a2b3c4d5e\./);
 assert.match(gateway,/env\.ADMIN_PBKDF2_HASH/);
 assert.match(gateway,/env\.ADMIN_PBKDF2_SALT/);
 assert.match(gateway,/crypto\.subtle\.deriveBits/);
 assert.match(gateway,/iterations:210000/);
});
test('admin login protects static pages and the revision API',()=>{
 assert.match(gateway,/async function session\(/);
 assert.match(gateway,/if\(!user\.ok\)/);
 assert.match(gateway,/context=\{request,env,authenticated:true\}/);
 assert.match(gateway,/if\(!context\.authenticated\)/);
 assert.match(gateway,/!sameOrigin\(req\)/);
 assert.match(gateway,/CF-Connecting-IP/);
 assert.match(gateway,/name="username"/);
 assert.match(gateway,/name="password"/);
 assert.match(gateway,/\/admin\/login/);
 assert.doesNotMatch(gateway,/Cf-Access-Jwt-Assertion/);
});
test('trusted browsers use hardened long-lived HttpOnly secure cookies',()=>{
 assert.match(gateway,/__Host-branddesign_session/);
 assert.match(gateway,/HttpOnly; Secure; SameSite=Lax/);
 assert.match(gateway,/Max-Age=/);
 assert.match(gateway,/31536000/);
 assert.match(gateway,/crypto\.getRandomValues\(new Uint8Array\(32\)\)/);
 assert.match(gateway,/authObject\(env,'revoke'/);
 assert.match(auth,/const DAY=86400000, YEAR=365\*DAY, RENEW=30\*DAY/);
 assert.match(auth,/session:/);
 assert.match(auth,/this\.ctx\.storage\.delete/);
});
test('private auth DO is isolated from the public gateway and includes rate limiting',()=>{
 assert.equal(authConfig.workers_dev,false);
 assert.equal(authConfig.durable_objects.bindings[0].class_name,'BrandstudioAuthObject');
 assert.ok(authConfig.migrations[0].new_sqlite_classes.includes('BrandstudioAuthObject'));
 assert.ok(config.durable_objects.bindings.some(x=>x.name==='BRANDSTUDIO_AUTH'&&x.script_name==='brandstudio-admin-auth'));
 assert.match(auth,/state\.count<6/);
 assert.match(auth,/15\*60000/);
 assert.match(auth,/await this\.ctx\.storage\.put/);
 assert.match(auth,/new Response\("Not Found",\{status:404\}\)/);
});

test('browser performs PBKDF2 and server verifies a one-time HMAC proof without server PBKDF2',()=>{
 assert.match(gateway,/LOGIN_SCRIPT/);
 assert.match(gateway,/\/admin\/challenge/);
 assert.match(gateway,/script-src 'nonce-/);
 assert.match(gateway,/connect-src 'self'/);
 assert.match(gateway,/crypto\.subtle\.deriveBits/);
 assert.match(gateway,/crypto\.subtle\.sign\('HMAC'/);
 assert.match(gateway,/async function correctProof/);
 assert.match(gateway,/authObject\(env,'consume',clientId/);
 assert.match(auth,/action==="challenge"\|\|action==="consume"/);
 assert.match(auth,/this\.ctx\.storage\.delete\(key\)/);
 assert.doesNotMatch(gateway,/const bits=await crypto\.subtle\.deriveBits\(\{name:'PBKDF2',salt:fromHex\(env/);
});
