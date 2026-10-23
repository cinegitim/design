/* Brandstudio Browser Editor UX utilities; no storage or network. */
(function(root) {
"use strict";
function copy(value){return JSON.parse(JSON.stringify(value))}
function createHistory(max) {
 var limit=Math.min(60,Math.max(1,Number(max)||30)),past=[],future=[];
 return {
  checkpoint:function(value){past.push(copy(value));if(past.length>limit)past.shift();future.length=0;return {undo:past.length,redo:future.length}},
  undo:function(value){if(!past.length)return null;future.push(copy(value));return copy(past.pop())},
  redo:function(value){if(!future.length)return null;past.push(copy(value));return copy(future.pop())},
  clear:function(){past.length=0;future.length=0},
  status:function(){return {undo:past.length,redo:future.length}}
 };
}
function proximity(a,b) {
 if(!a||!b)return 0;
 var ix=Math.max(0,Math.min(a.x+a.w,b.x+b.w)-Math.max(a.x,b.x));
 var iy=Math.max(0,Math.min(a.y+a.h,b.y+b.h)-Math.max(a.y,b.y));
 var overlap=ix*iy,denom=Math.max(1,a.w*a.h);
 if(overlap/denom>0.03)return 100+overlap/denom;
 var dx=Math.max(0,Math.max(a.x-b.x-b.w,b.x-a.x-a.w));
 var dy=Math.max(0,Math.max(a.y-b.y-b.h,b.y-a.y-a.h));
 var gap=Math.sqrt(dx*dx+dy*dy);
 return gap<=55?55-gap:0;
}
function groupLayers(entries) {
 var sections=[],photos=[],text=[],identity=[],misc=[];
 for(var entry of entries) {
  if(entry.isLogo||entry.isFooter)identity.push(entry);
  else if(entry.isPhoto)photos.push(entry);
  else if(entry.isText)text.push(entry);
  else misc.push(entry);
 }
 var clusters=photos.map(function(p,i){return {id:'photo-'+i,label:photos.length>1?'Fotoğraf '+(i+1)+' ve üzerindeki yazılar':'Fotoğraf ve üzerindeki yazılar',items:[p],rank:p.id}});
 var loose=[];
 for(var t of text) {
  var best=null,max=0;
  for(var c of clusters) {
   var score=proximity(t.rect,c.items[0].rect);
   if(score>max){max=score;best=c}
  }
  if(best&&max>0)best.items.push(t);else loose.push(t);
 }
 // Keep semantic headings visible even if photos are far away.
 if(loose.length)sections.push({id:'copy',label:'Başlıklar ve açıklamalar',items:loose,rank:loose[0].id});
 for(var c of clusters)sections.push(c);
 if(misc.length)sections.push({id:'other',label:'Diğer katmanlar',items:misc,rank:misc[0].id});
 if(identity.length)sections.push({id:'identity',label:'Logo ve dipnot',items:identity,rank:identity[0].id});
 sections.sort(function(a,b){return a.rank-b.rank});
 for(var c of sections)c.items.sort(function(a,b){return a.id-b.id});
 return sections;
}
root.BrandstudioUX={createHistory:createHistory,groupLayers:groupLayers,proximity:proximity};
})(globalThis);
