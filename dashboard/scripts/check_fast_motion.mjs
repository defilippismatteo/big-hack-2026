import {createRequire} from 'node:module';
import fs from 'node:fs';
import {resolve} from 'node:path';
const {chromium}=createRequire('/tmp/adera-motion-runtime/package.json')('playwright-core');
const root=resolve(import.meta.dirname,'..'),out=resolve(root,'review/fast-motion');fs.mkdirSync(out,{recursive:true});
const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
try{
 const page=await browser.newPage({viewport:{width:1600,height:1000}});
 await page.goto('file://'+root+'/public/motion/studio.html');
 await page.emulateMedia({reducedMotion:'no-preference'});
 const frames=[];const clipping=[];
 for(let i=0;i<3;i++){
  await page.locator('.scene-tabs button').nth(i).click();
  for(const t of [0,.3,.8,1.6,2.4,3.6,3.85,4.05,4.5,5.2,6,7.4,7.96]){
   await page.evaluate(t=>document.querySelector('#stage').getAnimations({subtree:true}).forEach(a=>{a.pause();a.currentTime=t*1000;}),t);
   const bad=await page.evaluate(()=>[...document.querySelectorAll('#stage svg > .shot text')].filter(e=>{const b=e.getBBox();return b.x<0||b.x+b.width>1600||b.y<0||b.y+b.height>900;}).map(e=>e.textContent));
   clipping.push(...bad.map(text=>({scene:i,time:t,text})));
   const file=`scene-${i+1}-${String(t).replace('.','_')}.png`;
   await page.locator('#stage').screenshot({path:resolve(out,file)});frames.push({scene:i,time:t,file});
  }
 }
 // Real-time playback: sample every display frame, without seeking.
 await page.locator('#sequence').click();
 const playback=await page.evaluate(()=>new Promise(resolve=>{
  const start=performance.now(),stages=new Set(),counts={routing:0,decision:0,interview:0};let prior=0,jumps=0,frameCount=0;
  function sample(now){const svg=document.querySelector('#stage svg');const key=['routing','decision','interview'].find(x=>svg.classList.contains(x));if(key){stages.add(key);counts[key]++;}const t=document.querySelector('#stage').getAnimations({subtree:true})[0]?.currentTime??0;if(t+80<prior&&t>100)jumps++;prior=t;frameCount++;
   if(now-start<24200)requestAnimationFrame(sample);else resolve({stages:[...stages],counts,frameCount,unexpectedTimelineRewinds:jumps,stopped:document.querySelector('#sequence').getAttribute('aria-pressed')==='false'});
  }requestAnimationFrame(sample);
 }));
 const report={fps:30,frames,clipping,playback};fs.writeFileSync(resolve(out,'qc.json'),JSON.stringify(report,null,2));console.log(JSON.stringify({clipping,playback}));
 if(clipping.length||!playback.stopped||playback.stages.length!==3)process.exitCode=1;
}finally{await browser.close();}
