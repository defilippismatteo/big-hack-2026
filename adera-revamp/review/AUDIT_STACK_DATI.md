# Audit ADERA: stack, provenienza e grafico quasi piatto

Audit in sola lettura del runtime e dei dati, 14 novembre 2026. Nessuna inferenza, API o modifica ai dati sorgente. Gli unici nuovi file sono questo rapporto e gli strumenti nella cartella `review/`.

## Verdetto

**Il CTR quasi piatto della Overview corrisponde ai dati esportati: non ho trovato un errore numerico nella curva.** La scelta del modello produce un CTR costante nel tempo per ogni annuncio; il grafico aggrega tutte le campagne e usa un asse Y da 0 a 2%. Il movimento effettivo occupa circa 1,5 pixel su un grafico alto 200 pixel.

Questo non dimostra che il CTR reale resterà stabile durante il Black Friday. La baseline non stima un effetto temporale dell’evento; lo scenario stagionale è una serie separata, basata su ipotesi del benchmark 2025. Le evidenze sulle personas non entrano nel forecast.

Ho trovato invece un problema concreto di **riproducibilità e denominazione dei modelli**: la Overview è stata aggiornata a CTR baseline + CPM Timestral, ma parte della documentazione, il selettore Forecast Analytics e il controllo di `export_parallel.py` assumono ancora una baseline 14 giorni anche per il CPM. È già presente nel ramo originale ADERA, non è stato introdotto dal revamp.

## Risultati prioritari

| Priorità | Tipo | Riscontro | Implicazione |
|---|---|---|---|
| Alta | Riproducibilità | Le 699 righe CPM della Overview differiscono da `cpm_baseline` del sorgente pilota; il controllo dell’export si interrompe. | Non è possibile rigenerare i tre snapshot con la procedura documentata attuale senza riallineare contratto e provenienza. |
| Media | Presentazione del modello | Forecast Analytics chiama la serie principale «Baseline a 14 giorni», ma il suo CPM è Timestral-28M. | Il confronto fra modelli viene interpretato male, pur leggendo valori numerici validi. |
| Media | Freschezza/copertura | Lo snapshot pubblico contiene 18 asset e 3.600 valutazioni; durante l’audit gli artefatti live ne contenevano 29 e 5.800. | Il frontend è una fotografia parziale, non una vista dello stato corrente del processo Decision. |
| Media | Limite del modello | Il CTR è costante per tutti i 51 annunci lungo l’orizzonte. | Una curva quasi piatta è attesa; non rappresenta una previsione dinamica dell’effetto Black Friday. |
| Bassa | Leggibilità | Escursione CTR aggregato 0,01518 punti percentuali su asse 0–2%. | La differenza è quasi invisibile. Un eventuale zoom deve essere esplicito, senza fabbricare oscillazioni. |

## 1. Quale dashboard e quali snapshot

La dashboard corretta è il frontend React del branch `feat/adera-dashboard`, copiato dal commit `a2e17cefdc196c775e5b85eca02b90cd16be9697` in `adera-revamp/`. Il revamp mantiene gli stessi tre JSON del branch; `REVAMP_SOURCE.json` ne registra gli hash.

Il frontend dispone di sei viste: Overview, Audience Lab, Creative Explorer, Forecast Analytics, Budget Planner e Model Validation. Non usa il vecchio `dashboard_gemini2.html` e non carica il payload completo di `market_mirror/design_dashboard.py`.

| Snapshot | Contenuto effettivo | Provenienza dichiarata |
|---|---|---|
| `public/data/overview.json` | Forecast principale, scenari budget, aggregati storici, 12 ipotesi, aggregati di 600 persone, reazioni aggregate su 18 asset | Runtime `3f092dd8c614220ddc43c2ec99d407b33c786be9`, metodo `ctr_baseline14d__cpm_timestral28m` |
| `public/data/pilot-forecast.json` | CPM ensemble CatBoost–Timestral e CTR/CPM arricchiti stagionali sulle stesse 699 chiavi | Pilota `2e817b282df525ef9ac6635b808d3752d684bdd2` |
| `public/data/model-validation.json` | Errori dei modelli su 759 righe di holdout, due finestre cronologiche | Pilota `2e817b282df525ef9ac6635b808d3752d684bdd2` |

Ho confrontato tutte le previsioni della Overview con `artifacts/wevion_v4/forecasts_2026-11-16_30.csv`: **differenza massima assoluta CTR = 0, CPM = 0**. Il CPM del pilota coincide esattamente con il CSV conservato nel suo commit. Le serie numeriche non sono state inventate o sostituite dal redesign.

Il commit del runtime principale, il commit dell’export Timestral, il commit del pilota e quello del frontend sono riferimenti distinti: non sono tutti una singola versione del modello.

## 2. Stack e percorso dei dati

```text
Kit simulato organizzatori
  ├─ storico_giornaliero.csv (1.879 righe / 91 giorni)
  ├─ da_prevedere.csv (699 chiavi annuncio–giorno)
  ├─ campagne, adset, annunci, budget e calendario
  └─ benchmark 2025 + 36 asset testuali
       │
       ├─ Python Market Mirror
       │   ├─ tassi dai conteggi e audit qualità
       │   ├─ baseline gerarchica pesata 14 giorni
       │   ├─ import di export Timestral già calcolati da Git
       │   ├─ 12 ipotesi audience con evidenze
       │   ├─ scenario budget entro ±20% con pacing/quote congelati
       │   └─ scenario stagionale separato dal benchmark 2025
       │
       ├─ ramo pilota quantitativo
       │   └─ CatBoost, Timestral, confronto storico, mix CPM, arricchimento BF/CM
       │
       └─ ramo sintetico indipendente
           ├─ Python: slot e controlli di diversità
           ├─ Gemini tramite T3/Antigravity: schede sintetiche
           ├─ Gemini Decision 1: azioni/motivi per persona–stimolo
           └─ interviste cieche e report qualitativi
                    │
Script Python di export frontend → tre JSON statici
                    │
React 19 + Vite 7 → fetch locale → modelli JS → componenti SVG/CSS
```

Il frontend usa React 19.2.9, React DOM 19.2.9, Vite 7.3.8, Lucide React 1.73.0 e Inter locale. Non serve un backend mentre si naviga: `useDashboardData.js` legge gli snapshot con `fetch`. L’anteprima offline incorpora gli stessi snapshot, logo e font; non riesegue i modelli.

Lo storico copre il 17 agosto–15 novembre 2026; l’orizzonte richiesto è 16–30 novembre. Ci sono 3 campagne, 12 ad set, 51 annunci futuri, 36 asset e €16.950 di budget pianificato. Le 699 righe non sono 699 misure osservate: sono coppie annuncio–giorno da prevedere. Il kit non contiene esiti futuri.

`observed` significa qui etichette fornite nel kit simulato. Non abbiamo in questi file prestazioni misurate di campagne reali.

Riferimenti: `market_mirror/delivery.py:12–49`, `market_mirror/analytics.py:29–42`, `adera-revamp/scripts/export_overview.py:57–202`, `adera-revamp/src/data/useDashboardData.js:3–29`.

## 3. Come siamo arrivati al forecast principale

La baseline prende gli ultimi 14 giorni disponibili al cutoff e calcola rapporti sui conteggi, non una media semplice dei CTR giornalieri:

- CTR = 100 × somma click / somma impression.
- CPM = 1.000 × somma spesa / somma impression.
- Cerca storico per annuncio, poi asset, ad set, settore e infine globale.

Il ciclo applica quel valore a ogni data futura dell’annuncio. **La data futura non modifica il CTR della baseline** (`market_mirror/forecast.py:16–36`). I cold-start ricevono fallback, non una previsione di risposta basata sul testo creativo.

Con `--timestral-ref`, il percorso principale non esegue Timestral: importa l’export dal commit `2d8adf033e747e147c401246c07ce656f9f1cfb7`. Il selettore confronta separatamente baseline e Timestral sulla WMAE del primo holdout storico: sceglie baseline per CTR, Timestral-28M per CPM (`forecast.py:93–132`). Il manifest lo dichiara e riporta ancora CatBoost come confronto pendente per questo specifico percorso.

Il ramo pilota successivo contiene invece già il confronto CatBoost–Timestral e seleziona baseline CTR + mix CPM. Non bisogna interpretare l’esistenza di questo confronto come un aggiornamento automatico del modello consumato dalla Overview.

Le metriche aggregate su 759 righe dei due holdout, nel JSON di Model Validation, sono:

| Modello | WMAE CTR (punti percentuali) | WMAE CPM (€) |
|---|---:|---:|
| Baseline 14g | 0,226029 | 0,755871 |
| CatBoost | 0,260558 | 0,700372 |
| Timestral-28M | 0,239581 | 0,699324 |
| Mix 50/50 | 0,225572 | 0,674187 |

La differenza aggregata CTR baseline/mix è minima; questi numeri non validano il Black Friday futuro. Le finestre sono 19 ottobre–1 novembre e 2–15 novembre; non abbiamo una verifica osservata sul periodo 16–30 novembre. Intervalli calibrati e validazione del ranking creativo restano distinti da questi errori medi.

## 4. Perché la curva è quasi orizzontale

La Overview parte da CTR e «Previsione base», non da CPM né da scenario stagionale (`ForecastChart.jsx:16–19`). La timeline è ricavata dalle righe budget al budget originario, non da quello riallocato (`src/overview/model.js:32–51`).

Per ogni ad set/giorno Python:

1. Fissa il pacing al valore mediano storico recente, escludendo i giorni oltre budget solo dalla stima del pacing.
2. Usa quote di spesa 90% distribuzione storica degli annunci attivi + 10% esplorazione uniforme. I nuovi annunci hanno perciò una quota positiva ma piccola.
3. Converte spesa prevista e CPM in impression, poi impression e CTR in click.
4. Aggrega nuovamente ad set e campagne.

Il frontend rappresenta quindi `100 × somma(click stimati) / somma(impression stimate)`. È la formula corretta per il CTR aggregato; non è una media aritmetica di percentuali (`marketing.py:28–85`, `export_overview.py:111–118`, `src/overview/model.js:37–51`).

Tutti i 51 annunci hanno CTR identico fra le proprie date. Le piccole variazioni globali dipendono dal mix di annunci attivi, dai pesi determinati dai CPM variabili e dai budget. Inoltre l’aggregazione fra campagne può smorzare differenze individuali: il CTR dei singoli annunci varia da 0,644701% a 3,495401%, benché la serie temporale aggregata resti vicina a 1,17%.

| Serie giornaliera, tutte le campagne | CTR min–max | Escursione CTR | CPM min–max |
|---|---|---:|---|
| Overview, previsione base | 1,160213–1,175390% | 0,015177 pp | €10,0492–11,2170 |
| Overview, scenario stagionale | 1,200042–1,412729% | 0,212687 pp | €10,6949–12,4384 |
| Forecast Analytics, pilota | 1,165333–1,173695% | 0,008362 pp | €9,7873–10,6454 |
| Forecast Analytics, scenario arricchito pilota | 1,220153–1,695928% | 0,475774 pp | €10,4265–16,3607 |

La serie Forecast Analytics di riferimento e quella Overview coincidono numericamente, entro precisione macchina. Lo scenario stagionale Overview e quello arricchito del pilota sono invece **due trasformazioni diverse**, non due nomi per lo stesso dato.

La scala grafica attuale parte da zero e arrotonda il massimo a 2% (`ForecastChart.jsx:8–11,29–31`). Il range base equivale allo 0,759% dell’altezza, cioè circa 1,52 px su 200 px. Non c’è bisogno di una mancata interpolazione o di un errore nel tracciato per spiegare la piattezza.

## 5. Cosa le personas aggiungono e cosa non aggiungono

Sono due livelli diversi:

- Le **12 ipotesi per ad set** derivano dallo storico aggregato, con evidenze, confidenza bassa e interpretazioni alternative. Non sono persone osservate.
- I **600 profili sintetici** sono generati da quote preparate in Python e schede scritte con Gemini tramite T3/Antigravity. Gli artefatti esaminati indicano provider `t3:antigravity`, modello `gemini-4-hydrogen` per tutte le 600 schede. Sono distribuiti per settore, non derivati dalle 12 ipotesi.
- Le **reazioni Gemini Decision 1** sono probabilità di azioni e motivazioni in un insieme chiuso. `calibrated_to_ctr=false`: l’intenzione di click non è il CTR del forecast e non viene usata per spostare la curva.
- Le **interviste cieche** sono ri-esposizioni qualitative, non spiegazioni certe dei risultati di Decision, né interviste a consumatori reali. Il task passa alla persona solo i suoi stimoli anonimizzati.

Le limitazioni di lettura del writer sono istruzioni e proiezioni del payload, non isolamento filesystem del sistema operativo (`t3_personas.py:69–127`).

Il frontend importa solo:

- numerosità globali e per settore, età, genere e frequenze degli interessi sintetici;
- azioni/motivi medi per asset, numero di persone, modello e run id;
- ipotesi storiche ed evidenze per ad set.

**Non importa** le schede nominative complete, i risultati persona–asset individuali, le interviste, le ricevute T3 o i report/summarizer. La ripartizione delle reazioni per età non è quindi disponibile nella dashboard, benché possa esserlo negli artefatti interni; il frontend lo dichiara. Il filtro ad set limita le ipotesi storiche, mentre i profili/reazioni sono riferiti al settore (`AudienceLab.jsx:28–35,59,92–104`; `scripts/audience_data.py:8–46`).

Lo snapshot conserva 18 asset × 200 valutazioni = 3.600 coppie. Gli asset comuni corrispondono esattamente all’aggregazione corrente. Durante una lettura dell’audit, il summary e il ledger in sola lettura indicavano 29 asset e 5.800 analisi completate; il ledger aveva ulteriori elementi pendenti. Sono processi in avanzamento: questi conteggi live possono crescere e non sono congelati nel frontend. I 600 profili e le loro distribuzioni pubbliche corrispondono invece agli attuali artefatti.

Le interviste trovate: 4 risposte nel pilota, con freeze presente; 400 file risposta nel pool 600, senza `frozen.json` in quel pool al momento del controllo. Contare file non certifica la validità o il completamento delle interviste. Nessuno di questi transcript è caricato dall’attuale frontend.

## 6. Problema riproducibile nel contratto tra export

`export_parallel.py:28–31` richiede che `cpm_baseline` nel CSV del pilota coincida con il CPM di ogni riga di `overview.json`. Ora il CPM Overview è Timestral. Il confronto fallisce su tutte le 699 righe.

Ho eseguito l’adattatore in una directory temporanea, estraendo i due CSV del commit dichiarato, senza cambiare il branch:

```text
ValueError: Provenienza o mapping incoerenti: 2026-11-16 CDF-AD03
```

Il JSON pilota già esistente rimane numericamente corretto rispetto al proprio CSV, e il CTR baseline è uguale nei due percorsi. Il difetto riguarda l’assunzione di uguaglianza del riferimento CPM e l’impossibilità di riprodurre l’intero set aggiornato con quella procedura. Anche `README.md:35–44` cita ancora un vecchio commit e un export solo baseline, mentre `ForecastAnalytics.jsx:8` denomina la serie principale «Baseline a 14 giorni».

I 4 test frontend controllano chiavi, copertura, totali budget, ranking coerente e ripartizioni dei holdout; non controllano la coerenza del metodo dichiarato o la riproduzione degli export, perciò possono passare nonostante questo problema.

## 7. Cosa farei dopo questo audit

1. Riallineare il contratto degli export e la provenienza per ogni serie. Ogni snapshot dovrebbe portare metodo, commit sorgente, hash degli input, timestamp e copertura; i dati Decision dovrebbero riportare chiaramente il freeze e lo stato parziale.
2. Correggere il nome del riferimento in Forecast Analytics e le istruzioni README, distinguendo baseline CTR, Timestral CPM, ensemble e arricchimento stagionale.
3. Nella Overview spiegare «CTR baseline costante per annuncio; aggregazione pesata». Affiancare eventualmente la serie stagionale senza presentarla come risultato osservato.
4. Se utile, aggiungere un’opzione di zoom Y esplicitamente indicata e il range numerico; conservare la possibilità di vedere l’asse da zero. Non introdurre rumore o cambiare i dati per rendere il grafico più mosso.
5. Esplorare CPM, singole campagne/ad set e i due scenari, anziché giudicare la qualità del modello dall’aspetto della sola media CTR. Per un effetto Black Friday validato servirebbe un holdout evento reale/simulato adeguato; lo zoom non colma quella mancanza.

Nessuna correzione è stata applicata in questo audit.

## Ripetere le misure

Dalla root del progetto:

```sh
python3 adera-revamp/review/audit_data.py
```

Lo script legge snapshot e artefatti, estrae un CSV immutabile da Git e aggiorna soltanto `review/measurements.json`. Non chiama API o modelli e non cambia sorgenti/dati. Le serie complete giornaliere sono incluse nel JSON, per controllare i numeri senza ricostruire il frontend.
