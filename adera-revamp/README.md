# ADERA · Audience & Advertising Intelligence

ADERA esplora i dati del kit simulato Wevion in sei viste. L’avvio usa gli snapshot versionati con il frontend e richiede soltanto Node.js.

## Avvio

Usa Node.js 20.19+ sulla serie 20 oppure 22.12+. Dalla root della repository:

```sh
cd frontend
npm ci
npm run dev
```

Apri http://127.0.0.1:5173. In VS Code usa `Browser: Open Integrated Browser` dalla palette comandi e inserisci l'indirizzo. Il server Vite è locale e aggiorna la pagina quando cambiano i file.

```sh
npm test
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

## Creative Explorer

La mappa e la classifica leggono le previsioni base del giorno selezionato, con il Black Friday come data iniziale. Puoi filtrare per campagna e ad set, cercare per headline, annuncio, asset, leva o formato, ordinare le colonne e scegliere fino a due annunci da confrontare. Il dettaglio usa i testi del catalogo Wevion e le sole date previste per l’annuncio. Il collegamento a Budget Planner trasferisce data, campagna e ad set. Lo script di esportazione include il testo, la CTA e la descrizione visuale degli asset.

## Audience Lab e Budget Planner

Audience Lab mostra le 12 ipotesi per ad set con le evidenze storiche e i collegamenti alle creatività. Il filtro campagna seleziona il settore dei profili sintetici. Per alimentare le reazioni per asset, aggiungi `--simulations ../artifacts/personas_t3/analyses/summary.json` alla rigenerazione e usa un riepilogo Decision del contratto Market Mirror. Le reazioni sono punteggi simulati e le eventuali distribuzioni di età e genere riguardano i profili sintetici.

Budget Planner usa il riferimento Market Mirror e le sue stime di spesa, impression e click. Nello scenario manuale seleziona una campagna e due ad set della stessa campagna. Il valore inserito è uno spostamento in euro per ogni giorno selezionato. Il limite è quello dell’export, con il totale giornaliero invariato e i coefficienti di pacing e pubblicazione fissi.

## Export del ramo pilota

Forecast Analytics consente di confrontare il riferimento Market Mirror, l’export pilota e il relativo scenario stagionale. Le tre serie coprono le stesse 699 coppie annuncio–giorno. L’export pilota da `2e817b282df525ef9ac6635b808d3752d684bdd2` usa la baseline per il CTR e il mix CatBoost–Timestral-28M per il CPM. Nelle timeline il peso è la spesa effettiva stimata e ripartita nell’export principale. Overview, Creative Explorer e Budget Planner usano il riferimento Market Mirror anche quando si esplora la serie pilota.

Model Validation calcola e confronta gli errori sulle righe già prodotte dai modelli. Il confronto usa due finestre storiche e permette di selezionare settore o annunci con e senza storico. I risultati non misurano l’accuratezza durante gli eventi di fine novembre.

Per rigenerare i due snapshot, dalla directory `frontend` con il ref pilota disponibile in Git:

```sh
pilot_ref=2e817b282df525ef9ac6635b808d3752d684bdd2
pilot_files="$(mktemp -d)"
git show "$pilot_ref:Prima_Analisi/Previsioni_Periodo_Vuoto/previsioni_2026-11-16_30.csv" > "$pilot_files/pilot.csv"
git show "$pilot_ref:Prima_Analisi/Analisi_Completa_Black_Friday/previsioni_arricchite_2026-11-16_30.csv" > "$pilot_files/seasonal.csv"
git show "$pilot_ref:Prima_Analisi/Validazione_Modelli/metriche.json" > "$pilot_files/backtest.json"
git show "$pilot_ref:Prima_Analisi/Validazione_Modelli/previsioni_2026-10-19.csv" > "$pilot_files/fold-1.csv"
git show "$pilot_ref:Prima_Analisi/Validazione_Modelli/previsioni_2026-11-02.csv" > "$pilot_files/fold-2.csv"
python3 scripts/export_parallel.py --selected "$pilot_files/pilot.csv" --seasonal "$pilot_files/seasonal.csv" --source-ref "$pilot_ref"
python3 scripts/export_validation.py --metrics "$pilot_files/backtest.json" --folds "$pilot_files/fold-1.csv" "$pilot_files/fold-2.csv" --source-ref "$pilot_ref"
```
