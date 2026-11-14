# Wevion BigHack 2026 · Kit dei dati

Prima leggete il PDF `Wevion-BigHack-sfida.pdf`: lì c'è la sfida. Questo file spiega i dati e le colonne.

**I dati sono simulati.** Sono costruiti per somigliare a campagne vere gestite con Wevion, ma inserzionisti,
creatività e numeri sono di fantasia. Nessun dato appartiene a un cliente reale.

## Cosa c'è in `dati/`

È il materiale da cui partite: lo leggete, lo analizzate, ci costruite sopra lo strumento. Non va riconsegnato.


| File | Cosa contiene |
|---|---|
| `inserzionisti.csv` | I 3 inserzionisti (uno per settore: beauty e skincare, e-commerce pet, abbigliamento). |
| `campagne.csv` | Le 3 campagne Meta (Facebook e Instagram), obiettivo vendite. |
| `adset.csv` | I 12 ad set, 4 per campagna. **Il pubblico non c'è: lo immaginate voi.** |
| `annunci.csv` | I 69 annunci: quale asset creativo gira in quale ad set, e quando parte e finisce. |
| `asset_creativi/asset_<settore>.csv` | Gli asset creativi, un file per settore: leva, formato, headline, testo, CTA, descrizione della visual, data di lancio. |
| `storico_giornaliero.csv` | Lo storico giorno per giorno di ogni annuncio, dal 17/08/2026 al 15/11/2026 (91 giorni). |
| `budget_giornaliero.csv` | Il budget giornaliero di ogni ad set, anche per il periodo da prevedere. |
| `da_prevedere.csv` | Le righe del periodo da prevedere, dal 16/11/2026 al 30/11/2026: annuncio e giorno, senza risultati. |
| `cpm_storici.csv` | Il CPM di mercato per mese, piattaforma, paese e obiettivo, da gennaio 2025 a ottobre 2026. |
| `benchmark_mercato_settimanale_2025.csv` | L'andamento settimanale di CPM e CTR del mercato nell'autunno 2025, per settore (100 = media set-ott 2025). |
| `calendario.csv` | I giorni del periodo, con weekend ed eventi (Black Friday 27/11, Cyber Monday 30/11, ...). |

Come sono collegati: **campagna → ad set → annuncio → asset creativo**.
`annunci.csv` dice quale `asset_id` gira in quale `adset_id`; lo stesso asset può girare in più ad set.

## Le parole che servono

- **KPI**: un numero che dice se una campagna sta andando bene. CTR e CPM sono due esempi, non gli unici:
  potete usare anche altri KPI (CPC, frequenza, copertura, spesa...). Fatevi guidare dai dati.
- **Impression**: quante volte l'annuncio è stato mostrato.
- **Click**: quante volte qualcuno ci ha cliccato (clic sul link).
- **CTR**: click ÷ impression × 100, in percentuale. Esempio: 150 click su 12.500 impression = 1,2%.
- **CPM**: quanto costano mille impression, in euro. CPM = spesa ÷ impression × 1000. Esempio: 100 € per 12.500 impression = 8 €.
- **CPC**: quanto costa un click, in euro. CPC = spesa ÷ click.
- **Copertura**: quante persone diverse hanno visto l'annuncio quel giorno. **Frequenza** = impression ÷ copertura.
- **Ad set**: il gruppo di annunci che condivide budget e pubblico.
- **Leva** dell'asset: `scarcity` (scarsità, "ultimi pezzi"), `urgency` (urgenza, "solo oggi", "scade tra..."),
  `black_friday` (saldi del Black Friday).

## Le colonne

### `storico_giornaliero.csv` (una riga per annuncio e giorno)
| Colonna | Significato |
|---|---|
| `data`, `giorno_settimana` | Il giorno (AAAA-MM-GG). |
| `piattaforma` | `meta`. |
| `inserzionista_id`, `vertical` | Inserzionista e settore. |
| `campaign_id`, `campaign_name`, `adset_id`, `ad_id`, `asset_id` | Dove sta l'annuncio e quale creatività usa. |
| `leva`, `formato` | Leva e formato dell'asset (immagine, video, carosello). |
| `budget_giornaliero_adset` | Il budget giornaliero dell'ad set quel giorno, in euro. Meta lo divide tra gli annunci attivi. |
| `spesa` | Euro spesi da quell'annuncio quel giorno. |
| `impression`, `copertura`, `frequenza`, `click` | Vedi sopra. |
| `ctr` | In percentuale. |
| `cpc` | Costo per click in euro (vuoto se 0 click). |
| `cpm` | Euro per mille impression. |

### `da_prevedere.csv`
Ha le stesse chiavi dello storico (`data`, `ad_id`, `adset_id`, `asset_id`, `leva`, `formato`, ...) e il budget
dell'ad set, ma nessun risultato: quelli li prevede il vostro strumento.
Nel periodo da prevedere partono anche annunci nuovi, che nello storico non ci sono.

### `asset_creativi/asset_<settore>.csv`
| Colonna | Significato |
|---|---|
| `asset_id`, `vertical` | Identificativo e settore. |
| `leva` | `scarcity`, `urgency` o `black_friday`. |
| `formato`, `durata_video_s` | Immagine, video (con durata in secondi) o carosello. |
| `headline`, `testo_principale`, `call_to_action` | I testi dell'annuncio. |
| `descrizione_visual` | Cosa si vede: al posto dell'immagine o del video c'è una descrizione fedele. |
| `data_lancio`, `data_fine` | Quando l'asset entra ed esce (vuota = ancora attivo). |

### `adset.csv`
`adset_id`, `campaign_id`, `adset_name`, `ottimizzazione`, `strategia_offerta`, `budget_giornaliero_iniziale`.
La colonna `pubblico` dice "da definire": il pubblico lo ipotizzate voi dai dati e lo motivate.

### `cpm_storici.csv`
`piattaforma`, `paese`, `mese`, `obiettivo`, `cpm_mediano`, `cpm_q1`, `cpm_q3` (25° e 75° percentile), `n_campagne`.

### `benchmark_mercato_settimanale_2025.csv`
`settimana_dal` (il lunedì), `vertical`, `piattaforma`, `paese`, `indice_cpm`, `indice_ctr`.

## Cosa consegnate

Sono i tre passi del PDF:

1. **Lo strumento**: il codice o il prototipo funzionante, in un repository. Mostra pubblici, previsioni e decisioni.
2. **Le previsioni**: i KPI previsti dal vostro strumento per ogni annuncio e ogni giorno dal 16 al 30 novembre
   (le righe di `dati/da_prevedere.csv`). I KPI li scegliete voi, guidati dai dati; il formato pure: mostrateli
   nello strumento o allegateli al repository.
3. **Il ragionamento**: i pubblici immaginati per ogni ad set, con la motivazione, e come ci siete arrivati, in un
   README e in un video di 3 minuti.

Per misurarvi da soli potete usare le ultime due settimane dello storico (02/11-15/11) come validazione:
prevedetele usando solo i dati fino all'01/11 e confrontate con i valori veri.

I file sono CSV in UTF-8, con la virgola come separatore. Se Excel mostra male gli accenti, importateli con
"Dati > Da testo/CSV" e scegliete UTF-8.
