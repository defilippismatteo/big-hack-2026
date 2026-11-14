# ADERA · Motion kit

Tre scene originali in SVG nativo, riutilizzabili nella dashboard e nel video demo. Il riferimento visivo è il loop indicato dall’utente: https://github.com/DarkWorldCoder/market-mirror/blob/main/docs/images/marketmirror-loop.svg. Disegni, layout, testi e keyframe sono stati scritti per ADERA; non è stato copiato codice MarketMirror.

## File pronti

- `01-routing.svg`: costruzione indipendente del pool e invio dell’annuncio ai profili del suo settore.
- `02-decision.svg`: Chiara Bellini / FGR-U3, quattro probabilità aggregate dai 12 esiti azione-motivo di Decision 1.
- `03-interview.svg`: ri-esposizione qualitativa dello stesso profilo, con estratti letterali dell’intervista registrata.
- `*.poster.svg`: stesse scene complete, senza movimento.
- `studio.html`: studio offline con tre scene, pausa, riavvio, cursore temporale, velocità e modalità video. Esc esce dalla modalità video. Aprilo direttamente, senza server.
- `case.json`: caso, probabilità, frasi, modello/provider dichiarati e hash dei file sorgente.
- `brand-sources.json` e `brands/`: loghi originali e rispettive fonti.
- `video/` e `posters/` nel pacchetto ZIP: clip MP4 Full HD e poster PNG.

Le scene hanno canvas 1600×900, rapporto 16:9 e ciclo di 12 secondi. Gli SVG possono essere ingranditi senza perdere definizione. Le clip sono 1920×1080, H.264, 24 fps, 12 secondi ciascuna, senza audio, con sfondo chiaro. Le percentuali e le qualificazioni sintetiche restano visibili nel montaggio. La durata è editoriale: non rappresenta il tempo impiegato da un’API.

## Cosa rappresentano i dati

Il profilo è sintetico. Il suo hash è identico nella scheda, nella valutazione Decision e nel job di intervista. L’annuncio è una descrizione testuale del kit, non un’immagine realmente vista dal modello.

Le probabilità registrate, arrotondate a un decimale, sono: scorre oltre 46,7%; occhiata 26,2%; si sofferma 17,0%; apertura 10,1%. Le quattro azioni sommano le rispettive coppie azione-motivo; P(apertura) somma offerta, utilità e informazioni. Non confondere il 10,1% con un CTR misurato/calibrato sulla popolazione umana, né con la confidence della singola coppia scelta. Non viene animata una misurazione pubblicitaria reale.

Le frasi nella terza scena sono estratti letterali, con ellissi, della risposta sintetica registrata. L’intervista non vede le probabilità Decision. Il suggerimento finale è uno spunto di test interpretativo, non una spiegazione causale dell’esito. Non sono state chiamate API generative o Decisions per produrre questi asset.

I percorsi separati nel diagramma indicano la proiezione dei payload e le istruzioni di visibilità; non attestano una sandbox filesystem del sistema operativo. Il writer dei profili non riceve creatività, storico, audience inferite o forecast. Il quantitativo resta un ramo distinto.

## Loghi e font

T3 Code: SVG originale dal repository ufficiale `pingdotgg/t3code`, `assets/prod/logo.svg`.

Gemini: SVG vettoriale ufficiale Google servito da `https://www.gstatic.com/images/branding/productlogos/gemini/v1/192px.svg`. Si usa il marchio Gemini accanto all’etichetta `Gemini Decision 1 / Decisions API`: non viene inventato un logo autonomo per l’API. I percorsi e i colori dei marchi sono conservati; gli ID interni dei gradienti vengono prefissati soltanto per evitare collisioni nel documento.

I marchi appartengono ai rispettivi titolari. Inter è incluso come font vettoriale WOFF2; licenza in `Inter-LICENSE.txt`. Tutte le scene sono prive di `<image>`, immagini raster, script, foreignObject o dipendenze remote. Lo studio HTML usa invece JavaScript per i controlli. È presente un fallback statico per `prefers-reduced-motion`.

## Uso nella dashboard

La copia ADERA contiene la pagina `#/process`, “Come funziona”, e un collegamento dalla Panoramica. In `src/motion/MotionStudio.jsx` gli SVG sono inseriti inline per consentire pausa e avanzamento con Web Animations. `src/motion/scenes.js` è generato, non va corretto manualmente. Le versioni autonome possono essere incorporate con `<img src="motion/02-decision.svg" alt="...">`; per controlli interattivi usare il componente o lo studio.

## Rigenerazione nel repository

Dalla root, con l’ambiente Market Mirror:

```sh
.venv-market-mirror/bin/python adera-revamp/scripts/build_motion.py
```

Lo script legge soltanto gli artefatti esistenti, controlla gli hash persona, la provenienza e la somma delle probabilità, quindi salva SVG, dati della scena e studio. Non avvia inferenza. Non contiene chiavi o header API.

Esportazione video, dalla copia frontend:

```sh
npm install --prefix /tmp/adera-motion-runtime playwright-core
node scripts/export_motion.mjs --runtime /tmp/adera-motion-runtime
```

Serve FFmpeg e Chrome; il percorso di Chrome è modificabile con `--chrome`. Il renderer usa un profilo temporaneo headless e nessun server. Campiona deterministicamente i keyframe SVG a 24 fps. Output: `assets/demo-motion/`. `verification.json` contiene il controllo FFprobe su dimensioni, durata e frame.

## Verifiche

Nove test frontend passati: copertura quantitativa, budget, scale del grafico, separazione mock/profili e tre test dedicati alle animazioni. Build Vite completata. Lo studio è stato controllato in un browser headless: cambio scena, pausa, avanzamento a 9s, velocità 1,5×, modalità video/Esc, assenza di accumulo delle animazioni, layout a 390px e modalità movimento ridotto; nessun errore JavaScript. Il risultato è in `studio-check.json`.

I tre MP4 hanno esattamente 288 frame a 24 fps e durata 12s. Sono stati controllati anche fotogrammi estratti dai video esportati. Queste verifiche non sono una prova con utenti o una certificazione di accessibilità.
