# Persone, feed e Decision: orchestrazione T3

Questa è l'architettura confermata dall'utente. Sostituisce il precedente writer
via Google API. La pipeline forecasting e l'unione con Timestral restano separate.

1. **Python:** costruisce slot per settore con seed fisso, senza CTR o risultati.
2. **T3 → subagente Gemini/Antigravity:** scrive i profili usando l'abbonamento.
3. **Python:** valida, congela, salva e visualizza le schede del run effettivo.
4. **Python:** costruisce feed e richieste con un solo profilo per domanda.
5. **T3 → subagente Decision worker:** verifica il piano e chiama l'API Decisions.
6. **Python:** conserva raw e segnali; nessuna integrazione col forecast in questa fase.

## Quantità e randomizzazione

Default: **24 persone per settore, 72 totali**, seed 2026. Sei fasce: 18–24,
25–34, 35–44, 45–54, 55–64, 65+. Età esatta campionata uniformemente entro
fascia; per il gruppo 65+ il limite progettuale è 80 anni, modificabile.
Le fasce hanno quote bilanciate; genere 45% donna / 45% uomo / 10% non binario
o non dichiarato, arrotondate a conteggi interi. Sono quote manuali, non stime
demografiche. Motivazioni, uso social, rischio e interesse vengono distribuiti
e mescolati con seed stabile. L'interesse include basso, medio e alto.

Gemini non sceglie l'età e non modifica gli slot. Aggiunge nome fittizio,
3–8 interessi anche esterni alla categoria, professione, contesto economico,
routine/occasioni, decisioni, fiducia, scetticismo, timori e contraddizione.
I primi quattro profili servono a provare il percorso, non sono un campione
rappresentativo di tutte le fasce. Il seed rende ripetibili gli slot; il testo
del modello non è garantito deterministico e viene perciò salvato e riusato.

## Job e prompt riutilizzabili

```bash
source .venv-market-mirror/bin/activate
python -m market_mirror t3-prepare
```

In `artifacts/personas_t3/`:

- `ORCHESTRATE.md`: prompt per far gestire i passaggi al coordinatore T3.
- `jobs/*.prompt.txt`: testo effettivo da passare a ciascun nuovo subagente Gemini.
- `jobs/*.json`: slot, settore e contratto di risposta con hash.
- `safe_inputs/`: contesto e slot originali.

La preparazione crea 18 job da quattro schede. Non ne esegue automaticamente 18:
il primo test usa soltanto `beauty_skincare-01`. La delega usa provider
`antigravity`, modello `gemini-4-hydrogen`, opzione `thinking_level=low`.
Non vi è una chiamata `models.generate_content`. Non sostituire il provider
se non è disponibile. Nessuna chiave Google è richiesta per scrivere le persone.

Il figlio riceve il solo prompt inline, senza storia del coordinatore; deve
rispondere con JSON e non leggere file o usare strumenti. Un batch writer vede
gli slot del proprio batch per diversificare le biografie. I giudizi successivi
sono invece indipendenti per persona. Le istruzioni di non lettura non sono
permessi OS: la delega condivisa non è una sandbox filesystem.

## Import e schede

Il coordinatore salva la risposta JSON e una ricevuta ricavata dal risultato
T3 con `taskId`, `link`, `providerInstanceId`, `executedModel`; il modello non
autocertifica quale provider sia stato usato.

```bash
python -m market_mirror t3-import --job artifacts/personas_t3/jobs/beauty_skincare-01.json --response artifacts/personas_t3/responses/beauty_skincare-01.json --receipt artifacts/personas_t3/responses/beauty_skincare-01.receipt.json
python -m market_mirror personas-view
```

L'import rifiuta job alterati, record mancanti/duplicati, campi KPI o modifiche
agli attributi assegnati. Le schede hanno schema 2.0 e provenienza `t3:antigravity`.
I vecchi template di smoke restano `mock_not_model` e non sono risultati Gemini.
Il viewer è un HTML standalone; non genera nulla e non chiama API.

## Feed e worker Decision

I feed attuali sono testuali e controllati: tre post neutri fissi più un annuncio
descritto dagli organizzatori. Non sono immagini/video originali né un motore
che replica l'algoritmo Meta. Posizione, piattaforma e ora dipendono dal seed e
dall'identità; restano stabili nel confronto tra creatività.

```bash
python -m market_mirror plan --personas artifacts/personas_t3/persona_cards.json --asset-id NDL-S1 --n 4 --out artifacts/personas_t3/decision_plan.json
python -m market_mirror personas-view --plan artifacts/personas_t3/decision_plan.json
```

Il coordinatore delega il task di `docs/prompts/decision-worker.md` a un nuovo
subagente. Solo questo worker avvia il comando Python che usa l'API Decisions.
La singola domanda contiene soltanto la propria persona e il proprio feed;
l'input condiviso contiene la sola creatività. Non sono visibili altre schede,
risposte, KPI, ranking o forecast. Probabilità per azione/motivo, non CTR misurati.

Il preflight non usa rete o token Decisions. Per il live serve la chiave
`GEMINI_API_KEY` locale **esclusivamente per Decision 1**: abbonamento e accesso
a quella API sono distinti. Non scrivere il segreto nel task o nella ricevuta.

```bash
python -m market_mirror decide --preflight --plan artifacts/personas_t3/decision_plan.json --out artifacts/personas_t3/decision_preflight.json
# Solo nel worker Decision e con chiave disponibile:
python -m market_mirror decide --live --plan artifacts/personas_t3/decision_plan.json --out artifacts/personas_t3/decision_raw.json
python -m market_mirror aggregate --plan artifacts/personas_t3/decision_plan.json --raw artifacts/personas_t3/decision_raw.json --out artifacts/personas_t3/signals.json
```

Niente fallback inventato in caso di accesso o quota insufficienti. La presenza
dei feed e la validazione locale non garantiscono l'esito o la qualità dell'API.
