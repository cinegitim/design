import { createRequire } from 'node:module';
import { dirname, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { writeFileSync } from 'node:fs';
const here=dirname(fileURLToPath(import.meta.url));
const require=createRequire(import.meta.url);
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright-core');
const browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_PATH||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',args:['--allow-file-access-from-files']});
const ids=['01-cover','02-perspective','03-five-worlds','04-experience','05-invitation'];
const report={};
try{
 for(const id of ids){
  const page=await browser.newPage({viewport:{width:1080,height:1350},deviceScaleFactor:1});
  await page.goto(pathToFileURL(resolve(here,'source',id+'.html')).href,{waitUntil:'networkidle'});
  await page.evaluate(()=>document.fonts.ready);
  const info=await page.evaluate(()=>{
   const canvas=document.createElement('canvas'),ctx=canvas.getContext('2d');
   const texts=[...document.querySelectorAll('text')].map(el=>{
    const b=el.getBBox(),style=getComputedStyle(el);
    ctx.font=`${style.fontWeight} ${style.fontSize} Jost`;const ink=ctx.measureText(el.textContent),baseline=Number(el.getAttribute('y'));
    return{copy:el.textContent,x:b.x,y:baseline-ink.actualBoundingBoxAscent,width:b.width,height:ink.actualBoundingBoxAscent+ink.actualBoundingBoxDescent,weight:style.fontWeight,family:style.fontFamily,fontBox:{x:b.x,y:b.y,width:b.width,height:b.height}};
   });
   const mark=document.querySelector('#canonical-lockup');const r=mark.getBBox();
   return{jostLoaded:document.fonts.check('720 96px Jost'),textBounds:texts,logoBounds:{x:r.x,y:r.y,width:r.width,height:r.height},viewport:[innerWidth,innerHeight]};
  });
  const issues=[];
  if(!info.jostLoaded)issues.push(id+': Jost not loaded');
  for(const b of info.textBounds){if(b.x<30||b.y<30||b.x+b.width>1050||b.y+b.height>1320)issues.push(id+': unsafe text bounds '+JSON.stringify(b));}
  for(let i=0;i<info.textBounds.length;i++)for(let j=i+1;j<info.textBounds.length;j++){
   const a=info.textBounds[i],b=info.textBounds[j];
   if(a.x<b.x+b.width&&a.x+a.width>b.x&&a.y<b.y+b.height&&a.y+a.height>b.y)issues.push(id+': text collision '+a.copy+' / '+b.copy);
  }
  const l=info.logoBounds;
  if(l.x<30||l.y<30||l.x+l.width>1050||l.y+l.height>1320)issues.push(id+': unsafe lockup bounds');
  for(const b of info.textBounds){if(b.x<l.x+l.width&&b.x+b.width>l.x&&b.y<l.y+l.height&&b.y+b.height>l.y)issues.push(id+': copy intersects complete lockup clearspace: '+b.copy);}
  info.issues=issues;
  if(issues.length&&!process.env.DRAFT_RENDER)throw Error(issues.join('\n'));
  await page.screenshot({path:resolve(here,'final',id+'.png'),type:'png',fullPage:false});
  report[id]=info;console.log('Rendered',id,issues.length?issues:'Jost loaded, text/logo bounding boxes pass');await page.close();
 }
}finally{await browser.close();}
writeFileSync(resolve(here,'render-validation.json'),JSON.stringify(report,null,2));
