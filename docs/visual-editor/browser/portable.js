/* Brandstudio browser-only portable version codec.
   Pure helpers; no network calls, no remote writes, no paid services. */
(function(root) {
"use strict";
var SELECTOR='h1,h2,h3,p,.eyebrow,.dek,.photo,.country-line,.country-grid b,.country-list span,.options span,.cta-pill,.pathways span,.folio,.logo-foot,.cover-rule,.question-bottom,.question-photo,img';
var COLORS={paper:'#f7f3e9',ink:'#1d2027',red:'#bd2120'};
var ALLOWED_STYLES={'position':1,'left':1,'top':1,'right':1,'bottom':1,'width':1,'height':1,'margin':1,'font-size':1,'font-weight':1,'letter-spacing':1,'line-height':1,'text-align':1,'opacity':1,'object-fit':1,'object-position':1,'border-radius':1,'z-index':1,'visibility':1};
var ALLOWED_MODES={inherit:1,paper:1,ink:1,red:1,direct:1};
var HEX=/^#[0-9a-fA-F]{6}$/;
var SLUG=/^[a-z0-9]+(?:-[a-z0-9]+)*$/;
function err(message){throw new Error(message)}
function plain(x){return !!x&&typeof x==='object'&&!Array.isArray(x)}
function state(input,maxPages) {
 if(!plain(input)||!plain(input.colors)||!plain(input.edits))err('Geçersiz sürüm durumu');
 if(JSON.stringify(input).length>32768)err('Sürüm durumu 32 KB sınırını aşıyor');
 var colors={};Object.keys(COLORS).forEach(function(k){var v=input.colors[k];if(!HEX.test(v||''))err('Geçersiz renk: '+k);colors[k]=v.toLowerCase()});
 if(Object.keys(input.colors).some(function(k){return !Object.prototype.hasOwnProperty.call(COLORS,k)}))err('Bilinmeyen renk anahtarı');
 var edits={},keys=Object.keys(input.edits);
 if(keys.length>500)err('Çok fazla düzenleme');
 keys.forEach(function(key){
   if(!/^(0|[1-9][0-9]*):(0|[1-9][0-9]*)$/.test(key))err('Geçersiz katman anahtarı');
   var bits=key.split(':').map(Number);
   if(bits[0]>=maxPages||bits[1]>500)err('Bu ürüne ait olmayan slayt/katman');
   var e=input.edits[key];if(!plain(e))err('Geçersiz katman');
   var mode=e.mode||'inherit';if(!ALLOWED_MODES[mode])err('Geçersiz renk modu');
   var styles={};
   if(e.styles!==undefined&&!plain(e.styles))err('Geçersiz CSS');
   Object.keys(e.styles||{}).forEach(function(k){
     if(!ALLOWED_STYLES[k])err('İzin verilmeyen CSS özelliği');
     var v=e.styles[k];if(typeof v!=='string'||v.length>40)err('Geçersiz CSS değeri');
     var px=/^-?[0-9]{1,5}(?:\.[0-9]{1,2})?px$/,n=Number.parseFloat(v);
     if(k==='position'){if(v!=='absolute')err('Sadece absolute position destekleniyor')}
     else if(k==='margin'){if(v!=='0')err('Geçersiz margin')}
     else if(k==='right'||k==='bottom'){if(v!=='auto')err('Yerleşim ankrajı yalnızca auto olabilir')}
     else if(k==='text-align'){if(!['left','right','center','justify','start','end'].includes(v))err('Geçersiz hizalama')}
     else if(k==='object-fit'){if(!['cover','contain','fill'].includes(v))err('Geçersiz fotoğraf uyumu')}
     else if(k==='visibility'){if(!['visible','hidden'].includes(v))err('Geçersiz görünürlük')}
     else if(k==='object-position'){var m=v.match(/^(\d{1,3})% (\d{1,3})%$/);if(!m||Number(m[1])>100||Number(m[2])>100)err('Geçersiz kadraj')}
     else if(k==='font-weight'){if(!/^[1-9]\d{1,2}$/.test(v)||n<100||n>900)err('Geçersiz font ağırlığı')}
     else if(k==='line-height'){if(!/^(?:[0-3](?:\.\d{1,2})?)$/.test(v)||n<0.6||n>3)err('Geçersiz satır yüksekliği')}
     else if(k==='opacity'){if(!/^(?:0(?:\.\d{1,2})?|1(?:\.0{1,2})?)$/.test(v))err('Geçersiz opaklık')}
     else if(k==='z-index'){if(!/^-?\d{1,2}$/.test(v)||n< -30||n>30)err('Geçersiz katman sırası')}
     else if(!px.test(v))err('Yalnızca sayısal px kabul ediliyor');
     if((k==='width'||k==='height'||k==='font-size')&&(n<1||n>5000))err('Geçersiz boyut');
     if(k==='border-radius'&&(n<0||n>600))err('Geçersiz köşe yarıçapı');
     if(k==='letter-spacing'&&(n< -20||n>100))err('Geçersiz harf aralığı');
     styles[k]=v;
   });
   var color=e.color;
   if(mode==='direct'&&!HEX.test(color||''))err('Geçersiz özel renk');
   edits[key]={styles:styles,mode:mode};
   if(e.segments!==undefined){
     if(!Array.isArray(e.segments)||e.segments.length<1||e.segments.length>20)err('Geçersiz metin bölümleri');
     var total=0;
     edits[key].segments=e.segments.map(function(part){
       if(typeof part!=='string'||part.length>400||/[\u0000-\u0008\u000B\u000C\u000E-\u001F]/.test(part))err('Geçersiz metin');
       total+=part.length;return part;
     });
     if(total>1600)err('Metin uzunluğu sınırı aşıldı');
   }
   if(mode==='direct')edits[key].color=color.toLowerCase();
 });
 return{colors:colors,edits:edits};
}
function archive(product,versions,current) {
 if(!SLUG.test(product))err('Geçersiz ürün');
 if(!Array.isArray(versions)||versions.length>25)err('Çok fazla sürüm');
 var out=versions.map(function(v){
   if(!plain(v)||!Number.isInteger(v.version)||v.version<2||v.version>26)err('Geçersiz sürüm numarası');
   return{version:v.version,note:String(v.note||'').slice(0,140),time:String(v.time||''),state:state(v.state,25)};
 });
 return{format:'brandstudio-portable',schema:2,brand:'asyada-egitim',product:product,exportedAt:new Date().toISOString(),versions:out,current:state(current,25)};
}
function parse(input,product,pages) {
 if(!plain(input)||input.format!=='brandstudio-portable'||input.schema!==2)err('Bu dosya bir Brandstudio sürüm arşivi değil');
 if(input.brand!=='asyada-egitim'||input.product!==product)err('Arşiv farklı bir marka veya ürüne ait');
 if(!Array.isArray(input.versions)||input.versions.length>25)err('Geçersiz sürüm sayısı');
 var seen={};
 var versions=input.versions.map(function(v){
   if(!plain(v)||!Number.isInteger(v.version)||v.version<2||v.version>26||seen[v.version])err('Tekrarlanan/geçersiz sürüm');
   seen[v.version]=true;
   if(typeof v.note!=='string'||v.note.length>140)err('Geçersiz sürüm notu');
   return {version:v.version,note:v.note,state:state(v.state,pages),time:String(v.time||'')};
 }).sort(function(a,b){return a.version-b.version});
 return{versions:versions,current:state(input.current,pages)};
}
function textNodes(el) {
 var walker=el.ownerDocument.createTreeWalker(el,4),found=[],n;
 while((n=walker.nextNode())){found.push(n);if(found.length>20)break}
 return found;
}
function applyText(el,segments){
 if(segments===undefined)return;
 var parts=textNodes(el);
 if(parts.length!==segments.length)err('Kaynak metin yapısı değişmiş; düzenleme uygulanmadı');
 parts.forEach(function(part,i){part.nodeValue=segments[i]});
}
function locked(el){return el.classList.contains('folio')||!!el.closest('.logo-foot')}
function nodes(doc) {return Array.from(doc.querySelectorAll('.slide '+SELECTOR))}
function colorCSS(colors){return ':root{'+Object.entries(colors).map(function(p){return'--'+p[0]+':'+p[1]+';'}).join('')+'}\n'}
function patch(el,edit){
 if(locked(el))err('Kilitli marka öğesi düzenlenemez');
 applyText(el,edit.segments);
 Object.entries(edit.styles||{}).forEach(function(p){el.style.setProperty(p[0],p[1])});
 if(edit.mode&&edit.mode!=='inherit')el.style.setProperty('color',edit.mode==='direct'?edit.color:'var(--'+edit.mode+')');
}
function sourceDocument(html,sourceUrl,selectedState,index) {
 var doc=new DOMParser().parseFromString(html,'text/html');
 var slide=doc.querySelector('.slide');if(!slide)err('HTML slayt yapısı bulunamadı');
 var base=doc.createElement('base');base.href=sourceUrl;doc.head.insertBefore(base,doc.head.firstChild);
 Object.entries(selectedState.colors).forEach(function(p){doc.documentElement.style.setProperty('--'+p[0],p[1])});
 doc.querySelectorAll('style').forEach(function(el){el.textContent=el.textContent.replace(/#F7F3E9/gi,'var(--paper)').replace(/#1D2027/gi,'var(--ink)').replace(/#BD2120/gi,'var(--red)')});
 slide.dataset.slideIndex=String(index+1);
 nodes(doc).forEach(function(el,i){el.dataset.editIndex=String(i);var edit=selectedState.edits[index+':'+i];if(edit)patch(el,edit)});
 return doc;
}
function html(html,sourceUrl,selectedState,index) {
 var doc=sourceDocument(html,sourceUrl,state(selectedState,25),index);
 return '<!doctype html>\n'+doc.documentElement.outerHTML;
}
function path(el,rootEl) {
 var parts=[];
 while(el&&el!==rootEl) {
  var n=1,other=el.previousElementSibling;
  while(other){if(other.tagName===el.tagName)n++;other=other.previousElementSibling}
  parts.unshift(el.tagName.toLowerCase()+':nth-of-type('+n+')');
  el=el.parentElement;
 }
 if(el!==rootEl)err('Katman seçicisi oluşturulamadı');
 return '.slide > '+parts.join(' > ');
}
function css(htmlSource,selectedState,index){
 var checked=state(selectedState,25);
 var doc=new DOMParser().parseFromString(htmlSource,'text/html'),slide=doc.querySelector('.slide');
 if(!slide)err('Kaynak HTML bulunamadı');
 var ns=nodes(doc),output=colorCSS(checked.colors);
 Object.entries(checked.edits).forEach(function(pair){
  var sp=pair[0].split(':');if(Number(sp[0])!==index)return;
  var el=ns[Number(sp[1])];if(!el)err('Kaynakta düzenlenen katman artık yok');if(locked(el))err('Kilitli marka öğesi CSS ile düzenlenemez');
  var e=pair[1],styles=Object.assign({},e.styles);
  if(e.mode&&e.mode!=='inherit')styles.color=e.mode==='direct'?e.color:'var(--'+e.mode+')';
  output+=path(el,slide)+'{'+Object.entries(styles).map(function(p){return p[0]+':'+p[1]+';'}).join('')+'}\n';
 });
 return output;
}
root.BrandstudioPortable={selector:SELECTOR,validateState:state,makeArchive:archive,parseArchive:parse,html:html,css:css,textNodes:textNodes,applyText:applyText};
})(globalThis);
