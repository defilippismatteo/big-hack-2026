# Wevion · Big Hack 2026

**Architettura personas aggiornata:** [T3/Antigravity → schede → worker Decision](docs/PERSONAS_T3.md).
La generazione via Google API e i precedenti comandi `personas --live` sono
superati: le persone sono scritte dai subagenti tramite l'abbonamento; soltanto
Decision 1 usa la sua API. Il task corrente non comprende l'unione con Timestral.


Obiettivo: **699 previsioni CTR/CPM, 12 pubblici motivati, decisioni su budget e
creatività**, con prototipo esplorabile e video di 3 minuti. Fonte progettuale:
[specifica operativa v4](BigHack2026_Wevion_Specifica_Operativa_v4.md).

Procedura: [guida completa](docs/MARKET_MIRROR_GUIDA.md).

```bash
source .venv-market-mirror/bin/activate
python -m market_mirror deliver --timestral-ref origin/feat/timestral-pilot
python -m unittest discover -s tests -v
```

Apri [il viewer generato](artifacts/wevion_v4/viewer.html). La cartella contiene
`forecasts_2026-11-16_30.csv`, `persona_adset.json`, `decisions.csv`, metriche,
scenari stagionali e manifest con provenienza. I file si rigenerano dal comando.
Senza `--timestral-ref` il percorso usa una baseline gerarchica a 14 giorni.

L'export Timestral è letto dal ref Git locale, senza checkout o modifiche al
branch. Al commit `2d8adf0`, la regola WMAE sul primo fold seleziona baseline per
CTR e Timestral-28M per CPM. Questi sono candidati: il confronto CatBoost e la
calibrazione degli intervalli restano da completare. Le inferenze Timestral
importate non vengono rieseguite dal viewer.

Le audience sono ipotesi comportamentali con evidenze e alternative, non pubblico
reale ricostruito. Gli scenari budget preservano il totale per campagna/giorno,
entro ±20%, con pacing e quote di delivery espliciti. Non stimano causalmente il
ritorno di un aumento di budget. Il video di 180 secondi resta da registrare.

Hydrogen, pool di 72 personas e Gemini Decision 1 sono **P4 opzionale**:
`python -m market_mirror smoke` verifica soltanto quel percorso con fixture.
La consegna principale non richiede una chiave Google. Per test API opzionali:
`requirements-market-mirror.txt` e `.env` alla root da `.env.example`.
Per ricreare l'ambiente: `python3 -m venv .venv-market-mirror`, poi attivazione
e `python -m pip install -r requirements-market-mirror.txt`.

Skill del progetto in `.agents/skills/`; runtime in `market_mirror/`.
Forecasting avanzato nel ramo `feat/timestral-pilot`, collegato tramite export.
