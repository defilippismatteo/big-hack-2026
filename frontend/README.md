# ADERA · Audience & Advertising Intelligence

Checkpoint 1: identità visiva, layout, navigazione e anteprima locale. Le cinque sezioni analitiche sono raggiungibili e indicano quando il contenuto non è ancora disponibile. Questa versione non carica KPI o fixture e non richiede processi Python o credenziali per l'avvio.

## Avvio

Usa Node.js 20.19+ sulla serie 20 oppure 22.12+. Dalla root della repository:

```sh
cd frontend
npm ci
npm run dev
```

Apri http://127.0.0.1:5173. In VS Code usa `Browser: Open Integrated Browser` dalla palette comandi e inserisci l'indirizzo. Il server Vite è locale e aggiorna la pagina quando cambiano i file.

```sh
npm run build
npm run preview
```

La preview della build è su http://127.0.0.1:4173.

## Stack e output esistenti

React gestisce la navigazione e i componenti riutilizzabili; Vite fornisce il server di sviluppo e la build statica. Inter e le icone Lucide sono serviti con l'app. Il ramo di sviluppo è `feat/adera-dashboard`.

Il viewer Python di Market Mirror resta disponibile. Quando verranno collegati i dati, la fonte prevista sono gli artefatti del percorso `python -m market_mirror deliver`: forecast per chiave `(data, ad_id)`, ipotesi pubblico in `persona_adset.json`, scenari in `decisions.csv`, metriche e provenienza in `validation_metrics.json` e `manifest.json`. Il budget appartiene all'ad set; le schede con ipotesi sul pubblico sono distinte dai profili sintetici e dalle reazioni simulate.
