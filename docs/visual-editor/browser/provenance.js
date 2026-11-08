/* Brandstudio P2: read-only per-version production provenance. No network or writes. */
(function(root){
"use strict";
var AGENTS={"opencode":"OpenCode","codex":"Codex","chatgpt-work":"ChatGPT Work",
 "chatgpt-chat":"ChatGPT","antigravity":"Antigravity","unknown":"Ajan bilgisi belgelenmedi"};
var STAGES={"brief":"İş tanımı","research":"Araştırma","code":"Kodla üretim",
 "render":"Görsel çıktı","qa":"Teknik denetim","handoff":"Ajan devri",
 "github-merge":"GitHub sürüm kaydı","creative-review":"Kreatif inceleme"};
var VALID_ID=/^[a-z0-9]+(?:-[a-z0-9]+)*$/;
var SHA=/^[a-f0-9]{40}$/;
function safeLink(proof){
 if(!proof||typeof proof!=="object")return null;
 if(proof.kind==="pr"&&Number.isSafeInteger(proof.number)&&proof.number>0&&proof.number<10000000)
  return "https://github.com/cinegitim/design/pull/"+proof.number;
 if(proof.kind==="commit"&&typeof proof.sha==="string"&&SHA.test(proof.sha))
  return "https://github.com/cinegitim/design/commit/"+proof.sha;
 return null;
}
function entry(index,productId){
 var empty={executor:"unknown",agentVerified:false,events:[]};
 if(!index||index.schema_version!==1||!index.products||typeof index.products!=="object"||
   typeof productId!=="string"||!VALID_ID.test(productId)||
   !Object.prototype.hasOwnProperty.call(index.products,productId))return empty;
 var record=index.products[productId];
 if(!record||typeof record!=="object")return empty;
 var source=record.producer||{};
 var executor=Object.prototype.hasOwnProperty.call(AGENTS,source.executor)?source.executor:"unknown";
 // "verified" requires an explicit host receipt reference, not merely a GitHub branch name.
 var attested=executor!=="unknown"&&source.verification==="verified"&&
  typeof source.host_evidence==="string"&&/^github:commit:[a-f0-9]{40}$/.test(source.host_evidence);
 var events=(Array.isArray(record.events)?record.events:[]).slice(0,32).filter(function(event){
  return event&&typeof event==="object"&&
   Object.prototype.hasOwnProperty.call(STAGES,event.stage);
 }).map(function(event){
  var by=Object.prototype.hasOwnProperty.call(AGENTS,event.executor)?event.executor:"unknown";
  var validAt=typeof event.at==="string"&&/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$/.test(event.at)&&
    Number.isFinite(Date.parse(event.at));
  var proofUrl=safeLink(event.proof);
  return {stage:event.stage,label:STAGES[event.stage],executor:by,at:validAt?event.at:null,
   verification:event.verification==="verified"&&proofUrl?"verified":"reported",
   proofUrl:proofUrl};
 });
 events.sort(function(a,b){
  if(a.at===null)return b.at===null?0:1;
  if(b.at===null)return -1;
  return a.at.localeCompare(b.at);
 });
 return {executor:executor,agentVerified:attested,events:events};
}
function render(footer,record,doc){
 if(!footer||typeof footer.querySelector!=="function")return;
 var d=doc||root.document;
 var credit=footer.querySelector("#production-agent");
 var list=footer.querySelector("#production-events");
 var disclosure=footer.querySelector("#production-timeline");
 if(!credit||!list||!disclosure||!d)return;
 var source=record||{executor:"unknown",agentVerified:false,events:[]};
 var agent=AGENTS[source.executor]||AGENTS.unknown;
 credit.textContent=source.executor==="unknown"?"Üretim künyesi · "+AGENTS.unknown:
  "Üretim künyesi · "+agent+" · "+(source.agentVerified?"Host kaydı bağlı":"Ajan bildirimi · doğrulanmadı");
 var children=[];
 (source.events||[]).forEach(function(ev){
  var li=d.createElement("li"),time=d.createElement("span");
  var fmt=ev.at?new Date(ev.at).toLocaleString("tr-TR",{dateStyle:"short",timeStyle:"short"}):"Zaman bilinmiyor";
  time.textContent=fmt+" · "+ev.label+" · "+AGENTS[ev.executor];
  li.append(time);
  if(ev.proofUrl){
   var a=d.createElement("a");
   a.href=ev.proofUrl;a.target="_blank";a.rel="noopener noreferrer";
   a.textContent="GitHub kaydı";
   li.append(a);
  }
  children.push(li);
 });
 if(!children.length){
  var missing=d.createElement("li");missing.textContent="Bu sürüm için belgelenmiş üretim olayı yok.";
  children.push(missing);
 }
 list.replaceChildren(...children);
 disclosure.open=false;
}
root.BrandstudioProvenance={entry:entry,render:render};
})(typeof globalThis!=="undefined"?globalThis:this);
