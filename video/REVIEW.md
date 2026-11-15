# Review del montaggio unificato ADERA

## Revisione corrente — date ancorate e fondo richiesto

Le etichette Black Week, Black Friday e Cyber Monday sono centrate sulle X esatte del 20/27/30 novembre, con cerchi sulle Y esatte dei CPM salvati e guide verticali tratteggiate. Trasformazioni camera e scala contenitore incluse tramite `getScreenCTM()`. Verifica su 21 casi (3 date × 7 timestamp di ingresso/hold): errore indicatori **0 px**, massimo errore centro etichetta **0.004421 px** (`date-layout-verified.json`). Aggiunto tick 27/11, centrati i testi delle date sugli stessi punti. Le card mantengono il look Gemini, con larghezza 208px e titolo 22px per evitare sovrapposizioni tra 27 e 30.

La scena grafico ha ora fondo plum uniforme #35214f, pannello arrotondato e area previsione leggermente tinta come il secondo allegato utente. Nessuna orbita in questa scena; non sono stati copiati né la curva né lo storico dell'immagine. Il resto delle scene mantiene le precedenti selezioni.

Copione **approvato**, parole invariate. `SINCRONIZZAZIONE.md` e `copione-cues.json` allineano le frasi agli eventi: «poi la vista si allarga» 36.7–38.95 s attraversa lo zoom-out 37.2–38 s; Timestral da 46.1 s segue l'ingresso widget; CatBoost da 48.4 s. Ritmo pianificato massimo circa 136.4 parole/min. Nessuna voce generata: sincronizzazione effettiva e durata delle parole da misurare dopo l'accesso alla generazione.

Le note sotto documentano le verifiche precedenti ancora applicabili; per sfondo, posizione delle etichette e stato del copione prevale questa revisione. `graph-v3-encoded.jpg` è estratto dal nuovo MP4; i filmstrip v1/v2 sono storici.

Fedeltà **mixed**. Riutilizzo dei sorgenti editabili, non concatenazione dei tre video. Nessuna delega, nessun servizio persistente, nessuna API Google, nuova previsione, immagine generativa o spesa. Nessun commit e nessuna modifica alle sorgenti esterne alle due directory autorizzate.

## Selezioni ed evidenze

La mappa completa è in `.reanimate/adera-unified/spec.md`. Intro, scena successiva, dati, T3, singola persona, zoom-out persone, segnali, attenzione e finale provengono dal DOM/CSS/GSAP Matteo, commit `2a9019ecfa6ee2785fe88471a70c4ce34af4ead0`. Il suo fondo paper/plum/ink e le orbite rimangono sotto tutti i layer. I contenuti Matteo delle scene sostituite sono esclusi anche dalle code delle transizioni.

Revisione richiesta dall'utente: **grafico originale ChatGPT**, incluso DOM, titoli, assi, camera, linea e punta; nessuna ricostruzione nella geometria Gemini. Chiamata diretta a `chatgpt.seek(t)` fra 27 e 43.999 s. Solo le etichette evento sopra e i widget Timestral/CatBoost sotto provengono da Gemini, con stile e ingresso originali. Fra 43.2 e 44 s un raccordo cubic out riduce il contenitore a scala .72 e lo centra, lasciando spazio ai widget a y815; poi il grafico resta in hold fino a 53 s. I popup ChatGPT sono esclusi per evitare duplicati. Le probabilità e gli swipe sono Gemini; aggiunta etichetta «Gemini Decision 1» con SVG ufficiale. Pan dashboard Gemini originale: 128.4–131 s, cubic(.65,0,.35,1).

Ho guardato i contact sheet dei tre MP4 sorgenti (`matteo-sheet.jpg`, `gemini-sheet.jpg`, `chatgpt-sheet.jpg`) e del risultato (`final-sheet.jpg`), in `.reanimate/adera-unified/`. Catture aggiuntive controllano i confini 27, 44, 53, 76, 95, 127, 144 s e gli stati intermedi dello zoom/pan. `boundary-qc.json` conserva gli stati di visibilità e trasformazione. `browser-errors.json`: zero errori JavaScript nelle catture.

## Dati e dashboard

- Le **15/15 righe FGR-AD09** di ChatGPT coincidono esattamente con `adera-revamp/public/data/overview.json` corrente, chiave data/annuncio. CPM 9.494775–10.118596 €; CTR costante 0.809073%. Nessun picco aggiunto. Etichette eventi aggiornate alla stessa serie.
- Assi ChatGPT originali: tick CPM 9.4/9.6/9.8/10.0/10.2 €, date 16–30 novembre; formula locale y=410−(CPM−9.4)×430. Non viene più mostrato l'ancoraggio storico aggregato della precedente struttura Gemini. La serie è esclusivamente il forecast salvato FGR-AD09.
- Widget confrontati con fold 02–15/11 di `model-validation.json`: Timestral CPM MAE 0.884087 €, WMAE 0.706742 €; CatBoost CTR MAE 0.274314 pp; baseline 0.316285 pp; mix CPM MAE 0.874059 €. Sono metriche di validazione, non una fusione Decision/forecast.
- Dashboard: sorgenti locali correnti copiate nella directory output, build Vite completata, esportazione offline e nuova cattura Overview. Confronto con `adera-revamp/preview.html` corrente a 1920×1080: **identità pixel esatta, MAE 0**. `dashboard-comparison.json` e `dashboard-text.txt` in evidence. Nessuna pagina «Come funziona». I file e loghi locali correnti sono inclusi, hash nel manifest.
- Le probabilità Decision rimangono probabilità simulate, mai chiamate CTR; i profili sono sintetici e le creatività tipografiche illustrative. Timestral 28M usa il marchio Mistral approvato.

## Confronto e limiti

Nove campioni delle scene Matteo, contro fotogrammi del suo MP4 compresso: errore RGB medio normalizzato **0.30–1.78%** (`comparison.json`). Questa è una misura MAE dei pixel, **non** percentuale pixelmatch, e non dimostra una soglia globale di fedeltà. Le timeline Matteo/Gemini sono riusate, ma non è stata misurata l'intera traiettoria di ogni elemento a intervalli di 80 ms. Nessun pass globale dichiarato.

Difformità deliberate: raccordi tra runtime con tagli al cambio sorgente e code di transizione prive dei contenuti esclusi; ridimensionamento del grafico dopo il suo movimento originale per ospitare le sole aggiunte Gemini; logo Gemini aggiunto; dashboard aggiornata a cattura raster a schermo intero. La dashboard è una cattura statica dopo il pan, non una sessione interattiva né un nuovo tour di tutte le sue pagine. Il logo e alcune scritte UI rimangono piccoli nella schermata prodotto originale; nessuna nuova nota in basso è stata introdotta.

Le interviste Matteo sono mantenute come «intervista simulata · esempio»: mostrano domanda e approfondimenti, non nuove citazioni attribuite a un run. Gli asset avatar e marchi sono quelli delle fonti, senza nuove generazioni.

L'HTML richiede accesso locale fra iframe (Chromium `--allow-file-access-from-files`) oppure un server statico avviato dall'utente. Il render usa il flag locale e chiude Chromium alla fine. Progetto e riproduzione dipendono dai file relativi nella directory, non da servizi remoti.

## Verifica MP4 finale

MP4 corrente: **1920×1080, 30/1 fps, 150.000 s, 4.500 frame, H.264/yuv420p, nessuna traccia audio**. Decodifica completa ffmpeg terminata con codice 0 e stderr vuoto. Dimensione 13.584.683 byte. SHA-256 `0215b99b4d3288f2c42ded0cf80bf10d6cd96080177c62ef2d72371819ef3346`.

Confronto diretto con il runtime ChatGPT originale a 11 timestamp fra 27 e 43 s: **11/11 stati identici** per path linea, trasformazione camera e coordinate punta (`chart-original-comparison.json`). Il raccordo di scala successivo è un'aggiunta dichiarata. Fotogramma a 50 s estratto dal nuovo MP4: `graph-v2-encoded.jpg`. Il copione proposto è in `COPIONE.md`, con cue JSON; audio non generato, in attesa di approvazione utente.

Esito tecnico e decodifica revisionati: `.reanimate/adera-unified/final-probe.json` e `final-qc.json`. Il filmstrip `encoded-filmstrip.jpg` documenta la versione precedente; per la scena modificata vale `graph-v2-encoded.jpg` e le catture aggiornate. Il controllo tecnico passa; non equivale a un pass globale di fedeltà delle animazioni. Browser di cattura e renderer chiusi; nessun server avviato.
