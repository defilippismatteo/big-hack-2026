"""Export three existing synthetic cards and explicitly illustrative report content."""
from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parents[2]
source=root/'artifacts/personas_t3_600/persona_cards.json'
raw=source.read_bytes();cards=json.loads(raw)['personas']
examples={}
for p in cards:
 if p['vertical'] not in examples:
  examples[p['vertical']]={k:p.get(k) for k in ['persona_id','name','vertical','age_years','occupation','persona_summary','interests','concerns','trust_requirements','decision_habits','ad_avoidance','provider','model']}
reports={
'abbigliamento':{'positive':['Una vestibilità facile da valutare riduce i dubbi.','Praticità e qualità del tessuto rendono il prodotto rilevante.','Un’offerta leggibile aiuta a capire il vantaggio.'],'negative':['Taglie poco chiare possono bloccare la scelta.','La sola urgenza non spiega il valore del capo.','Resi e materiali devono essere facili da trovare.'],'next':'Provare un messaggio con taglie, materiali e reso in evidenza.'},
'beauty_skincare':{'positive':['Una routine semplice rende il beneficio comprensibile.','Ingredienti e modalità d’uso aiutano a valutare il prodotto.','Un risultato descritto in modo concreto incuriosisce.'],'negative':['Promesse generiche possono ridurre la fiducia.','Mancano indicazioni per capire a quale pelle è adatto.','Lo sconto da solo non risolve i dubbi sul prodotto.'],'next':'Provare un annuncio che chiarisca tipo di pelle e modalità d’uso.'},
'pet_ecommerce':{'positive':['Un beneficio concreto per l’animale attira l’attenzione.','Ingredienti e composizione aiutano il confronto.','Una promozione semplice facilita la valutazione.'],'negative':['Troppe condizioni rendono l’offerta difficile da leggere.','Non è sempre chiaro per quali animali è indicato.','Spedizione e costo totale possono restare incerti.'],'next':'Provare una versione con offerta, destinatario e costo totale espliciti.'}}
out={'schemaVersion':1,'examplesKind':'synthetic','examplesSource':{'path':str(source.relative_to(root)),'sha256':hashlib.sha256(raw).hexdigest()},'examples':examples,'reportsKind':'mock_not_model','reportsStatus':'Esempio di struttura: non deriva dalle interviste. Il rapporto finale è in preparazione.','reports':reports}
(root/'adera-revamp/public/data/product-story.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
