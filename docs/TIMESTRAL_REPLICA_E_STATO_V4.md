# Timestral: replica locale e stato rispetto alla specifica v4

Verifica del 14 novembre 2026. **I risultati del branch sono riprodotti sul tuo Mac**:
stessi hash dei pesi, stesse metriche pubblicate per Timestral-5M e Timestral-28M,
stessi risultati del primo esperimento CatBoost. Le predizioni differiscono soltanto
di piccole quantità numeriche tra le due piattaforme CPU; i CSV non sono identici byte per byte.

Il progetto dispone di una consegna candidata funzionante, ma la scelta del modello
finale e la calibrazione dell'incertezza restano aperte. Il confronto completo con
CatBoost rende più circoscritta la raccomandazione del report `Prima_Analisi`.

## 1. Che cosa è stato replicato

- Branch remoto `origin/feat/timestral-pilot`, commit completo
  `2d8adf033e747e147c401246c07ce656f9f1cfb7`, aggiornato con `git fetch`.
- Pilot originario al commit `c0f02811724f8ab61e37d4e7a26035b4096e19f7`, incluso
  nel commit successivo insieme a `Prima_Analisi/analisi.py`, report e risultati.
- Copia immutata dei sorgenti sotto `artifacts/timestral_reproduction/source/`.
  Nessun checkout, merge o modifica al branch forecasting; il lavoro locale su main è preservato.
- Pesi ufficiali 5M e 28M scaricati localmente, con `config.json`, README e licenza.
  Nessun fine-tuning, chiamata Google, upload del kit o servizio persistente.
- Due backtest cronologici e forecast finale per entrambi i modelli, in CPU e
  con rete disabilitata a livello Hugging Face durante l'inferenza (`HF_HUB_OFFLINE=1`).
  Non si tratta di isolamento di rete a livello OS.
- Riesecuzione immutata di `Wevion_Validation_Baseline.py`: due modelli CatBoost
  per fold, senza cambiare iperparametri o scegliere una nuova configurazione sugli holdout.

La specifica v4 nella root e la copia nel percorso indicato dall'utente sono identiche.

### Ambiente e identità dei modelli

| Elemento | Report originale | Replica locale |
|---|---|---|
| CPU | Intel x86_64 | Apple arm64 |
| Python | 3.12.16 | 3.12.13 |
| PyTorch | 2.7.1 | 2.7.1 |
| Thread PyTorch | 2 | 2 |
| Sorgente Timestral | Dipendenza fissata dal pilot | `a534bdbd244d64f3d9d743f46c7bf6fc330ed4ff` |
| NumPy / pandas locali | Non registrati nel report | 2.5.4 / 2.3.3 |

| Modello | Revisione Hugging Face | SHA-256 dei pesi, identico al report |
|---|---|---|
| Timestral-5M, 20.843.960 byte | `bdd20cfc15a3fea0e4cb5ccef37f8d3ca7aa335f` | `7ace108c4987e7f2a99a75a445240019d1d31c2117139d1bd05ffdfd25aca738` |
| Timestral-28M, 111.296.464 byte | `49b26409ac87b5935539a5d8ffe7f397b720db47` | `dfc83c6220937ce5fc6687b35a4df94cd25e28a2cfe6fb92a23dad6301b2015d` |

Tutte le metriche serializzate dei due modelli coincidono alla precisione pubblicata
(quattro decimali), compresi ad set, cold start e copertura. Anche il JSON CatBoost
coincide interamente con quello iniziale. Cambiano ambiente e tempi.

| Scarto massimo assoluto rispetto ai CSV originali | 5M | 28M |
|---|---:|---:|
| CTR mediano, punti percentuali | 0,000006 | 0,000002 |
| CPM mediano, euro | 0,000027 | 0,000054 |
| Qualsiasi quantile CTR, punti percentuali | 0,000025 | 0,000065 |
| Qualsiasi quantile CPM, euro | 0,000231 | 0,000063 |
| Baseline CTR e CPM | 0 | 0 |

Gli scarti sono compatibili con differenze di calcolo floating point tra piattaforme;
la verifica non isola il contributo specifico di CPU, patch Python e librerie numeriche.
Il controllo numerico usa una soglia assoluta di 0,0005 nelle rispettive unità:
è una tolleranza di riproduzione, non una misura di accuratezza previsionale.

Tempi del codice `run_model` nei due passaggi locali: 0,31–0,33 s per il 5M e
0,80–0,85 s per il 28M, contro 3,78 s e 11,22 s nel report Intel. Includono caricamento, due backtest,
forecast e controlli di quello script; escludono download, creazione dell'ambiente
e import iniziali. Sono due misure esplorative, non un benchmark controllato.

## 2. Confronto completo con baseline e CatBoost

Target ricalcolati dai conteggi: CTR = 100 × click/impression, CPM = 1000 × spesa/impression.
**MAE** dà uguale peso a ciascuna riga; **WMAE** pesa per impression. Le impression
dell'holdout sono usate per valutare, non fornite al modello come futuro noto.
Timestral qui significa previsione ad-level ottenuta dall'adattatore del pilot.

| Holdout | Metodo | MAE CTR, pp | WMAE CTR, pp | MAE CPM, € | WMAE CPM, € |
|---|---|---:|---:|---:|---:|
| 19/10–01/11, 315 righe | Baseline 14 giorni | 0,2451 | **0,1977** | 0,7986 | 0,7143 |
| | Timestral-5M | 0,2727 | 0,2235 | 0,7705 | 0,7013 |
| | Timestral-28M | **0,2420** | 0,2020 | 0,7649 | 0,6927 |
| | CatBoost | 0,3536 | 0,3057 | **0,7122** | **0,6862** |
| 02/11–15/11, 444 righe | Baseline 14 giorni | 0,3163 | 0,2576 | 1,0218 | 0,8022 |
| | Timestral-5M | 0,3585 | 0,2859 | 0,9673 | 0,7573 |
| | Timestral-28M | 0,3446 | 0,2815 | **0,8841** | **0,7067** |
| | CatBoost | **0,2743** | **0,2103** | 0,9274 | 0,7161 |

**Lettura del report originale.** La raccomandazione «baseline CTR + 28M CPM» è
supportata nel confronto baseline/Timestral sul WMAE: il 28M riduce l'errore CPM
del 3,0% e dell'11,9% rispetto alla baseline, peggiorando però il WMAE CTR in
entrambi i fold. Sul MAE CTR non ponderato del primo fold il 28M migliora leggermente:
non è corretto generalizzare che peggiori ogni misura del CTR.

**Che cosa cambia aggiungendo CatBoost.** CatBoost vince sul CPM nel primo fold,
mentre il 28M vince nel secondo; CatBoost vince sul CTR nel secondo fold ma perde
nettamente nel primo. Il vantaggio WMAE CPM del 28M rispetto a CatBoost nel
secondo fold è circa 1,3%, più piccolo dell'11,9% relativo alla baseline.
Non è stata stimata la significatività di queste differenze, né l'indipendenza
degli errori tra annunci dello stesso ad set/giorno.

La regola della consegna candidata seleziona separatamente i due target sul
**primo fold**, ma confronta soltanto baseline e 28M. Aggiungendo CatBoost alla
stessa regola WMAE, il primo fold sceglierebbe baseline CTR + CatBoost CPM.
Questo non obbliga a cambiare subito la consegna: dimostra che la selezione
documentata è incompleta. Scegliere CatBoost CTR + 28M CPM guardando il secondo
fold e poi presentare quel fold come verifica indipendente sarebbe scorretto.
I risultati dei due fold erano già noti; questa replica non crea un nuovo test cieco.

Raccomandazione corrente: conservare la candidata esistente e questa replica come
esperimenti tracciati; definire metrica e protocollo prima di ulteriori scelte.
L'ibrido **CatBoost × correzione temporale Timestral** della v4 non è stato valutato:
il pilot moltiplica una baseline gerarchica, non CatBoost.

### Valutazione ad set e incertezza

Il report `Prima_Analisi` corregge appropriatamente un problema del pilot: il
punteggio originale chiamato `timestral_direct_adset` confronta una previsione
di ad set con ciascun annuncio. La vera valutazione ad set richiede invece
somma di click/spesa/impression per `(data, adset_id)`: 168 righe per fold.
La replica conferma i numeri aggregati del report:

| Holdout | WMAE CTR baseline → 28M, pp | WMAE CPM baseline → 28M, € |
|---|---:|---:|
| 19/10–01/11 | 0,1574 → 0,1781 | 0,6625 → 0,6349 |
| 02/11–15/11 | 0,1836 → 0,2047 | 0,7479 → 0,6045 |

Anche i quantili del report sono riprodotti. Sono quantili del modello trasformati
dall'adattatore, senza calibrazione empirica della copertura ad-level.

| Bande CPM 28M q10–q90 | Primo fold | Secondo fold |
|---|---:|---:|
| Copertura, tutti gli annunci | 82,54% | 83,11% |
| Ampiezza media, € | 3,01 | 3,12 |
| Copertura, annunci nuovi | **66,67%** su 63 righe | **69,70%** su 66 righe |
| Ampiezza media annunci nuovi, € | 3,83 | 3,48 |

L'intervallo nominale q10–q90 ha massa 80%: la copertura globale vicina a quel
valore non garantisce la copertura sugli annunci nuovi. Per il CTR del 28M nel
secondo fold la copertura è 69,59% globale e 56,06% cold start. Non trasferire
le bande CTR di Timestral a una previsione centrale prodotta dalla baseline.
La consegna candidata conserva correttamente lo stato «non calibrato».

## 3. Dati disponibili e informazioni realmente usate

| Dato | Disponibile nel kit | Uso verificato |
|---|---|---|
| Storico | 1.879 righe, 17/08–15/11, 91 giorni; 57 annunci storici | Baseline, CatBoost, aggregazione Timestral |
| Futuro richiesto | 699 righe, 16–30/11, 51 annunci | Solo chiavi e metadati noti; esiti assenti |
| Nuovi annunci/asset | 12 annunci, 114 righe; 6 asset nuovi BF | Fallback della baseline; metadati CatBoost; incertezza da migliorare |
| Gerarchia | 3 campagne/vertical, 12 ad set, 69 annunci, 36 asset | Aggregazioni e mapping; nessuna audience osservata |
| Budget | 1.272 righe adset/giorno | Covariata Timestral, feature CatBoost e scenari di budget |
| Benchmark 2025 | 66 righe settimanali, Meta IT | Due covariate Timestral; feature CatBoost; scenari stagionali |
| CPM mensili | 704 righe fino a ottobre 2026 | Disponibili; non usati nel pilot né nello script CatBoost iniziale |
| Testi/visual | Descrizioni testuali, nessun media originale | Nel catalogo personas; lo script CatBoost iniziale usa leva/formato, non feature dei testi |

Timestral riceve due target per ciascuno dei 12 ad set e sette covariate:
budget, indice CTR 2025, indice CPM 2025, weekend, Black Week, Black Friday e
Cyber Monday. Il benchmark viene allineato di 364 giorni per settimana/evento.
Le forme sono `(12,2,63)` + `(12,7,77)`, `(12,2,77)` + `(12,7,91)` e infine
`(12,2,91)` + `(12,7,106)`. Nessuna cella di contesto mancante nei tre periodi.

I flag Black Week/Friday/Cyber Monday sono tutti **zero nel contesto storico**
e diventano uno soltanto nel futuro. Il modello riceve i numeri, non il significato
linguistico degli eventi. La loro presenza non dimostra che abbia appreso l'effetto
del Black Friday. Gli indici 2025 offrono un prior più informativo, ma la loro
efficacia specifica non è stata isolata con ablation. Gli indici CPM futuri arrivano
fino a circa 1,599, oltre il massimo storico fornito al modello di circa 1,218:
si sta anche chiedendo un'estrapolazione fuori dal range del contesto.

**Controlli effettuati:** 699 chiavi esatte, mapping coerenti, valori finiti,
CTR 0–100, CPM positivo e quantili ordinati; hash pesi e sorgenti; modifica
artificiale dei target successivi ai cutoff senza alcun cambiamento degli input
Timestral. Passano i 4 test del pilot, i 27 test del runtime e lo smoke offline.
Lo smoke genera fixture e non prova Gemini live.

**Anomalia già individuata e ancora presente:** 21/10, FGR-AS1, spesa 397,55 €
contro budget 100 €. È segnalata dall'audit e non corretta tacitamente. Il
forecasting originario conserva quel dato; manca una misura della sensibilità
dei risultati all'anomalia. Il motore decisionale esclude i giorni con spesa
superiore al budget dalla sola stima del pacing recente. L'audit segnala anche
50,01 € contro 50 € il 10/11 per CDF-AS3, differenza di un centesimo.

Tutti i numeri del kit sono **simulati dagli organizzatori**. «Osservato» qui
significa etichetta disponibile nel kit, non misura raccolta su campagne reali.
Nessun backtest include il periodo futuro 16–30/11 o il Black Friday.

## 4. A che punto siamo rispetto alla v4

| Priorità v4 | Stato verificato oggi | Limite residuo |
|---|---|---|
| P0: QA, join, baseline | Eseguiti, testati; anomalie esplicite | Sensibilità all'outlier non misurata |
| P0: CatBoost e confronto | Esperimento originale riprodotto; tabella completa sopra | Selezione finale incompleta; niente cold-start CatBoost dettagliato nel report iniziale |
| P0: 699 previsioni | Candidata in `artifacts/wevion_v4/`; replica indipendente in questa cartella | Esiti futuri indisponibili; candidata ancora provvisoria |
| P1: Timestral pilot | 5M/28M eseguiti localmente e risultati confermati | Ibrido con CatBoost e ablation covariate non eseguiti |
| P1: intervalli e ranking | Copertura e ampiezza quantili ora misurate | Calibrazione e validazione del ranking da fare |
| P2: 12 pubblici ipotizzati | Schede, evidenze ai tre cutoff e alternative già presenti nella candidata | Ipotesi comportamentali a bassa confidenza da rivedere; nessuna demografia verificata |
| P2: budget/creatività | 180 righe adset/giorno, pacing e quote ad; vincoli ±20% e totale per campagna verificati dai test | What-if condizionale: nessuna risposta causale al budget stimata |
| P3: viewer | `artifacts/wevion_v4/viewer.html` esiste, con CSV/JSON esportati | Verifica visuale e percorso utente completo non effettuati qui |
| P3: riproducibilità | Ambiente locale bloccato e procedura di replica presenti | Nuovo clone pulito della consegna completa non provato; runtime attuale ancora non versionato |
| P3: README/repo/video | README candidato presente; sorgenti nel workspace | Commit/integrazione da organizzare; nessun video di 180 s trovato nella consegna candidata |
| P4: molte personas / Decision 1 | 72 slot/schede template, feed e aggregazione offline testati | Live Google e utilità per il forecast non dimostrati; non prerequisito per chiudere P0–P3 |

La candidata esistente dichiara `imported_precomputed_not_rerun` e importa i
CSV dal commit `2d8adf0`. Questa sessione ne verifica ora indipendentemente la
sorgente, ma **non riscrive il manifest né i risultati della candidata**: la
provenienza del file originale resta corretta. Il confronto col forecast locale
ha scarto massimo di circa 0,00000049 pp CTR e 0,00005430 € CPM, coerente con
arrotondamento della baseline e differenze numeriche già descritte.

La guida `MARKET_MIRROR_GUIDA.md`, sezione 9, descrive ancora la verifica precedente
al commit `c0f0281` e l'assenza di inferenza locale. È un resoconto storico superato
da questa replica. Non confondere quello stato con la verifica odierna del report
successivo sul remoto.

## 5. Valutazione delle fonti esterne del report

Le tabelle adtribute, Kanbar, Biddyco e Olifant nel report precedente sono
confronti di plausibilità o scenari condizionali. Non sono etichette delle
campagne simulate e non validano le 699 predizioni. In questa sessione sono stati
esaminati il testo e i calcoli salvati, non riverificati i contenuti correnti
dei siti esterni. La riproduzione quantitativa riguarda i file del kit e il modello.

`analisi.py` genera gli scenari pubblici con un prodotto cartesiano tra fattori
esterni e CPM di ottobre per vertical: nessun fattore esterno entra in
`predict()`. È corretto mantenerli separati dalle previsioni. La v4 dà priorità
ai benchmark sintetici interni del 2025; la candidata include già scenari
conservativo/centrale/alta pressione basati su quelli. Non sono intervalli di
confidenza o scenari probabilisticamente calibrati e non vanno moltiplicati di
nuovo a una previsione che incorpora già lo stesso effetto stagionale.

## 6. Prossimi passi coerenti con la v4

1. Fissare la metrica primaria e il protocollo di selezione. Confrontare le
   candidate senza ottimizzare ripetutamente sul secondo fold già esplorato;
   se si provano nuove configurazioni, usare origini precedenti per lo sviluppo
   e dichiarare la limitata indipendenza del controllo finale.
2. Valutare l'eventuale ibrido CatBoost/Timestral, il ranking creativo e il cold
   start. Misurare sensibilità a outlier e covariate 2025 con esperimenti separati;
   adottare maggiore complessità soltanto se utile.
3. Calibrare le bande su dati precedenti al cutoff di valutazione e verificare
   copertura e ampiezza per annunci nuovi. Tenere separati quantili grezzi,
   scenari BF e intervalli calibrati.
4. Congelare il metodo delle 699 righe, riesaminare le 12 ipotesi di pubblico,
   verificare viewer e scenari budget, versionare la pipeline e provare un clone
   pulito. Preparare infine il video di 3 minuti con numeri identici agli export.

## 7. Come rieseguire e dove leggere le prove

Dalla root del progetto, replica completa con eventuale download dalla cache/rete:

```bash
bash artifacts/timestral_reproduction/reproduce.sh
```

Solo verifica offline con ambiente e pesi già presenti (rigenera anche i raw):

```bash
HF_HUB_OFFLINE=1 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 \
  artifacts/timestral_reproduction/venv/bin/python \
  artifacts/timestral_reproduction/verify.py
```

| Percorso relativo alla root | Contenuto |
|---|---|
| `artifacts/timestral_reproduction/models/` | Pesi/config/licenze 5M e 28M |
| `artifacts/timestral_reproduction/requirements.lock.txt` | Versioni esatte dell'ambiente locale |
| `artifacts/timestral_reproduction/results/verification.json` | Commit, hash, identità pesi, scarti per colonna e controlli |
| `artifacts/timestral_reproduction/results/metriche.json` | Riesecuzione immutata del report Timestral |
| `artifacts/timestral_reproduction/results/method_comparison.csv` | Baseline, 5M, 28M e CatBoost, entrambi i fold |
| `artifacts/timestral_reproduction/results/interval_diagnostics.csv` | Copertura e ampiezza, anche cold start |
| `artifacts/timestral_reproduction/results/previsioni_28m.csv` | Replica delle 699 previsioni del report 28M |
| `artifacts/timestral_reproduction/results/forecast_candidate_2026-11-16_30.csv` | Candidata separata baseline CTR + 28M CPM, senza modifica alla consegna esistente |
| `artifacts/timestral_reproduction/raw/5m/`, `raw/28m/` | Raw dei due backtest e forecast finale completi |
| `artifacts/timestral_reproduction/catboost/catboost_metrics.json` | Risultati CatBoost iniziali riprodotti |
| `artifacts/timestral_reproduction/results/confronto.html` | Grafici interattivi MAE/WMAE dei quattro metodi |

La cartella `artifacts/` è ignorata da Git: questi file e l'ambiente sono disponibili
su questo PC, ma non fanno parte automaticamente di un nuovo clone. Nessun commit
o push è stato eseguito in questa sessione. Il lock riguarda questo ambiente macOS
arm64; non è una certificazione di portabilità su tutti i sistemi operativi.
