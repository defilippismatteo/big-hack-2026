# Prompt riutilizzabile per T3 Code

Usa i job in artifacts/personas_t3_600/jobs. Il pool previsto è 600 persone, 200 per settore; seed 2026. Prima esegui soltanto beauty_skincare-01.

1. Verifica le capacità T3 e il provider Antigravity/gemini-4-hydrogen, thinking low. Non sostituire il provider se indisponibile. Nessuna API generativa.
2. Per ogni job richiesto crea un task T3 nuovo, senza storia del padre; passa come task solo il contenuto del corrispondente .prompt.txt. Non allegare repository, creatività, storico o forecast. Il figlio restituisce JSON e non usa strumenti.
3. Salva risposta e ricevuta T3 (taskId, providerInstanceId, executedModel, link). Esegui t3-import. Ferma la pipeline su errori del contratto; non correggere silenziosamente le risposte del modello o chiamare un provider alternativo.
4. Mostra le schede con personas-view. Solo dopo il freeze costruisci plan con le schede approvate e il catalogo creativo separato.
5. Delega il worker Decisions con il solo piano, output e comando Python. Esegui prima il preflight senza rete. Per il live usa GEMINI_API_KEY locale solo per Decision 1, mai nel prompt. Non dichiarare disponibile Decision tramite abbonamento se non verificato: questa fase usa la sua API distinta.
6. Salva raw, aggrega e aggiorna il viewer. Nessuna integrazione Timestral ora.
