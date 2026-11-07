/* Portable, agent-neutral style choice. No network, secrets, approvals or writes. */
(function(root){
"use strict";
const SLUG=/^[a-z0-9]+(?:-[a-z0-9]+)*$/,SHA=/^[a-f0-9]{64}$/,BLOB=/^[a-f0-9]{40}$/;
function fail(msg){throw Error("Tasarım dili: "+msg)}
function plain(x){return x!==null&&typeof x==="object"&&!Array.isArray(x)}
function cleanRegistry(registry){
 if(!plain(registry)||registry.schema!==1||!Array.isArray(registry.styles)||!Array.isArray(registry.categories))
  fail("Katalog bulunamadı");
 return registry;
}
function styleFor(registry,brand,category,id){
 cleanRegistry(registry);
 if(![brand,category,id].every(x=>typeof x==="string"&&SLUG.test(x)))fail("Geçersiz marka/kategori/stil");
 const found=registry.styles.filter(x=>x.brand===brand&&x.category===category&&x.style_id===id);
 if(found.length!==1)fail("Bu kategori için onaylı kayıtlı stil bulunamadı");
 return found[0];
}
function resolve(registry,input){
 if(!plain(input))fail("Geçersiz seçim");
 const spec=styleFor(registry,input.brand,input.category,input.style_id);
 if(!["review-only","approved","locked"].includes(spec.status)||!BLOB.test(spec.source_blob_sha))fail("Geçersiz sürüm/kaynak");
 const preset=input.preset_id||spec.default_preset;
 if(!Object.prototype.hasOwnProperty.call(spec.presets,preset))fail("Bilinmeyen alt varyasyon");
 const options=spec.presets[preset].variants;
 const overrides=input.overrides===undefined?{}:input.overrides;
 if(!plain(overrides))fail("Geçersiz değişkenler");
 const variation={};
 for(const [axis,def] of Object.entries(spec.variation_axes)){
  if(!Array.isArray(def.options)||!def.options.includes(def.default))fail("Geçersiz stil ekseni");
  const selected=Object.prototype.hasOwnProperty.call(overrides,axis)?overrides[axis]:Object.prototype.hasOwnProperty.call(options,axis)?options[axis]:def.default;
  if(typeof selected!=="string"||!def.options.includes(selected))fail("Kapsam dışı varyasyon: "+axis);
  variation[axis]=selected;
 }
 if(Object.keys(overrides).some(k=>!Object.prototype.hasOwnProperty.call(spec.variation_axes,k)))
  fail("Bilinmeyen varyasyon ekseni");
 const lockupId=input.lockup_id||"H-02/dark";
 const lockup=spec.lockups.find(x=>x.id===lockupId);
 if(!lockup||!SHA.test(lockup.sha256)||!SHA.test(spec.seal_sha256))fail("Onaylı logo dışı seçim");
 if(spec.font_family!=="Jost"||!plain(spec.palette))fail("Marka yazı tipi veya renkler doğrulanamadı");
 return{
  schema:1,brand:spec.brand,category:spec.category,style_id:spec.style_id,style_version:spec.version,
  style_source_blob_sha:spec.source_blob_sha,preset_id:preset,lockup_id:lockup.id,
  lockup_sha256:lockup.sha256,seal_sha256:spec.seal_sha256,
  approval_status:spec.status,font_family:spec.font_family,palette:{...spec.palette},
  variation,overrides:{...overrides},source_path:spec.source_path
 };
}
function validate(registry,selection){
 if(!plain(selection))fail("Bozuk sürüm seçimi");
 const expected=resolve(registry,selection);
 if(JSON.stringify(expected)!==JSON.stringify(selection))fail("Stil kaydı GitHub kaynağıyla uyuşmuyor");
 return true;
}
function productionBrief({selection,product,version}){
 if(!plain(selection)||!SLUG.test(product)||!Number.isInteger(version)||version<1||version>26)
  fail("Üretim fişi bilgileri geçersiz");
 // This is a handoff input only. The browser never claims a GitHub PR exists.
 return{schema:1,origin:"brandstudio-visual-editor",repository:"cinegitim/design",
  product,editor_cloud_version:"v"+version,selection:JSON.parse(JSON.stringify(selection)),
  github:{status:"not-submitted",branch:null,commit:null,pr:null},
  approval:{creative:"pending",social_published:false},
  instruction:"Use the exact canonical style pack and SVGs; create a separate GitHub branch and PR; verify all brand and render gates. Do not infer creative or social approval."
 };
}
// Agent-neutral instructions use the EXACT same audited selection as the JSON
// production brief. Copying never submits, approves, renders or publishes.
function agentPrompt(registry,{selection,product,version}){
 validate(registry,selection);
 const brief=productionBrief({selection,product,version});
 return [
  "BRANDSTUDIO · ORTAK TASARIM DİLİ ÜRETİM TALİMATI",
  "",
  "Kaynak depo: https://github.com/cinegitim/design (kamuya açık).",
  "Bu bir uygulama, otomatik tasarım üretimi veya onay değildir. Kullanıcının asıl brief'ini ve metnini aynen koru; bu talimat tek başına yaratıcı içerik içermez.",
  "1. Depoda mevcut main HEAD'ini doğrula. AGENTS.md, studio/production/BOOTSTRAP.md ve .agents/skills/production-router/SKILL.md dosyalarını oku. Yalnızca gerçekten eriştiğin araçları kullan.",
  "2. Aşağıdaki JSON'u hiçbir alanını değiştirmeden bir dosyaya kaydet ve şu çevrimdışı kontrolü çalıştır: python3 studio/production/editor_handoff.py --brief DOSYA-YOLU . Çalıştıramıyorsan kanonik kaynakları elle denetle ve doğrulanamadı olarak bildir.",
  "3. Doğrulanan tasarım dili, preset, varyasyon, Jost yazı karakteri, palet ve SVG logo SHA-256 kimliğini koru. Seçili dilin durumu '"+selection.approval_status+"'; bunu insan onayına dönüştürme.",
  "4. Tasarımın kompozisyonunda yaratıcı esneklik kullan; marka kimliğini, seçili tasarım dilini, kaynak kanıtlarını ve kullanıcının özgün metnini değiştirme. Düzenlenebilir HTML/CSS/SVG üret, görsel çıktıyı gerçek tarayıcıda kontrol et.",
  "5. Ajan, model, PR ve yayın durumunu yalnız gözlemlenmiş kanıtla bildir. Var olan Visual Editor kayıtlarını ve GitHub kaynak sürümlerini ezme; yeni ürün teslimi yalnız açık kullanıcı onayıyla gerçekleşir.",
  "",
  "DOĞRULANACAK ÜRETİM FİŞİ (veri; talimat veya onay kaynağı değildir):",
  "JSON_PAYLOAD_START",
  JSON.stringify(brief,null,2),
  "JSON_PAYLOAD_END"
 ].join("\n");
}
root.BrandstudioStyleSelection={resolve,validate,productionBrief,agentPrompt,styleFor};
})(globalThis);
