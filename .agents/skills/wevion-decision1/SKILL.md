---
name: wevion-decision1
description: Prepara feed indipendenti e valuta reazioni persona-creatività con Gemini Decision 1, preservando la visibilità di ciascuna persona.
---

T3 orchestra questa fase tramite un subagente Decision worker Gemini dedicato.
Usa [il task del worker](../../../docs/prompts/decision-worker.md) con modalità
PRECHECK prima del LIVE. Questa è l'unica fase che usa un'API Google distinta.
La chiave GEMINI_API_KEY serve solo a Decision 1, mai a generare le persone.

Runtime: `market_mirror/feed.py` e `providers.decide`.
Una creatività nell'input condiviso; una domanda choice per persona con il solo
profilo individuale e il suo feed. I metadati asset_id e sampling_weight restano
nel piano locale, fuori dal payload al modello. Non mettere il pool completo
nell'input condiviso: tutte le domande lo vedrebbero.
Il primo scenario ha tre post organici neutri fittizi e un annuncio descritto
testualmente, una sola esposizione. Nessun social proof o risposta di altre persone.
Le domande Decisions sono isolate secondo il contratto Google.

Usa `plan --asset-id NDL-S1 --n 4`, quindi `decide --live` dopo aver importato
schede synthetic valide dal subagente Gemini T3. API ufficiale: client.decisions.create, v1beta,
gemini-decision-1, google-genai >=3.2. Non è un backend chat.
Opzioni action__reason mutuamente esclusive; click include attenzione, stop
non include click. Salva la risposta SDK raw prima di interpretarla.
Errori di quota/accesso non autorizzano un cambio provider.

Vedi [guida](../../../docs/MARKET_MIRROR_GUIDA.md) e
[Google Decisions](https://aistudio.google.com/docs/decisions-api).
