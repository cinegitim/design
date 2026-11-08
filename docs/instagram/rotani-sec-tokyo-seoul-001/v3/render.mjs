import {createRequire} from 'node:module';
import {dirname,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
const here=dirname(fileURLToPath(import.meta.url));
const require=createRequire(import.meta.url);
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright-core');
const executablePath=process.env.CHROME_PATH||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const ids=['01-admission-letter','02-campus-geography','03-six-universities','04-english-taught','05-accommodation','06-final-decision'];
const exact=JSON.parse(readFileSync(resolve(here,'exact-copy.json'),'utf8')).slides;
mkdirSync(resolve(here,'final'),{recursive:true});
mkdirSync(resolve(here,'mobile'),{recursive:true});
const browser=await chromium.launch({headless:true,executablePath,args:['--allow-file-access-from-files']});
const report={};
const norm=s=>s.replace(/\s+/g,' ').trim();
try{
 for(const id of ids){
  const page=await browser.newPage({viewport:{width:1080,height:1350},deviceScaleFactor:1});
  await page.goto(pathToFileURL(resolve(here,'source',id+'.html')).href,{waitUntil:'networkidle'});
  await page.evaluate(()=>document.fonts.ready);
  const info=await page.evaluate(()=>{
   const rect=e=>{const r=e.getBoundingClientRect();return{x:r.x,y:r.y,width:r.width,height:r.height,right:r.right,bottom:r.bottom}};
   const groups=[...document.querySelectorAll('#editable-campaign-copy > g[data-copy]')].sort((a,b)=>Number(a.dataset.copy)-Number(b.dataset.copy));
   const copy=groups.map(e=>{
    const texts=e.querySelectorAll('text');
    // Same measured line concatenates directly; separate lines join with one space.
    let joined='',prevY=null;
    texts.forEach(t=>{
     const y=Number(t.getAttribute('y'));
     if(prevY!==null&&Math.abs(y-prevY)>4)joined+=' ';
     joined+=t.textContent;prevY=y;
    });
    // Typographic line boxes: baseline-anchored intervals from the DOM measurement,
    // not generous ink bounds, so adjacent blocks do not false-positive.
    let top=Infinity,bottom=-Infinity,left=Infinity,right=-Infinity;
    texts.forEach(t=>{
     const bb=t.getBBox();const lt=Number(t.getAttribute('data-linetop')),lh=Number(t.getAttribute('data-lineheight'));
     const ltop=isNaN(lt)?bb.y:Math.min(lt,lt+lh),lbot=isNaN(lt)?bb.y+bb.height:Math.max(lt,lt+lh);
     top=Math.min(top,ltop);bottom=Math.max(bottom,lbot);left=Math.min(left,bb.x);right=Math.max(right,bb.x+bb.width);
    });
    // Ink extents from real glyph outlines, and the painted chip each line sits in.
    let inkX=Infinity,inkY=Infinity,inkR=-Infinity,inkB=-Infinity;
    const lines=[];
    texts.forEach(t=>{
     const bb=t.getBBox();
     inkX=Math.min(inkX,bb.x);inkY=Math.min(inkY,bb.y);
     inkR=Math.max(inkR,bb.x+bb.width);inkB=Math.max(inkB,bb.y+bb.height);
     // Centring is per line: a multi-line block has its own chip per line, so
     // unioning the group would measure line 2 against line 1's box.
     if(t.dataset.chipX!==undefined)lines.push({y:bb.y,bottom:bb.y+bb.height,
      chip:{x:Number(t.dataset.chipX),y:Number(t.dataset.chipY),
            width:Number(t.dataset.chipW),height:Number(t.dataset.chipH)}});});
    return{index:Number(e.dataset.copy),role:e.getAttribute('data-role'),
     text:joined.replace(/\s+/g,' ').trim(),
     runCount:texts.length,
     box:{x:left,y:top,width:right-left,height:bottom-top,right:right,bottom:bottom},
     ink:isFinite(inkX)?{x:inkX,y:inkY,width:inkR-inkX,height:inkB-inkY}:null,
     lines};
   });
   const logo=document.querySelector('#canonical-lockup');
   const logoBox=logo?rect(logo):null;
   // How far down the canvas real content reaches. A slide whose content stops
   // short leaves a dead band at the base, which no collision test would catch.
   const mediaBottom=[...document.querySelectorAll('img')]
    .reduce((m,i)=>Math.max(m,i.getBoundingClientRect().bottom),0);
   return{viewport:[innerWidth,innerHeight],jostLoaded:document.fonts.check('700 60px Jost'),copy,mediaBottom,
    logo:logo?{box:logoBox,lockupId:logo.dataset.lockupId,href:logo.getAttribute('href')}:null,
    images:[...document.images].map(i=>({src:i.getAttribute('src')||i.getAttribute('href'),complete:i.complete}))};
  });
  const issues=[],expected=exact[id].map(norm),rendered=info.copy.map(x=>norm(x.text));
  if(!info.jostLoaded)issues.push('Jost failed to load');
  // Centring gate: ink must sit inside its chip, never riding high. Measured from
  // real glyph outlines against the painted chip rect, because a synthesised line
  // top silently pins copy to the top of an otherwise centred box.
  for(const x of info.copy){
   // Group lines by the chip they share. A badge holding a wrapped paragraph is
   // centred as a block; a row of separate chips is centred line by line.
   const byChip=new Map();
   for(const ln of x.lines||[]){
    const c=ln.chip,k=[c.x,c.y,c.width,c.height].join(',');
    if(!byChip.has(k))byChip.set(k,{chip:c,y:Infinity,bottom:-Infinity});
    const e=byChip.get(k);if(ln.y<e.y)e.y=ln.y;if(ln.bottom>e.bottom)e.bottom=ln.bottom;}
   for(const e of byChip.values()){
    const topGap=e.y-e.chip.y;
    const botGap=(e.chip.y+e.chip.height)-e.bottom;
    const lift=botGap-topGap;
    if(topGap<2)issues.push(`copy sits on the top edge of its chip: #${x.index} ${x.role} gap=${topGap.toFixed(1)}px`);
    else if(lift>8)issues.push(`copy rides high in its chip: #${x.index} ${x.role} lift=${lift.toFixed(1)}px`);
   }
  }
  if(JSON.stringify(rendered)!==JSON.stringify(expected))
   issues.push(`exact-copy mismatch\nexpected=${JSON.stringify(expected)}\nrendered=${JSON.stringify(rendered)}`);
  if(info.copy.some((x,i)=>x.index!==i))issues.push('data-copy indexes are not contiguous');
  for(const x of info.copy){
   const b=x.box;
   if(b.x<24||b.y<24||b.right>1056||b.bottom>1326)issues.push(`copy outside safe margins: #${x.index} ${x.role}`);
   if(x.runCount<1)issues.push(`no glyph runs: #${x.index}`);
   if(x.text.length<1)issues.push(`empty text: #${x.index}`);
  }
  for(let i=0;i<info.copy.length;i++)for(let j=i+1;j<info.copy.length;j++){
   const a=info.copy[i].box,b=info.copy[j].box;
   const ox=Math.min(a.right,b.right)-Math.max(a.x,b.x),oy=Math.min(a.bottom,b.bottom)-Math.max(a.y,b.y);
   if(ox>2&&oy>2)issues.push(`copy collision: #${info.copy[i].index} ${info.copy[i].role} / #${info.copy[j].index} ${info.copy[j].role}`);
  }
  if(!info.logo)issues.push('canonical lockup missing');
  else{
   const l=info.logo.box;
   if(l.x<24||l.y<24||l.right>1056||l.bottom>1326)issues.push('logo outside safe margins');
   for(const x of info.copy){
    const b=x.box;const ox=Math.min(b.right,l.right)-Math.max(b.x,l.x),oy=Math.min(b.bottom,l.bottom)-Math.max(b.y,l.y);
    if(ox>2&&oy>2)issues.push(`copy intersects logo: #${x.index} ${x.role}`);
   }
  }
  // Base fill gate: content must reach the foot of the canvas. Without this, a
  // slide can pass every collision test and still ship a large empty band.
  // 1250 = a dead band no deeper than 100px; the design's own bottom margins run
  // 46-78px, so this leaves slack for editorial variation but fails loudly on
  // the real defect class (a slide that once ended 330px short).
  const MIN_BASE_FILL=1250;
  const fill=Math.max(info.mediaBottom||0,...info.copy.map(x=>x.box.bottom),info.logo?info.logo.box.bottom:0);
  info.baseFill=Math.round(fill);
  if(fill<MIN_BASE_FILL)issues.push(`dead band at the base: content ends at y=${Math.round(fill)}, expected >=${MIN_BASE_FILL}`);

  for(const img of info.images)if(!img.complete)issues.push(`image failed: ${img.src}`);
  info.expectedCopy=expected;info.geometryIssues=issues;
  if(issues.length&&!process.env.DRAFT_RENDER)throw Error(`${id}\n${issues.join('\n')}`);
  await page.screenshot({path:resolve(here,'final',id+'.png'),type:'png',fullPage:false});
  await page.setViewportSize({width:375,height:469});
  await page.screenshot({path:resolve(here,'mobile',id+'-375x469.png'),type:'png',fullPage:false});
  report[id]={jostLoaded:info.jostLoaded,copy:info.copy,logo:info.logo,baseFill:info.baseFill,geometryIssues:issues,expectedCopy:expected};
  console.log(`Rendered ${id}: copy=${rendered.length}, collisions/geometry=${issues.length}, mobile preview exported`);
  await page.close();
 }
}finally{await browser.close()}
writeFileSync(resolve(here,'geometry-audit.json'),JSON.stringify(report,null,2));
