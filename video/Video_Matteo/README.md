# ADERA · Video preliminare

Composizione HyperFrames, 1920 × 1080, 30 fps, 150 secondi, senza audio.

Con Node.js 22 o successivo e FFmpeg/ffprobe nel PATH, eseguire i comandi dalla cartella del progetto.

```sh
npx --yes hyperframes@0.9.48 browser ensure
npm run check
npx --yes hyperframes@0.9.48 preview --background --port 3021
npm run render -- --fps 30 --quality standard --output renders/ADERA-preliminare.mp4
```

La preview si apre in [HyperFrames Studio](http://localhost:3021/#project/Video_Matteo).

- Lo storico è quello simulato del kit challenge. Il grafico usa il CPM effettivamente presente nel kit per FGR-AD05 dal 9 al 15 novembre e le previsioni salvate di Timestral 28M dal 16 al 30 novembre. Le due linee sono separate al cutoff. I valori del confronto sono i WMAE ponderati per impression del fold 2–15 novembre.
- I tre annunci sono ricostruzioni tipografiche basate sulle descrizioni FGR-U3, FGR-B1 e FGR-S1. L’esempio di intervista contiene domande dimostrative. La build disponibile non include esportazioni di Decision o risposte delle interviste.
- Nel mosaico entrano il ritratto di Chiara, un ritratto singolo e otto ritagli della tavola trasparente. Le altre tavole e la variante di Chiara sono conservate con gli originali. Le due tavole alternative hanno la scacchiera incorporata e sono state usate per confrontare le illustrazioni.
- Le tre schermate di prodotto provengono dalla build locale della dashboard (Overview, Forecast Analytics, Creative Explorer). I riferimenti al nome precedente sono stati rimossi in fase di cattura. Brief, inventario e aggiornamento degli asset sono in `sources/`. I manifest originali e le immagini fornite restano in `assets/`.
