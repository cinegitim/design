/* Brandstudio browser-only portable version codec.
   Pure helpers; no network calls, no remote writes, no paid services. */
(function(root) {
"use strict";
var SELECTOR='h1,h2,h3,p,.eyebrow,.dek,.photo,.country-line,.country-grid b,.country-list span,.options span,.cta-pill,.pathways span,.folio,.logo-foot,.cover-rule,.question-bottom,.question-photo,img';
var COLORS={paper:'#f7f3e9',ink:'#1d2027',red:'#bd2120'};
var ALLOWED_STYLES={'position':1,'left':1,'top':1,'width':1,'margin':1,'font-size':1};
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
     if(k==='position'&&v!=='absolute')err('Sadece absolute position destekleniyor');
     else if(k==='margin'&&v!=='0')err('Geçersiz margin');
     else if(k!=='position'&&k!=='margin'&&!/^-?[0-9]{1,5}(?:\.[0-9]{1,2})?px$/.test(v))err('Yalnızca sayısal px kabul ediliyor');
     if(k==='width'&&parseFloat(v)<=0)err('Genişlik pozitif olmalı');
     styles[k]=v;
   });
   var color=e.color;
   if(mode==='direct'&&!HEX.test(color||''))err('Geçersiz özel renk');
   edits[key]={styles:styles,mode:mode};
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
function nodes(doc) {return Array.from(doc.querySelectorAll('.slide '+SELECTOR))}
function colorCSS(colors){return ':root{'+Object.entries(colors).map(function(p){return'--'+p[0]+':'+p[1]+';'}).join('')+'}\n'}
function patch(el,edit){
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
  var el=ns[Number(sp[1])];if(!el)err('Kaynakta düzenlenen katman artık yok');
  var e=pair[1],styles=Object.assign({},e.styles);
  if(e.mode&&e.mode!=='inherit')styles.color=e.mode==='direct'?e.color:'var(--'+e.mode+')';
  output+=path(el,slide)+'{'+Object.entries(styles).map(function(p){return p[0]+':'+p[1]+';'}).join('')+'}\n';
 });
 return output;
}
root.BrandstudioPortable={selector:SELECTOR,validateState:state,makeArchive:archive,parseArchive:parse,html:html,css:css};
})(globalThis);
