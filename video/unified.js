const m=document.querySelector('#m'),g=document.querySelector('#g'),c=document.querySelector('#c'),a=document.querySelector('#a');
const cuts=[0,9,16,27,44,53,65,76,95,104,112,127,144,150];
const ids=['question','brand','dataset','forecast','events','agents','persona','feed','audience','signals','interview','dashboard','end'];
window.ready=Promise.all([m,g,c,a].map(f=>new Promise(r=>f.onload=r))).then(async()=>{
 const md=m.contentDocument,gd=g.contentDocument;
 await Promise.all([md.fonts.ready,gd.fonts.ready,a.contentWindow.ready]);
 const css=gd.createElement('style');css.textContent='html,body,#stage,.scene.light,.scene.dark,.scene.plum{background:transparent!important}#hud{display:none!important}.s12-dash-pane{padding:0!important;background:transparent!important}.s12-dash-pane>*{visibility:hidden}.unified-dash{position:absolute;inset:0;width:1920px;height:1080px;object-fit:contain;visibility:visible!important}';gd.head.append(css);
 const cd=c.contentDocument;await cd.fonts.ready;
 const cc=cd.createElement('style');cc.textContent='html,body,.scene{background:transparent!important}#controls,#eventbf,#eventcm{display:none!important}';cd.head.append(cc);
 cc.textContent+='#s3{background:#35214f!important}#chartwindow{border:1px solid #80649b;border-radius:22px;background:#35214f}';
 const ns='http://www.w3.org/2000/svg';const zone=cd.createElementNS(ns,'rect');Object.entries({x:110,y:0,width:1480,height:475,rx:14,fill:'#ffffff',opacity:'.055'}).forEach(([k,v])=>zone.setAttribute(k,v));cd.querySelector('#chartcam').prepend(zone);
 cd.querySelectorAll('#grid text[y="520"]').forEach(el=>el.setAttribute('text-anchor','middle'));
 const day27=cd.createElementNS(ns,'text');Object.entries({x:1240,y:520,'text-anchor':'middle',fill:'#DED0FF','font-size':24,'font-family':'Inter','font-weight':750}).forEach(([k,v])=>day27.setAttribute(k,v));day27.textContent='27/11';cd.querySelector('#grid').append(day27);
 const graphScene=gd.querySelector('#s4');
 graphScene.append(gd.querySelector('#s5-events'),gd.querySelector('#s5-models'));
 const gc=gd.createElement('style');gc.textContent='#s4 .s4-wrap{display:none!important}#s5-events{position:absolute;top:320px;left:120px;right:120px}#s5-models{position:absolute;top:815px;left:110px;right:110px;height:220px}';gd.head.append(gc);
 gc.textContent+='#s5-events{inset:0;display:block}#s5-events .s5-popup{position:absolute;min-width:0;width:208px;padding:12px 14px;box-sizing:border-box}#s5-events .s5-popup strong{font-size:22px}#s5-events .s5-popup small{font-size:14px}';
 const guides=gd.createElementNS(ns,'svg');guides.id='date-guides';guides.setAttribute('viewBox','0 0 1920 1080');guides.style.cssText='position:absolute;inset:0;width:1920px;height:1080px;pointer-events:none';graphScene.insertBefore(guides,gd.querySelector('#s5-events'));
 for(const [id] of [['pop-bw'],['pop-bf'],['pop-cm']]){const group=gd.createElementNS(ns,'g');group.id=id+'-guide';group.innerHTML='<line stroke="#BFA0F3" stroke-width="2" stroke-dasharray="7 7"/><circle r="7" fill="#35214f" stroke="#C9ADFF" stroke-width="3"/>';guides.append(group);}
 const dash=gd.createElement('img');dash.src='../dashboard/current.png';dash.className='unified-dash';gd.querySelector('.s12-dash-pane').append(dash);
 const label=gd.querySelector('.s8-telemetry h3 span');label.innerHTML='<img src="assets/brands/gemini.svg" style="width:35px;height:35px;vertical-align:middle;margin-right:12px">Gemini Decision 1';
 // Main heading carries synthetic provenance; probability is never relabelled CTR.
 for(const [id,day] of [['pop-bw','20'],['pop-bf','27'],['pop-cm','30']]){const row=g.contentWindow.ADERA_DATA.dailyForecast.find(x=>x.day.endsWith(day));gd.querySelector('#'+id+' small').textContent='CPM '+row.cpm.toFixed(2).replace('.',',')+' € · CTR '+row.ctr.toFixed(3).replace('.',',')+'%';}
 await dash.decode();window.seek(0);
});
window.seek=function(t){
 const mw=m.contentWindow,gw=g.contentWindow,md=m.contentDocument;
 mw.__timelines.adera.seek(t,false);gw.__ADERA_SEEK__(t*1000);
 const inChart=t>=27&&t<53;
 a.style.display=inChart?'block':'none';
 c.style.display='none';
 if(inChart){a.contentWindow.seek(t-27);}
 const idx=Math.max(0,cuts.findIndex((v,i)=>t>=v&&t<cuts[i+1]));
 const overlay=(t>=76&&t<95)||(t>=127&&t<144);
 g.style.display=overlay?'block':'none';
 if(t>=127&&t<144){
   const gd=g.contentDocument;
   const dashEl=gd&&gd.querySelector('.unified-dash');
   if(dashEl){
     const dt=t-127;
     const easeIO=x=>x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2;
     const seg=(a,b)=>Math.max(0,Math.min(1,(dt-a)/(b-a)));
     const z1=easeIO(seg(3.8,5.6));
     const pan=easeIO(seg(8.2,10.2));
     const zOut=easeIO(seg(13.2,15.6));
     let sc=1+0.46*z1-0.04*pan-0.40*zOut;
     let ox=50-18*z1+44*pan-24*zOut;
     let oy=50-22*z1+30*pan-8*zOut;
     dashEl.style.transformOrigin=ox.toFixed(2)+'% '+oy.toFixed(2)+'%';
     dashEl.style.transform='scale('+sc.toFixed(4)+')';
   }
 }
 // Preserve Matteo's original animated orbit/background; remove only its foreground when Gemini/HyperFrames supplies selected components.
 md.querySelectorAll('.scene-content').forEach(el=>el.style.visibility=inChart||overlay||['forecast','events','feed','dashboard'].includes(el.closest('.scene').id)?'hidden':'visible');
 if(overlay){md.querySelectorAll('.scene').forEach(el=>{el.style.opacity=el.id===ids[idx]?'1':'0';el.style.transform='none'});}
 window.currentTime=t;
};
function fit(){document.querySelector('#stage').style.transform=`scale(${Math.min(innerWidth/1920,innerHeight/1080)})`}fit();addEventListener('resize',fit);
if(!location.search.includes('capture')){window.ready.then(()=>{let start=performance.now();function tick(now){seek(((now-start)/1000)%150);requestAnimationFrame(tick)}requestAnimationFrame(tick)})}
