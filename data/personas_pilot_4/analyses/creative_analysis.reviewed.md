# Dalle reazioni alle modifiche della campagna

Fonte: 48 risposte Decision già congelate, 12 asset skincare, 4 profili sintetici.
Sintesi iniziale prodotta da un subagente Gemini in T3; revisione del coordinatore
per separare i punteggi dalle ipotesi e rendere i test interpretabili.
Nessuna nuova chiamata Decision è stata eseguita per questa analisi.

## Che cosa è una decisione nel run

Per Chiara Bellini su NDL-S3: P(scroll)=0,4445, P(glance)=0,3016,
P(stop)=0,2045, P(click)=0,0493. Scroll è la marginale più probabile,
non un evento umano osservato. Il reason_code prevalente all'interno di scroll
è irrelevant. Le categorie dei motivi sono state scritte da noi.

Una scelta campionata per il replay è un oggetto diverso: può anche essere
un evento raro. Non usare le azioni campionate come frequenze di CTR; i confronti
usano le distribuzioni originali, preservate nel registro.

## Tre segnali del panel

1. **Bassa pertinenza o bisogno.** Il punteggio medio delle categorie
   scroll__irrelevant + glance__low_need è 0,2604 sulle 48 coppie con peso
   uniforme. Chiara e Davide hanno interesse basso nello slot. Per Davide
   l'asset SPF NDL-S4 produce un segnale di click più alto degli altri asset.
   Ipotesi: un bisogno pratico specifico può contare più dell'interesse generale
   nella skincare. Alternativa: il modello sta soprattutto rispettando gli
   attributi assegnati; non abbiamo scoperto una nicchia reale verificata.

2. **Scetticismo.** Il punteggio medio scroll__skeptical è 0,1613.
   NDL-U1 e NDL-B4 sono associati a scetticismo anche nei profili più interessati.
   Possibili fattori sono pressione temporale, formulazione dell'offerta e
   presentazione, ma questi dati non isolano quale fattore causi il risultato.

3. **Attenzione senza apertura.** Lorenzo si ferma su NDL-S3 con score 0,4506
   e apre con score 0,1527. Può volere più informazioni o semplicemente
   mantenere la routine abituale. Questi risultati non consentono diagnosi
   della landing page, del checkout o di conversioni che non sono stati mostrati.

Sono pattern del panel su un insieme fisso di asset, non trend temporali né
percentuali di persone reali. Non dedurre preferenze per età o genere da quattro schede.

## Interventi verificabili: una variabile per volta

| Asset e profilo | Ipotesi da verificare | Prima variante proposta | Che cosa resta fisso |
|---|---|---|---|
| NDL-U1 / Patrizia | Il countdown iniziale aumenta la diffidenza | Spostare il countdown in chiusura, usando in apertura la stessa applicazione del siero già descritta | Prodotto, sconto, durata, CTA e altre informazioni |
| NDL-S4 / Lorenzo | L'infografica fitta ostacola la lettura | Ridurre la densità del layout, usando soltanto le informazioni già fornite: SPF50 e assenza di bianco | Copy, CTA e pressione sulle scorte; un'eventuale rimozione della scarsità è un altro test |
| NDL-S3 / Lorenzo | La CTA di acquisto non corrisponde alla ricerca di informazioni | Testare una CTA informativa coerente con una pagina prodotto realmente disponibile | Prodotto, offerta e visual; prima verificare la destinazione |
| NDL-U2 / Davide | La scadenza prevale sul beneficio pratico | Cambiare la gerarchia visuale: spedizione gratuita in primo piano, scadenza meno dominante | La medesima offerta, i medesimi prodotti e la medesima CTA |

Queste sono proposte, non miglioramenti già dimostrati. Non aggiungere
certificazioni, INCI, tollerabilità, proprietà anti-sudore, tempi di consegna
o nuovi prodotti se non sono disponibili e verificati. L'analista aveva anche
proposto varianti con queste informazioni: richiedono dati ulteriori e non sono
pronte per il test con il solo kit attuale.

Confrontare originale e variante con le medesime persone congelate e lo stesso
feed. Registrare un nuovo asset/versione: non sovrascrivere le risposte originali.
Un miglioramento nel simulatore resta un'ipotesi da verificare su dati reali.

## Estendere Decision senza chiedergli una strategia libera

Mantenere fissa la domanda comportamentale. Aggiungere domande diagnostiche
separate, con opzioni neutrali e non determinabile: ostacolo prevalente,
informazione mancante, contributo del contesto rispetto all'annuncio.
Queste risposte sarebbero nuove classificazioni del modello, non prove causali.
Non fornire alle singole domande giudizi altrui o conclusioni dell'analista.

Il subagente analista T3 legge soltanto a valle dati congelati, schede e asset,
aggrega i segnali e propone modifiche, alternative e test. Non riscrive le persone
in funzione dei vincitori e non inventa feedback attribuiti alle personas.

Le tre domande proposte sono nel file diagnostic_questions.proposal.json.
Sono una specifica da implementare e valutare: non sono state inviate all'API.
