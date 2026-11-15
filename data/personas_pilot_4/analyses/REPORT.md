# Decision 1 · primo giro skincare

Completati 12 asset × 4 persone = 48 valutazioni.
Richieste registrate: 13; completate: 12; una risposta HTTP429, ripresa solo sull'asset rifiutato.
Token input dichiarati dall'API: 53056; output token: zero secondo il protocollo Decisions.
Costo monetario non misurato. Tempi delle singole risposte e uso token originali sono conservati nei raw.

## Interpretazione
Probabilità su opzioni chiuse di persone sintetiche: non CTR reali, CPM, vendite o ricavi.
Il ranking è una media uniforme di quattro persone, un probe tecnico senza rappresentatività o significatività statistica dimostrate.
Stessa identità e stesso layout/orario di feed per persona tra asset. Un solo annuncio, con visual descritta testualmente.

| Asset | Titolo | Intenzione click (score) | Attenzione (score) |
|---|---|---:|---:|
| NDL-S3 | Edizione limitata: kit routine autunno | 0.1392 | 0.6974 |
| NDL-S4 | Rimasti in pochi: SPF 50 invisibile | 0.1363 | 0.6618 |
| NDL-S2 | Torna disponibile, ma per poco | 0.1277 | 0.5775 |
| NDL-B3 | Black Friday: fino al -40% | 0.1244 | 0.6423 |
| NDL-S1 | Siero Vitamina C: ultimi 200 flaconi | 0.1232 | 0.6236 |
| NDL-U2 | Spedizione gratis: scade domenica | 0.1200 | 0.6335 |
| NDL-U4 | Ultime 24 ore: regalo con ogni ordine | 0.1188 | 0.6194 |
| NDL-U3 | 48 ore per la tua routine a -15% | 0.1160 | 0.6224 |
| NDL-B1 | Black Friday anticipato: -25% | 0.0842 | 0.5468 |
| NDL-B4 | Black Friday: solo oggi -40% | 0.0821 | 0.4807 |
| NDL-U1 | Solo fino a mezzanotte: -20% | 0.0794 | 0.4775 |
| NDL-B2 | La Black Week è iniziata | 0.0625 | 0.5276 |

## Differenze fra persone

- Chiara Bellini (31 anni): NDL-S3 (0.0493), NDL-S2 (0.0433), NDL-S1 (0.0408).
- Patrizia Ferri (64 anni): NDL-S2 (0.3093), NDL-S3 (0.2862), NDL-U3 (0.2651).
- Lorenzo Cattaneo (53 anni): NDL-S3 (0.1527), NDL-B3 (0.1520), NDL-S1 (0.1265).
- Davide Marchetti (52 anni): NDL-S4 (0.1831), NDL-U4 (0.1341), NDL-B4 (0.1039).

Queste differenze sono indizi esplorativi sulle risposte dei profili, non nicchie di mercato già dimostrate.

## Registro e riuso
ledger.sqlite è il registro persistente, ledger.json la sua versione leggibile. Conservare questi file insieme a raw/ e assets/.
La chiave di analisi comprende persona, input effettivo, asset, modello, istruzioni e scenario. Un panel più ampio invia solo le persone nuove; un semplice riordino non ripete le analisi.
Il replay finale ha riutilizzato tutte le 48 risposte con zero API. Il risultato è verificato anche dai test su cache/riordino/estensione.
Stati pending, ambiguous e invalid_response richiedono ispezione: nessuna ripetizione automatica. Rejected può essere ripreso solo esplicitamente.

## Comandi
```bash
python -m personas_simulation.runtime analyze  # solo cache: zero API
python -m personas_simulation.runtime analysis-view
# Worker T3 per analisi nuove autorizzate:
python -m personas_simulation.runtime analyze --live
```
La cadenza predefinita di 6,5 secondi fra nuove richieste limita il burst; non è una dichiarazione del rate limit assegnato da Google.

Nessuna integrazione Timestral eseguita nel run.
