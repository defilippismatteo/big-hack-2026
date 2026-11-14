# Market Mirror — personas orchestrate da T3 Code

Architettura confermata dall'utente: Python prepara slot e controlli di diversità;
un subagente Gemini in T3/Antigravity scrive le schede tramite l'abbonamento;
un subagente dedicato coordina le chiamate a Gemini Decision 1. Decisions è
l'unica API Google da usare. Non generare persone con models.generate_content.
L'integrazione con Timestral/forecast è un passaggio successivo fuori dal task personas.

Per un task di generazione usare esclusivamente il job inline sanitizzato:
nessuna lettura di repository, storico, creatività, audience inferite o forecast.
Il subagente restituisce JSON; il coordinatore valida e salva modello/provider
effettivi e la ricevuta T3. Ogni valutazione riceve solo una persona e il suo feed.
Le restrizioni di lettura sono istruzioni, non una sandbox filesystem: non
dichiarare isolamento OS se non è stato effettivamente applicato.

La fonte progettuale corrente è `BigHack2026_Wevion_Specifica_Operativa_v4.md`.
Priorità: P0 forecast/validazione sulle 699 righe; P1 verifica Timestral; P2 dodici
pubblici motivati e scenari budget/creatività; P3 viewer, README e video di 180s.
Le priorità generali della consegna non sostituiscono il task richiesto:
quando l'utente lavora sulle personas, proseguire su persone/feed/Decision,
senza avviare forecasting, budget optimizer o unioni non richieste.

Percorso principale: `python -m market_mirror deliver`. Con
`--timestral-ref origin/feat/timestral-pilot` importa export precomputati da Git,
salvando commit e hash; non rifà l'inferenza e non modifica il ramo parallelo.
Senza ref usa una baseline pesata a 14 giorni. Gli output sono in
`artifacts/wevion_v4/`: 699 forecast, 12 audience, decisioni, metriche e viewer.
Non dichiarare il modello finale migliore finché manca il confronto CatBoost.

Il runtime del prototipo è `market_mirror/`; istruzioni operative in `docs/MARKET_MIRROR_GUIDA.md`.
Le skill canoniche del progetto sono in `.agents/skills/`. Le due cartelle
`Wevion_Personas_*` sono pacchetti sorgente/versioni precedenti: non copiarle entrambe
in `.agents`, perché contengono nomi duplicati e due diversi modelli informativi.
Il runtime riusa gli script di preparazione di `Wevion_Personas_Architettura_v1/scripts/`.

Per l'estensione feed la scelta corrente è **simulation_blind**: pool generici per settore, senza
creatività, adset o ipotesi inferite dallo storico durante la scrittura delle persone.
Solo il motore di decisione riceve la singola creatività. Nessuna persona vede
risposte altrui, KPI, previsioni o pesi stimati da Analytics. Le ipotesi di audience
appartengono al ramo Analytics e non rientrano nei profili.

T3 Code coordina il lavoro e i comandi; Python costruisce i payload e salva gli
artefatti riproducibili. Le skill non sono modelli né autorizzazioni filesystem.
Per isolamento OS usare worker/container con i soli input ammessi, come descritto
nella guida. Il coordinator di sviluppo conserva accesso al repository.

Non modificare `Test_Timestral/` né il branch forecasting durante lavoro sul ramo
personas. Scambio tramite asset_id e CSV con chiave (data, ad_id). Qualunque
calibrazione va allenata prima del cutoff, inclusi audience e pesi.

Separare `observed`, `hypothesis`, `synthetic`, `simulated_decision`, `mock_not_model`.
I dati organizzatori sono simulati; “observed” indica etichette fornite nel kit.
Nessun click_intent_signal è un CTR misurato o calibrato. Nessuna fixture va al
forecast. Non copiare codice MarketMirror AGPL senza gestire attribuzione/licenza.

Verifica appropriata, nell'ambiente `.venv-market-mirror` attivo:
`python -m unittest discover -s tests -v` e `python -m market_mirror deliver`.
`python -m market_mirror smoke` verifica soltanto l'estensione feed opzionale.
Chiamate Google solo con `--live`; il comando
`smoke` è sempre offline. Non stampare o salvare chiavi/API headers negli artefatti.
