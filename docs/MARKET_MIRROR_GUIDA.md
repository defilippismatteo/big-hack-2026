# Market Mirror per Wevion: struttura e primi passi

**Architettura personas aggiornata:** [T3/Antigravity → schede → worker Decision](PERSONAS_T3.md).
La generazione via Google API e i precedenti comandi `personas --live` sono
superati: le persone sono scritte dai subagenti tramite l'abbonamento; soltanto
Decision 1 usa la sua API. Il task corrente non comprende l'unione con Timestral.


Stato verificato il 14 novembre 2026. La fonte progettuale è la specifica v4.
Il percorso principale è ora **forecast → pubblici motivati → decisioni → viewer**.
La simulazione di persone con Hydrogen/Decision 1 è P4 opzionale.

## 0. Prima la consegna v4

```bash
source .venv-market-mirror/bin/activate
python -m market_mirror deliver --timestral-ref origin/feat/timestral-pilot
python -m unittest discover -s tests -v
```

Apri `artifacts/wevion_v4/viewer.html`: non richiede server, API Google o T3 aperto.
Il comando produce una consegna candidata, ancora da validare completamente:

| File | Contenuto |
|---|---|
| forecasts_2026-11-16_30.csv | 699 chiavi esatte con CTR/CPM, metodo e cold start |
| persona_adset.json | 12 ipotesi comportamentali con evidenze e alternative |
| decisions.csv | 180 scenari adset/giorno, budget, pacing e creatività consigliata |
| ad_delivery.csv | Quote che ripartiscono la spesa dell'ad set, senza duplicarla |
| validation_metrics.json | Baseline rieseguita localmente e metriche Timestral importate |
| seasonal_scenarios.csv | Tre ipotesi di pressione dal benchmark 2025 del kit |
| data_quality.json | Anomalie segnalate, inclusa spesa oltre budget |
| manifest.json | Versione codice, commit sorgente, hash input e lavoro residuo |
| README.md e viewer.html | Ragionamento, esplorazione e download |

L'import usa soltanto il ref Git già disponibile localmente; per aggiornare
consapevolmente gli export si aggiorna prima il ref. Il commit risolto è salvato:
un movimento successivo del branch non cambia la provenienza del pacchetto.
Nessun checkout o merge del ramo parallelo. Senza `--timestral-ref`, `deliver`
produce una baseline pesata a 14 giorni e i suoi backtest senza scaricare modelli.

La selezione attuale confronta solo baseline e Timestral sul **primo fold WMAE**,
separatamente per target. Nel commit 2d8adf0 sceglie baseline CTR e Timestral-28M CPM.
CatBoost non è ancora incluso nel confronto: non dichiarare il metodo vincitore
finale. Le metriche del secondo fold servono a verificare, non a ritarare la regola.

Il motore budget conserva il totale per campagna/giorno entro ±20% per ad set.
Stima pacing come mediana degli ultimi 14 giorni, escludendo dalla sola stima i
giorni di overspend e segnalandoli. Le quote di delivery sono 90% proporzionali
alla spesa storica degli annunci attivi + 10% uniformi per esplorazione; se non
c'è storia sono uniformi. Sono assunzioni, non una replica dell'algoritmo Meta.
CTR/CPM del gruppo derivano dal mix di spesa/impression previsto, non dalla media
semplice degli annunci. Non sono previsti acquisti o ricavi senza conversioni.

I tre scenari stagionali partono dalla baseline14d e applicano il rapporto tra
indice 2025 futuro e indice 2025 del periodo storico, allineato di 364 giorni:
forza 0,5 / 1 / 1,5, scelte ex ante. Sono un'analisi di sensibilità separata dal
forecast centrale adottato e non vengono moltiplicati di nuovo sul CPM Timestral.
Non sono quantili o intervalli calibrati; high_pressure non promette più click.

**Ordine da ora:** confronto CatBoost e selezione → calibrazione e ranking →
revisione delle 12 ipotesi → revisione degli scenari → video di 180 secondi.
Traccia in `docs/VIDEO_180S.md`. Il pool di persone e Decision 1 vengono dopo.

## 1. Come si collegano le cartelle

| Percorso | Ruolo e scelta corrente |
|---|---|
| `BigHack2026_Wevion_Specifica_Operativa_v4.md` | Specifica della challenge aggiornata: forecast, 12 pubblici ipotizzati e decisioni |
| `Specifica_Operativa_v3.md` | Versione precedente, da leggere tenendo presenti le correzioni v4 |
| `info fornite dagli organizzatori /` | Kit sorgente: CSV sintetici e brief. Il nome della cartella termina con uno spazio |
| `Wevion_Personas_Skill_Starter/` | Prima proposta: persone condizionate da audience inferite. Le sue skill non sono runtime |
| `Wevion_Personas_Architettura_v1/` | Proposta successiva: pool indipendenti per settore. Riutilizziamo i preparatori Python di questa versione |
| `.agents/skills/` | Istruzioni canoniche aggiornate ai comandi attuali; le copie nei pacchetti sono riferimenti storici |
| `market_mirror/` | Pipeline v4 e viewer; moduli feed/Decisions come estensione opzionale |
| `artifacts/market_mirror/` | File generati, ignorati da Git; nessuna chiave al loro interno |
| `feat/timestral-pilot:Test_Timestral/` | Ramo forecasting separato; non presente in questo checkout main |
| `TEST INIZIALI FATTI DA CHAT GPT DA VERIFICARE /` | Baseline/CatBoost e metriche preesistenti, non risultati Timestral |

Le due architetture personas **non sono equivalenti**. Lo starter permette a
ipotesi derivate dallo storico di entrare nei profili: anche senza numeri, questo
trasmette informazioni sui risultati. La scelta attuale è `simulation_blind`:
nessuna ipotesi Analytics arriva al generatore. Se in futuro serve un esperimento
`analytics_conditioned`, va etichettato e confrontato separatamente.

## 2. Skill, modelli e motore sono tre cose diverse

Una skill è un file `SKILL.md` che istruisce il coding agent su input, procedura,
output e verifiche. Non è un processo in esecuzione, non crea automaticamente una
persona e non applica permessi filesystem. Il modello scrive o valuta; Python
prepara gli input e conserva risultati e provenienza; T3 Code coordina i passi.

| Skill canonica | Responsabilità | Implementazione corrente |
|---|---|---|
| `audit-marketmirror` | Selezionare cosa adattare dall'originale | Audit descritto sotto |
| `wevion-persona-diversity` | Slot diversi con seed e quote dichiarate | `prepare`; preparatore v1 |
| `wevion-persona-writer` | Arricchire gli slot senza vedere annunci | `personas.py`, endpoint generativo Hydrogen |
| `wevion-decision1` | Feed individuali e reazioni a una creatività | `feed.py`, `providers.decide` |
| `wevion-persona-signals` | Validare e aggregare probabilità | `signals.py` |
| `wevion-evidence` | Evidenze per ad set fino al cutoff | analytics.evidence, invocato da deliver |
| `wevion-audience-inference` | 12 ipotesi motivate sui pubblici | analytics.audiences: prima regola deterministica da rivedere |
| `wevion-signal-validation` | Ablation forecast-only / forecast+segnali | Da costruire sul lato Analytics |
| `wevion-persona-explain` | Spiegazione con fonti e alternative | README e viewer prodotti da deliver |
| `wevion-delivery` | Verifica consegne e provenienza | delivery, forecast, marketing e viewer |

Le skill vecchie `wevion-persona-generation`, `wevion-creative-packets` e
`wevion-decision-simulation` non vanno installate in parallelo: sono sostituite
rispettivamente da diversity+writer, preparazione catalogo e decision1.
T3 espone le skill comunicate dal provider: i file sono stati preparati nel
progetto, ma la loro comparsa nel menu va verificata nella sessione/provider usati.
L'esecuzione dei comandi funziona anche senza menu `$`.

## 3. Estensione P4: come nasce una persona

1. `prepare_safe_inputs.py` legge esclusivamente descrizioni di settore e
   obiettivo da inserzionisti/campagne. Non legge storico o creatività.
2. `make_slots.py` costruisce 24 slot per ognuno dei 3 settori: **72 persone**.
   Fissa età, genere, motivazione, abitudini social, rischio e interesse basso/medio/alto.
   Sono quote manuali per esplorare diversità, non demografia ricostruita.
3. Il writer vede **un solo slot e il settore generale**. Hydrogen aggiunge
   occupazione, contesto economico, routine, fiducia, scetticismo e contraddizione.
   Gli ID e i pesi vengono mantenuti dal codice, non riscritti dal modello.
4. Si valida la scheda e la si conserva con seed, modello, provider e input hash.

Il seed rende ripetibili gli slot e la costruzione dei feed. Non garantisce che
due chiamate generative Google producano lo stesso testo: per confronti paired
si riusano le stesse schede già salvate. In questo MVP non ci sono cache persistente,
retry per singolo record o generazione batch massiva: prima si verifica il probe.
Le schede offline sono template esplicitamente `mock_not_model`.

Tre pool di personas e dodici audience sono oggetti diversi: i primi sono persone
fittizie indipendenti; le seconde sono ipotesi sul pubblico dei 12 ad set, costruite
da Analytics e motivate con evidenze, alternative e incertezza.

## 4. Che cosa vede ciascuno

| Attore | Input visibili | Input esclusi dal payload |
|---|---|---|
| Coding agent coordinatore in T3 | Repository e istruzioni di sviluppo | Non è un worker isolato: può leggere il kit |
| Writer Hydrogen | Un settore generale + un singolo slot | Creatività, adset, storico, pubblici inferiti, previsioni |
| Persona nella domanda Decision 1 | Proprio profilo, proprio feed, creatività condivisa del solo asset assegnato | Altre schede, altre domande/risposte, altre creatività, storico, budget, forecast, pesi Analytics |
| Aggregatore Python | Piano locale, pesi manuali, probabilità raw | Non consulta lo storico e non interroga LLM |
| Analytics / Timestral | Storico entro cutoff, calendario/budget noti, segnali esportati | Outcome dopo cutoff durante training/calibrazione |
| Spiegazione/demo | Risultati pubblicabili, prove, ipotesi e segnali | Non può correggere le predizioni attraverso la narrazione |

Nel payload Google l'**input condiviso contiene soltanto la creatività**;
ciascuna domanda contiene solo la propria persona e il proprio feed. Google
documenta le domande Decisions come isolate. L'associazione question_id →
persona_id/asset_id/peso resta nel piano locale: tutti i profili non vengono mai
inseriti insieme nell'input condiviso. La durata video resta solo un dato testuale.

Le allowlist sono applicate ai campi strutturati. Non costituiscono una difesa
da contenuti arbitrari inseriti a mano dentro campi testuali: conservare i safe
inputs prodotti dalla preparazione ed esaminare i profili prima dei probe.
Per garanzia di accesso ai file serve un processo/container separato. Le skill
o un generatore scritto direttamente dalla chat T3, già esposta al repository,
non garantiscono da sole l'indipendenza informativa.

## 5. Feed e interazioni: originale e nuovo scheletro

Upstream verificato in lettura: `DarkWorldCoder/market-mirror`, branch main,
`backend/app/services/persona_planner.py`, `fast_population.py`, `feed_test.py`,
`docs/PROVIDERS_AND_SCALE.md`, `docs/HUMAN_BEHAVIOR_RESEARCH.md`, `LICENSE`.
Sono sorgenti remoti consultati il 14/11, non una versione upstream fissata nel progetto.

| Originale: file/funzione | Adattamento |
|---|---|
| `persona_planner.demographic_slots`, `generate_personas` | Manteniamo l'idea di slot deterministici e identità stabile; usiamo il preparatore locale |
| `persona_planner._persona_prompt`, `_write_fast`, `fast_population.write_cards` | Schede concise; nessun contesto dell'annuncio nel writer. Interviste estese escluse |
| `fix_duplicates`, `population_weights` | ID unici verificati; pesi manuali. Deduplica semantica/stereotipi e pesi di pubblico reali non implementati |
| `feed_test.organic_pool`, `assign`, `render_item`, `scroll_prompt` | Feed testuale controllato costruito da Python; assegnazione per settore e profilo individuale |
| `feed_test.run_feed_test` | Sostituito dal piano locale e dall'endpoint Decisions |
| `NOTICE_RATE`, `WEAR_OUT`, ondate con social proof | Esclusi dal primo scenario; non imponiamo un tasso di attenzione non misurato |
| `_metrics.expected_ctr`, proiezioni economiche | Esclusi: esportiamo intenzione simulata, non CTR né ricavi |
| OASIS, grafo, survey, scraping, landing browser | Fuori dal primo prototipo |

L'originale può generare pool di post organici, mescolare annunci, ripetere
esposizioni e mostrare nelle ondate successive contatori/commenti delle reazioni
precedenti. La visibilità quindi cambia con le opzioni del run.
Questo scheletro ha un solo scenario: **3 post neutri fittizi + 1 sponsorizzato,
una sola esposizione**. Nessun commento, condivisione, contagio sociale, landing
o conversazione tra personas. Le azioni sono `scroll`, `glance`, `stop`, `click`.

Si può aggiungere un feed più ricco dopo il probe, con contesto organico
congelato e test paired. Esposizioni ripetute, memoria e social proof cambiano
l'esperimento: vanno versionati come nuovi scenari, senza introdurre reazioni
altrui nel percorso corrente. Non è una simulazione dell'algoritmo reale Meta.

Il kit non include immagini o video originali. Tutto il feed è **testuale**:
`descrizione_visual` non equivale a visione del contenuto. Il prototipo non copia
codice upstream AGPL-3.0, ma riusa gli script dello starter locale fornito.

## 6. API Google e variabili d'ambiente

Confermato con l'utente: il modello richiesto è **Gemini Decision 1**.
Il writer usa `gemini-4-hydrogen` con thinking `LOW`; le reazioni usano
`gemini-decision-1` tramite `client.decisions.create`, API `v1beta`.
Sono due endpoint distinti. Le API richiedono una chiave Google AI Studio e
accesso/quota del progetto; la presenza di un provider in T3 non prova l'accesso API.

La chiave va in **`.env` nella root**. Il file `.env.example` contiene il modello
di configurazione. `.env` è ignorato da Git; il CLI lo carica automaticamente
con python-dotenv. Variabili già esportate nella shell hanno precedenza.

```dotenv
GEMINI_API_KEY=la_tua_chiave
MM_PERSONA_MODEL=gemini-4-hydrogen
MM_DECISION_MODEL=gemini-decision-1
MM_SEED=2026
WEVION_DATA_DIR="info fornite dagli organizzatori /dati"
MM_FORECAST_CSV=/percorso/outputs/forecast_2026-11-16_30.csv
```

Non inserire chiavi nelle skill, nei prompt o nei JSON di risultato.
Il client usa esplicitamente la Gemini Developer API (`vertexai=False`), timeout
di 60 secondi e un solo tentativo. Errori di permessi/quota non causano fallback
a modelli diversi. La struttura della richiesta e della risposta è stata
verificata con **google-genai 3.3.0**, senza eseguire chiamate live.

La risposta ufficiale è `answers[question_id]` con `type=choice`, `choice`,
`probabilities` e `confidence`. La confidence è la probabilità della scelta
vincente: **non** certifica accuratezza del CTR né fedeltà a esseri umani reali.
Le domande usano categorie congiunte `action__reason` per evitare motivi
incoerenti con l'azione. Le marginali sono somme calcolate dal codice.

Per asset: `attention_signal=1-P(scroll)` e `click_intent_signal=P(click)`.
Non sono CTR. La distribuzione motivi riflette categorie scritte da noi.
La scelta campionata per animare la demo è separata dalle probabilità raw.
Risposte mancanti, massa non valida o hash diverso fanno fallire l'aggregazione.

## 7. Procedura opzionale P4 per le API, dalla root

**Passo 1 — ambiente e primo giro offline.** L'ambiente `.venv-market-mirror` è
già stato creato in questa sessione; questi comandi lo rendono ricostruibile.

```bash
python3 -m venv .venv-market-mirror
source .venv-market-mirror/bin/activate
python -m pip install -r requirements-market-mirror.txt
python -m market_mirror doctor
python -m market_mirror smoke
python -m unittest discover -s tests -v
```

`smoke` non chiama modelli, anche se esiste una chiave. Produce contesto sicuro,
72 schede template, catalogo di 36 asset, piano per NDL-S1 × 4 persone, raw fixture
e segnali fixture. Le probabilità mock sono costanti e non dipendono dalla qualità
dell'annuncio: servono soltanto a verificare il collegamento dei componenti.
Se requirements non sono installati, il percorso offline funziona con la sola
libreria standard finché non esiste `.env`; con `.env` serve python-dotenv.

**Passo 2 — configurazione.** Apri `.env` nella root e imposta GEMINI_API_KEY.
Se ricrei il progetto e `.env` non esiste, copia `.env.example` in `.env`.
`doctor` mostra presenza della chiave e nomi modello, senza stampare il segreto
o verificare quota/accesso remoto.

**Passo 3 — primo writer live: 4 schede dello stesso settore.** Salviamo le
prove live in file separati per non sovrascrivere le fixture dello smoke.

```bash
python -m market_mirror prepare
python -m market_mirror personas --live --vertical beauty_skincare --limit 4 --out artifacts/market_mirror/personas/live_cards.json
```

Sono 4 chiamate generative, una per slot. Leggi le schede: routine, contraddizioni,
diversità e assenza di informazioni su annunci/campagne. Il piccolo campione è
un probe tecnico; le prime quattro schede non sono una popolazione rappresentativa.

**Passo 4 — prima decisione live: 1 asset × 4 persone.**

```bash
python -m market_mirror plan --personas artifacts/market_mirror/personas/live_cards.json --asset-id NDL-S1 --n 4 --out artifacts/market_mirror/decision_inputs/live_plan.json
python -m market_mirror decide --live --plan artifacts/market_mirror/decision_inputs/live_plan.json --out artifacts/market_mirror/decisions/live_raw.json
python -m market_mirror aggregate --plan artifacts/market_mirror/decision_inputs/live_plan.json --raw artifacts/market_mirror/decisions/live_raw.json --out artifacts/market_mirror/signals/live_signals.json
```

`live_plan.json` è ispezionabile prima dell'invio. `live_raw.json` conserva la
risposta effettiva dentro `response`, con provenienza e hash fuori dal payload
originale. `decide` senza --live produce solo fixture. Il percorso live rifiuta
schede mock. Il limite iniziale di 4 persone è applicato anche dal CLI.

**Passo 5 — confronto paired.** Riusa `live_cards.json`, stesso seed e stesso
scenario su un altro asset dello stesso settore, cambiando i nomi dei file.
Confronta raw e motivi: identità e feed devono restare stabili. Non rigenerare
persone tra due creatività. Prima di salire a 24 per settore rivediamo il probe
e sostituiamo il limite tecnico iniziale con batching/cache/ripartenza per record.
A regime, 36 asset × 24 persone = 864 domande, raggruppabili in 36 richieste
Decisions. La stessa risposta di un asset può servire a più ad set; è Analytics
a distinguere i pubblici con evidenze/pesi, non il worker persona.

**Passo 6 — unione con Timestral.** Nessun merge del ramo è necessario per leggere
un CSV già esportato dal checkout/ambiente del forecasting:

```bash
python -m market_mirror join --forecast /percorso/outputs/forecast_2026-11-16_30.csv --signals artifacts/market_mirror/signals/live_signals.json
```

Il join verifica tutte le chiavi del file `da_prevedere.csv` e il mapping asset/adset,
controlla CTR/CPM finiti, aggiunge colonne di spiegazione e lascia i forecast identici.
Asset non ancora simulati hanno `simulation_status=not_run` e segnali null.
Fixture rifiutate. Non è ancora una calibrazione o un ensemble.

## 8. Isolamento del runtime, se serve una garanzia sui file

Le proiezioni evitano invii accidentali ai modelli. Il processo Python locale
ha comunque i permessi dell'utente. `Dockerfile.market-mirror` costruisce un
worker con solo codice, senza kit/forecast/.env. Per esempio, dopo `prepare`:

```bash
docker build -f Dockerfile.market-mirror -t market-mirror-worker .
docker run --rm --network none --mount "type=bind,src=$PWD/artifacts/market_mirror/safe_inputs,dst=/inputs,readonly" --mount "type=bind,src=$PWD/artifacts/market_mirror/personas,dst=/out" market-mirror-worker personas --inputs /inputs --out /out/container_cards.json
```

Questo è un esempio offline con input montati esplicitamente. Per writer live
abilitare la rete e passare solo GEMINI_API_KEY (per esempio `--env GEMINI_API_KEY`
dalla shell già configurata), mantenendo gli stessi mount. Per Decisions montare
solo il piano validato e una directory output. Non montare il repository intero,
la cartella audit, lo storico o il forecast. Il container non è stato costruito
o eseguito in questa sessione; il Dockerfile è una predisposizione.

## 9. Stato aggiornato del branch Timestral

Dopo la prima verifica il ramo remoto è avanzato a
`2d8adf033e747e147c401246c07ce656f9f1cfb7`. Contiene ora `Prima_Analisi/` con
`metriche.json`, `previsioni_28m.csv`, `previsioni_5m.csv`, script e README.
Questo supera la precedente osservazione di assenza di risultati versionati.

Ho letto sorgenti e metriche e validato le 699 chiavi dell'export importato.
Non ho rieseguito i pesi Timestral in questa sessione. Il pacchetto conserva uno
snapshot CSV e il commit, distinguendo inferenza importata da baseline locale.
Il confronto adset-level nel nuovo analisi.py aggrega correttamente i target;
corregge il precedente problema di etichettatura della valutazione diretta.

I risultati importati sostengono la combinazione baseline CTR / Timestral CPM
tra i due candidati del pilot. La selezione è congelata sulla WMAE del primo fold.
Il fold 02–15/11 conferma la direzione per entrambi i target; non misura però BF.
Il confronto CatBoost e la calibrazione degli intervalli restano aperti.
I quantili del CSV sorgente restano esplorativi: non li rinominiamo intervalli
calibrati nel CSV di consegna. Fonti pubbliche citate nel branch non vengono
utilizzate al posto dei benchmark stagionali del kit per questo prototipo.

## 10. Organizzazione coerente con la v4

T3 Code coordina sviluppo, verifiche, confronto degli export e narrazione.
La pipeline Python resta eseguibile senza una sessione chat o una chiave Google.
Il viewer legge risultati precomputati incorporati nell'HTML.

- **P0:** baseline, CatBoost, backtest cronologici e 699 righe corrette. Baseline
  e import sono operativi; confronto CatBoost da completare.
- **P1:** integrare Timestral se utile, preservando metodo, commit e metriche.
  Export disponibile e collegato; inferenza non rieseguita qui.
- **P2:** dodici pubblici motivati e scenari budget/creatività. Prima versione
  operativa, con alternative e assunzioni da rivedere.
- **P3:** viewer, README e video da 180 secondi. Viewer e documenti generati;
  video ancora da registrare e verificare.
- **P4:** pool personas, Decision 1, nuove creatività e ablation dei segnali.
  Non devono rallentare P0–P3 né sostituire i forecast numerici.

Per il fold 02–15/11 evidenze e ipotesi si fermano al 01/11; deliver pubblica anche
le versioni per i cutoff dei fold. Nel forecast 16–30/11 il cutoff è il 15/11.
La demografia resta non identificabile. Le ipotesi iniziali usano ranking di CTR
per leva/formato, quindi espongono anche la confusione possibile con asset,
periodi e delivery; non sono segmenti certi o scoperte causali.

## Fonti e verifiche

- [Google Decisions API](https://aistudio.google.com/docs/decisions-api): SDK >=3.2,
  choice, isolamento domande, schema answers, limiti 1000 domande/255 opzioni.
- [Annuncio Google dell'11/11/2026](https://blog.google/innovation-and-ai/technology/developers-tools/gemini-decisions-api/).
- [Gemini 4 Hydrogen](https://ai.google.dev/gemini-api/docs/models/gemini-4-hydrogen)
  e [guida thinking/API](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/guides/gemini-4-hydrogen).
- [MarketMirror](https://github.com/DarkWorldCoder/market-mirror), sorgenti elencati sopra.
- [T3 provider e skill](https://github.com/pingdotgg/t3code/blob/main/docs/user/providers-acp.md).
- Fonti locali: LEGGIMI degli organizzatori, architettura personas v1,
  specifica v4, branch Timestral al commit indicato e baseline JSON preesistente.

Test del runtime: 27 casi passati, inclusi confini dei payload opzionali,
backtest past-only, 699 chiavi/cold start, audience con alternative, conservazione
budget e quote delivery. Nessuna inferenza Google o Timestral reale rieseguita
qui; gli export Timestral provengono dal commit riportato nel manifest.
Nessun commit o push effettuato da questa sessione.
