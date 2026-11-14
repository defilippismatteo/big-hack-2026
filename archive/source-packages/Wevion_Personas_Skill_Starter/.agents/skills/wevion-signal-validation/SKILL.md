---
name: wevion-signal-validation
description: Aggrega e verifica se i segnali delle personas migliorano realmente la previsione.
---

# wevion-signal-validation

## Input consentiti
persona_reactions, pesi dichiarati, metriche SOLO di training del fold, baseline e predizioni del modello statistico del ramo forecast per gli stessi split.

## Input vietati e confini
Non usare etichette del holdout per scegliere ipotesi, pesi, parametri o selezionare modelli; non sovrascrivere predizioni già validate.

## Output obbligatori
outputs/persona_signals.csv e outputs/persona_ablation.json con ranking, MAE CTR, differenza rispetto a baseline/forecast-only, fold/seed/provenienza.

## Procedura essenziale
Confrontare baseline, simulazione isolata, baseline+simulazione. Fare split temporale; ricordare che ogni nuovo fold richiede audience inferite senza i dati del fold. Persona signals possono entrare nel forecasting solo se migliorano holdout; il CPM rimane al modello quantitativo.

## Requisiti comuni
Restituire JSON valido, versione schema, cut-off, modello, seed, errori e fonte dei dati. Segnalare i limiti senza riempire a fantasia. Non leggere altri file, anche se accessibili tecnicamente.
