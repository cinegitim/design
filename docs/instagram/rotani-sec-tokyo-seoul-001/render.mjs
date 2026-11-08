import {createRequire} from 'node:module';
import {dirname,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
const here=dirname(fileURLToPath(import.meta.url));
const require=createRequire(import.meta.url);
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright-core');
const executablePath=process.env.CHROME_PATH||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const ids=['01-hook','02-life-after-class','03-universities','04-language','05-budget','06-decision'];
const exact=JSON.parse(readFileSync(resolve(here,'exact-copy.json'),'utf8')).slides;
mkdirSync(resolve(here,'final'),{recursive:true});
const browser=await chromium.launch({headless:true,executablePath,args:['--allow-file-access-from-files']});
const report={};const norm=s=>s.replace(/\s+/g,' ').trim();
try{
 for(const id of ids){
  const page=await browser.newPage({viewport:{width:1080,height:1350},deviceScaleFactor:1});
  await page.goto(pathToFileURL(resolve(here,'source',id+'.html')).href,{waitUntil:'networkidle'});await page.evaluate(()=>document.fonts.ready);
  const info=await page.evaluate(()=>{
   const rect=e=>{const r=e.getBoundingClientRect();return{x:r.x,y:r.y,width:r.width,height:r.height,right:r.right,bottom:r.bottom}};
   const copy=[...document.querySelectorAll('#editable-campaign-copy > g[data-copy]')].sort((a,b)=>Number(a.dataset.copy)-Number(b.dataset.copy)).map(e=>({index:Number(e.dataset.copy),text:[...e.querySelectorAll('text')].map(t=>t.textContent).join(' ').replace(/\s+/g,' ').trim(),bounds:rect(e)}));
   const logo=document.querySelector('#canonical-lockup');const imgs=[...document.images].map(i=>({src:i.getAttribute('href')||i.getAttribute('src'),complete:i.complete,naturalWidth:i.naturalWidth,naturalHeight:i.naturalHeight}));
   return{viewport:[innerWidth,innerHeight],jostLoaded:document.fonts.check('700 60px Jost'),copy,logo:logo?{bounds:rect(logo),lockupId:logo.dataset.lockupId,src:logo.getAttribute('href')}:null,images:imgs};
  });
  const issues=[],expected=exact[id].map(norm),rendered=info.copy.map(x=>norm(x.text));
  if(!info.jostLoaded)issues.push('Jost not loaded');if(JSON.stringify(rendered)!==JSON.stringify(expected))issues.push(`exact-copy mismatch expected=${JSON.stringify(expected)} rendered=${JSON.stringify(rendered)}`);
  if(info.copy.some((x,i)=>x.index!==i))issues.push('data-copy indexes are not contiguous');
  for(const x of info.copy){const b=x.bounds;if(b.x<24||b.y<24||b.right>1056||b.bottom>1326)issues.push(`unsafe copy bounds: ${x.text} ${JSON.stringify(b)}`)}
  for(let i=0;i<info.copy.length;i++)for(let j=i+1;j<info.copy.length;j++){const a=info.copy[i].bounds,b=info.copy[j].bounds;const ox=Math.min(a.right,b.right)-Math.max(a.x,b.x),oy=Math.min(a.bottom,b.bottom)-Math.max(a.y,b.y);if(ox>2&&oy>2)issues.push(`copy collision: ${info.copy[i].text} / ${info.copy[j].text}`)}
  if(!info.logo)issues.push('canonical lockup missing');else{const l=info.logo.bounds;if(l.x<24||l.y<24||l.right>1056||l.bottom>1326)issues.push('unsafe lockup bounds');for(const x of info.copy){const b=x.bounds;if(b.x<l.right&&b.right>l.x&&b.y<l.bottom&&b.bottom>l.y)issues.push(`copy intersects lockup: ${x.text}`)}}
  info.expectedCopy=expected;info.issues=issues;if(issues.length&&!process.env.DRAFT_RENDER)throw Error(`${id}\n${issues.join('\n')}`);
  await page.screenshot({path:resolve(here,'final',id+'.png'),type:'png',fullPage:false});report[id]=info;console.log(`Rendered ${id}: ${issues.length?'DRAFT '+issues.length+' issues':'copy, imagery, font and bounds PASS'}`);await page.close();
 }
}finally{await browser.close()}
writeFileSync(resolve(here,'render-validation.json'),JSON.stringify(report,null,2));
