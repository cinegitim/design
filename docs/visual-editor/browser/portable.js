/* Brandstudio browser-only portable version codec.
   Pure helpers; no network calls, no remote writes, no paid services. */
(function(root) {
"use strict";
var SELECTOR='h1,h2,h3,p,.eyebrow,.dek,.photo,.country-line,.country-grid b,.country-list span,.options span,.cta-pill,.pathways span,.folio,.logo-foot,.cover-rule,.question-bottom,.question-photo,img';
var COLORS={paper:'#f7f3e9',ink:'#1d2027',red:'#bd2120'};
var ALLOWED_STYLES={'position':1,'left':1,'top':1,'right':1,'bottom':1,'width':1,'height':1,'margin':1,'font-size':1,'font-weight':1,'letter-spacing':1,'line-height':1,'text-align':1,'opacity':1,'object-fit':1,'object-position':1,'border-radius':1,'z-index':1,'visibility':1,'background-color':1,'max-width':1,'font-family':1};
var ALLOWED_MODES={inherit:1,paper:1,ink:1,red:1,direct:1};
var HEX=/^#[0-9a-fA-F]{6}$/;
var SLUG=/^[a-z0-9]+(?:-[a-z0-9]+)*$/;
var MEDIA=/^data:image\/(?:webp|jpeg|png);base64,([A-Za-z0-9+/]+={0,2})$/;
var MAX_MEDIA=260000,MAX_MEDIA_COUNT=8,MAX_STATE=2100000;
function err(message){throw new Error(message)}
function plain(x){return !!x&&typeof x==='object'&&!Array.isArray(x)}
function state(input,maxPages) {
 if(!plain(input)||!plain(input.colors)||!plain(input.edits))err('Geçersiz sürüm durumu');
 var inputLength=JSON.stringify(input).length;
 var withMedia=Object.values(input.edits).some(function(e){return plain(e)&&e.image!==undefined});
 if(inputLength>(withMedia?MAX_STATE:32768))err(withMedia?'Fotoğraflı sürüm 2,1 MB sınırını aşıyor':'Sürüm durumu 32 KB sınırını aşıyor');
 var colors={};Object.keys(COLORS).forEach(function(k){var v=input.colors[k];if(!HEX.test(v||''))err('Geçersiz renk: '+k);colors[k]=v.toLowerCase()});
 if(Object.keys(input.colors).some(function(k){return !Object.prototype.hasOwnProperty.call(COLORS,k)}))err('Bilinmeyen renk anahtarı');
 var edits={},keys=Object.keys(input.edits),mediaCount=0;
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
     else if(k==='max-width'){if(v!=='none')err('Yalnızca max-width:none destekleniyor')}
     else if(k==='right'||k==='bottom'){if(v!=='auto')err('Yerleşim ankrajı yalnızca auto olabilir')}
     else if(k==='font-family'){if(!['Jost','Arial','Georgia','Inter'].includes(v))err('Geçersiz font')}
     else if(k==='text-align'){if(!['left','right','center','justify','start','end'].includes(v))err('Geçersiz hizalama')}
     else if(k==='background-color'){if(!HEX.test(v))err('Geçersiz arka plan rengi')}
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
   if(e.image!==undefined){
     if(typeof e.image!=='string'||e.image.length>MAX_MEDIA||!MEDIA.test(e.image)||e.image.length<60)err('Yalnızca küçük PNG/JPEG/WebP fotoğraf verisi kabul ediliyor');
     var encoded=e.image.slice(e.image.indexOf(',')+1);
     if(encoded.length%4!==0)err('Geçersiz fotoğraf kodlaması');
     mediaCount++;if(mediaCount>MAX_MEDIA_COUNT)err('Bir sürümde en fazla 8 fotoğraf değiştirilebilir');
     edits[key].image=e.image;
   }
   if(mode==='direct')edits[key].color=color.toLowerCase();
 });
 var groups={},inputGroups=input.groups===undefined?{}:input.groups;
 if(!plain(inputGroups))err('Geçersiz katman grupları');
 if(Object.keys(inputGroups).length>maxPages)err('Çok fazla slayt grubu');
 Object.entries(inputGroups).forEach(function(pair){
   var key=pair[0],page=Number(key),list=pair[1];
   if(!/^(0|[1-9][0-9]*)$/.test(key)||page>=maxPages||!Array.isArray(list)||list.length>25)err('Geçersiz grup slaytı');
   var members=new Set();
   groups[key]=list.map(function(group){
     if(!Array.isArray(group)||group.length<2||group.length>24)err('Geçersiz grup boyutu');
     return group.map(function(id){
       if(!Number.isInteger(id)||id<0||id>500||members.has(id))err('Çakışan/geçersiz grup katmanı');
       members.add(id);return id;
     });
   });
 });
 return{colors:colors,edits:edits,groups:groups};
}
function archive(product,versions,current) {
 if(!SLUG.test(product))err('Geçersiz ürün');
 if(!Array.isArray(versions)||versions.length>25)err('Çok fazla sürüm');
 var out=versions.map(function(v){
   if(!plain(v)||!Number.isInteger(v.version)||v.version<2||v.version>26)err('Geçersiz sürüm numarası');
   return{version:v.version,note:String(v.note||'').slice(0,140),time:String(v.time||''),state:state(v.state,25)};
 });
 var result={format:'brandstudio-portable',schema:2,brand:'asyada-egitim',product:product,exportedAt:new Date().toISOString(),versions:out,current:state(current,25)};
 if(JSON.stringify(result).length>16000000)err('Arşiv 16 MB sınırını aşıyor');
 return result;
}
function parse(input,product,pages) {
 if(!plain(input)||input.format!=='brandstudio-portable'||input.schema!==2)err('Bu dosya bir Brandstudio sürüm arşivi değil');
 if(input.brand!=='asyada-egitim'||input.product!==product)err('Arşiv farklı bir marka veya ürüne ait');
 if(!Array.isArray(input.versions)||input.versions.length>25)err('Geçersiz sürüm sayısı');
 if(JSON.stringify(input).length>16000000)err('Arşiv 16 MB sınırını aşıyor');
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
function locked(el){return false} // Placement, typography and folio text are all editable.
function identityArtwork(el){return el.tagName==='IMG'&&!!el.closest('.logo-foot')}
function identityGuard(el,e){
 if(!identityArtwork(el))return;
 if(e.image!==undefined||e.segments!==undefined||e.mode&&e.mode!=='inherit')err('Onaylı logonun içeriği, kaynağı ve rengi değiştirilemez');
 var allowed={'position':1,'left':1,'top':1,'right':1,'bottom':1,'width':1,'margin':1,'z-index':1};
 Object.keys(e.styles||{}).forEach(function(k){if(!allowed[k])err('Logo yalnızca orantılı boyutlandırılabilir ve taşınabilir')});

}
function nodes(doc) {return Array.from(doc.querySelectorAll('.slide '+SELECTOR))}
function colorCSS(colors){return ':root{'+Object.entries(colors).map(function(p){return'--'+p[0]+':'+p[1]+';'}).join('')+'}\n'}
function patch(el,edit){
 // Folio may be edited just like other text.
 identityGuard(el,edit);
 applyText(el,edit.segments);
 if(edit.image!==undefined){
   if(el.tagName!=='IMG')err('Fotoğraf yalnızca img katmanına uygulanabilir');
   el.setAttribute('src',edit.image);
 }
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
  var el=ns[Number(sp[1])];if(!el)err('Kaynakta düzenlenen katman artık yok');var e=pair[1];identityGuard(el,e);var styles=Object.assign({},e.styles);
  if(e.mode&&e.mode!=='inherit')styles.color=e.mode==='direct'?e.color:'var(--'+e.mode+')';
  output+=path(el,slide)+'{'+Object.entries(styles).map(function(p){return p[0]+':'+p[1]+';'}).join('')+'}\n';
 });
 return output;
}
root.BrandstudioPortable={selector:SELECTOR,validateState:state,makeArchive:archive,parseArchive:parse,html:html,css:css,textNodes:textNodes,applyText:applyText,MAX_MEDIA:MAX_MEDIA};
})(globalThis);
