/* On-demand read-only social-media publication checking.
   Uses the existing administrator session, never browser API credentials. */
(function () {
"use strict";
if(location.hostname!=="studio.asyadaegitim.com")return;
const area=document.getElementById("publication-check");
const button=document.getElementById("publication-check-button");
const status=document.getElementById("publication-check-status");
const chooser=document.getElementById("publication-check-platforms");
if(!area||!button||!status||!chooser)return;
const labels={instagram:"Instagram",facebook:"Facebook",linkedin:"LinkedIn",x:"X"};
const key="brandstudio:publication-check:result";
const fmt=value=>value&&!isNaN(Date.parse(value))?new Date(value).toLocaleString("tr-TR",{timeZone:"Europe/Istanbul",dateStyle:"medium",timeStyle:"short"}):"Henüz yok";
let configuration=null;
function selected(){return [...chooser.querySelectorAll('input[type="checkbox"]:checked')].map(x=>x.value)}
function drawPlatforms(result){
 chooser.replaceChildren();
 for(const p of ["instagram","facebook","linkedin","x"]){
  const config=result.platforms?.[p]||{};
  const span=document.createElement("label");span.className="publication-platform";
  const checkbox=document.createElement("input");checkbox.type="checkbox";checkbox.value=p;checkbox.disabled=!config.configured;
  checkbox.checked=p==="instagram"&&!!config.configured;
  const name=document.createElement("span");name.textContent=labels[p];
  const note=document.createElement("small");note.textContent=config.configured?
   (config.source==="voholabs_api"?"Voholabs yayınları":"Bağlı"):
   (p==="instagram"?"Bağlantı gerekli":"API anahtarı gerekli");
  span.append(checkbox,name,note);chooser.append(span);
  checkbox.addEventListener("change",()=>{button.disabled=!selected().length});
 }
 button.disabled=!selected().length;
}
async function init(){
 try{
  const response=await fetch("/admin/publications/status",{credentials:"same-origin",cache:"no-store"});
  if(!response.ok)throw Error("Yönetici erişimi yok");
  configuration=await response.json();
  drawPlatforms(configuration);
  area.hidden=false;
  const notice=sessionStorage.getItem(key);
  if(notice){sessionStorage.removeItem(key);status.textContent=notice}
  else status.textContent="Son denetim: "+fmt(configuration.lastScan?.finishedAt||configuration.lastScan?.startedAt);
 }catch(_){area.hidden=true}
}
button.addEventListener("click",async()=>{
 const platforms=selected();if(button.disabled||!platforms.length)return;
 button.disabled=true;
 status.textContent=platforms.map(p=>labels[p]).join(", ")+" denetleniyor…";
 try{
  const r=await fetch("/admin/publications/refresh",{method:"POST",credentials:"same-origin",cache:"no-store",
   headers:{"Content-Type":"application/json","Accept":"application/json"},
   body:JSON.stringify({platforms})});
  const result=await r.json();
  if(!r.ok)throw Error(result.details||result.error||"Denetim başarısız");
  const ok=platforms.filter(p=>result.platforms?.[p]?.state==="ok");
  const bad=platforms.filter(p=>result.platforms?.[p]?.state!=="ok");
  if(!ok.length)throw Error("Hiçbir platform denetlenemedi");
  const saved=ok.reduce((n,p)=>n+Number(result.platforms?.[p]?.saved||0),0);
  sessionStorage.setItem(key,"Denetim tamamlandı: "+ok.map(p=>labels[p]).join(", ")+
   " · "+saved+" yayın kaydı · "+(bad.length?"Bağlanamayan: "+bad.map(p=>labels[p]).join(", ")+" · ":"")+fmt(result.completedAt));
  location.reload();
 }catch(e){status.textContent="Denetim tamamlanamadı: "+String(e.message||e).slice(0,220);button.disabled=!selected().length}
});
init();
})();