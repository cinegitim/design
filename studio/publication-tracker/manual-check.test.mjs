import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";
import {webcrypto} from "node:crypto";

const code=fs.readFileSync(new URL("../cloudflare-brandstudio/asya-gateway/worker.mjs",import.meta.url),"utf8");
const browser=fs.readFileSync(new URL("../../docs/workspaces/asyada-egitim/publication-check.js",import.meta.url),"utf8");
const html=fs.readFileSync(new URL("../../docs/workspaces/asyada-egitim/index.html",import.meta.url),"utf8");
const worker=fs.readFileSync(new URL("./worker.mjs",import.meta.url),"utf8");
const config=fs.readFileSync(new URL("./wrangler.toml",import.meta.url),"utf8");
const scope={crypto:webcrypto,TextEncoder,TextDecoder,Headers,Request,Response,URL,URLSearchParams,console,fetch:()=>{throw Error("unexpected upstream call")}};
vm.runInNewContext(code.replace(/^export /gm,"").replace("default {","globalThis.gateway = {"),scope);
const ORIGIN="https://studio.asyadaegitim.com";
const COOKIE="__Host-brandstudio_session="+ "a".repeat(64);
function mock(){
 let called=0,request=null;
 const env={
  BRANDSTUDIO_PUBLICATION_BRIDGE_TOKEN:"dummy-test-credential",
  BRANDSTUDIO_AUTH:{idFromName:()=>({}),get:()=>({fetch:async()=>Response.json({ok:true})})},
  PUBLICATION_TRACKER:{fetch:async (url,options)=>{called++;request={url,options};return Response.json(options.method==="POST"?{platforms:{instagram:{state:"ok",fetched:8,saved:8,needsReview:2}},completedAt:"2026-10-30T15:00:00Z"}:{mode:"on_demand_only",lastScan:null})}}
 };
 return {env,count:()=>called,last:()=>request};
}
test("no cron handler or schedule remains in worker and config",()=>{
 assert.doesNotMatch(worker,/async scheduled\s*\(/);
 assert.match(worker,/mode:"on_demand_only"/);
 assert.match(config,/crons\s*=\s*\[\s*\]/);
});
test("manual refresh denies unauthenticated requests before contacting Worker",async()=>{
 const m=mock();const request=new Request(ORIGIN+"/admin/publications/refresh",{method:"POST",headers:{Origin:ORIGIN}});
 const r=await scope.gateway.fetch(request,m.env,{});
 assert.equal(r.status,401);assert.equal(m.count(),0);
});
test("manual refresh denies missing or external Origin even with an admin cookie",async()=>{
 const m=mock();
 for(const headers of [{Cookie:COOKIE},{Cookie:COOKIE,Origin:"https://evil.example"}]){
  const r=await scope.gateway.fetch(new Request(ORIGIN+"/admin/publications/refresh",{method:"POST",headers}),m.env,{});
  assert.equal(r.status,403);
 }
 assert.equal(m.count(),0);
});
test("manual refresh uses existing admin session, server-side token, and Instagram-only scope",async()=>{
 const m=mock();
 const r=await scope.gateway.fetch(new Request(ORIGIN+"/admin/publications/refresh",{method:"POST",headers:{Origin:ORIGIN,Cookie:COOKIE}}),m.env,{});
 assert.equal(r.status,200);
 const payload=await r.json();
 assert.equal(payload.platforms.instagram.fetched,8);
 assert.equal(m.count(),1);
 const outbound=m.last();
 assert.match(outbound.url,/\/api\/refresh$/);
 assert.equal(outbound.options.headers.Authorization,"Bearer dummy-test-credential");
 assert.deepEqual(JSON.parse(outbound.options.body).platforms,["instagram"]);
 assert.doesNotMatch(JSON.stringify(payload),/dummy-test-credential/);
});
test("admin status is read-only and never initiates a refresh",async()=>{
 const m=mock();
 const r=await scope.gateway.fetch(new Request(ORIGIN+"/admin/publications/status",{headers:{Cookie:COOKIE}}),m.env,{});
 assert.equal(r.status,200);assert.match(m.last().url,/\/api\/status$/);assert.equal(m.last().options.method,"GET");
});
test("browser only posts on user click; controls are present but hidden until admin authentication",()=>{
 assert.match(browser,/button\.addEventListener\("click"/);
 assert.match(browser,/\/admin\/publications\/refresh/);
 assert.doesNotMatch(browser,/PUBLICATION_REFRESH_TOKEN|BRANDSTUDIO_PUBLICATION_BRIDGE_TOKEN|META_IG_TOKEN|setInterval|setTimeout\s*\(/);
 assert.match(html,/id="publication-check"[^>]*hidden/);
 assert.match(html,/publication-check\.js/);
});
