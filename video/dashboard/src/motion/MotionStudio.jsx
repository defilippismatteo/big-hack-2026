import { useEffect, useRef, useState } from 'react';
import { Download, Pause, Play, RotateCcw, Film } from 'lucide-react';
import { scenes } from './scenes';
import './motion.css';
const notes=[
 'Python prepara quote e diversità; Gemini scrive i profili attraverso T3 Code. L’annuncio viene mostrato dopo, soltanto ai profili del suo settore.',
 'Le percentuali registrate per Chiara e FGR-U3 sommano gli esiti azione–motivo. Sono probabilità del modello per un profilo sintetico, non un CTR misurato.',
 'La stessa persona rivede lo stimolo senza conoscere il risultato di Decision. I due estratti provengono dalla sua intervista sintetica già registrata.'
];
export function MotionStudio({headingRef,compact=false}) {
 const [index,setIndex]=useState(0),[paused,setPaused]=useState(false),[speed,setSpeed]=useState(1),[time,setTime]=useState(0);
 const stage=useRef(null),animations=useRef([]),reduced=useRef(window.matchMedia('(prefers-reduced-motion:reduce)').matches);
 useEffect(()=>{animations.current=stage.current.getAnimations({subtree:true});animations.current.forEach(a=>{a.playbackRate=speed;if(paused||reduced.current){a.pause();a.currentTime=7400;}});setTime(paused?7.4:0);},[index]);
 useEffect(()=>{animations.current.forEach(a=>{a.playbackRate=speed;if(paused)a.pause();else a.play();});},[paused,speed]);
 useEffect(()=>{let frame,last=0;const tick=now=>{if(now-last>100){const t=animations.current.find(a=>a.currentTime!=null)?.currentTime;if(t!=null)setTime((t%8000)/1000);last=now;}frame=requestAnimationFrame(tick);};frame=requestAnimationFrame(tick);return()=>cancelAnimationFrame(frame);},[]);
 function seek(value){setPaused(true);setTime(value);animations.current.forEach(a=>{a.pause();a.currentTime=value*1000;});}
 const scene=scenes[index];
 const svgDownload='data:image/svg+xml;charset=utf-8,'+encodeURIComponent(scene.svg);
 const posterDownload='data:image/svg+xml;charset=utf-8,'+encodeURIComponent(scene.svg.replace('class="motion-root ','class="motion-root poster '));
 return <section className={'motion-studio'+(compact?' motion-compact':'')} aria-labelledby="motion-title">
  <header className="motion-heading"><div>{compact?<h2 id="motion-title">Dall’annuncio alla risposta di una persona</h2>:<h1 id="motion-title" ref={headingRef} tabIndex={-1}>Come funziona ADERA, in movimento.</h1>}<p>Un caso registrato: Chiara Bellini, il suo annuncio e la sua intervista sintetica.</p></div><Film size={23} aria-hidden="true"/></header>
  <div className="motion-tabs" role="group" aria-label="Scene del processo">{scenes.map((s,i)=><button type="button" key={s.id} aria-pressed={i===index} onClick={()=>setIndex(i)}>{s.title}</button>)}</div>
  <div className="motion-stage" ref={stage} dangerouslySetInnerHTML={{__html:scene.svg}}/>
  <div className="motion-transport"><button type="button" disabled={reduced.current} onClick={()=>setPaused(!paused)} aria-label={paused?'Riproduci':'Metti in pausa'}>{paused?<Play size={15}/>:<Pause size={15}/>} {paused?'Riproduci':'Pausa'}</button><button type="button" disabled={reduced.current} onClick={()=>{animations.current.forEach(a=>a.currentTime=0);setTime(0);}}><RotateCcw size={15}/> Ricomincia</button><label className="motion-seek">Tempo<input type="range" min="0" max="7.99" step="0.01" aria-label="Posizione nell’animazione" value={time} disabled={reduced.current} onChange={e=>seek(Number(e.target.value))}/></label><output>{time.toLocaleString('it-IT',{maximumFractionDigits:1,minimumFractionDigits:1})} / 8 s</output><label>Velocità <select aria-label="Velocità animazione" value={speed} onChange={e=>setSpeed(Number(e.target.value))}><option value="0.5">0,5×</option><option value="1">1×</option><option value="1.5">1,5×</option></select></label></div>
  {reduced.current&&<p className="motion-note">Movimento ridotto: mostriamo lo schema completo, senza riproduzione automatica.</p>}
  <p className="motion-note">{notes[index]}</p>
  <div className="motion-downloads"><a href={svgDownload} download={scene.download}><Download size={14}/> SVG animato</a><a href={posterDownload} download={scene.poster}><Download size={14}/> Poster vettoriale</a><a href={window.location.protocol==='file:'?'./public/motion/studio.html':import.meta.env.BASE_URL+'motion/studio.html'} target="_blank" rel="noreferrer"><Film size={14}/> Studio per il video demo</a></div>
 </section>;
}
