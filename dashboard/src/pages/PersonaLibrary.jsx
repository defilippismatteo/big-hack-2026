import {useEffect, useRef, useState} from 'react';
import {ArrowRight, X, ThumbsUp, ThumbsDown} from 'lucide-react';
import {useDashboardData} from '../data/useDashboardData';
import {verticalNames} from '../overview/model';
import {avatarFor} from './avatarPool';
import './personas.css';

export function Avatar({persona}) {
 const {src,bg}=avatarFor(persona);
 return <img className="voice-avatar" src={src} alt="" style={{backgroundColor:bg}} loading="lazy" decoding="async"/>;
}
function Profile({persona, assetId, assets, onClose}) {
 const dialog=useRef(null);
 useEffect(()=>{const node=dialog.current;node.showModal();return()=>node.close();},[]);
 const ordered=[...persona.answers].sort((a,b)=>Number(b.asset_id===assetId)-Number(a.asset_id===assetId));
 return <dialog ref={dialog} className="persona-dialog" onCancel={onClose} onClick={e=>{if(e.target===e.currentTarget)onClose();}} aria-labelledby="profile-name"><button className="icon-button profile-close" aria-label="Chiudi profilo" onClick={onClose}><X/></button><div className="persona-identity"><Avatar persona={persona}/><div><small>Profilo sintetico · {persona.persona_id}</small><h2 id="profile-name">{persona.name}</h2><p>{persona.age_years} anni · {persona.occupation}</p></div></div><p>{persona.persona_summary}</p><details className="profile-background" open><summary>Conosci questa persona</summary>{[['Cosa cerca','trust_requirements'],['Cosa teme','concerns'],['Come sceglie','decision_habits'],['Vita quotidiana','daily_routine'],['Contesto economico','economic_context'],['Rapporto con gli annunci','ad_avoidance'],['Contraddizioni','contradiction']].map(([label,key])=><p key={key}><b>{label}.</b> {persona[key]||'Non disponibile'}</p>)}<p><b>Interessi.</b> {(persona.interests??[]).join(', ')}</p><small>{persona.cohort==='unbiased'?'Generalista':'In-target critico'} · {persona.gender_identity} · {persona.country} · Generato con {persona.provider} / {persona.model}</small></details><h3>{assetId?'La sua risposta a questo annuncio e agli altri':'Tutte le sue risposte agli annunci'}</h3>{ordered.length?ordered.map(a=><details className="profile-answer" key={a.asset_id} open={a.asset_id===assetId}><summary>{a.asset_id} · {assets.find(x=>x.asset_id===a.asset_id)?.headline??'Annuncio'}</summary>{[['Prima impressione','first_impression'],['Cosa convince','positive'],['Cosa frena','negative'],['Cosa manca','missing'],['Cosa farebbe','next_step'],['Cosa cambierebbe','change']].map(([label,key])=>a[key]&&<div key={key}><h4>{label}</h4><blockquote>{a[key]}</blockquote></div>)}</details>):<p>Questa intervista contiene un giudizio complessivo, senza risposte per singolo annuncio.</p>}<details className="profile-answer" open={!ordered.length}><summary>Intervista complessiva</summary><p>{persona.interview?.summary}</p><h4>Punti a favore</h4><blockquote>{persona.interview?.punti_a_favore}</blockquote><h4>Freni</h4><blockquote>{persona.interview?.perche_si_allontana}</blockquote><p>Più utili: {persona.interview?.most_useful?.join(', ')||'nessuno'} · Meno utili: {persona.interview?.least_useful?.join(', ')||'nessuno'}</p><small>Modello intervista: {persona.interview?.receipt_model??'Non disponibile'}</small></details></dialog>;
}
const useful=t=>t&&!/^nulla\b|^nessun\b/i.test(t.trim());
function adVoiceFor(p, assetId) {
 const exact=p.answers.find(a=>a.asset_id===assetId);
 if(exact) return exact;
 const positive=p.interview?.most_useful?.includes(assetId)?p.interview.punti_a_favore:'';
 const negative=p.interview?.least_useful?.includes(assetId)?p.interview.perche_si_allontana:'';
 return (positive||negative)?{positive,negative}:null;
}
export function PersonaLibrary({vertical}) {
 const {data,phase,retry}=useDashboardData('persona-library.json');
 const [assetId,setAsset]=useState('');const [quickFilter,setQuickFilter]=useState('all');const [page,setPage]=useState(0);const [profile,setProfile]=useState(null);
 useEffect(()=>{setAsset('');setPage(0);setQuickFilter('all');},[vertical]);
 if(!data)return <p role={phase==='error'?'alert':'status'}>{phase==='error'?<>Archivio non disponibile. <button onClick={retry}>Riprova</button></>:'Caricamento delle interviste…'}</p>;
 const people=data.personas.filter(p=>!vertical||p.vertical===vertical);
 const assets=data.assets.filter(a=>a.vertical===vertical);
 const chosen=assets.find(a=>a.asset_id===assetId);
 const voices=assetId?people.flatMap(p=>{const a=adVoiceFor(p,assetId);return a?[{p,a}]:[];}):people.filter(p=>p.interview).map(p=>({p,a:{positive:p.interview.punti_a_favore,negative:p.interview.perche_si_allontana}}));
 const filters=[
  ['all','Tutti',()=>true],
  ['under35','Under 35',p=>p.age_years<35],
  ['35_54','35–54 anni',p=>p.age_years>=35&&p.age_years<=54],
  ['55plus','55+ anni',p=>p.age_years>=55],
  ['critical','In-target critici',p=>p.cohort!=='unbiased'],
  ['generalist','Generalisti',p=>p.cohort==='unbiased'],
  ['women','Donne',p=>p.gender_identity==='donna'],
  ['men','Uomini',p=>p.gender_identity==='uomo'],
  ...(assetId?[
   ['ad_pos','Convinti dall’annuncio',p=>{const a=adVoiceFor(p,assetId);return Boolean(a&&useful(a.positive));}],
   ['ad_neg','Frenati dall’annuncio',p=>{const a=adVoiceFor(p,assetId);return Boolean(a&&useful(a.negative));}],
  ]:[]),
 ];
 const activeFilter=filters.find(([id])=>id===quickFilter)??filters[0];
 const filtered=people.filter(activeFilter[2]);
 return <section className="persona-library"><div className="section-line"><h2>Le persone, con le loro parole</h2><span>Citazioni dalle interviste sintetiche</span></div>{vertical&&<><label className="asset-interview-select">Quale annuncio vuoi capire?<select value={assetId} onChange={e=>{const next=e.target.value;setAsset(next);if(!next&&(quickFilter==='ad_pos'||quickFilter==='ad_neg'))setQuickFilter('all');setPage(0);}}><option value="">Scegli tra i {assets.length} annunci</option>{assets.map(a=><option key={a.asset_id} value={a.asset_id}>{a.asset_id} · {a.headline}</option>)}</select></label><h3 className="interview-ad-title">{chosen?.headline??'Prime voci dal settore'}</h3><p className="muted-copy">{chosen?`${voices.length} profili con citazioni collegate a questo annuncio.`:'Giudizi complessivi sul settore. Scegli un annuncio per le risposte specifiche.'} Apri una citazione per leggere la risposta integrale e conoscere il profilo.</p><div className="voice-columns">{[['positive','Cosa convince',ThumbsUp],['negative','Cosa frena',ThumbsDown]].map(([key,title,Icon])=><section className={'voice-column '+key} key={key}><h3><Icon size={18}/>{title}</h3>{voices.filter(({a})=>useful(a[key])).slice(0,3).map(({p,a})=><button className="voice-note" key={p.persona_id} onClick={()=>setProfile(p)}><Avatar persona={p}/><span><strong>{p.name} <small>{p.age_years} anni</small></strong><q>{a[key]}</q><span className="voice-open">Leggi la risposta <ArrowRight size={14}/></span></span></button>)}{!voices.some(({a})=>useful(a[key]))&&<p>Nessuna citazione disponibile per questo punto.</p>}</section>)}</div>{chosen&&<details className="all-ad-responses"><summary>Tutte le {voices.length} risposte a questo annuncio</summary><div className="persona-directory">{voices.map(({p})=><button key={p.persona_id} onClick={()=>setProfile(p)}><Avatar persona={p}/><span><strong>{p.name}</strong><small>{p.age_years} anni · Leggi la risposta</small></span><ArrowRight size={16}/></button>)}</div></details>}</>}
 <div className="section-line"><h2>{vertical?'Tutti i '+people.length+' profili del settore':'Esplora tutti i '+people.length+' profili'}</h2><span>Ogni scheda include profilo e intervista</span></div><div className="persona-quick-filters" role="group" aria-label="Filtri veloci profili">{filters.map(([id,label,pred])=>{const count=people.filter(pred).length;return <button type="button" className="quick-filter" aria-pressed={activeFilter[0]===id} key={id} onClick={()=>{setQuickFilter(id);setPage(0);}}>{label} <span>{count}</span></button>;})}</div><p className="muted-copy">{filtered.length} profili selezionati{!vertical?' · Beauty & skincare, pet e-commerce e abbigliamento':''}</p><div className="persona-directory">{filtered.slice(page*12,page*12+12).map(p=><button key={p.persona_id} onClick={()=>setProfile(p)}><Avatar persona={p}/><span><strong>{p.name}</strong><small>{p.age_years} anni · {verticalNames[p.vertical]}</small><small>{p.occupation}</small></span><ArrowRight size={16}/></button>)}</div>{!filtered.length&&<p>Nessun profilo in questo filtro. Prova un’altra categoria.</p>}<nav className="persona-pagination" aria-label="Pagine dei profili"><button disabled={page===0} onClick={()=>setPage(page-1)}>Precedenti</button><span>Pagina {page+1} di {Math.max(1,Math.ceil(filtered.length/12))}</span><button disabled={(page+1)*12>=filtered.length} onClick={()=>setPage(page+1)}>Successivi</button></nav>{profile&&<Profile persona={profile} assetId={assetId} assets={data.assets} onClose={()=>setProfile(null)}/>}</section>;
}
