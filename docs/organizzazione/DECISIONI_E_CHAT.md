# Decisioni e informazioni recuperate dalla chat

Fonte primaria: `outputs/code-rot-cleaner/chat/CONVERSAZIONE.md`, 59 messaggi utente/assistente disponibili nello snapshot del 14 novembre 2026. Le posizioni citate sono identificatori dello snapshot, non numeri di riga. È un archivio di messaggi, non una certificazione di tutte le affermazioni storiche. Tool output e segreti riconosciuti sono esclusi.

## Architettura confermata

- Posizioni 186 e 203: Python prepara quote, età e attributi con randomizzazione riproducibile; Gemini tramite abbonamento T3/Antigravity scrive le biografie. Nessuna API generativa Google per le persone. Gemini Decision 1 è l'unica API Google ammessa, coordinata da un subagente dedicato.
- Persone generiche per settore, senza asset, storico, CTR/CPM, audience inferite o forecast nella scrittura. Profili diversi, non varianti cosmetiche dello stesso cliente ideale. La scelta vigente è simulation_blind.
- T3 orchestra; skill e prompt descrivono procedure, non creano una sandbox OS. Il coordinatore mantiene accesso al repository; writer e intervistati ricevono solo task inline e istruzioni di non usare strumenti. Provider/modello effettivi vanno documentati dalla ricevuta, senza autocertificazione del modello.
- L'unione con Timestral è successiva e distinta. Le priorità generali della consegna non autorizzano a sostituire il task personas con un optimizer o una nuova inferenza.

## Quantità: non confondere proposta e run effettivo

- Default del preparatore: 24 slot per settore, 72 totali, sei fasce di età e seed 2026; 18 job di quattro schede.
- Run effettivo: soltanto quattro schede skincare importate, non tutte le 72 persone.
- Posizione 279: l'utente propone cinque fasce e dieci persone per sesso per stimare il carico. È una richiesta di dimensionamento, non prova che tale pool sia stato generato. Esiste `artifacts/personas_t3/load-estimate.html`; prima dell'espansione vanno fissate fasce e categorie di genere.
- Una richiesta API può contenere più domande indipendenti: distinguere richieste, persone, asset e coppie persona–asset nel conto dei costi.

## Feed e risultati

- Posizioni 158 e 272: richiesta di mostrare prompt, schede e feed prima di spendere token. Il feed attuale ha tre post organici fittizi e un annuncio descritto testualmente. Non replica il ranking Meta e non mostra immagini o video originali.
- Posizione 296: autorizzate le prime analisi sulle quattro persone, con registro per evitare duplicazioni. Conservare insieme SQLite, export JSON, richieste e raw. L'identità della cache include profilo, creatività, modello e scenario; una modifica può legittimamente richiedere una nuova analisi.
- 12 asset skincare × 4 persone = 48 valutazioni Decision completate. Il registro conserva anche un tentativo iniziale rifiutato con 429. Un esito campionato serve al replay, non dimostra che Chiara abbia realmente scrollato.
- Posizione 368: richiesta di ricavare indicazioni per migliorare le campagne. Decision restituisce probabilità su azioni/motivi; un analista interpreta. Le domande diagnostiche aggiuntive in `diagnostic_questions.proposal.json` sono predisposte, non eseguite.

## Interviste e conoscenza di ciascun ruolo

- Posizione 408: dopo Decision intervistare ogni persona, senza comunicarle i risultati, per ottenere aspetti positivi e negativi e individuare trend.
- Eseguiti quattro colloqui separati via Gemini/Antigravity. Ogni colloquio riceve solo una scheda, il suo feed e dodici descrizioni in ordine mescolato; nessun punteggio, azione campionata, profilo altrui, KPI o risposta altrui. Sei domande uguali per asset.
- Sono riesposizioni riflessive, non ricordi spontanei né spiegazioni causali del comportamento precedente. Le 48 valutazioni qualitative comprendono 288 risposte aperte e quattro sintesi individuali.
- Congelamento prima del confronto. Il coordinatore è l'analista del confronto; non è stato avviato un ulteriore subagente analista dopo le interviste. L'analisi creativa precedente ha invece una propria ricevuta T3.
- I profili incorporano già avversioni alla pressione promozionale: ritrovarle nelle risposte può essere aderenza alla scheda. Quattro persone non sono un campione rappresentativo; 288 risposte non sono 288 soggetti.
- Divergenze conservate: Patrizia/NDL-S2 e Lorenzo/NDL-B3 hanno score Decision relativamente alti, ma giudizi qualitativi critici. Non riscrivere una misura per farla concordare con l'altra.
- Ricevute: modello richiesto/configurato gemini-4-hydrogen; executedModel restituito null. Non affermare di avere verificato separatamente il modello effettivo.

## Informazioni storiche superate o parziali

README e manifest della consegna dicono che il confronto CatBoost è pending. La successiva replica ha prodotto un confronto locale con CatBoost: `docs/TIMESTRAL_REPLICA_E_STATO_V4.md` e `artifacts/timestral_reproduction/results/method_comparison.csv`. Questo non aggiorna automaticamente la selezione del modello nella consegna. Mantenere entrambe le provenienze e non dichiarare già selezionato un vincitore finale.

Vedi il report delle interviste per le proposte sperimentali. Le varianti non sono state eseguite. Nessun click_intent_signal è CTR misurato/calibrato; nessuna fixture va al forecast.
