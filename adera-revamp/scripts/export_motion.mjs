/** Render the SVG timelines deterministically to Full HD MP4 and PNG posters.
 * npm install --prefix /tmp/adera-motion-runtime playwright-core
 * node scripts/export_motion.mjs --runtime /tmp/adera-motion-runtime
 * Uses a temporary headless browser profile; no server.
 */
import fs from 'node:fs';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
import {spawn} from 'node:child_process';
import {once} from 'node:events';
const app=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const arg=(name,fallback)=>process.argv.includes(name)?process.argv[process.argv.indexOf(name)+1]:fallback;
const runtime=arg('--runtime','/tmp/adera-motion-runtime');
const {chromium}=createRequire(resolve(runtime,'package.json'))('playwright-core');
const source=resolve(app,'public/motion'),out=resolve(app,'assets/demo-motion');
fs.mkdirSync(out,{recursive:true});
const scenes=JSON.parse(fs.readFileSync(resolve(source,'scene-manifest.json')));
const fps=30,width=1920,height=1080;
const browser=await chromium.launch({executablePath:arg('--chrome','/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'),headless:true});
try {
 const page=await browser.newPage({viewport:{width,height},deviceScaleFactor:1});
 await page.emulateMedia({reducedMotion:'no-preference'});
 await page.route('**/*',route=>route.abort());
 const load=async name=>{
  const svg=fs.readFileSync(resolve(source,name),'utf8');
  await page.setContent(`<meta charset="utf-8"><style>html,body{margin:0;width:${width}px;height:${height}px;overflow:hidden}svg.motion-root{width:${width}px;height:${height}px;display:block}</style>${svg}`);
  await page.evaluate(async()=>{await document.fonts.ready;document.getAnimations().forEach(a=>a.pause());});
 };
 for(const scene of scenes){
  await load(scene.poster);
  await page.screenshot({path:resolve(out,scene.id+'.poster.png')});
  await load(scene.download);
  const count=await page.evaluate(()=>document.getAnimations().length);
  if(!count)throw new Error('No animation tracks for '+scene.id);
  const video=resolve(out,scene.id+'.mp4');
  const encoder=spawn('ffmpeg',['-y','-hide_banner','-loglevel','error','-framerate',String(fps),'-f','image2pipe','-vcodec','png','-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',video],{stdio:['pipe','ignore','pipe']});
  let err='';encoder.stderr.on('data',b=>err+=b.toString());
  const completed=once(encoder,'close');
  for(let frame=0;frame<scene.duration*fps;frame++){
   await page.evaluate(ms=>document.getAnimations().forEach(a=>{a.pause();a.currentTime=ms;}),frame*1000/fps);
   const png=await page.screenshot({animations:'allow'});
   if(!encoder.stdin.write(png))await once(encoder.stdin,'drain');
   if(frame%96===0)console.log(scene.id,frame+'/'+scene.duration*fps);
  }
  encoder.stdin.end();const [code]=await completed;if(code!==0)throw new Error(err);
  console.log('Exported',video,fs.statSync(video).size,'bytes');
 }
}finally{await browser.close();}

// Join the three scenes without re-encoding and publish the studio download.
const list=resolve(out,'sequence.txt');
fs.writeFileSync(list,scenes.map(s=>`file '${s.id}.mp4'`).join('\n')+'\n');
const joined=resolve(out,'adera-personas.mp4');
const concat=spawn('ffmpeg',['-y','-hide_banner','-loglevel','error','-f','concat','-safe','0','-i',list,'-c','copy','-movflags','+faststart',joined],{stdio:'inherit'});
const [exitCode]=await once(concat,'close');
if(exitCode!==0)throw new Error('Sequence export failed');
fs.copyFileSync(joined,resolve(source,'adera-personas.mp4'));
