# ADERA · Audience & Advertising Intelligence

ADERA include l’Overview con dati del kit Wevion e navigazione fra le sei sezioni. Le pagine di dettaglio indicano quando i contenuti non sono ancora disponibili. L’avvio non richiede processi Python o credenziali.

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

Il viewer Python di Market Mirror resta disponibile. La fonte dei dati sono gli artefatti del percorso `python -m market_mirror deliver`: forecast per chiave `(data, ad_id)`, ipotesi pubblico in `persona_adset.json`, scenari in `decisions.csv`, metriche e provenienza in `validation_metrics.json` e `manifest.json`. Il budget appartiene all'ad set; le schede con ipotesi sul pubblico sono distinte dai profili sintetici e dalle reazioni simulate.

## Overview · dati e rigenerazione

La vista si avvia con `public/data/overview.json`, uno snapshot riproducibile degli output del kit simulato. Non richiede Python mentre navighi. Mostra lo storico pesato per impression, il forecast base per annuncio/giorno, uno scenario stagionale distinto, le ipotesi per ad set e la riallocazione condizionale. `Top Creative` ordina gli annunci del 27 novembre per clic previsti per euro nella selezione. Il grafico è aggregato sulle impression stimate a budget pianificato; lo scenario stagionale applica l'export centrale del benchmark 2025 mantenendo le quote di pubblicazione. La selezione del grafico non cambia la base usata da `Top Creative` o dallo scenario di budget.

Lo snapshot corrente usa la baseline a 14 giorni di Market Mirror da `2b52a4f01c19bba6f107e0b8a9858aaf57a1672c`. Per riprodurre lo snapshot da una copia Git completa, rigenera gli artefatti senza ref Timestral e proiettali nella cartella pubblica:

```sh
# Dalla root della repository, con l'ambiente Python Market Mirror attivo
python -m market_mirror deliver
cd frontend
python3 scripts/export_overview.py \
  --kit "../info fornite dagli organizzatori /dati" \
  --artifacts ../artifacts/wevion_v4 \
  --source-ref "$(git rev-parse HEAD)"
```

Per collegare un export T3 aggiungi `--personas ../artifacts/personas_t3/persona_cards.json`: il JSON pubblico conserva solo numerosità aggregate, senza nomi o singole schede. Senza il file, il KPI dei profili e i segmenti demografici risultano non disponibili. Le ipotesi comportamentali rimangono consultabili.
