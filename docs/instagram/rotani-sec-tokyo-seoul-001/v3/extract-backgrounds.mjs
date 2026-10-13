import {createRequire} from 'node:module';
import {dirname,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {writeFileSync,mkdirSync,readFileSync} from 'node:fs';
const here=dirname(fileURLToPath(import.meta.url));
const require=createRequire(import.meta.url);
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright-core');
const executablePath=process.env.CHROME_PATH||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const ids=['01-admission-letter','02-campus-geography','03-six-universities','04-english-taught','05-accommodation','06-final-decision'];
const exactCopy=JSON.parse(readFileSync(resolve(here,'exact-copy.json'),'utf8')).slides;
mkdirSync(resolve(here,'originals'),{recursive:true});
const browser=await chromium.launch({headless:true,executablePath,args:['--allow-file-access-from-files']});
const report={};
try{
 for(const id of ids){
  const page=await browser.newPage({viewport:{width:1080,height:1350},deviceScaleFactor:1});
  await page.goto(pathToFileURL(resolve(here,'templates',id+'.html')).href,{waitUntil:'networkidle'});
  await page.evaluate(()=>document.fonts.ready);
  const layout=await page.evaluate(()=>{
   const norm=s=>s.replace(/\s+/g,' ').trim();
   const rgbToHex=s=>{const m=s.match(/\d+(?:\.\d+)?/g)||[];return m.length>=3?'#'+m.slice(0,3).map(v=>Math.round(Number(v)).toString(16).padStart(2,'0')).join(''):'#1D2027'};
   // Real font metrics, measured from the loaded face rather than assumed.
   // The Range rect of a glyph run spans the inline box (ascent..descent), so the
   // baseline sits ascent below its top. Guessing a ratio here is what pinned
   // copy to the top of a vertically centred chip, so this is measured per style.
   const metricsCache=new Map();
   const probe=document.createElement('canvas').getContext('2d');
   const metricsOf=cs=>{
    const font=`${cs.fontStyle} ${cs.fontWeight} ${cs.fontSize} ${cs.fontFamily}`;
    let m=metricsCache.get(font);
    if(!m){probe.font=font;m=probe.measureText('Hxlp');
     m={ascentRatio:m.fontBoundingBoxAscent/parseFloat(cs.fontSize),
        descentRatio:m.fontBoundingBoxDescent/parseFloat(cs.fontSize)};metricsCache.set(font,m);}
    return m;};
   // The chip a run sits in: nearest painted ancestor, so "is this copy
   // centred in its box?" becomes a measurable question instead of an opinion.
   // A chip is a badge dedicated to one copy block. Large painted regions (the
   // slide, a full-bleed scrim) and composite cards that hold several copy
   // blocks are excluded: a heading sitting at the top of a card is correct
   // composition, not a centring defect, so it must not be gated.
   const paintedBox=(el,copyEl)=>{
    let e=el;
    while(e&&e!==document.body){
     const c=getComputedStyle(e);
     if(c.backgroundColor&&c.backgroundColor!=='rgba(0, 0, 0, 0)'&&c.backgroundColor!=='transparent'){
      const r=e.getBoundingClientRect();
      const inner=[...e.querySelectorAll('[data-copy]')];
      const dedicated=!e.querySelector('[data-decor]')
       &&inner.length<=1&&(inner.length===0?copyEl.contains(e):inner[0]===copyEl);
      if(dedicated&&r.width>=24&&r.height>=12&&r.height<=280&&r.width*r.height<=120000)
       return{x:r.x,y:r.y,width:r.width,height:r.height,right:r.right,bottom:r.bottom};}
     e=e.parentElement;}
    return null;};
   // Immutable copy blocks. Decorative editorial type is excluded via data-decor.
   const copy=[...document.querySelectorAll('[data-copy]')].sort((a,b)=>Number(a.dataset.copy)-Number(b.dataset.copy)).map(el=>{
    const runs=[];const walker=document.createTreeWalker(el,NodeFilter.SHOW_TEXT);let node;
    while(node=walker.nextNode()){
     if(!node.data)continue;
     if(node.parentElement&&node.parentElement.closest('[data-decor="1"]'))continue;
     const parent=node.parentElement||el,cs=getComputedStyle(parent);
     let run=null,lastX=-Infinity,lineIndex=0;
     for(let i=0;i<node.data.length;i++){
      const range=document.createRange();range.setStart(node,i);range.setEnd(node,i+1);
      const rect=range.getBoundingClientRect();const ch=node.data[i];
      // Zero-width whitespace carries no box but must stay in the run text
      // so inline-span spacing survives (SVG default collapsing would eat it).
      if(!rect.width&&ch.trim()===''){if(run)run.text+=ch;else if(runs.length)runs[runs.length-1].text+=ch;continue}
      if(!rect.width&&!ch.trim())continue;
      const style={fontSize:parseFloat(cs.fontSize),fontWeight:cs.fontWeight,color:rgbToHex(cs.color),letterSpacing:parseFloat(cs.letterSpacing)||0,lineHeight:parseFloat(cs.lineHeight)||parseFloat(cs.fontSize)*1.2,...metricsOf(cs)};
      if(run&&rect.x<lastX-5){lineIndex++;run=null}
      if(!run){run={text:'',x:rect.x,top:rect.top,height:rect.height,lineIndex,chipBox:paintedBox(parent,el),...style};runs.push(run)}
      run.text+=ch;run.height=Math.max(run.height,rect.height);lastX=rect.x;
     }
    }
    let globalLine=0,previousTop=null;
    for(const run of runs){if(previousTop!==null&&Math.abs(run.top-previousTop)>Math.max(8,run.lineHeight*.35))globalLine++;run.lineIndex=globalLine;previousTop=run.top;run.text=run.text.replace(/[\t\r\n]+/g,' ').replace(/ {2,}/g,' ');}
    const r=el.getBoundingClientRect(),ecs=getComputedStyle(el);
    let container=null,con=el.parentElement;
    while(con&&con!==document.body){const cr=con.getBoundingClientRect();
     if(cr.width<1080&&cr.height<1350){container=cr;break}con=con.parentElement}
    return{index:Number(el.dataset.copy),role:el.dataset.role||'',
     contractText:norm(el.innerText),
     box:{x:r.x,y:r.y,width:r.width,height:r.height,right:r.right,bottom:r.bottom},
     parent:container?{x:container.x,y:container.y,width:container.width,height:container.height,right:container.right,bottom:container.bottom}:null,
     paddingTop:parseFloat(ecs.paddingTop)||0,fontSize:parseFloat(ecs.fontSize),runs};
   });
   const decor=[...document.querySelectorAll('[data-decor="1"]')].map(el=>{
    const r=el.getBoundingClientRect(),cs=getComputedStyle(el);
    return{text:norm(el.innerText),box:{x:r.x,y:r.y,width:r.width,height:r.height,right:r.right,bottom:r.bottom},
     fontSize:parseFloat(cs.fontSize),lineHeight:parseFloat(cs.lineHeight)||parseFloat(cs.fontSize)*1.2,fontWeight:cs.fontWeight,color:rgbToHex(cs.color),...metricsOf(cs)};
   });
   const logo=document.querySelector('.logo,img[data-lockup-id]');const r=logo.getBoundingClientRect();
   const lcs=getComputedStyle(logo);
   // Record the lockup's own padding-box chip: visibility:hidden also hides the chip,
   // so the contrast check must know the true ground behind the artwork.
   return{copy,decor,logo:{x:r.x,y:r.y,width:r.width,height:r.height,right:r.right,bottom:r.bottom,
    lockupId:logo.dataset.lockupId,file:logo.getAttribute('src').split('/').pop(),
    chipColor:lcs.backgroundColor,chipAlpha:lcs.backgroundColor.indexOf('rgba')===0?Number(lcs.backgroundColor.split(',')[3]):1}};
  });
  const issues=[];
  if(layout.copy.some((x,i)=>x.index!==i))issues.push('data-copy indexes are not contiguous');
   // Chain 1: rendered DOM innerText must equal the immutable copy contract.
   const contract=exactCopy[id].map(s=>s.replace(/\s+/g,' ').trim());
   const domText=layout.copy.map(x=>x.contractText);
   if(JSON.stringify(domText)!==JSON.stringify(contract))
    issues.push(`exact-copy mismatch (DOM vs contract)\nexpected=${JSON.stringify(contract)}\nrendered=${JSON.stringify(domText)}`);
  for(const x of layout.copy){
   const b=x.box;
   if(b.x<24||b.y<24||b.right>1056||b.bottom>1326)issues.push(`copy outside safe margins: #${x.index} ${x.role} ${JSON.stringify(b)}`);
   if(b.width<1||b.height<1)issues.push(`empty copy box: #${x.index}`);
   if(x.parent){const p=x.parent;
    if(b.x<p.x-2||b.y<p.y-2||b.right>p.right+2||b.bottom>p.bottom+2)issues.push(`copy escapes its container: #${x.index} ${x.role}`)}
   if(!x.runs.length)issues.push(`no measured glyph runs: #${x.index} ${x.role}`);
  }
  // Decorative type is still audited for bounds and collisions, but is not contract text.
  for(const d of layout.decor){
   const b=d.box;
   if(b.x<24||b.y<24||b.right>1056||b.bottom>1326)issues.push(`decorative type outside safe margins: ${d.text}`);
  }
  for(let i=0;i<layout.copy.length;i++)for(let j=i+1;j<layout.copy.length;j++){
   const a=layout.copy[i].box,b=layout.copy[j].box;
   const ox=Math.min(a.right,b.right)-Math.max(a.x,b.x),oy=Math.min(a.bottom,b.bottom)-Math.max(a.y,b.y);
   if(ox>2&&oy>2)issues.push(`copy collision: #${layout.copy[i].index} ${layout.copy[i].role} / #${layout.copy[j].index} ${layout.copy[j].role} ${JSON.stringify(a)} vs ${JSON.stringify(b)}`);
  }
  for(const x of layout.copy)for(const d of layout.decor){
   const a=x.box,b=d.box;
   const ox=Math.min(a.right,b.right)-Math.max(a.x,b.x),oy=Math.min(a.bottom,b.bottom)-Math.max(a.y,b.y);
   if(ox>2&&oy>2)issues.push(`copy/decor collision: #${x.index} ${x.role} / ${d.text}`);
  }
  const l=layout.logo;
  if(l.x<24||l.y<24||l.right>1056||l.bottom>1326)issues.push(`logo outside safe margins ${JSON.stringify(l)}`);
  for(const x of [...layout.copy,...layout.decor]){
   const b=x.box;const ox=Math.min(b.right,l.right)-Math.max(b.x,l.x),oy=Math.min(b.bottom,l.bottom)-Math.max(b.y,l.y);
   if(ox>2&&oy>2)issues.push(`copy intersects logo: #${x.index!==undefined?x.index:'decor'} ${x.role||x.text}`);
  }
  const imgs=await page.evaluate(()=>[...document.images].map(i=>({src:i.getAttribute('src'),complete:i.complete,naturalWidth:i.naturalWidth,naturalHeight:i.naturalHeight})));
  for(const img of imgs)if(!img.complete||!img.naturalWidth)issues.push(`image failed to load: ${img.src}`);
  layout.issues=issues;layout.images=imgs;
  if(issues.length&&!process.env.DRAFT_RENDER)throw Error(`${id}\n${issues.join('\n')}`);
  await page.addStyleTag({content:'[data-copy],[data-copy] *,[data-decor="1"]{color:transparent!important;-webkit-text-stroke-color:transparent!important;text-shadow:none!important}img[data-lockup-id]{visibility:hidden!important}'});
  await page.screenshot({path:resolve(here,'originals',id+'.png'),type:'png',fullPage:false});
  report[id]=layout;
  console.log(`Extracted ${id}: ${layout.copy.length} copy blocks, ${layout.decor.length} decorative, ${issues.length} geometry issues`);
  await page.close();
 }
}finally{await browser.close()}
writeFileSync(resolve(here,'text-layout.json'),JSON.stringify(report,null,2));
