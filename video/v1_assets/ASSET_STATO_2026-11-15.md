# Asset ricevuti — 15 novembre 2026

Aggiornamento che prevale sulle precedenti indicazioni di asset da generare.

## Ricevuti
- Sei immagini utente importate senza modifiche in `avatars/originals/`, con fonte e hash in `avatars/sources.json`.
- Tre ritratti singoli e tre tavole con più ritratti: i soggetti sono sufficienti. Non chiedere altri avatar.
- Scelta iniziale: `chiara-hero.png` per Chiara nel primo piano; selezionare dieci figure coerenti per lo zoom-out. Le varianti della stessa persona non vanno contate automaticamente come persone nuove.
- Le tavole con scacchiera richiedono controllo: la scacchiera potrebbe essere incorporata nel bitmap, non vera trasparenza. Anche le immagini con alpha richiedono controllo dei bordi e possibili pixel colorati residui prima dell'animazione. Non dichiarare ancora tutti i PNG pronti per compositing.
- Nessuna identità degli altri profili assegnata soltanto dall'aspetto del ritratto.

## Mistral / Timestral
L'utente chiede esplicitamente il logo Mistral accanto a Timestral. Aggiunto il download dal dominio ufficiale a `collect_assets.py`; esito e hash in `brands/sources.json`. Presentare il marchio come Mistral e mantenere l'etichetta «Timestral 28M»: non chiamare il marchio un logo dedicato Timestral.

## Mancanti: tre immagini pubblicitarie
Non sono state allegate creatività prodotto. Restano da ottenere le tre immagini descritte in `ASSET_E_PROMPT.md`: `ad-FGR-U3.png` (capo indossato), `ad-FGR-B1.png` (capi su fondo nero), `ad-FGR-S1.png` (ultime taglie, spazio testo). Testi/offerte saranno HTML. I bitmap sono illustrazioni, non gli input delle esecuzioni Decision originali.

Non bloccano l'avvio di layout e animazioni: usare temporaneamente card tipografiche basate sulle descrizioni originali, senza spacciarle per immagini generate. Voce e musica non sono richieste ora. Nessun'altra domanda necessaria sul brief.

## Passo successivo
Separare e rifinire dieci avatar, poi storyboard animato senza voce: orchestrazione, feed, zoom-out e interviste. Proseguire con il workflow reverse/HyperFrames e i suoi controlli prima di dichiarare un video ricreato o renderizzato. Nessun render finale prodotto in questo aggiornamento.
