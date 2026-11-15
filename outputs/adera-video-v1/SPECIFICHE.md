# ADERA — video di presentazione, direzione v1


## informazioni aggiuntive utente : 
Rendere il video complessivamente dinamico, non soltanto animare la comparsa dei singoli titoli.


## Stato e approvazioni
Brief consolidato il 14 novembre 2026. Fase attuale: asset e storyboard da approvare, non montaggio definitivo. Nessuna modifica alla dashboard in questa fase. Eliminare dal video ogni riferimento al precedente brand; il rebranding della dashboard resta da verificare separatamente.

## Formato e identità
- 1920 × 1080, 16:9, proposta 30 fps; durata obiettivo 150 secondi, massimo 180.
- Riferimento allegato: 1920 × 1080, 30 fps, 60,7 secondi. Non copiarne durata o sottotitoli.
- Prima lettura dei fotogrammi: tipografia grande e pesante, domande brevi, composizione asimmetrica, oggetti UI isolati, alternanza fondi chiari/scuri, numeri protagonisti. Timing e transizioni ancora da analizzare fotogramma per fotogramma.
- Adattare colori e font ADERA: Inter Variable; ink #292339, action #7046CE, accent #8861E8, plum #35214F, fondo #F6F5F9.
- Logo fornito dall'utente: triangolo viola con tre barre bianche e wordmark ADERA. Conservare l'originale; la proposta SVG del simbolo è una ricostruzione geometrica approssimata da approvare, non un tracciato esatto.
- Niente sottotitoli, note a piè di pagina o disclaimer piccoli. Testi principali leggibili e brevi. Chiarire la natura sintetica nel titolo delle scene pertinenti, non in basso.
- Voce/TTS rinviati per richiesta dell'utente; nessuna generazione audio ora.

## Fonti
- Dashboard: adera-revamp/preview.html. NON usare la pagina «Come funziona», anche se il link iniziale contiene #/process.
- Design: adera-revamp/src/styles.css e revamp.css.
- Dati: adera-revamp/public/data/{overview,pilot-forecast,model-validation,persona-library,product-story}.json.
- overview dichiara metodo ctr_baseline14d__cpm_timestral28m, cutoff 2026-11-15: non etichettare automaticamente quel risultato come ensemble CatBoost.
- model-validation contiene confronti CatBoost/Timestral/baseline per fold: verificare metrica e periodo prima di qualsiasi claim di superiorità.
- Il kit organizzatori è simulato. «Observed» indica etichette del kit, non campagne reali esterne.
- Le probabilità Decision non sono CTR misurati; non sommarle o mescolarle ai forecast. Non inventare commenti o azioni se lo schema salvato non le contiene.

## Storyboard proposto — 150 secondi
| Tempo | Scena | Testo e movimento |
|---|---|---|
| 0–9 | Domanda | «E se potessi testare una campagna prima di investirci?» Parole in sequenza, card campagna in ingresso. |
| 9–16 | ADERA | Logo; «Prima di investire, capisci.» Il simbolo si apre nel workspace. |
| 16–27 | Dati challenge | Righe e colonne si compattano in serie temporali. «Partiamo dai dati.» |
| 27–44 | Forecast | Camera segue l'estremità della linea, poi zoom-out. Serie note e previste distinte; gap temporale visibile. |
| 44–53 | Eventi e modelli | Popup Black Friday 27/11/2026 e Cyber Monday 30/11/2026; Timestral e CatBoost con ruoli verificati. Nessun picco aggiunto artificialmente. |
| 53–65 | Orchestrazione | T3 Code al centro, loghi ufficiali Claude/Gemini/ChatGPT come agenti. Non attribuire a ciascuno lo stesso ruolo operativo. |
| 65–76 | Persona | «Un pubblico sintetico. Profili diversi.» Card Chiara Bellini; avatar illustrato, dettagli dal profilo salvato. |
| 76–95 | Feed Decision | Feed simulato, creatività challenge illustrata. Swipe tipo Tinder, notifiche azione e probabilità registrate affiancate. |
| 95–104 | Scala | Zoom-out su 10 avatar, altri parzialmente fuori campo; il dato disponibile riporta 600 profili, da verificare nel run scelto. |
| 104–112 | Segnali | Card e segnali convergono con morph in documento: «Dalle reazioni, segnali.» |
| 112–127 | Interviste | T3 e agenti; domanda con due risposte significative tratte dagli output. Mostrare Gemini nel ruolo intervista quando documentato. |
| 127–144 | Dashboard | Pan a sinistra guidato da freccia; analisi quantitativa e segnali qualitativi entrano in viste distinte della dashboard. Nessuna fusione predittiva non implementata. |
| 144–150 | Chiusura | Logo originale e «ADERA. Prima di investire, capisci.» |

## Asset
Inventario aggiornato e prompt completi: `ASSET_E_PROMPT.md`. Cinque SVG scaricati da fonti ufficiali (T3 Code, Gemini, Claude, ChatGPT, CatBoost), originali in `brands/` con manifest URL e SHA-256. Immagini da generare: dieci avatar e tre creatività illustrative. Timestral resta un'etichetta testuale, non un marchio inventato. Nessuna API generativa chiamata.
### Generazione immagini richiesta, in attesa di strumento
- Dieci avatar illustrati coerenti, in file separati, mezzobusto, sfondo trasparente. Età e caratteristiche dai profili selezionati, niente stereotipi o testo incorporato.
- Una creatività fittizia basata sulla descrizione di un annuncio della challenge; settore abbigliamento come proposta iniziale, selezione asset_id da confermare dopo confronto con interviste disponibili.
- Le immagini generate sono illustrazioni del video: non sono gli stimoli originali valutati e non vanno reinserite nel motore Decision come se fossero tali.
- Il generatore built-in non è esposto in questa sessione. Nessuna immagine AI generata finora. Fallback CLI solo dopo conferma esplicita; richiede OPENAI_API_KEY. Non cercare né stampare credenziali.

### Asset deterministici
- SVG simbolo logo per animazione separata di triangolo e barre, approssimato.
- Prima proposta grafico con dati di forecast salvati, asse Y locale leggibile; niente serie storica inventata.
- UI, percentuali, frecce, documento, diagrammi e testi in SVG/HTML.
- Loghi provider: risorse ufficiali, non ricostruzioni generative.
- Dashboard: asset e screenshot della versione corrente, non mockup inventati presentati come prodotto funzionante.

## Prompt immagini pronti, NON eseguiti
### avatar-01
Illustrazione editoriale vettoriale morbida, mezzobusto di Chiara Bellini, donna italiana di 46 anni, tecnica di laboratorio, espressione attenta e pragmatica, abbigliamento quotidiano semplice. Palette viola ADERA e neutri, forme pulite leggibili in piccolo, nessun testo, nessun logo, sfondo trasparente. Ritratto di persona fittizia; non somigliare a persone note. Gli altri nove prompt saranno derivati da nove profili effettivamente selezionati, non inventati da questo brief.

### annuncio-challenge
Immagine pubblicitaria illustrativa da generare soltanto dopo aver scelto asset_id e visual dal kit. Riprendere la descrizione visuale documentata; testo promozionale sovrapposto in HTML, non nel bitmap. Non presentare questa immagine sostitutiva come input dell'esecuzione originale.

## Da approvare
- Direzione compositiva e tavolozza delle anteprime SVG.
- Scelta dell'annuncio protagonista e suoi output collegati.
- Fallback API per la generazione immagini, oppure disponibilità del generatore nella sessione.
- Grafico: prima bozza solo forecast; recuperare serie storica con schema documentato per sovrapposizione e gap. Non allungare artificialmente la curva.

## Verifiche successive
Analisi dei cut del riferimento; verifica dashboard corrente; font e loghi ufficiali; fonti puntuali di percentuali/citazioni; generazione immagini; approvazione storyboard; animazione HyperFrames; controlli e render. Non avviare servizi, chiamate Google o forecasting per produrre questi asset.
