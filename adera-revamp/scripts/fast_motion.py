"""Original 30 fps film choreography. Timings in seconds, shared by SVG and export."""
import json

def build(g):
 rect,txt,lines,pill,logo,person_icon=[g[k] for k in ('rect','txt','lines','pill','logo','person_icon')]
 font,C,creative,pair,positive,negative=[g[k] for k in ('font','C','creative','pair','positive','negative')]
 duration=8
 events=[]
 def event(content,t,kind='text'):
  n=len(events);events.append((n,t,kind))
  return f'<g class="event e{n}">{content}</g>'
 def shot(content,i):return f'<g class="shot shot-{i}">{content}</g>'
 def title(label,sub):return txt(90,205,label,52,weight=650)+txt(92,253,sub,25,C['muted'])
 def card(x,y,w,h):return rect(x,y,w,h,'#FFF',C['border'],20)
 def line(x1,y1,x2,y2,t):
  return event(f'<path d="M{x1} {y1}H{x2}" stroke="{C["purple"]}" stroke-width="4"/><circle cx="{x2}" cy="{y2}" r="7" fill="{C["purple"]}"/>',t,'link')
 def finish(name,a,b):
  css=f'@font-face{{font-family:InterMotion;src:url(data:font/woff2;base64,{font}) format("woff2");font-weight:100 900}}text{{font-family:InterMotion,Arial,sans-serif}}'
  # Outgoing and incoming overlap for 160 ms; no looping element motion.
  css+='@keyframes shotA{0%,46%{opacity:1;transform:translateX(0)}49%{opacity:0;transform:translateX(-28px)}100%{opacity:0;transform:translateX(-28px)}}'
  css+='@keyframes shotB{0%,47%{opacity:0;transform:translateX(36px)}54%{opacity:1;transform:translateX(0)}100%{opacity:1;transform:translateX(0)}}'
  css+='.shot-0{animation:shotA 8s linear both}.shot-1{animation:shotB 8s cubic-bezier(.22,.8,.22,1) both}'
  for n,t,kind in events:
   length=.16 if kind=='text' else .5 if kind=='ui' else .4
   start=t/8*100;end=(t+length)/8*100
   initial='translateX(24px)' if kind=='ui' else 'scaleX(0)' if kind=='link' else 'translateY(0)'
   final='scaleX(1)' if kind=='link' else 'translateX(0)'
   css+=f'@keyframes e{n}{{0%,{start}%{{opacity:0;transform:{initial}}}{end}%,100%{{opacity:1;transform:{final}}}}}.e{n}{{animation:e{n} 8s cubic-bezier(.22,.8,.22,1) both;transform-box:fill-box;transform-origin:left center}}'
  css+='@media(prefers-reduced-motion:reduce){*{animation:none!important}.shot-0{display:none}}.poster *{animation:none!important}.poster .shot-0{display:none}'
  shell=rect(0,0,1600,900,'#FAF8FD',rx=0)+logo('adera',86,56,46)+txt(148,89,'ADERA',26,weight=650)+pill(1190,60,320,'Profili e risposte sintetiche')
  footer=txt(90,854,'Un caso registrato · Chiara Bellini / FGR-U3 · Nessun CTR misurato',19,C['muted'])
  return f'<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900" class="motion-root {name}" role="img" aria-labelledby="{name}-title {name}-desc"><title id="{name}-title">ADERA · {name}</title><desc id="{name}-desc">Profili sintetici, probabilità del modello e intervista registrata. Nessuna probabilità Decision mostrata nell’intervista.</desc><defs><style>{css}</style></defs>{shell}{shot(a,0)}{shot(b,1)}{footer}</svg>'
 # Pool: cause and result, then focus on the individual context.
 a=title('Prima le persone. Poi l’annuncio.','Il pool nasce senza storico pubblicitario.')
 a+=event(card(90,330,390,330)+txt(120,389,'Python prepara',31,weight=600),.08,'ui')
 a+=event(txt(120,449,'Quote per settore',26),.55)+event(txt(120,499,'Varietà dei profili',26),1.1)+event(txt(120,549,'Controlli di diversità',26),1.65)
 a+=line(490,490,570,490,.7)
 a+=event(card(590,330,470,330)+logo('t3-code',624,367,54)+logo('gemini',699,367,54)+txt(624,484,'Gemini scrive',35,weight=600)+txt(624,533,'T3 Code coordina',25,C['muted']),.85,'ui')
 a+=line(1070,490,1135,490,2.1)
 a+=event(txt(1170,476,'600',92,C['purple'],650)+txt(1174,532,'profili sintetici',26),2.45,'ui')
 a+=event(pill(590,699,470,'Il contenuto pubblicitario arriva dopo'),3.05)
 b=title('Un contesto alla volta.','Ogni valutazione riceve solo ciò che le serve.')
 b+=event(card(90,330,620,365)+person_icon(155,399)+txt(210,404,'Chiara Bellini',36,weight=600),3.88,'ui')
 b+=event(txt(124,484,'Profilo sintetico · 46 anni',27),4.48)+event(txt(124,541,'Il suo feed personale',30,C['purple'],550),5.02)
 b+=line(727,510,848,510,4.65)
 b+=event(card(875,330,635,365)+pill(910,368,125,'FGR-U3'),4.86,'ui')
 b+=event(lines(910,465,creative['headline'],30,34,weight=600),5.48)
 b+=event(txt(910,625,'Un singolo annuncio del settore',26,C['muted']),6.03)
 b+=event(txt(124,750,'Nessun KPI, forecast o risposta altrui.',30,C['teal'],550),6.6)
 routing=finish('routing',a,b);events.clear()
 a=title('Dal contesto a dodici esiti.','Decision 1 valuta combinazioni chiuse di azione e motivo.')
 a+=event(card(90,340,470,340)+person_icon(155,405)+txt(211,414,'Chiara',38,weight=600),.08,'ui')
 a+=event(txt(124,494,'Profilo + feed personale',27),.58)+event(pill(124,544,200,'Annuncio FGR-U3'),1.08)
 a+=line(580,620,700,620,1.3)
 a+=event(logo('gemini',775,350,100)+txt(827,510,'Gemini Decision 1',33,weight=600,anchor='middle'),1.45,'ui')
 a+=event(txt(827,562,'Decisions API',25,C['muted'],anchor='middle'),1.96)
 a+=line(970,620,1080,620,2.15)
 a+=event(txt(1160,474,'12',96,C['purple'],650)+txt(1118,536,'esiti azione–motivo',25),2.45,'ui')
 a+=event(txt(90,750,'Una distribuzione di probabilità, per questa coppia.',30,C['purple'],550),3.1)
 b=title('Quattro comportamenti.','Le probabilità registrate per Chiara e FGR-U3.')
 for i,(key,label,color) in enumerate([('scroll','Scorre oltre',C['muted']),('glance','Dà un’occhiata',C['purple']),('stop','Si sofferma',C['teal']),('click','Apre l’annuncio',C['amber'])]):
  y=340+i*92;v=100*pair['actions'][key];t=3.88+i*.55
  b+=event(txt(95,y+26,label,30)+rect(465,y,850,32,'#EEE8F6',rx=8)+txt(1495,y+27,f'{v:.1f}%'.replace('.',','),32,color,600,'end'),t)
  b+=event(rect(465,y,850*v/100,32,color,rx=8),t+.13,'link')
 b+=event(txt(95,774,'Somma = 100% · Punteggi sintetici, non CTR misurati.',29,C['purple'],550),6.4)
 decision=finish('decision',a,b);events.clear()
 a=title('La stessa persona. Una nuova domanda.','Ri-esposizione qualitativa senza mostrare il punteggio Decision.')
 a+=event(card(90,330,450,365)+person_icon(155,399)+txt(211,410,'Chiara',38,weight=600),.08,'ui')
 a+=event(txt(124,494,'Rivede lo stimolo C12',27),.6)+event(pill(124,544,140,'FGR-U3'),1.12)
 a+=line(562,510,679,510,1.35)
 a+=event(logo('t3-code',740,357,65)+logo('gemini',826,357,65)+txt(740,491,'Intervista con Gemini',34,weight=600),1.5,'ui')
 a+=event(txt(740,548,'T3 Code coordina',27,C['muted']),2.05)
 a+=event(txt(740,606,'Nessuna probabilità in input',27,C['teal']),2.62)
 a+=event(txt(90,752,'Le ragioni sono una nuova risposta sintetica.',30,C['purple'],550),3.12)
 b=title('Ascoltiamo cosa conta.','Estratti letterali dell’intervista registrata.')
 b+=event(rect(90,317,1420,165,'#E9F5F0',rx=18)+txt(123,359,'Cosa apprezza',23,C['teal'],600),3.88,'ui')
 b+=event(lines(123,406,'«'+positive+'…»',82,30,leading=39),4.25)
 b+=event(rect(90,505,1420,165,'#FAEEEA',rx=18)+txt(123,547,'Cosa la allontana',23,C['coral'],600),4.8,'ui')
 b+=event(lines(123,594,'«'+negative+'…»',82,30,leading=39),5.17)
 b+=event(txt(90,735,'Da verificare: meno timer, più dettagli su materiali e reso.',30,C['purple'],600),5.85)
 b+=event(txt(90,782,'Confronta le creatività. Porta lo spunto in un test reale.',27,weight=550),6.4)
 interview=finish('interview',a,b)
 return routing,decision,interview
