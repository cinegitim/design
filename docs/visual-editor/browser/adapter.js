/* Generic source adapter for browser-only editing. Does not alter committed originals. */
(function(root){
"use strict";
var SELECTABLE='h1,h2,h3,h4,h5,p,figcaption,blockquote,.txt,.photo,img:not([data-canonical-id]),[data-copy],.cta-pill,.slide > *, .slide [class]';
function dimensions(text,kind){
 var w=1080,h=1350;
 if(kind==='image'){
  var rootSvg=text.match(/<svg\b[^>]*\bwidth=["'](\d{2,5})[^"']*["'][^>]*\bheight=["'](\d{2,5})/i);
  if(rootSvg){w=Number(rootSvg[1]);h=Number(rootSvg[2])}
 }else{
  var viewport=text.match(/<meta[^>]+name=["']viewport["'][^>]+content=["'][^"']*width=(\d{2,5})[^"']*height=(\d{2,5})/i);
  var body=text.match(/(?:html\s*,\s*body|html,body|\.slide|\.banner-container)\s*\{[^}]{0,200}\bwidth:\s*(\d{2,5})px\s*;[^}]{0,200}\bheight:\s*(\d{2,5})px/i);
  if(viewport){w=+viewport[1];h=+viewport[2]}
  else if(body){w=+body[1];h=+body[2]}
 }
 return{width:Math.max(160,Math.min(6000,w)),height:Math.max(160,Math.min(6000,h))}
}
function escapeAttr(s){return String(s).replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;')}
function normalize(source,url,kind){
 if(!/^https?:\/\//.test(url))throw Error('Kaynak URL geçersiz');
 var media=/\.(png|jpe?g|webp|svg)(?:[?#]|$)/i.test(url);
 if((kind==='image'||media)&&!url.toLowerCase().split(/[?#]/)[0].endsWith('.svg')){
  var dim=dimensions(source||'',kind),ext=url.split(/[?#]/)[0].split('.').pop().toLowerCase();
  // Image originals are preserved as a single editable object; rasterized text has no recoverable text layers.
  return{html:'<!doctype html><html><head><meta charset="utf-8"><style>html,body{margin:0;width:'+dim.width+'px;height:'+dim.height+'px}.slide{position:relative;width:'+dim.width+'px;height:'+dim.height+'px;overflow:hidden}img.photo{display:block;position:absolute;inset:0;width:100%;height:100%;object-fit:contain}</style></head><body><div class="slide"><img class="photo" alt="Orijinal tasarım" src="'+escapeAttr(url)+'"></div></body></html>',width:dim.width,height:dim.height,mode:'whole-image',format:ext}
 }
 var d=new DOMParser().parseFromString(source,'text/html');
 d.querySelectorAll('script').forEach(function(node){node.remove()});
 var meta=d.createElement('base');meta.href=url;d.head.insertBefore(meta,d.head.firstChild);
 var slide=d.querySelector('.slide');
 var embeddedSVG=d.body.querySelector('svg');
 var dims=dimensions(source,embeddedSVG?'image':'html');
 if(!slide){
  slide=d.createElement('div');slide.className='slide';
  slide.style.cssText='position:relative;width:'+dims.width+'px;height:'+dims.height+'px;overflow:hidden';
  var children=Array.from(d.body.childNodes);
  children.forEach(function(node){slide.appendChild(node)});
  d.body.appendChild(slide);
  if(embeddedSVG&&embeddedSVG.parentElement===slide){
   embeddedSVG.style.width='100%';embeddedSVG.style.height='100%';embeddedSVG.style.display='block'
  }
 }
 // DOM candidates are deterministic, so portable exports keep the same source index.
 // Never expose canonical SVG internals as independently editable objects.
 var candidates=Array.from(slide.querySelectorAll(SELECTABLE+',svg text,svg image,svg rect'));
 var n=0;
 candidates.forEach(function(el){
  if(n>=480)return;
  if(el.closest('[data-canonical-id],#canonical-lockup')||el.matches('svg rect')&&!el.hasAttribute('data-copy'))return;
  if(el.matches('svg image')&&el.getAttribute('id')==='canonical-lockup')return;
  if(el.closest('[data-browser-editable]')&&el.tagName.toLowerCase()!=='img')return;
  el.setAttribute('data-browser-editable','1');n++
 });
 return{html:'<!doctype html>\n'+d.documentElement.outerHTML,width:dims.width,height:dims.height,mode:'layers',format:'html'}
}
root.BrandstudioAdapter={normalize:normalize,dimensions:dimensions};
})(typeof globalThis!=='undefined'?globalThis:this);
