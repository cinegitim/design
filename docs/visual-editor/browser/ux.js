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
function selectionTargets(existing,clicked,groups,extend) {
 var related=(groups||[]).find(function(g){return g.includes(clicked)})||[clicked];
 if(!extend)return related.slice();
 var all=related.every(function(id){return existing.includes(id)});
 return all?existing.filter(function(id){return !related.includes(id)}):
  Array.from(new Set(existing.concat(related)));
}
function bounds(rects){
 if(!rects.length)return null;
 var x=Math.min(...rects.map(function(r){return r.x})),
 y=Math.min(...rects.map(function(r){return r.y})),
 right=Math.max(...rects.map(function(r){return r.x+r.w})),
 bottom=Math.max(...rects.map(function(r){return r.y+r.h}));
 return{x:x,y:y,w:right-x,h:bottom-y};
}
function resizeRect(box,direction,dx,dy,proportional) {
 var l=box.x,t=box.y,r=box.x+box.w,b=box.y+box.h;
 if(direction.includes('w'))l+=dx;
 if(direction.includes('e'))r+=dx;
 if(direction.includes('n'))t+=dy;
 if(direction.includes('s'))b+=dy;
 var w=Math.min(5000,Math.max(20,r-l)),h=Math.min(5000,Math.max(20,b-t));
 if(proportional){
  var sx=w/Math.max(1,box.w),sy=h/Math.max(1,box.h),horizontal=direction==='w'||direction==='e',vertical=direction==='n'||direction==='s';
  var scale=horizontal?sx:vertical?sy:(Math.abs(sx-1)>Math.abs(sy-1)?sx:sy);
  scale=Math.max(20/Math.max(1,box.w),20/Math.max(1,box.h),Math.min(scale,5000/Math.max(box.w,box.h)));
  w=box.w*scale;h=box.h*scale;
 }
 if(direction.includes('w'))l=box.x+box.w-w;
 else if(direction.includes('e'))l=box.x;
 else l=box.x+(box.w-w)/2;
 if(direction.includes('n'))t=box.y+box.h-h;
 else if(direction.includes('s'))t=box.y;
 else t=box.y+(box.h-h)/2;
 return{x:l,y:t,w:w,h:h};
}
// Absolute CSS left/top are relative to the nearest positioned ancestor,
// not necessarily the slide. Read its padding edge in artboard coordinates.
function containingBlockOrigin(node,slide){
 var parent=node.offsetParent;
 if(!parent||parent===slide||!slide.contains(parent))return{x:0,y:0};
 var origin=parent.getBoundingClientRect(),artboard=slide.getBoundingClientRect();
 return{x:origin.left-artboard.left+(parent.clientLeft||0),
         y:origin.top-artboard.top+(parent.clientTop||0)};
}
function scaleRect(box,from,to) {
 var sx=to.w/Math.max(1,from.w),sy=to.h/Math.max(1,from.h);
 return{x:to.x+(box.x-from.x)*sx,y:to.y+(box.y-from.y)*sy,w:box.w*sx,h:box.h*sy};
}
function groupLayers(entries,linkedGroups) {
 var sections=[],photos=[],text=[],identity=[],misc=[],used=new Set();
 (linkedGroups||[]).forEach(function(group,i){
  var items=group.map(function(id){return entries.find(function(e){return e.id===id&&!e.isLogo&&!e.isFooter})}).filter(Boolean);
  if(items.length!==group.length||items.length<2)return;
  items.forEach(function(e){used.add(e.id)});
  sections.push({id:'linked-'+i,label:'Bağlı grup '+(i+1),items:items,rank:Math.min(...items.map(function(e){return e.id}))});
 });
 for(var entry of entries) {
  if(used.has(entry.id))continue;
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
root.BrandstudioUX={createHistory:createHistory,groupLayers:groupLayers,proximity:proximity,selectionTargets:selectionTargets,bounds:bounds,resizeRect:resizeRect,scaleRect:scaleRect,containingBlockOrigin:containingBlockOrigin};
})(globalThis);
