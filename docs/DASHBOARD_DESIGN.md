# Wevion · Dashboard Design (`dashboard_design.html`)

Dashboard HTML standalone offline generata da `market_mirror/design_dashboard.py` e dal template `market_mirror/templates/dashboard_design.html` secondo i criteri della specifica operativa (`BigHack2026_Wevion_Specifica_Operativa_v4.md` §§8 e 11), la skill `frontend-design` e i pattern accessibili di `modern-web-guidance`.

## Direzione Visiva & Principi Epistemici

- **Estetica vettoriale da laboratorio (light-only):** fondo carta `#FAF9FC`, superfici `#FFFFFF` con bordi `#E4E2EE`, inchiostro `#111118` e scala cromatica dedicata per separare i piani epistemici:
  - **Viola (`#6D28D9`):** orizzonte futuro 16–30 novembre 2026, picchi Black Week / Black Friday / Cyber Monday, annunci cold-start e azioni decisionali.
  - **Blu quantitativo (`#1D4ED8`):** serie storica osservata (91 giorni, `1.879` righe), modelli e metriche di backtest su Track A.
  - **Verde ottanio (`#0F766E`):** Track B qualitativo sintetico (`simulation_blind`, `calibrated_to_ctr: false`).
  - **Ambra (`#B45309`):** cautele metodologiche (`confidence: bassa`, intervalli `q10–q90` non calibrati, anomalie QA).
- **Barriera informativa esplicita:** Track B non riceve mai metriche storiche o costi e non altera né le previsioni quantitative né l'allocazione budget di Track A.
- **Offline-first:** zero CDN esterni, font stack di sistema/editoriali (`serif` per display, `sans` per testo, `monospace` con `tabular-nums` per i numeri) e grafici SVG generati lato client.

## Architettura a 8 Sezioni

1. **Panoramica & 10s (`tab-overview`):** grafico orizzonte 106 giorni (`91` osservati + cutoff `15/11` + `15` previsti), matrice decisionale in 10 secondi per le 3 campagne (`CDF-C1`, `NDL-C1`, `FGR-C1`) con delta click a budget invariato e schema di separazione Track A / Track B.
2. **Previsioni 699 & BF (`tab-forecast`):** selettore modello (`Arricchito BF/CM 2025`, `Consegna v4`, `Consegna Mix 50/50`, `CatBoost vs Timestral-28M con p10–p90`), filtro per settore/giorno/cold-start, benchmark Meta IT 2025 e scenari esterni (`Biddyco`, `Gupta Media`), heatmap interattiva 51 annunci × 15 giorni, tabella ordinabile ed esportazione CSV.
3. **Audience & Budget (`tab-audience`):** simulatore what-if con cursori `±20%` per ad set (verifica invarianza totale campagna `€1.130/g = €16.950`) e 12 schede ipotesi comportamentali con confronto `matched_asset_day_comparison`, breakdown leve/formati e 2 spiegazioni alternative.
4. **Creatività 36 & Test A/B (`tab-creatives`):** catalogo completo 36 creatività con affiancamento Track A (`eCTR/eCPM`) e Track B (`click_intent_signal`, `attention_signal`, `unbiased` vs `category_conditioned`), alert di divergenza (`NDL-B2`, `NDL-U1`), 4 test A/B controllati e proposta diagnostica.
5. **Personas T3 (`tab-personas`):** selettore run (`Pool 600` vs `Pilota skincare`), banner SQLite read-only (`?mode=ro` su `ledger.sqlite`), filtri per settore/coorte/segmento/ricerca con paginazione e modale dettagliata (`<dialog closedby="any">`).
6. **Interviste Cieche (`tab-interviews`):** selettore tra interviste congelate (`Pilota skincare`) e interviste live completate (`Pool 600`), conteggio stimoli `most_useful` / `least_useful`, trascrizioni `C01..C12` risolte ad `asset_id` e `REPORT.md`.
7. **Validazione, QA & Scala (`tab-validation`):** confronto modelli su Fold 1 (`315` righe), Fold 2 (`444` righe) e Aggregato (`759` righe) separato su `tutti`, `annunci_gia_visti` e `annunci_nuovi`, copertura bande `q10–q90`, audit QA (`FGR-AS1`, `CDF-AS3`, `9` righe a zero click), perimetro dati e stack large-scale (`DuckDB + Parquet + GBDT + TSFM residuo + CQR + Hill`).
8. **Video 180s & Report (`tab-evidence`):** storyboard interattivo cronologico a 9 scene (`01..09`, `0–180 s`) con salto alle viste corrispondenti, lettore dei 7 report (`docs/report/00..06`) e registro SHA-256 provenance.

## Pattern Accessibili (`modern-web-guidance`)

- **Tabs:** `role="tablist"` scorrevole orizzontalmente con indicatore attivo combinato colore + bordo inferiore su pseudo-elemento (`::after`), navigazione `ArrowLeft` / `ArrowRight` / `Home` / `End`, pannelli inattivi con `hidden="until-found"` senza margini/padding/bordi su `[role="tabpanel"]` e riattivazione automatica via `beforematch`.
- **Tabelle responsive e ordinabili:** contenitori scrollabili `tabindex="0"` con `role="region"` e `container-type: inline-size`, intestazioni sticky, pulsanti `<button type="button">` dentro `<th scope="col">`, `aria-sort` solo sulla colonna attiva, spostamento DOM in-place (`tbody.moveBefore` con fallback `appendChild`) e singolo annuncio `<div role="status">` nascosto visivamente via `clip-path: inset(50%)`.
- **Finestre modali:** `<dialog closedby="any">` aperto con `showModal()` e fallback geometrico click-outside per browser privi di supporto `closedBy`.

## Rigenerazione Offline

```bash
cd big-hack-2026
.venv-market-mirror/bin/python -m market_mirror design-dashboard
# opzionale: --root /percorso/repo --out /percorso/output.html
```

Il comando legge esclusivamente gli artefatti presenti su disco e, in sola lettura non distruttiva tramite `git show`, gli output su `origin/feat/timestral-pilot`.
