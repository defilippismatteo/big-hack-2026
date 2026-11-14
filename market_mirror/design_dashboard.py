"""Build an offline presentation dashboard from existing artifacts only.

Run: python -m market_mirror.design_dashboard
No inference, API calls or changes to delivery artifacts.
"""
import csv
import hashlib
import json
import math
import sqlite3
import subprocess
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from .unified_dashboard import build_unified_payload

ROOT = Path(__file__).resolve().parents[1]
TIMESTRAL_PILOT_REF = "origin/feat/timestral-pilot"


def _sha256_bytes(raw):
    return hashlib.sha256(raw).hexdigest()


def _num(val, digits=4):
    if val is None or val == "":
        return None
    f = float(val)
    if not math.isfinite(f):
        return None
    return round(f, digits) if digits is not None else f


def _git_show_text(root, ref_spec):
    """Read a blob from a local Git ref without checkout or branch modification."""
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), "show", ref_spec],
            capture_output=True,
            check=False,
        )
    except OSError:
        return None, None
    if proc.returncode != 0 or not proc.stdout:
        return None, None
    return proc.stdout.decode("utf-8-sig"), _sha256_bytes(proc.stdout)


def _inspect_sqlite_ro(db_path):
    """Inspect ledger.sqlite in strict read-only mode without touching WAL/locks."""
    if not db_path.exists():
        return None
    try:
        con = sqlite3.connect(f"file:{db_path.resolve()}?mode=ro", uri=True, timeout=0.5)
    except sqlite3.Error:
        return None
    try:
        cur = con.cursor()
        req_counts = dict(cur.execute("SELECT status, COUNT(*) FROM requests GROUP BY status").fetchall())
        ana_counts = dict(cur.execute("SELECT status, COUNT(*) FROM analyses GROUP BY status").fetchall())
        asset_rows = cur.execute(
            "SELECT asset_id, COUNT(*) FROM analyses WHERE status='completed' GROUP BY asset_id ORDER BY asset_id"
        ).fetchall()
        return {
            "request_status_counts": req_counts,
            "analysis_status_counts": ana_counts,
            "completed_assets": [
                {"asset_id": aid, "completed_questions": cnt} for aid, cnt in asset_rows
            ],
            "completed_assets_count": len(asset_rows),
            "completed_questions_total": sum(cnt for _, cnt in asset_rows),
        }
    except sqlite3.Error:
        return None
    finally:
        con.close()


def _load_live_interviews(interviews_dir, frozen_ids):
    """Load completed interview responses not yet frozen, mapping C01..C12 via manifest."""
    resp_dir = interviews_dir / "responses"
    manifest_path = interviews_dir / "manifest.json"
    if not resp_dir.exists() or not manifest_path.exists():
        return []
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    mapping_by_pid = {j["persona_id"]: j.get("mapping", {}) for j in manifest.get("jobs", [])}
    out = []
    for path in sorted(resp_dir.glob("*.json")):
        if path.name.endswith(".receipt.json"):
            continue
        pid = path.stem
        if pid in frozen_ids:
            continue
        try:
            resp = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        receipt_path = resp_dir / f"{pid}.receipt.json"
        receipt = {}
        if receipt_path.exists():
            try:
                receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                receipt = {}
        mapping = mapping_by_pid.get(pid, {})
        answers = []
        for a in resp.get("answers", []):
            sid = a.get("stimulus_id", "")
            answers.append({
                "stimulus_id": sid,
                "asset_id": mapping.get(sid, sid),
                "first_impression": a.get("first_impression", ""),
                "positive": a.get("positive", ""),
                "negative": a.get("negative", ""),
                "missing": a.get("missing", ""),
                "next_step": a.get("next_step", ""),
                "change": a.get("change", ""),
            })
        overall = resp.get("overall", {})
        out.append({
            "persona_id": pid,
            "frozen": False,
            "status": receipt.get("status", "completed_unfrozen"),
            "model": receipt.get("model"),
            "executed_model": receipt.get("executedModel"),
            "most_useful": [mapping.get(s, s) for s in overall.get("most_useful", [])],
            "least_useful": [mapping.get(s, s) for s in overall.get("least_useful", [])],
            "summary": overall.get("summary", ""),
            "answers": answers,
            "receipt_link": receipt.get("link", ""),
        })
    return out


def _load_history_daily(kit_dir):
    """Aggregate 91 historical days and 15 future calendar days from kit CSVs."""
    hist_path = kit_dir / "storico_giornaliero.csv"
    cal_path = kit_dir / "calendario.csv"
    bud_path = kit_dir / "budget_giornaliero.csv"
    if not hist_path.exists():
        return None

    cal_by_date = {}
    if cal_path.exists():
        with cal_path.open(encoding="utf-8-sig", newline="") as f:
            for r in csv.DictReader(f):
                cal_by_date[r["data"]] = r

    # Deduplicate budget per (data, adset_id) and group by date and vertical
    adset_vertical = {}
    daily_agg = defaultdict(lambda: {"impressions": 0, "clicks": 0, "spend": 0.0, "ads": set(), "adset_budgets": {}})
    vert_daily = defaultdict(lambda: {"impressions": 0, "clicks": 0, "spend": 0.0, "ads": set(), "adset_budgets": {}})
    vert_totals = defaultdict(lambda: {"rows": 0, "impressions": 0, "clicks": 0, "spend": 0.0, "ads": set()})
    lever_totals = defaultdict(lambda: {"rows": 0, "impressions": 0, "clicks": 0, "spend": 0.0, "ads": set()})

    with hist_path.open(encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            day = r["data"]
            vert = r["vertical"]
            asid = r["adset_id"]
            adid = r["ad_id"]
            leva = r["leva"]
            imp = int(float(r["impression"]))
            clk = int(float(r["click"]))
            sp = float(r["spesa"])
            bud = float(r["budget_giornaliero_adset"])
            adset_vertical[asid] = vert

            d = daily_agg[day]
            d["impressions"] += imp
            d["clicks"] += clk
            d["spend"] += sp
            d["ads"].add(adid)
            d["adset_budgets"][asid] = bud

            vd = vert_daily[(day, vert)]
            vd["impressions"] += imp
            vd["clicks"] += clk
            vd["spend"] += sp
            vd["ads"].add(adid)
            vd["adset_budgets"][asid] = bud

            vt = vert_totals[vert]
            vt["rows"] += 1
            vt["impressions"] += imp
            vt["clicks"] += clk
            vt["spend"] += sp
            vt["ads"].add(adid)

            lt = lever_totals[(vert, leva)]
            lt["rows"] += 1
            lt["impressions"] += imp
            lt["clicks"] += clk
            lt["spend"] += sp
            lt["ads"].add(adid)

    def _rates(imp, clk, sp):
        ctr = (100.0 * clk / imp) if imp > 0 else 0.0
        cpm = (1000.0 * sp / imp) if imp > 0 else 0.0
        cpc = (sp / clk) if clk > 0 else None
        return round(ctr, 4), round(cpm, 2), (round(cpc, 4) if cpc is not None else None)

    daily = []
    for day in sorted(daily_agg):
        d = daily_agg[day]
        cal = cal_by_date.get(day, {})
        ctr, cpm, cpc = _rates(d["impressions"], d["clicks"], d["spend"])
        daily.append({
            "data": day,
            "giorno_settimana": cal.get("giorno_settimana", ""),
            "weekend": cal.get("weekend", "") == "si",
            "evento": cal.get("evento", ""),
            "periodo": cal.get("periodo", ""),
            "impressions": d["impressions"],
            "clicks": d["clicks"],
            "spend_eur": round(d["spend"], 2),
            "budget_eur": round(sum(d["adset_budgets"].values()), 2),
            "ctr_pct": ctr,
            "cpm_eur": cpm,
            "cpc_eur": cpc,
            "active_ads": len(d["ads"]),
        })

    by_vertical_daily = []
    for day, vert in sorted(vert_daily):
        vd = vert_daily[(day, vert)]
        ctr, cpm, cpc = _rates(vd["impressions"], vd["clicks"], vd["spend"])
        by_vertical_daily.append({
            "data": day,
            "vertical": vert,
            "impressions": vd["impressions"],
            "clicks": vd["clicks"],
            "spend_eur": round(vd["spend"], 2),
            "budget_eur": round(sum(vd["adset_budgets"].values()), 2),
            "ctr_pct": ctr,
            "cpm_eur": cpm,
            "cpc_eur": cpc,
            "active_ads": len(vd["ads"]),
        })

    future_budget = defaultdict(lambda: defaultdict(float))
    if bud_path.exists():
        with bud_path.open(encoding="utf-8-sig", newline="") as f:
            for r in csv.DictReader(f):
                if r.get("periodo") == "da_prevedere":
                    vert = adset_vertical.get(r["adset_id"], "unknown")
                    future_budget[r["data"]][vert] += float(r["budget_giornaliero_eur"])

    future_calendar = []
    for day in sorted(d for d, c in cal_by_date.items() if c.get("periodo") == "test"):
        c = cal_by_date[day]
        verts = dict(future_budget.get(day, {}))
        future_calendar.append({
            "data": day,
            "giorno_settimana": c.get("giorno_settimana", ""),
            "weekend": c.get("weekend", "") == "si",
            "evento": c.get("evento", ""),
            "budget_total_eur": round(sum(verts.values()), 2),
            "budget_by_vertical": {k: round(v, 2) for k, v in sorted(verts.items())},
        })

    historical_summary = []
    for vert, vt in sorted(vert_totals.items()):
        ctr, cpm, cpc = _rates(vt["impressions"], vt["clicks"], vt["spend"])
        historical_summary.append({
            "vertical": vert,
            "rows": vt["rows"],
            "ads": len(vt["ads"]),
            "impressions": vt["impressions"],
            "clicks": vt["clicks"],
            "spend_eur": round(vt["spend"], 2),
            "ctr_pct": ctr,
            "cpm_eur": cpm,
            "cpc_eur": cpc,
        })

    historical_by_lever = []
    for (vert, leva), lt in sorted(lever_totals.items()):
        ctr, cpm, cpc = _rates(lt["impressions"], lt["clicks"], lt["spend"])
        historical_by_lever.append({
            "vertical": vert,
            "leva": leva,
            "rows": lt["rows"],
            "ads": len(lt["ads"]),
            "impressions": lt["impressions"],
            "clicks": lt["clicks"],
            "spend_eur": round(lt["spend"], 2),
            "ctr_pct": ctr,
            "cpm_eur": cpm,
            "cpc_eur": cpc,
        })

    return {
        "daily": daily,
        "by_vertical_daily": by_vertical_daily,
        "future_calendar": future_calendar,
        "historical_summary": historical_summary,
        "historical_by_lever": historical_by_lever,
    }


def _compact_consegna(rows):
    if not rows:
        return []
    return [
        {
            "data": r["data"],
            "ad_id": r["ad_id"],
            "adset_id": r["adset_id"],
            "asset_id": r["asset_id"],
            "vertical": r["vertical"],
            "campaign_id": r["campaign_id"],
            "leva": r["leva"],
            "formato": r["formato"],
            "budget_giornaliero_adset": _num(r.get("budget_giornaliero_adset"), 2),
            "ctr_predetto_pct": _num(r.get("ctr_predetto_pct"), 4),
            "cpm_predetto_eur": _num(r.get("cpm_predetto_eur"), 2),
            "cpm_p10_eur": _num(r.get("cpm_p10_eur"), 2),
            "cpm_p90_eur": _num(r.get("cpm_p90_eur"), 2),
            "cpc_stimato_eur": _num(r.get("cpc_stimato_eur"), 4),
            "modello": r.get("modello", ""),
        }
        for r in rows
    ]


def _compact_cb_t28(rows):
    if not rows:
        return []
    return [
        {
            "data": r["data"],
            "ad_id": r["ad_id"],
            "adset_id": r["adset_id"],
            "asset_id": r["asset_id"],
            "vertical": r["vertical"],
            "ctr_predetto_pct": _num(r.get("ctr_predetto_pct"), 4),
            "cpm_predetto_eur": _num(r.get("cpm_predetto_eur"), 2),
            "ctr_catboost_pct": _num(r.get("ctr_catboost_pct"), 4),
            "cpm_catboost_eur": _num(r.get("cpm_catboost_eur"), 2),
            "ctr_timestral_p10": _num(r.get("ctr_timestral_p10"), 4),
            "ctr_timestral_p50": _num(r.get("ctr_timestral_p50"), 4),
            "ctr_timestral_p90": _num(r.get("ctr_timestral_p90"), 4),
            "cpm_timestral_p10": _num(r.get("cpm_timestral_p10"), 2),
            "cpm_timestral_p50": _num(r.get("cpm_timestral_p50"), 2),
            "cpm_timestral_p90": _num(r.get("cpm_timestral_p90"), 2),
            "ctr_baseline_pct": _num(r.get("ctr_baseline_pct"), 4),
            "cpm_baseline_eur": _num(r.get("cpm_baseline_eur"), 2),
        }
        for r in rows
    ]


def _compact_bf_enriched(text):
    if not text:
        return []
    out = []
    for r in csv.DictReader(text.splitlines()):
        out.append({
            "data": r["data"],
            "ad_id": r["ad_id"],
            "adset_id": r["adset_id"],
            "asset_id": r["asset_id"],
            "vertical": r["vertical"],
            "leva": r["leva"],
            "formato": r["formato"],
            "budget_giornaliero_adset": _num(r.get("budget_giornaliero_adset"), 2),
            "ctr_scelto_pct": _num(r.get("ctr_scelto_pct"), 4),
            "cpm_scelto_eur": _num(r.get("cpm_scelto_eur"), 2),
            "ctr_settimanale_kit_pct": _num(r.get("ctr_settimanale_kit_pct"), 4),
            "cpm_settimanale_kit_eur": _num(r.get("cpm_settimanale_kit_eur"), 2),
            "ctr_arricchito_pct": _num(r.get("ctr_arricchito_pct"), 4),
            "cpm_arricchito_eur": _num(r.get("cpm_arricchito_eur"), 2),
            "delivery_share": _num(r.get("delivery_share"), 4),
            "budget_stimato_annuncio_eur": _num(r.get("budget_stimato_annuncio_eur"), 2),
            "impression_stimate_base": _num(r.get("impression_stimate_base"), 1),
            "click_stimati_base": _num(r.get("click_stimati_base"), 2),
            "impression_stimate_arricchito": _num(r.get("impression_stimate_arricchito"), 1),
            "click_stimati_arricchito": _num(r.get("click_stimati_arricchito"), 2),
            "cpc_stimato_arricchito_eur": _num(r.get("cpc_stimato_arricchito_eur"), 4),
            "nuovo_annuncio": r.get("nuovo_annuncio") == "True",
        })
    return out


def _build_video_scenes():
    """Return the 9 verified 180-second pitch scenes from Specifica v4 §11 and report 06."""
    return [
        {
            "seq": 1,
            "time": "0–15 s",
            "title": "Il problema: decidere prima di spendere",
            "message": "Chi lancia campagne Meta decide pubblico, creatività e budget prima di avere i risultati. Con Wevion portiamo la decisione prima della spesa.",
            "facts": ["3 campagne Meta (Beauty, Pet, Abbigliamento)", "€16.950 budget pianificato su 15 gg (€1.130/giorno)"],
            "tab": "overview",
        },
        {
            "seq": 2,
            "time": "15–29 s",
            "title": "Il kit Wevion e la sfida cold-start",
            "message": "Non è un dataset statico: 12 annunci nuovi entrano solo nel futuro e il Black Friday 2026 non è presente nello storico recente.",
            "facts": ["91 gg storici (1.879 righe)", "699 righe target (16–30 nov)", "114 righe cold-start (12 annunci, 6 nuovi asset BF)", "2 anomalie QA flaggate (FGR-AS1 €397,55 vs €100)"],
            "tab": "forecast",
        },
        {
            "seq": 3,
            "time": "29–45 s",
            "title": "Pubblico nascosto: 12 ipotesi comportamentali",
            "message": "Senza inventare età o genere non osservabili, confrontiamo gli ad set a parità di asset e giorno nella stessa campagna.",
            "facts": ["AS4 = alta intenzione (CTR 1,89%–2,39%, CPM €9,95–€13,42)", "AS1 = prospecting ampio (CTR 0,89%–1,13%, CPM €5,22–€7,63)", "Confidenza bassa dichiarata + 2 ipotesi alternative"],
            "tab": "audience",
        },
        {
            "seq": 4,
            "time": "45–66 s",
            "title": "Motore quantitativo: confronto onesto tra 5 approcci",
            "message": "Confronto su Fold 1+2 (759 righe): Baseline 14g, CatBoost ad-level, Mistral Timestral-5M/28M ad-set level (12×2×91 + 7 covariate) e Mix 50/50.",
            "facts": ["CPM: Mix 50/50 CatBoost+Timestral-28M migliora su entrambi i fold (WMAE €0,6742, -10,8% vs baseline €0,7559)", "CTR: Baseline 14g stabile (WMAE 0,2260 pp vs 0,2256 pp Mix)"],
            "tab": "validation",
        },
        {
            "seq": 5,
            "time": "66–82 s",
            "title": "Shock Black Friday senza doppio conteggio",
            "message": "Usiamo i benchmark Meta IT 2025 del kit allineati a -364 giorni, rimuovendo la quota stagionale già espressa dalla covariata di Timestral.",
            "facts": ["Indici BW 2025: CPM 156–160, CTR 116–135", "Picco 27/11 arricchito: CPM mediana €17,04, CTR 1,55%", "30/11 Cyber Monday: CPM €13,82, CTR 1,36%"],
            "tab": "forecast",
        },
        {
            "seq": 6,
            "time": "82–107 s",
            "title": "Validazione temporale, anti-leakage e bande q10–q90",
            "message": "Zero data leakage verificato mutando i target futuri. Mostra con trasparenza dove la copertura q10–q90 scende sugli annunci nuovi.",
            "facts": ["Fold 1 (315 righe) & Fold 2 (444 righe) congelati al cutoff", "Copertura CPM Timestral-28M: 82,5%–83,1% globale, 66,7%–69,7% cold-start", "Intervalli marcati non calibrati → roadmap CQR"],
            "tab": "validation",
        },
        {
            "seq": 7,
            "time": "107–137 s",
            "title": "Prototipo: 699 previsioni & Track B diagnostico",
            "message": "Esplorazione interattiva per settore/giorno/ad set con layer qualitativo parallelo (Personas T3 + Decision 1 + Interviste) non calibrato al CTR.",
            "facts": ["600 personas T3 (3 settori, 50% unbiased / 50% in-target)", "Valutazioni gemini-decision-1 & interviste cieche", "Divergenza NDL-B2 (alto eCTR in AS4, 12°/12 su campione misto) e NDL-U1 (scetticismo)"],
            "tab": "creatives",
        },
        {
            "seq": 8,
            "time": "137–165 s",
            "title": "Decisioni: dove spostare il budget in 10 secondi",
            "message": "Riallocazione what-if condizionale entro ±20% a totale campagna invariato, pacing storico e quote 90/10 per esplorare i nuovi annunci.",
            "facts": ["€16.950 invariati → click attesi v4: 18.170,1 → 18.717,6 (+547,5)", "Best CPC BF arricchito: FGR-AS4 €0,56, CDF-AS4 €0,62, NDL-AS2 €0,98"],
            "tab": "audience",
        },
        {
            "seq": 9,
            "time": "165–180 s",
            "title": "Chiusura: riproducibilità, limiti e scala produttiva",
            "message": "Pipeline CPU offline riproducibile con SHA-256 tracciati, test automatici e architettura pronta per produzione multi-tenant.",
            "facts": ["Suite automatica di test verificata", "SHA-256 pesi e sorgenti nel manifest", "Evoluzione scala: DuckDB + GBDT binomiale + TSFM residuo + CQR + Hill curves"],
            "tab": "evidence",
        },
    ]


def build_dashboard(root=ROOT):
    root = Path(root)
    v4 = root / "artifacts/wevion_v4"
    kit_dir = root / "info fornite dagli organizzatori /dati"
    catalog = root / "artifacts/market_mirror/decision_inputs/creative_catalog.json"
    sources = []

    def load(path):
        p = root / path
        if not p.exists():
            return None
        raw = p.read_bytes()
        sources.append({"path": str(p.relative_to(root)), "sha256": _sha256_bytes(raw)})
        if p.suffix == ".json":
            return json.loads(raw)
        if p.suffix == ".csv":
            return list(csv.DictReader(raw.decode("utf-8-sig").splitlines()))
        return raw.decode("utf-8")

    runs = {}
    for label, folder in [("Pool 600", "personas_t3_600"), ("Pilota skincare", "personas_t3")]:
        base = root / "artifacts" / folder
        if (base / "analyses/summary.json").exists():
            run_data = build_unified_payload(
                v4,
                base / "persona_cards.json",
                catalog,
                base / "analyses",
                base / "interviews",
                base / "interviews/REPORT.md",
            )
            frozen_ids = {p["persona_id"] for p in run_data.get("personas", []) if p.get("interview")}
            run_data["sqlite_live"] = _inspect_sqlite_ro(base / "analyses/ledger.sqlite")
            run_data["live_interviews"] = _load_live_interviews(base / "interviews", frozen_ids)
            runs[label] = run_data
            for name in [
                "persona_cards.json",
                "analyses/summary.json",
                "analyses/categorization.json",
                "interviews/frozen.json",
                "interviews/interview_summary.json",
            ]:
                load(f"artifacts/{folder}/{name}")

    # Load optional git branch artifacts from origin/feat/timestral-pilot without checkout
    bf_text, bf_sha = _git_show_text(
        root, f"{TIMESTRAL_PILOT_REF}:Prima_Analisi/Analisi_Completa_Black_Friday/previsioni_arricchite_2026-11-16_30.csv"
    )
    if bf_sha:
        sources.append({"path": f"git:{TIMESTRAL_PILOT_REF}:previsioni_arricchite_2026-11-16_30.csv", "sha256": bf_sha})

    bf_sum_text, bf_sum_sha = _git_show_text(
        root, f"{TIMESTRAL_PILOT_REF}:Prima_Analisi/Analisi_Completa_Black_Friday/riepilogo_analisi.json"
    )
    if bf_sum_sha:
        sources.append({"path": f"git:{TIMESTRAL_PILOT_REF}:riepilogo_analisi.json", "sha256": bf_sum_sha})

    pilot_met_text, pilot_met_sha = _git_show_text(
        root, f"{TIMESTRAL_PILOT_REF}:Prima_Analisi/Validazione_Modelli/metriche.json"
    )
    if pilot_met_sha:
        sources.append({"path": f"git:{TIMESTRAL_PILOT_REF}:Validazione_Modelli/metriche.json", "sha256": pilot_met_sha})

    cpm_storici_all = load("info fornite dagli organizzatori /dati/cpm_storici.csv") or []
    cpm_storici_it = [
        {
            "mese": r["mese"],
            "cpm_mediano": _num(r["cpm_mediano"], 2),
            "cpm_q1": _num(r["cpm_q1"], 2),
            "cpm_q3": _num(r["cpm_q3"], 2),
            "n_campagne": int(r["n_campagne"]),
        }
        for r in cpm_storici_all
        if r.get("piattaforma") == "meta" and r.get("paese") == "IT" and r.get("obiettivo") == "vendite"
    ]

    history_daily = _load_history_daily(kit_dir)
    if (kit_dir / "storico_giornaliero.csv").exists():
        sources.append({
            "path": "info fornite dagli organizzatori /dati/storico_giornaliero.csv",
            "sha256": _sha256_bytes((kit_dir / "storico_giornaliero.csv").read_bytes()),
        })

    payload = {
        "runs": runs,
        "manifest": load("artifacts/wevion_v4/manifest.json"),
        "forecasts": load("artifacts/wevion_v4/forecasts_2026-11-16_30.csv"),
        "forecasts_consegna": _compact_consegna(load("artifacts/wevion_v4/consegna_previsioni_2026-11-16_30.csv")),
        "forecasts_cb_t28": _compact_cb_t28(load("artifacts/wevion_v4/forecast_catboost_timestral_2026-11-16_30.csv")),
        "forecasts_bf_enriched": _compact_bf_enriched(bf_text),
        "bf_summary": json.loads(bf_sum_text) if bf_sum_text else None,
        "history_daily": history_daily,
        "benchmarks_2025": load("info fornite dagli organizzatori /dati/benchmark_mercato_settimanale_2025.csv"),
        "cpm_storici_it": cpm_storici_it,
        "cpm_event_scenarios": load("artifacts/timestral_reproduction/results/cpm_scenari_evento.csv"),
        "audiences": load("artifacts/wevion_v4/persona_adset.json"),
        "audience_evidence": load("artifacts/wevion_v4/audience_evidence_2026-11-15.json"),
        "decisions": load("artifacts/wevion_v4/decisions.json"),
        "scenarios": load("artifacts/wevion_v4/seasonal_scenarios.csv"),
        "quality": load("artifacts/wevion_v4/data_quality.json"),
        "validation": load("artifacts/wevion_v4/validation_metrics.json"),
        "pilot_metrics": json.loads(pilot_met_text) if pilot_met_text else None,
        "catalog": load(str(catalog.relative_to(root))),
        "comparison": load("artifacts/timestral_reproduction/results/method_comparison.csv"),
        "intervals": load("artifacts/timestral_reproduction/results/interval_diagnostics.csv"),
        "verification": load("artifacts/timestral_reproduction/results/verification.json"),
        "creative_analysis_md": load("artifacts/personas_t3/analyses/creative_analysis.reviewed.md"),
        "diagnostic_proposal": load("artifacts/personas_t3/analyses/diagnostic_questions.proposal.json"),
        "video_scenes": _build_video_scenes(),
        "reports": [
            {"title": p.stem.replace("_", " "), "text": load(str(p.relative_to(root)))}
            for p in sorted((root / "docs/report").glob("*.md"))
        ],
        "built_at": datetime.now(timezone.utc).isoformat(),
        "sources": sources,
    }
    template = (Path(__file__).parent / "templates/dashboard_design.html").read_text(encoding="utf-8")
    data = json.dumps(payload, ensure_ascii=False, allow_nan=False).replace("<", "\\u003c")
    return template.replace("__PAYLOAD__", data)


if __name__ == "__main__":
    output = ROOT / "dashboard_design.html"
    output.write_text(build_dashboard(), encoding="utf-8")
    print(output)
