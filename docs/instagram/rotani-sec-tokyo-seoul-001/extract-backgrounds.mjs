import {createRequire} from 'node:module';
import {dirname,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {writeFileSync,mkdirSync} from 'node:fs';
const here=dirname(fileURLToPath(import.meta.url));
const require=createRequire(import.meta.url);
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright-core');
const executablePath=process.env.CHROME_PATH||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const ids=['01-hook','02-life-after-class','03-universities','04-language','05-budget','06-decision'];
mkdirSync(resolve(here,'originals'),{recursive:true});
const browser=await chromium.launch({headless:true,executablePath,args:['--allow-file-access-from-files']});
const report={};
try{
 for(const id of ids){
  const page=await browser.newPage({viewport:{width:1080,height:1350},deviceScaleFactor:1});
  await page.goto(pathToFileURL(resolve(here,'templates',id+'.html')).href,{waitUntil:'networkidle'});
  await page.evaluate(()=>document.fonts.ready);
  const data=await page.evaluate(()=>{
   const rgbToHex=s=>{const m=s.match(/\d+(?:\.\d+)?/g)||[];return m.length>=3?'#'+m.slice(0,3).map(v=>Math.round(Number(v)).toString(16).padStart(2,'0')).join(''):'#1D2027'};
   const copy=[...document.querySelectorAll('[data-copy]')].sort((a,b)=>Number(a.dataset.copy)-Number(b.dataset.copy)).map(el=>{
    const runs=[];const walker=document.createTreeWalker(el,NodeFilter.SHOW_TEXT);let node;
    while(node=walker.nextNode()){
     if(!node.data)continue;const parent=node.parentElement||el,cs=getComputedStyle(parent);let run=null,lastX=-Infinity,lineIndex=0;
     for(let i=0;i<node.data.length;i++){
      const range=document.createRange();range.setStart(node,i);range.setEnd(node,i+1);const rect=range.getBoundingClientRect();const ch=node.data[i];
      if(!rect.width&&!ch.trim())continue;
      const style={fontSize:parseFloat(cs.fontSize),fontWeight:cs.fontWeight,color:rgbToHex(cs.color),letterSpacing:parseFloat(cs.letterSpacing)||0,lineHeight:parseFloat(cs.lineHeight)||parseFloat(cs.fontSize)*1.2};
      if(run&&rect.x<lastX-5){lineIndex++;run=null}
      if(!run){run={text:'',x:rect.x,top:rect.top,height:rect.height,lineIndex,...style};runs.push(run)}
      run.text+=ch;run.height=Math.max(run.height,rect.height);lastX=rect.x;
     }
    }
    let globalLine=0,previousTop=null;
    for(const run of runs){if(previousTop!==null&&Math.abs(run.top-previousTop)>Math.max(8,run.lineHeight*.35))globalLine++;run.lineIndex=globalLine;previousTop=run.top;run.text=run.text.replace(/^\s+/,'')}
    const r=el.getBoundingClientRect(),ecs=getComputedStyle(el);return{index:Number(el.dataset.copy),text:el.innerText.replace(/\s+/g,' ').trim(),paddingTop:parseFloat(ecs.paddingTop)||0,bounds:{x:r.x,y:r.y,width:r.width,height:r.height},runs};
   });
   const logo=document.querySelector('.logo'),r=logo.getBoundingClientRect();
   return{copy,logo:{x:r.x,y:r.y,width:r.width,height:r.height,lockupId:logo.dataset.lockupId,file:logo.getAttribute('src').split('/').pop()}};
  });
  await page.addStyleTag({content:'[data-copy],[data-copy] *{color:transparent!important;-webkit-text-stroke-color:transparent!important;text-shadow:none!important}.logo{visibility:hidden!important}'});
  await page.screenshot({path:resolve(here,'originals',id+'.png'),type:'png',fullPage:false});
  report[id]=data;console.log('Extracted editable text geometry and clean background',id);await page.close();
 }
}finally{await browser.close()}
writeFileSync(resolve(here,'text-layout.json'),JSON.stringify(report,null,2));
