# Wevion · consegna candidata v4

Metodo: ctr_baseline14d__cpm_timestral28m.
699 previsioni CTR/CPM, 12 audience ipotizzate, 180 scenari adset/giorno e viewer.html.

Gli output sono calcolati dai dati del kit sintetico; nessun risultato futuro è osservato.
Gli scenari stagionali derivano dal benchmark 2025 del kit, non da campagne esterne.
La selezione importata confronta baseline e Timestral sul primo fold WMAE; CatBoost resta da confrontare.
Le audience sono ipotesi comportamentali a confidenza bassa, con alternative; nessuna demografia è osservata.
I budget sono conservati per campagna/giorno entro ±20%; pacing e quote delivery sono ipotesi dichiarate.

## Audience e ragionamento

### CDF-AS1
Persone plausibilmente sensibili alla disponibilità limitata, quando il prodotto è già pertinente
CTR storico 1.134%; CPM 5.22 €.
Alternativa: Il divario può dipendere da contenuto specifico, calendario, costo d'asta o selezione della delivery, senza riflettere un diverso pubblico

### CDF-AS2
Persone plausibilmente orientate a confrontare promozioni e convenienza stagionale
CTR storico 1.049%; CPM 6.39 €.
Alternativa: Il divario può dipendere da contenuto specifico, calendario, costo d'asta o selezione della delivery, senza riflettere un diverso pubblico

### CDF-AS3
Persone plausibilmente sensibili alla disponibilità limitata, quando il prodotto è già pertinente
CTR storico 1.204%; CPM 6.15 €.
Alternativa: Il divario può dipendere da contenuto specifico, calendario, costo d'asta o selezione della delivery, senza riflettere un diverso pubblico

### CDF-AS4
Persone plausibilmente orientate a confrontare promozioni e convenienza stagionale
CTR storico 2.388%; CPM 9.95 €.
Alternativa: Il divario può dipendere da contenuto specifico, calendario, costo d'asta o selezione della delivery, senza riflettere un diverso pubblico

### FGR-AS1
Persone plausibilmente disponibili a decidere entro una scadenza chiara
CTR storico 0.903%; CPM 5.93 €.
Alternativa: Il divario può dipendere da contenuto specifico, calendario, costo d'asta o selezione della delivery, senza riflettere un diverso pubblico

### FGR-AS2
Persone plausibilmente sensibili alla disponibilità limitata, quando il prodotto è già pertinente
CTR storico 1.189%; CPM 7.25 €.
Alternativa: Il divario può dipendere da contenuto specifico, calendario, costo d'asta o selezione della delivery, senza riflettere un diverso pubblico

### FGR-AS3
Persone plausibilmente sensibili alla disponibilità limitata, quando il prodotto è già pertinente
CTR storico 1.208%; CPM 10.10 €.
Alternativa: Il divario può dipendere da contenuto specifico, calendario, costo d'asta o selezione della delivery, senza riflettere un diverso pubblico

### FGR-AS4
Persone plausibilmente orientate a confrontare promozioni e convenienza stagionale
CTR storico 2.190%; CPM 10.84 €.
Alternativa: Il divario può dipendere da contenuto specifico, calendario, costo d'asta o selezione della delivery, senza riflettere un diverso pubblico

### NDL-AS1
Persone plausibilmente sensibili alla disponibilità limitata, quando il prodotto è già pertinente
CTR storico 0.888%; CPM 7.63 €.
Alternativa: Il divario può dipendere da contenuto specifico, calendario, costo d'asta o selezione della delivery, senza riflettere un diverso pubblico

### NDL-AS2
Persone plausibilmente orientate a confrontare promozioni e convenienza stagionale
CTR storico 1.142%; CPM 8.45 €.
Alternativa: Il divario può dipendere da contenuto specifico, calendario, costo d'asta o selezione della delivery, senza riflettere un diverso pubblico

### NDL-AS3
Persone plausibilmente sensibili alla disponibilità limitata, quando il prodotto è già pertinente
CTR storico 1.385%; CPM 9.87 €.
Alternativa: Il divario può dipendere da contenuto specifico, calendario, costo d'asta o selezione della delivery, senza riflettere un diverso pubblico

### NDL-AS4
Persone plausibilmente orientate a confrontare promozioni e convenienza stagionale
CTR storico 1.889%; CPM 13.42 €.
Alternativa: Il divario può dipendere da contenuto specifico, calendario, costo d'asta o selezione della delivery, senza riflettere un diverso pubblico

## Da completare prima della consegna finale
- Confrontare CatBoost e completare la selezione del modello
- Calibrare gli intervalli e validare il ranking delle creatività
- Rivedere le ipotesi di pubblico e le evidenze che le sostengono
- Registrare e verificare il video di 180 secondi
