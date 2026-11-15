"""Build original ADERA vector scenes from an existing persona/decision/interview.
No inference or API calls. Brand files are unchanged vendor SVGs.
"""
from pathlib import Path
import base64,hashlib,json,math,re,textwrap,xml.etree.ElementTree as ET
from datetime import datetime,timezone
from html import escape
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from personas_simulation.runtime.contracts import digest
APP=ROOT/'dashboard';OUT=APP/'public/motion';OUT.mkdir(parents=True,exist_ok=True)
BRANDS=OUT/'brands'
# The gstatic v1 mark is a native vector. Other official exports embed raster texture.
vector=BRANDS/'gemini-vector.svg'
if vector.exists(): (BRANDS/'gemini.svg').write_bytes(vector.read_bytes())
for extra in ['gemini-vector.svg','gemini-sparkle.svg']:
 (BRANDS/extra).unlink(missing_ok=True)
pid='abbigliamento-P001';aid='FGR-U3';run=ROOT/'data/personas_600'
paths={'cards':run/'persona_cards.json','summary':run/'analyses/summary.json','interview':run/f'interviews/responses/{pid}.json','job':run/f'interviews/jobs/{pid}.json','receipt':run/f'interviews/responses/{pid}.receipt.json','catalog':ROOT/'data/personas_600/safe_inputs/creative_catalog.json'}
source_raw={k:p.read_bytes() for k,p in paths.items()}
load=lambda p:json.loads(source_raw[next(k for k,v in paths.items() if v==p)])
cards=load(paths['cards']);person=next(p for p in cards['personas'] if p['persona_id']==pid)
summary=load(paths['summary']);asset=next(a for a in summary['ranking'] if a['asset_id']==aid)
pair=next(p for p in asset['per_person'] if p['persona_id']==pid)
job=load(paths['job']);response=load(paths['interview']);receipt=load(paths['receipt'])
assert digest(person)==pair['persona_sha256']==job['persona_sha256']
assert asset['data_kind']=='simulated_decision' and not asset['calibrated_to_ctr']
assert receipt['status']=='completed' and receipt['providerInstanceId']=='antigravity'
assert math.isclose(sum(pair['actions'].values()),1,abs_tol=1e-8)
assert math.isclose(sum(v for k,v in pair['probabilities'].items() if k.startswith('click__')),pair['actions']['click'])
stimulus=next(k for k,v in job['mapping'].items() if v==aid)
answer=next(a for a in response['answers'] if a['stimulus_id']==stimulus)
creative=next(c for c in load(paths['catalog'])['creatives'] if c['asset_id']==aid)
positive="Apprezzo molto il riferimento a spedizione e reso gratuiti e al 'reso facile'"
negative="Anche qui c'è il timer delle 48 ore, che trovo superfluo e un po' forzato"
assert positive in answer['positive'] and negative in answer['negative']
case={'schemaVersion':1,'dataKind':'simulated_decision','persona':{k:person[k] for k in ['persona_id','name','age_years','occupation','persona_summary','trust_requirements','concerns']},'personaSha256':digest(person),'asset':creative,'decision':{'model':asset['model'],'provider':asset['provider'],'runId':asset['run_id'],'requestSha256':asset['request_sha256'],'actions':pair['actions'],'probabilities':pair['probabilities'],'calibratedToHumanCtr':False},'interview':{'method':'blind_reflective_reexposure','stimulus':stimulus,'answers':answer,'literalExcerpts':{'positive':positive,'negative':negative},'receipt':{k:receipt.get(k) for k in ['status','model','executedModel','providerInstanceId','taskId','link']},'decisionOutputsVisible':False},'poolCount':len(cards['personas']),'sources':{k:{'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(source_raw[k]).hexdigest()} for k,p in paths.items()}}
(OUT/'case.json').write_text(json.dumps(case,ensure_ascii=False,indent=2)+'\n')
font=base64.b64encode((APP/'node_modules/@fontsource-variable/inter/files/inter-latin-wght-normal.woff2').read_bytes()).decode()
C={'ink':'#292339','muted':'#756B85','purple':'#7951D0','light':'#F1EBFA','border':'#E5DDED','teal':'#25836E','amber':'#B07836','coral':'#AC665C'}
routing_people=[p for p in cards['personas'] if p['vertical']==person['vertical']][:3]
routing_names=[(p['name'].split()[0],''.join(n[0] for n in p['name'].split()[:2])) for p in routing_people]
logo_n=0

def logo(name,x,y,size):
 global logo_n
 logo_n+=1
 f=(APP/'public/adera.svg') if name=='adera' else BRANDS/(name+'.svg')
 s=re.sub(r'<\?xml[^>]*>','',f.read_text()).strip();view=ET.fromstring(s).attrib['viewBox']
 s=re.sub(r'<svg\b[^>]*>',f'<svg x="{x}" y="{y}" width="{size}" height="{size}" viewBox="{view}">',s,count=1)
 if name=='gemini': s=s.replace('linear-gradient',f'gemini-{logo_n}-gradient')
 return s

def rect(x,y,w,h,fill='#FFF',stroke=None,rx=18,extra=''):
 return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"'+(f' stroke="{stroke}"' if stroke else '')+f' {extra}/>'

def txt(x,y,s,size=24,color=None,weight=400,anchor='start'):
 return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color or C["ink"]}" font-weight="{weight}" text-anchor="{anchor}">{escape(str(s))}</text>'

def lines(x,y,s,width=44,size=23,color=None,weight=400,leading=None):
 return ''.join(txt(x,y+i*(leading or size*1.45),l,size,color,weight) for i,l in enumerate(textwrap.wrap(s,width=width)))

def pill(x,y,w,s,color=None,fill=None):
 return rect(x,y,w,34,fill or C['light'],rx=8)+txt(x+12,y+23,s,17,color or C['purple'],550)

def person_icon(x,y,name='CB',r=30,color=None):
 return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color or C["light"]}"/>'+txt(x,y+8,name,23,C['purple'],600,'middle')

def arrow(path,scene,stage=2):
 return f'<path d="{path}" fill="none" stroke="{C["border"]}" stroke-width="3" marker-end="url(#{scene}-arrow)"/><path class="packet phase-{stage}" d="{path}" pathLength="100" fill="none" stroke="{C["purple"]}" stroke-width="5" stroke-linecap="round" stroke-dasharray="8 108"/>'

def group(content,stage):return f'<g class="reveal stage-{stage}">{content}</g>'

def frame(scene,title,sub,body,footer):
 css=f'''@font-face{{font-family:InterMotion;src:url(data:font/woff2;base64,{font}) format('woff2');font-weight:100 900}}.motion-root text{{font-family:InterMotion,Arial,sans-serif}}.motion-root .reveal{{opacity:1}}.motion-root .packet{{opacity:0}}'''
 for n,(start,end) in enumerate([(0,4),(8,14),(21,28),(36,43),(52,59),(66,73),(77,83)]):
  css+=f'@keyframes {scene}-s{n}{{0%,{start}%{{opacity:0;transform:translateY(7px)}}{end}%,94%{{opacity:1;transform:translateY(0)}}100%{{opacity:0;transform:translateY(0)}}}}.motion-root.{scene} .stage-{n}{{animation:{scene}-s{n} 12s linear infinite;transform-box:fill-box;transform-origin:center}}'
  css+=f'@keyframes {scene}-p{n}{{0%,{start}%{{opacity:0;stroke-dashoffset:108}}{end}%{{opacity:1;stroke-dashoffset:100}}{min(end+18,93)}%{{opacity:1;stroke-dashoffset:0}}{min(end+21,96)}%,100%{{opacity:0;stroke-dashoffset:0}}}}.motion-root.{scene} .phase-{n}{{animation:{scene}-p{n} 12s linear infinite}}'
 css+=f'@keyframes {scene}-bar{{0%,43%{{transform:scaleX(0)}}64%,94%{{transform:scaleX(1)}}100%{{transform:scaleX(0)}}}}.motion-root.{scene} .score-bar{{animation:{scene}-bar 12s cubic-bezier(.2,.7,.2,1) infinite;transform-box:fill-box;transform-origin:left center}}'
 css+='@media(prefers-reduced-motion:reduce){.motion-root *{animation:none!important}.motion-root .packet{display:none}}.motion-root.poster *{animation:none!important}.motion-root.poster .packet{display:none}'
 desc='Animazione illustrativa del flusso ADERA. Profilo sintetico e risultati del modello dagli artefatti locali. Nessuna persona reale o risultato pubblicitario misurato.'
 return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900" class="motion-root {scene}" role="img" aria-labelledby="{scene}-title {scene}-desc"><title id="{scene}-title">{escape(title)}</title><desc id="{scene}-desc">{desc}</desc><metadata>{escape(json.dumps({'author':'ADERA project','originalArtwork':True,'durationSeconds':12,'case':'case.json','persona':pid,'asset':aid,'dataKind':'simulated_decision'},ensure_ascii=False))}</metadata><defs><style>{css}</style><marker id="{scene}-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1L9 5L0 9" fill="{C['border']}"/></marker></defs>{rect(0,0,1600,900,'#FAF8FD',rx=0)}{logo('adera',54,45,46)}{txt(116,78,'ADERA',25,weight=650)}{pill(1280,48,266,'Profili e risposte sintetiche')}{txt(54,148,title,41,weight=600)}{txt(56,190,sub,23,C['muted'])}{body}{txt(56,860,footer,18,C['muted'])}</svg>'''

# 1: creation and evaluation are separate lanes: no creative reaches the writer.
b=rect(54,231,1492,222,'#FFF',C['border'])+txt(82,269,'Prima costruiamo il pool, senza usare lo storico pubblicitario',22,weight=550)
b+=group(rect(82,292,324,128,C['light'],rx=12)+txt(104,327,'Python prepara gli slot',24,weight=550)+lines(104,363,'Quote, varietà e controlli di diversità.',25,20,C['muted']),0)
b+=arrow('M414 355H482','routing',0)
b+=group(rect(493,292,475,128,'#FFF',C['border'],12)+logo('t3-code',514,313,44)+logo('gemini',571,312,44)+txt(633,333,'T3 Code + Gemini',25,weight=550)+txt(515,385,'Gemini scrive le schede sintetiche',21,C['muted']),1)
b+=arrow('M977 355H1045','routing',1)
b+=group(rect(1057,292,460,128,C['light'],rx=12)+person_icon(1097,340,routing_names[0][1],color='#FFF')+person_icon(1167,340,routing_names[1][1],color='#FFF')+person_icon(1237,340,routing_names[2][1],color='#FFF')+txt(1286,342,'600',37,weight=600)+txt(1286,377,'profili sintetici',20,C['muted']),2)
b+=txt(82,500,'Poi valutiamo l’annuncio con le personas del suo settore',24,weight=550)
b+=group(rect(82,531,350,218,'#FFF',C['border'],14)+txt(105,569,'Un solo annuncio',25,weight=550)+txt(105,601,aid+' · carosello',19,C['purple'])+lines(105,640,creative['headline'],24,24)+txt(105,717,'Il visual è descritto nel kit.',18,C['muted']),2)
b+=group(rect(526,555,445,155,C['light'],rx=14)+logo('t3-code',549,578,42)+txt(610,608,'T3 Code orchestra',25,weight=550)+txt(549,656,'Persona + feed personale + annuncio',21,C['muted']),3)
b+=arrow('M442 639H513','routing',2)
for i,(name,tag,y) in enumerate([(name,initials,529+i*104) for i,(name,initials) in enumerate(routing_names)]):
 b+=arrow(f'M982 636C1030 636 1030 {y+29} 1092 {y+29}','routing',3+i)
 b+=group(rect(1106,y,410,76,'#FFF',C['border'],12)+person_icon(1145,y+38,tag,24)+txt(1185,y+33,name,23,weight=550)+txt(1185,y+59,'Solo il proprio contesto',18,C['muted']),3+i)
b+=pill(83,779,891,'Niente KPI, forecast o risposte altrui nei profili',C['teal'],'#E9F5F0')
svg1=frame('routing','Ogni persona riceve solo ciò che le serve.','Il pool nasce indipendente. Ogni valutazione riceve il profilo e il suo feed.',b,'Schema del processo: contesti personali separati, annunci del kit, nessuna risposta condivisa fra le personas.')

# 2: actual recorded probabilities, aggregated from the twelve closed outcomes.
b=group(rect(54,235,420,254,'#FFF',C['border'])+person_icon(105,287)+txt(151,284,'Chiara Bellini',27,weight=550)+txt(151,315,'46 anni · profilo sintetico',19,C['muted'])+lines(82,366,'Tecnica di laboratorio. Cerca praticità e un reso senza complicazioni.',31,24)+pill(82,449,248,'abbigliamento-P001'),0)
b+=group(rect(54,514,420,270,'#FFF',C['border'])+txt(82,554,'Il suo annuncio nel feed',22,weight=550)+pill(82,575,111,aid)+lines(82,649,creative['headline'],26,26,weight=550)+lines(82,726,creative['testo_principale'],34,19,C['muted']),1)
b+=arrow('M486 389C550 389 530 475 595 475','decision',1)+arrow('M486 642C550 642 530 530 595 530','decision',2)
b+=group(rect(610,347,302,320,'#FFF',C['border'])+logo('gemini',710,377,100)+txt(761,515,'Gemini Decision 1',25,weight=550,anchor='middle')+txt(761,555,'Decisions API',20,C['muted'],anchor='middle')+txt(761,603,'12 esiti azione–motivo',19,C['purple'],anchor='middle'),2)
b+=arrow('M923 504H990','decision',3)
b+=rect(1008,235,538,549,'#FFF',C['border'])+txt(1040,283,'Probabilità del comportamento',25,weight=550)+txt(1040,319,'Questa persona, questo annuncio.',19,C['muted'])
for i,(key,label,color) in enumerate([('scroll','Scorre oltre',C['muted']),('glance','Dà un’occhiata',C['purple']),('stop','Si sofferma',C['teal']),('click','Apre l’annuncio',C['amber'])]):
 y=359+i*94;v=pair['actions'][key]*100
 b+=txt(1040,y+15,label,23)+rect(1040,y+34,390,18,'#F0ECF5',rx=8)+f'<g class="reveal stage-4">{rect(1040,y+34,390*v/100,18,color,rx=8,extra="class=\"score-bar\"")}</g>'+group(txt(1509,y+17,f'{v:.1f}%'.replace('.',','),27,color,550,'end'),4)
b+=group(rect(1028,736,497,33,'#F1EBFA',rx=8)+txt(1042,759,'Quattro azioni: somma delle probabilità = 100%',17,C['purple']),5)
click=f"{100*pair['actions']['click']:.1f}%".replace('.',',')
b+=group(txt(54,822,f'P(apre) = P(offerta) + P(utilità) + P(informazioni) = {click}',25,C['purple'],550),5)
svg2=frame('decision','Quanto è probabile ogni comportamento?','Decision 1 distribuisce probabilità tra esiti chiusi. Non simula una persona reale che clicca.',b,'Valori realmente registrati per Chiara / FGR-U3, arrotondati a 1 decimale. Punteggi sintetici, non CTR misurati.')

# 3: fresh qualitative re-exposure, no Decision output passed to interviewer.
b=group(rect(54,235,374,397,'#FFF',C['border'])+person_icon(105,287)+txt(151,284,'Chiara Bellini',26,weight=550)+txt(151,315,'Lo stesso profilo sintetico',18,C['muted'])+txt(82,372,'Rivede lo stimolo C12',22,weight=550)+lines(82,417,creative['headline'],23,25)+pill(82,488,111,aid)+lines(82,563,'Nessuna probabilità Decision mostrata a chi risponde.',25,20,C['muted']),0)
b+=arrow('M440 420H503','interview',1)
b+=group(rect(518,306,320,276,C['light'],rx=18)+logo('t3-code',550,334,54)+logo('gemini',621,334,54)+txt(550,434,'Intervista con Gemini',24,weight=550)+txt(550,476,'Coordinata da T3 Code',20,C['muted'])+txt(550,530,'Una nuova ri-esposizione',19,C['purple']),1)
b+=arrow('M851 444H914','interview',2)
b+=group(rect(932,235,614,228,'#FFF',C['border'])+pill(959,258,211,'Cosa apprezzi?',C['teal'],'#E9F5F0')+lines(959,327,'«'+positive+'…»',43,24,leading=35),3)
b+=group(rect(932,487,614,228,'#FFF',C['border'])+pill(959,510,262,'Cosa ti allontana?',C['coral'],'#FAEEEA')+lines(959,579,'«'+negative+'…»',43,24,leading=35),4)
b+=group(rect(54,671,784,122,'#FFF',C['border'],14)+txt(81,708,'Uno spunto da verificare con un test',23,weight=550)+txt(81,753,'Meno timer, più dettagli su materiali e reso.',23,C['purple']),5)
b+=group(txt(960,768,'Estratti letterali dell’intervista registrata.',19,C['muted'])+txt(960,800,'Non una spiegazione causale del punteggio.',19,C['muted']),5)
svg3=frame('interview','Dopo la probabilità, ascoltiamo le ragioni.','Una ri-esposizione qualitativa: stessa persona e stimoli, senza mostrare il risultato di Decision.',b,'Intervista sintetica già registrata. Le parole appartengono al profilo simulato; lo spunto di test è un’interpretazione.')
from fast_motion import build as build_fast_motion
svg1,svg2,svg3=build_fast_motion(globals())
scenes=[]
for name,title,svg in [('01-routing','Informazioni alle personas',svg1),('02-decision','Probabilità dei comportamenti',svg2),('03-interview','Intervista individuale',svg3)]:
 ET.fromstring(svg)
 assert '<image' not in svg and 'data:image/' not in svg
 (OUT/(name+'.svg')).write_text(svg)
 poster=svg.replace('class="motion-root ', 'class="motion-root poster ',1)
 (OUT/(name+'.poster.svg')).write_text(poster)
 scenes.append({'id':name,'title':title,'duration':8,'svg':svg,'download':name+'.svg','poster':name+'.poster.svg'})
font_face=re.search(r'@font-face\{[^}]+\}',scenes[0]['svg']).group(0)
compact_scenes=[{**s,'svg':s['svg'].replace(font_face,'__MOTION_FONT_CSS__')} for s in scenes]
js='// Generated by scripts/build_motion.py; original artwork, local evidence.\nconst fontFace='+json.dumps(font_face)+';\nconst sourceScenes='+json.dumps(compact_scenes,ensure_ascii=False)+';\nexport const scenes=sourceScenes.map(s=>({...s,svg:s.svg.replace("__MOTION_FONT_CSS__",fontFace)}));\n'
(APP/'src/motion').mkdir(exist_ok=True);(APP/'src/motion/scenes.js').write_text(js)
(OUT/'scene-manifest.json').write_text(json.dumps([{k:v for k,v in s.items() if k!='svg'} for s in scenes],ensure_ascii=False,indent=2)+'\n')
brand_sources={'t3-code.svg':'https://raw.githubusercontent.com/pingdotgg/t3code/main/assets/prod/logo.svg','gemini.svg':'https://www.gstatic.com/images/branding/productlogos/gemini/v1/192px.svg'}
(OUT/'brand-sources.json').write_text(json.dumps({'retrievedAt':datetime.now(timezone.utc).isoformat(),'assets':[{ 'file':k,'source':v,'sha256':hashlib.sha256((BRANDS/k).read_bytes()).hexdigest(),'treatment':'Original vendor paths and colors, scaled proportionally; no redraw'} for k,v in brand_sources.items()],'reference':{'url':'internal-svg-loop-reference','use':'Visual concept reference only. No source code, text, keyframes, layout or illustrations copied.'},'google_decisions_docs':'https://aistudio.google.com/docs/decisions-api'},ensure_ascii=False,indent=2)+'\n')
print('Built 3 animated SVGs, 3 vector posters, case evidence, scene manifest and React scene data.')

html=(APP/'scripts/motion_studio_template.html').read_text().replace('__SCENES__',json.dumps(scenes,ensure_ascii=False).replace('<','\\u003c'))
(OUT/'studio.html').write_text(html)
print('Built standalone motion studio.')
