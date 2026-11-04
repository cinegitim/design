/* Brandstudio style picker: browser presentation only, no network or GitHub writes. */
(function(root){
"use strict";
const $=id=>document.getElementById(id);
function options(select,records,wanted){
 select.replaceChildren();
 records.forEach(function(x){const o=document.createElement("option");o.value=x.value;o.textContent=x.label;select.appendChild(o)});
 if(records.some(x=>x.value===wanted))select.value=wanted;
 select.disabled=!records.length;
}
function create({module,getContext,commit,exportBrief}){
 let registry=null;
 const status=message=>$("style-status").textContent=message;
 const eligible=ctx=>!!ctx.record&&ctx.record.family==="instagram"&&ctx.record.kind==="html"&&
   (ctx.record.pages?.length>1||ctx.record.categoryPath?.includes("Karuseller"));
 const find=()=>registry?.styles?.find(x=>{
  const c=getContext();
  return x.brand===c.brand&&x.category===$("style-category").value&&x.style_id===$("style-family").value;
 })||null;
 function axes(spec,selected){
  const node=$("style-axes");node.replaceChildren();
  if(!spec)return;
  const preset=spec.presets[$("style-preset").value]||spec.presets[spec.default_preset];
  for(const [key,axis] of Object.entries(spec.variation_axes)){
   const label=document.createElement("label"),select=document.createElement("select");
   label.textContent=key.replaceAll("_"," ");select.dataset.axis=key;select.title=axis.description||key;
   options(select,axis.options.map(v=>({value:v,label:v.replaceAll("-"," ")})),
    selected?.[key]||preset.variants[key]||axis.default);
   label.append(select);node.append(label);
  }
 }
 function fillPresets(saved){
  const s=find();
  options($("style-preset"),s?Object.entries(s.presets).map(([id,p])=>({value:id,label:p.label})):[],
    saved?.preset_id||s?.default_preset);
  options($("style-logo"),s?s.lockups.map(p=>({value:p.id,label:p.id})):[],
    saved?.lockup_id||"H-02/dark");
  axes(s,saved?.variation);
 }
 function fillFamilies(saved){
  const ctx=getContext(),category=$("style-category").value;
  const styles=(registry?.styles||[]).filter(s=>s.brand===ctx.brand&&s.category===category);
  options($("style-family"),styles.map(s=>({value:s.style_id,label:s.name+" · "+s.status})),
    saved?.style_id||styles[0]?.style_id);
  fillPresets(saved);
  const maySave=eligible(ctx)&&category==="instagram-carousel"&&styles.length>0;
  $("style-save").disabled=!maySave;
  if(!maySave)status("Bu ürün için kayıtlı tasarım dili yok. Mevcut tasarım korunuyor.");
  else if(!saved)status("Stil adayı · henüz çalışma alanına uygulanmadı. İnsan kreatif onayı gerekiyor.");
 }
 function sync(){
  if(!registry||!module){status("Stil kataloğu yüklenemedi.");$("style-save").disabled=true;$("style-export").disabled=true;return}
  const ctx=getContext();let chosen=ctx.state?.designStyle||null;
  if(chosen){try{module.validate(registry,chosen)}catch(e){status("Kayıtlı stil güncel katalogla eşleşmiyor: "+e.message);chosen=null}}
  const category=chosen?.category||(eligible(ctx)?"instagram-carousel":null);
  options($("style-category"),registry.categories.map(c=>({value:c.id,label:c.label+(c.registered?"":" · stil yok")})),category);
  if(!category)$("style-category").selectedIndex=-1;
  fillFamilies(chosen);
  $("style-export").disabled=!chosen;
  if(chosen)status("Çalışma alanında seçili · "+chosen.style_id+" / "+chosen.preset_id+" · "+chosen.approval_status+"");
 }
 function read(){
  const ctx=getContext(),s=find();
  if(!eligible(ctx)||!s||$("style-category").value!=="instagram-carousel")
   throw Error("Bu tasarımın kategorisi için stil seçilemedi");
  const preset=s.presets[$("style-preset").value],overrides={};
  $("style-axes").querySelectorAll("select[data-axis]").forEach(el=>{
   const defaultValue=preset.variants[el.dataset.axis]||s.variation_axes[el.dataset.axis].default;
   if(el.value!==defaultValue)overrides[el.dataset.axis]=el.value;
  });
  return module.resolve(registry,{brand:ctx.brand,category:s.category,style_id:s.style_id,
    preset_id:$("style-preset").value,lockup_id:$("style-logo").value,overrides});
 }
 $("style-category").addEventListener("change",()=>fillFamilies(null));
 $("style-family").addEventListener("change",()=>{fillPresets(null);status("Seçim henüz çalışma alanına uygulanmadı.")});
 $("style-preset").addEventListener("change",()=>{axes(find(),null);status("Varyasyonu düzenlemeye uygulamak için butona basın.")});
 $("style-save").addEventListener("click",()=>{
  try{const selection=read();commit(selection);
   $("style-export").disabled=false;
   status("Stil uygulandı, ancak buluta kaydedilmedi. Üstteki kayıt düğmelerini kullanın · "+selection.approval_status+"")
  }catch(e){status("Stil uygulanamadı: "+e.message)}
 });
 $("style-export").addEventListener("click",()=>{
  try{
   const ctx=getContext(),selection=ctx.state?.designStyle;
   if(!selection)throw Error("Önce stili çalışma alanına uygulayın");
   module.validate(registry,selection);
   exportBrief(selection,ctx);
   status("Üretim fişi indirildi · GitHub PR henüz açılmadı. Bir ajan bu fişi PR'a eklemeli.")
  }catch(e){status("Üretim fişi hazırlanamadı: "+e.message)}
 });
 $("style-save").disabled=true;$("style-export").disabled=true;
 return{setRegistry(value){if(!value||value.schema!==1||!Array.isArray(value.styles))throw Error("Geçersiz stil kataloğu");registry=value;sync()},sync};
}
root.BrandstudioStyleUI={create};
})(globalThis);
