# ADERA: intervento UX e verifiche

Fonte implementazione: copia `adera-revamp/` da `feat/adera-dashboard`, a2e17ce. Il branch originale non è stato modificato. I tre snapshot originali mantengono gli SHA-256 registrati in `REVAMP_SOURCE.json`.

## Metodo di revisione

Tre subagenti con contesto iniziale indipendente: giudizio al primo accesso, audit euristico UX e requisiti organizzatori. Nessuno ha ricevuto lo storico dei problemi o il verdetto desiderato. Un quarto revisore ha ricevuto solo gli HTML aggiornati e il brief, senza diagnosi precedenti. Le restrizioni sono istruzioni, non una sandbox del sistema operativo. È una simulazione, non ricerca con utenti o giudici reali. I report conservano la distinzione fra rendering osservato e inferenze dal codice.

Non è stata trovata un’ulteriore richiesta ufficiale oltre PDF/LEGGIMI/CSV nel materiale esaminato. La specifica v4 e lo storyboard del team restano fonti interne, non nuove richieste ufficiali.

## Interventi

- Panoramica: budget, beneficio condizionale e percorso dati → previsione → confronto dei piani prima dei contatori tecnici. Errori storici globali visibili; non presentati come intervalli futuri o prova causale dell’aumento di clic.
- Grafico: CPM iniziale, asse di dettaglio esplicitamente indicato e ripristino da zero, scelta CTR/CPM, periodo da/a, giorni esplorabili via mouse/tastiera/touch. Nessuna alterazione o oscillazione aggiunta ai dati.
- Pubblici: campagne chiaramente cliccabili; persona sintetica già generata anticipata; sintesi positive/negative distinte dai dati del modello. Eliminato il confronto di segmenti sintetici. Ipotesi storiche e motivazioni accessibili con evidenze per gruppo.
- Creatività: tre proposte con stime chiave, spiegazione degli assi e del rapporto clic/euro; hover/focus/tocco aggiorna la scheda a fianco, click sulla CTA apre il dettaglio; tabella completa opzionale con avviso di scorrimento e metriche prima delle dimensioni secondarie.
- Budget: azione esplicita per scegliere la campagna e aprire il cursore di trasferimento manuale.
- Navigazione: nomi italiani orientati al compito, icone esistenti Lucide, stati di selezione e dettagli espandibili.

## Separazione dati

`product-story.json` è nuovo. Contiene tre schede estratte dagli artefatti sintetici esistenti, con ID, provider, modello e hash sorgente; le sintesi qualitative sono invece etichettate `mock_not_model`, con avviso anche nella UI. Sono una struttura dimostrativa richiesta dall’utente mentre il rapporto è in preparazione. Non sono interviste né risultati dei modelli. Nessun dato mock alimenta forecast o budget.

Le medie di reazione per campagna sono calcolate sulle coppie persona–asset presenti nello snapshot, pesando per numerosità; non sono utenti unici né CTR. La copertura parziale è visibile, inclusi settori privi di risultati nello snapshot. Non è stato aggiornato il congelamento dei processi in corso.

## Verifiche effettive

- `npm test`: 6 test passati, incluse scale per serie piatte/mancanti e separazione fra mock e profili sintetici.
- `npm run build`: passata.
- Browser locale della copia: CTR/titolo contestuale, asse da zero, intervallo ridotto a quattro giorni, filtri campagna e risposta del budget; tutti verificati.
- Campagne: selezione Abbigliamento, rapporto unico, scheda Chiara Bellini, avviso fittizio, espansione del profilo e ritorno alle tre campagne; verificati.
- Creatività: focus aggiorna scheda, proposte sincronizzano punto e scheda, hover reale su NDL-AD22 aggiorna la scheda, apertura/chiusura del dialog e recupero da ricerca senza risultati; verificati.
- Browser a 390×844: tutte le sei route senza overflow della pagina; ingresso manuale budget e apertura/chiusura menu verificati. Le tabelle possono scorrere nei contenitori previsti.
- Rendering offline desktop e mobile, con messaggi console assenti nei controlli visivi eseguiti.

Durante il controllo hover il collegamento di automazione ha avuto un timeout transitorio; dopo ripristino, hover e interazioni sono stati verificati con successo. Nessuna certificazione di accessibilità completa o prova con screen reader.

## Limiti ancora aperti

Il rapporto finale dalle interviste resta da collegare. Intervalli predittivi calibrati e robustezza causale del piano budget non sono disponibili. L’audit precedente ha rilevato un contratto di export pilota da riallineare: questo intervento UX non cambia quella pipeline. I testi di alcune ipotesi audience rimangono simili perché sono quelli prodotti dalla fonte; sono stati aggiunti segnali specifici, senza inventare differenze demografiche.

## Rigenerazione

Dalla copia: `python3 scripts/export_story.py` estrae gli esempi dagli artefatti esistenti; `npm run build`, poi `python3 scripts/export_preview.py` produce la home offline. Passare output e hash come secondo e terzo argomento per le viste dedicate, ad esempio `python3 scripts/export_preview.py preview-audience.html '#/audience'`.
