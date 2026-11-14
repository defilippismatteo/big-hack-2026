# Wevion / T3 Code — delega e isolamento informativo

Obiettivo ufficiale: 12 ipotesi motivate sui pubblici degli ad set; 699 righe future CTR/CPM affidate al ramo forecasting; scenari di budget e creatività. I CSV sono sintetici, non esistono risultati veri esterni di queste campagne.

Questa cartella contiene skill di **sviluppo**. Le restrizioni READ/WRITE indicate qui sono contratti di lavoro, NON autorizzazioni filesystem. Il codice runtime deve passare viste JSON esplicitamente filtrate e deve applicare l'isolamento fisico degli input ai modelli.

- Nessuna skill di generazione/valutazione personas può leggere previsioni, CTR/CPM storici grezzi, dati del holdout, reazioni di altre personas, o risultati non esplicitamente ammessi.
- Solo evidence e audience-inference possono usare le metriche storiche, rispettando il cut-off del fold.
- Per validazione 02–15/11 rigenerare le audience usando solo storia fino al 01/11. Per forecast 16–30/11 usare storia fino al 15/11.
- Dati creativi originali: headline, testo_principale, call_to_action, descrizione_visual; NON ci sono immagini/video reali nel kit.
- Le percentuali delle simulazioni NON sono CTR osservati. Le distribuzioni della Decision API NON sono automaticamente probabilità di clic reali.
- Obbligo di esportazione e JSON schema test. Seed e modello/provider devono essere salvati.
- Non cambiare il ramo forecasting; usare solo contratti di output stabili.

Ordine: audit-marketmirror -> evidence -> audience -> creative (parallelo con personas) -> personas -> simulation -> calibration -> explain.

Le skill si invocano con `$nome-skill` nel provider compatibile in T3 Code; verificare che siano effettivamente rilevate, poi riavviare la sessione dopo modifiche.
