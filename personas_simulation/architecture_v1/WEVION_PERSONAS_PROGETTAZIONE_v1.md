# WEVION — progettazione del SOLO ramo personas · 14 novembre 2026

## A. Le sorgenti del kit ufficiale

Il PDF richiede di **immaginare e motivare i 12 pubblici**, prevedere CTR/CPM **per annuncio e giorno** e suggerire decisioni di budget/creatività. In questa progettazione si sviluppa **solo** il ramo personas e il suo output verso forecasting; il forecasting è autonomo. Il README dice che tutti i dati sono simulati, che il pubblico è sconosciuto e che le creatività sono descrizioni testuali, non file immagine/video.

Gerarchia relazionale:

```
inserzionisti.csv (3)   1 → 1  campagne.csv (3)
                                    |
                                    | 1 → 4
                               adset.csv (12) ─── budget_giornaliero.csv
                                    |
                                    | 1 → N
                               annunci.csv (69) ─── storico_giornaliero.csv
                                    |                  (1.879 righe; 17/08–15/11)
                                    | ogni riga ha asset_id
                                    v
                         asset_creativi/*.csv (36)
                                    └── stesso asset riutilizzato in più ad set

       da_prevedere.csv (699 righe 16/11–30/11) = chiavi degli annunci futuri, NON risultati
       calendario.csv / cpm_storici.csv / benchmark_mercato_settimanale_2025.csv
           = SOLO ANALYTICS/FORECASTING, NON PERSONA WRITER O DECISIONS
```

- Tre campagne **Meta**, obiettivo vendite: `NDL-C1` Nuvola Derma Lab/skincare; `CDF-C1` Coda Felice/pet; `FGR-C1` Filo Grigio/abbigliamento.
- Per ciascuna campagna ci sono quattro ad set `AS1..AS4`, *senza* pubblico noto; ogni ad set raggruppa 5 o 6 annunci.
- In ogni settore: 12 asset distinti = 4 `scarcity`, 4 `urgency`, 4 `black_friday`; formati `immagine`, `video`, `carosello`. 33 asset sono riutilizzati in due ad set, tre in uno soltanto.
- Ci sono 57 annunci già comparsi nello storico, e 12 annunci futuri senza storico (114 righe future), che utilizzano 6 asset nuovi (`B3`, `B4` dei tre settori). Ci sono 51 annunci distinti nel futuro, per 699 righe.
- `NDL-AD01` e `NDL-AD12` **non sono lo stesso annuncio**: sono due annunci in ad set diversi che usano **lo stesso asset** `NDL-S1`.
- `spesa`, `impression`, `click`, `ctr`, `cpm`, `copertura`, `frequenza` sono aggregati per **annuncio e giorno**; non contengono l'età, il genere, gli interessi o l'identità di persone reali.

## B. Cosa possiamo inferire, e cosa no

**Osservabile:** settore, messaggi e format delle creatività, distribuzione in ad set, budget e KPI storici. **Non osservabile:** età, sesso/genere, interessi, classe sociale, professioni e reali criteri di targeting per singolo ad set. Un CTR maggiore per un ad set non dimostra una differenza di genere/età: influiscono molte variabili di delivery, creatività e asta.

Non confondere inferenza del pubblico con creazione delle persone. **L'inferenza dei 12 ad set da CTR e CPM appartiene ad Analytics**, che può vedere lo storico (soltanto il training cut-off). Le sue spiegazioni sono ipotesi, non audience osservate.

Se il requisito è *zero informazioni sui risultati per le personas*, non consegnare alla generazione né le metriche **né un riassunto costruito a partire dalle metriche**: anche la frase “questo pubblico risponde molto a scarcity” è leakage semantico. Per avere comunque 12 ipotesi diverse, Analytics può associare/re-pesare i segnali di un pool generico di persone **dopo** la simulazione (train only). Distinguere **simulation_blind** e **analytics_conditioned**, mai etichettarli entrambi come privi di bias.

## C. Proposta di implementazione: 3 pool, non 12 generatori condizionati

1. `public_context.json`: `vertical`, descrizione generale dell'inserzionista, paese e obiettivo `vendite`, estratti **soltanto da** `inserzionisti.csv` e `campagne.csv`; non leggiamo nulla relativo ai risultati.
2. `persona_slots.json`: 24 persone per settore (72 totali) tramite stratificazione deterministica, età, genere dichiarato, routine d'uso social, propensione allo scetticismo, interessi anche bassi, stile decisionale, contesto economico. Composizione **bilanciata per progetto**, non stimata dai dati degli organizzatori. Nessuna persona conosce il proprio ad set.
3. `persona_cards.json`: Gemini Hydrogen `LOW` amplia ogni slot con dettagli realistici coerenti e contraddizioni. Limitarsi a profili sintetici concisi, non interviste da 12+2 domande per tutti. Conservare seed, provenienza, modello e JSON. Il costo/scalabilità può essere migliorato usando batch di 8–20 persone con validazione per record.
4. `creatives.json`: costruito **separatamente** dai tre CSV sotto `asset_creativi/`; contiene letteralmente headline, testo, CTA, formato, leva e descrizione del visual. Non contiene KPI o ranking. Le descrizioni sono surrogate dell'immagine, non visual originali.
5. `Gemini Decision 1`: un batch per **asset**. Shared input = creatività. Ogni persona è UNA domanda `choice` indipendente sulle combinazioni mutuamente esclusive azione+motivo. I quattro ad set possono riutilizzare la stessa risposta dell'asset. Non sono chiamate a una chat generativa; solo categorie/probabilità.
6. `signal_by_asset.json`: aggrega senza riferimenti a CTR reali. Il team Analytics associa gli asset ad `ad_id/adset_id`, costruisce pesi ipotizzati dei 12 ad set a partire dai soli dati precedenti il cut-off e decide in backtest se usare i segnali per forecasting.

### Nota sui gruppi e sui pesi

Il formato `24 persone/settore` è un **numero di partenza**, non una stima del pubblico reale. La composizione 45% uomo / 45% donna / 10% altro o non dichiarato è un esempio **arbitrario e modificabile**, non qualcosa ricavato dal kit. Potete avere banche di persone diverse per provider (Hydrogen per la maggioranza, altro modello per controlli), ma la stessa persona deve mantenere identità stabile nel confronto tra creatività.

## D. ADERA: cosa conserva, come genera le persone

Fonte: `(architettura interna ADERA)`

### Generazione originale

1. `persona_planner.py::plan_segments` legge i criteri dei segmenti e può generarli automaticamente con un LLM.
2. `demographic_slots()` distribuisce caratteristiche fisse (età, genere, città, reddito, life stage, ecc.) con un seed Python, prima di chiamare un modello.
3. `generate_personas()` decide modalità `full` / `fast`.
4. Modalità `full` -> `_persona_prompt()` produce schede da 150–250 parole; `interview_batch()` realizza 12 domande biografiche, seguite da probe e card decisionale. **Rischio leakage nel nostro caso**: il prompt originale include `requirement` e `context`, può includere una specifica creatività e dati del prodotto, quindi non va riusato senza filtrare gli input.
5. Modalità `fast` -> `_write_fast()` / `fast_population.py::write_cards()` produce schede corte in batch, con interviste complete solo per un campione. Si usano controlli di duplicazione (`fix_duplicates`), pesi (`population_weights`) e cache hash per prompt, modello e provider (`PromptCache`). Il modello genera dettagli, **non decide gli slot demografici**.
6. Provider: backend usa API/provider chat compatibili con OpenAI o CLI gateway di Codex/Antigravity/Claude, tramite `LLM_POOL`, `Caller` e lane/concurrency. L'identità del provider è tracciata per profilo. `LLM_POOL_STRICT=true` evita che un agente sia interpretato da un provider diverso durante il run. Queste sono chiamate di **generazione LLM**, non Decision 1.
7. `feed_test.py` crea feed sintetici, assegna una creatività per persona/piattaforma (`assign`), produce azioni con un prompt generativo (`scroll_prompt`), usa `NOTICE_RATE` e `WEAR_OUT` hardcoded e calcola `expected_ctr` dalla media delle `p_click` dichiarate. Queste ultime **non sono CTR reali**.

### Keep / Adapt / Exclude

| Componenti | Scelta per il nostro ramo | Azione specifica |
|---|---|---|
| `persona_planner.py`: slot e diversità | **KEEP/ADAPT** | Ricostruire slot senza contesto delle creatività; seed deterministico |
| `fast_population.py`: batch, retry, cache, lanes | **KEEP/ADAPT** | Usare Hydrogen per JSON brevi, provider audit e missing-record retries |
| `persona_planner.py`: 12 interviste + probe | **OPTIONAL/LATER** | Non servono per MVP; il rischio di profili molto narrativi non migliora necessariamente la previsione |
| `feed_test.py`: `normalize_creatives`, input per piattaforma, stable habits | **KEEP/ADAPT** | Prendere il contratto ad + persona, sostituire interamente il generatore di feedback |
| `feed_test.py`: `scroll_prompt`, `_llm_json`, `run_feed_test` LLM / feed organico | **REPLACE** | `decision1_adapter.py` con shared creative + domande indipendenti per persona |
| `feed_test.py`: summary metriche | **ADAPT** | Aggregare probabilità solo come segnali sintetici, non CTR/CPM |
| `predict.py`, `calibration.py` | **HANDOFF ANALYTICS** | Non aggiungerli alla runtime personas |
| Social OASIS, knowledge graph, survey SSR/Jev, sales pitch, landing browser | **EXCLUDE** | Non necessari per la richiesta principale Wevion |

Se si copiano fisicamente file o funzioni del repository originale, la licenza **AGPL-3.0** impone obblighi che vanno valutati, soprattutto in caso di distribuzione o servizio in rete. Questo starter contiene codice originale e fa riferimento al comportamento upstream, non incorpora file upstream.

## E. Gemini APIs e feedback

### Gemini 4 Hydrogen

Modello per generare testi, con `thinking_level=LOW`, schema JSON e batch piccoli. Google documenta che Hydrogen ignora `temperature`, `top_k` e `top_p` personalizzati: la diversità deve quindi provenire soprattutto dagli slot e dai prompt, non da un parametro `temperature=0.9`. Limiti e quota della sottoscrizione Antigravity/Gemini non equivalgono automaticamente a una chiave Gemini API.

### Gemini Decision 1

Modello diverso, `gemini-decision-1`, endpoint `client.decisions.create` con `api_version='v1beta'`. Input condiviso per l'annuncio, fino a 1000 domande indipendenti, 2–255 opzioni per `choice`, percentuali/probabilità normalizzate. Non scrive racconti: per un feedback qualitativo il risultato è `reason_code` scelto tra categorie motivate. Se serve una frase nel video, è un **resoconto** costruito a valle dal codice o un LLM narratore che non prende decisioni per le persone. La Decision API è autonoma dai modelli di chat e richiede accesso API specifico; la disponibilità/no-cost tier va controllata sull'account.

Esempio: un'unica domanda per persona `__outcome` con opzioni `scroll__irrelevant`, `scroll__busy`, `glance__visual`, `stop__curiosity`, `click__utility`, `click__offer`, ecc.; sommare le probabilità dei codici con la stessa azione. Il motore restituisce probabilità per **categorie definite da noi**; non sono frequenze reali osservate. Se si vuole un outcome concreto per il video, **campionare** con un seed dal vettore di probabilità dopo il risultato, senza passare una seconda volta dal modello.

### Due accortezze di misurazione

- Una domanda separata su `action` e `reason` non produce motivi condizionati all'azione. Per evitare contraddizioni e dimezzare le domande, qui usiamo le combinazioni `action__reason` come opzioni di un'unica domanda; le probabilità per azione sono somme marginali.
- Le opzioni `scroll/glance/stop/click` assumono una gerarchia di comportamento mutualmente esclusiva solo per questa simulazione: `click` implica necessariamente almeno un minimo di attenzione. Non confondere `glance` con visualizzazioni reali o `stop` con una metrica di view-through ufficiale Meta.

## F. Prova minima e criteri di accettazione

- `prepare_safe_inputs.py` legge **solo** inserzionisti/campagne, mai storico o ads; `make_slots.py` genera 24 slot/settore con seed fisso.
- `build_creative_catalog.py` legge **solo** asset creatives e non recupera KPI.
- `decision1_requests.py` produce una richiesta per asset e una domanda combinata e indipendente per persona, rispettando i 1000 question limit. Un primo live test deve usare quattro personas di un solo settore e `NDL-S1`.
- Risultato atteso: schede persona valide, nessuna exposure a KPI o altre risposte, JSON raw API separato, output di segnale senza etichette osservate. Testare se la stessa persona mantiene scelte coerenti con le sue motivazioni su creatività differenti.

## G. Scambio dati tra team

Il ramo personas pubblica **solo** `persona_cards.json`, `decision_raw.json`, `signals_by_asset.json` e relativi schema/manifest. Analytics pubblica, in un altro spazio, le 12 audience **ipotesi**, i pesi adset condizionati allo storico e le previsioni CTR/CPM. Il ramo personas non può leggere questi risultati. Il team forecast può leggere il ramo personas. Per validare i modelli, il ramo Analytics applica il cut-off storico a *tutte* le sue inferenze e i suoi pesi.

## H. Risorse

- Organizzatori: `Wevion-BigHack-sfida.pdf`, `LEGGIMI.md`, `dati/*.csv` (kit allegato).
- ADERA tecnico: (architettura interna ADERA)
- ADERA provider: (architettura interna ADERA)
- Gemini Decisions: https://blog.google/innovation-and-ai/technology/developers-tools/gemini-decisions-api/
- Gemini 4 Hydrogen: https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/guides/gemini-4-hydrogen
- T3 Code provider/skills: https://github.com/pingdotgg/t3code/blob/main/docs/user/providers-acp.md
