"""Build the standalone unified dashboard combining Track A (v4) and Track B (600 personas, Decision 1, blind interviews, and separate summarizer insights)."""
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

from .contracts import read
from .decision_runs import CAMPAIGN_BY_VERTICAL
from .feed import exposure


def _load_forecast_by_asset(v4_dir):
    path = Path(v4_dir) / "forecasts_2026-11-16_30.csv"
    if not path.exists():
        return {}
    buckets = defaultdict(list)
    with path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            buckets[row["asset_id"]].append((float(row["ctr_predetto_pct"]), float(row["cpm_predetto_eur"])))
    out = {}
    for aid, pairs in buckets.items():
        n = len(pairs)
        out[aid] = {
            "avg_ctr_pct": round(sum(x[0] for x in pairs) / n, 4),
            "avg_cpm_eur": round(sum(x[1] for x in pairs) / n, 2),
            "forecast_rows": n,
        }
    return out


def _load_seasonal_summary(v4_dir):
    path = Path(v4_dir) / "seasonal_scenarios.csv"
    if not path.exists():
        return []
    buckets = defaultdict(list)
    with path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            ctr_val = row.get("ctr_scenario_pct") or row.get("ctr_predetto_pct")
            cpm_val = row.get("cpm_scenario_eur") or row.get("cpm_predetto_eur")
            buckets[(row["vertical"], row["scenario"])].append(
                (float(ctr_val), float(cpm_val))
            )
    out = []
    for (vert, scen), vals in sorted(buckets.items()):
        n = len(vals)
        out.append({
            "vertical": vert,
            "scenario": scen,
            "rows": n,
            "avg_ctr_pct": round(sum(v[0] for v in vals) / n, 3),
            "avg_cpm_eur": round(sum(v[1] for v in vals) / n, 2),
        })
    return out


def _aggregate_adsets(decisions_json, persona_adset_json):
    if decisions_json.get("adsets"):
        return decisions_json["adsets"]
    pa_map = {a["adset_id"]: a for a in persona_adset_json.get("adsets", [])}
    buckets = defaultdict(list)
    for r in decisions_json.get("rows", []):
        buckets[r["adset_id"]].append(r)
    adsets = []
    for asid, rows in sorted(buckets.items()):
        pa = pa_map.get(asid, {})
        sig = pa.get("segnali_osservati", {})
        rec_counts = Counter(r["recommended_asset_id"] for r in rows)
        top_rec = rec_counts.most_common(1)[0][0] if rec_counts else ""
        n = len(rows)
        adsets.append({
            "adset_id": asid,
            "campaign_id": rows[0]["campaign_id"],
            "vertical": rows[0]["vertical"],
            "ctr_storico_pct": round(float(sig.get("ctr_storico_pct", 0.0)), 4),
            "ectr_pct": round(sum(r["ectr_pct"] for r in rows) / n, 4),
            "ecpm_eur": round(sum(r["ecpm_eur"] for r in rows) / n, 2),
            "budget_base_eur": round(sum(r["budget_base_eur"] for r in rows), 2),
            "budget_scenario_eur": round(sum(r["budget_scenario_eur"] for r in rows), 2),
            "expected_clicks_base": round(sum(r["expected_clicks_base"] for r in rows), 1),
            "expected_clicks_scenario": round(sum(r["expected_clicks_scenario"] for r in rows), 1),
            "recommended_asset_id": top_rec,
            "segmento_ipotizzato": pa.get("segmento_ipotizzato", ""),
        })
    return adsets


def build_unified_payload(
    v4_dir,
    cards_path,
    catalog_path,
    analyses_dir,
    interviews_dir,
    report_md_path=None,
    seed=2026,
):
    v4_dir = Path(v4_dir)
    analyses_dir = Path(analyses_dir)
    interviews_dir = Path(interviews_dir)

    manifest = read(v4_dir / "manifest.json")
    dq = read(v4_dir / "data_quality.json")
    val = read(v4_dir / "validation_metrics.json")
    decisions_json = read(v4_dir / "decisions.json")
    pa_path = v4_dir / "persona_adset.json"
    persona_adset_json = read(pa_path) if pa_path.exists() else {"adsets": []}
    cards = read(cards_path)
    catalog = read(catalog_path)
    summary = read(analyses_dir / "summary.json")
    cat_path = analyses_dir / "categorization.json"
    categorization = read(cat_path) if cat_path.exists() else {}

    frozen_path = interviews_dir / "frozen.json"
    frozen = read(frozen_path) if frozen_path.exists() else {"interviews": []}
    camp_op_path = interviews_dir / "campaign_opinions.json"
    camp_opinions = read(camp_op_path) if camp_op_path.exists() else {"campaigns": [], "assets": []}
    int_summary_path = interviews_dir / "interview_summary.json"
    interview_summary = read(int_summary_path) if int_summary_path.exists() else {}

    forecast_by_asset = _load_forecast_by_asset(v4_dir)
    seasonal_summary = _load_seasonal_summary(v4_dir)
    creatives_map = {c["asset_id"]: c for c in catalog["creatives"]}

    # Build compact per-persona map combining cards + Decision 1 evaluations + interview transcript
    dec_by_asset = {a["asset_id"]: a for a in summary.get("ranking", [])}
    person_evals = defaultdict(list)
    for aid, asset_sig in dec_by_asset.items():
        cr = creatives_map.get(aid, {})
        for pp in asset_sig["per_person"]:
            top_pair = max(pp["probabilities"].items(), key=lambda kv: kv[1])
            reason_agg = Counter()
            for k, v in pp["probabilities"].items():
                _, r = k.split("__", 1)
                reason_agg[r] += v
            person_evals[pp["persona_id"]].append({
                "asset_id": aid,
                "headline": cr.get("headline", aid),
                "leva": cr.get("leva", ""),
                "formato": cr.get("formato", ""),
                "actions": {k: round(v, 4) for k, v in pp["actions"].items()},
                "reasons": {k: round(v, 4) for k, v in reason_agg.items()},
                "top_pair": top_pair[0],
                "top_pair_prob": round(top_pair[1], 4),
            })

    interview_by_pid = {}
    for item in frozen.get("interviews", []):
        pid = item["persona_id"]
        mapping = item["mapping"]
        resp = item["response"]
        answers = []
        for a in resp.get("answers", []):
            answers.append({
                "asset_id": mapping.get(a["stimulus_id"], a["stimulus_id"]),
                "stimulus_id": a["stimulus_id"],
                "first_impression": a["first_impression"],
                "positive": a["positive"],
                "negative": a["negative"],
                "missing": a["missing"],
                "next_step": a["next_step"],
                "change": a["change"],
            })
        interview_by_pid[pid] = {
            "mode": resp.get("mode", "full"),
            "punti_a_favore": resp.get("punti_a_favore", ""),
            "perche_si_allontana": resp.get("perche_si_allontana", ""),
            "most_useful": [mapping.get(s, s) for s in resp["overall"]["most_useful"]],
            "least_useful": [mapping.get(s, s) for s in resp["overall"]["least_useful"]],
            "summary": resp["overall"]["summary"],
            "answers": answers,
            "receipt_link": item.get("receipt", {}).get("link", ""),
        }

    cat_by_pid = {p["persona_id"]: p for p in categorization.get("personas", [])}
    personas_out = []
    for p in cards["personas"]:
        pid = p["persona_id"]
        camp = CAMPAIGN_BY_VERTICAL.get(p["vertical"], {"campaign_id": p["vertical"], "campaign_name": p["vertical"]})
        evals = sorted(person_evals.get(pid, []), key=lambda x: -x["actions"]["click"])
        cinfo = cat_by_pid.get(pid, {})
        avg_actions = cinfo.get("mean_actions") or (
            {k: round(sum(e["actions"][k] for e in evals) / len(evals), 4) for k in ("scroll", "glance", "stop", "click")}
            if evals else {"scroll": 0, "glance": 0, "stop": 0, "click": 0}
        )
        avg_reasons = dict(cinfo.get("top_reasons", []))
        if not avg_reasons and evals:
            rc = Counter()
            for e in evals:
                for rk, rv in e["reasons"].items():
                    rc[rk] += rv
            avg_reasons = {k: round(v / len(evals), 4) for k, v in rc.most_common(6)}

        personas_out.append({
            "persona_id": pid,
            "name": p.get("name", pid),
            "age_years": p.get("age_years"),
            "age_band": p.get("age_band"),
            "gender_identity": p.get("gender_identity"),
            "vertical": p["vertical"],
            "campaign_id": camp["campaign_id"],
            "cohort": p.get("cohort", "unbiased"),
            "motivation": p.get("motivation"),
            "social_habit": p.get("social_habit"),
            "risk_attitude": p.get("risk_attitude"),
            "interest_in_category": p.get("interest_in_category"),
            "interests": p.get("interests", []),
            "occupation": p.get("occupation", ""),
            "economic_context": p.get("economic_context", ""),
            "daily_routine": p.get("daily_routine", ""),
            "decision_habits": p.get("decision_habits", ""),
            "trust_requirements": p.get("trust_requirements", ""),
            "ad_avoidance": p.get("ad_avoidance", ""),
            "concerns": p.get("concerns", ""),
            "contradiction": p.get("contradiction", ""),
            "persona_summary": p.get("persona_summary", ""),
            "segment": cinfo.get("segment", "unknown"),
            "dominant_action": cinfo.get("dominant_action", ""),
            "dominant_reason": cinfo.get("dominant_reason", ""),
            "feed": exposure(p, seed),
            "avg_actions": avg_actions,
            "avg_reasons": avg_reasons,
            "evaluations": evals,
            "interview": interview_by_pid.get(pid),
        })

    # Asset table combining Decision 1 + cohorts + interviews + quantitative forecast
    op_by_asset = {a["asset_id"]: a for a in camp_opinions.get("assets", [])}
    cat_by_asset = {a["asset_id"]: a for a in categorization.get("assets", [])}
    assets_out = []
    for idx, sig in enumerate(summary.get("ranking", []), 1):
        aid = sig["asset_id"]
        cr = creatives_map.get(aid, {})
        camp = CAMPAIGN_BY_VERTICAL.get(sig["vertical"], {"campaign_id": sig["vertical"], "campaign_name": sig["vertical"]})
        op = op_by_asset.get(aid, {})
        ca = cat_by_asset.get(aid, {})
        assets_out.append({
            "rank": idx,
            "asset_id": aid,
            "campaign_id": camp["campaign_id"],
            "campaign_name": camp["campaign_name"],
            "vertical": sig["vertical"],
            "leva": cr.get("leva", ""),
            "formato": cr.get("formato", ""),
            "headline": cr.get("headline", ""),
            "testo_principale": cr.get("testo_principale", ""),
            "call_to_action": cr.get("call_to_action", ""),
            "descrizione_visual": cr.get("descrizione_visual", ""),
            "n_personas": sig["n_personas"],
            "click_intent_signal": round(sig["click_intent_signal"], 5),
            "attention_signal": round(sig["attention_signal"], 5),
            "actions": {k: round(v, 5) for k, v in sig["actions"].items()},
            "top_reasons": ca.get("top_reasons", []),
            "by_cohort": ca.get("by_cohort", {}),
            "most_useful_count": op.get("most_useful_count", 0),
            "least_useful_count": op.get("least_useful_count", 0),
            "net_interview_mentions": op.get("most_useful_count", 0) - op.get("least_useful_count", 0),
            "forecast": forecast_by_asset.get(aid),
        })

    # Campaign summary combining Decision 1 + Interviews + Forecast
    adset_rows = _aggregate_adsets(decisions_json, persona_adset_json)
    campaigns_out = []
    for camp_info in categorization.get("campaigns", []):
        cid = camp_info["campaign_id"]
        c_assets = [a for a in assets_out if a["campaign_id"] == cid]
        c_adsets = [a for a in adset_rows if a["campaign_id"] == cid]
        c_op = next((c for c in camp_opinions.get("campaigns", []) if c["campaign_id"] == cid), {})
        pos_m = sum(a["most_useful_count"] for a in c_assets)
        neg_m = sum(a["least_useful_count"] for a in c_assets)
        tot_budget_base = sum(a["budget_base_eur"] for a in c_adsets)
        tot_clicks_scen = sum(a["expected_clicks_scenario"] for a in c_adsets)
        mean_ectr = sum(a["ectr_pct"] for a in c_adsets) / len(c_adsets) if c_adsets else 0
        mean_ecpm = sum(a["ecpm_eur"] for a in c_adsets) / len(c_adsets) if c_adsets else 0
        campaigns_out.append({
            "campaign_id": cid,
            "campaign_name": camp_info["campaign_name"],
            "vertical": camp_info["vertical"],
            "n_assets": len(c_assets),
            "n_personas": sum(p["campaign_id"] == cid for p in personas_out),
            "n_interviews": c_op.get("n_interviews", 0),
            "mean_click_intent_signal": camp_info["mean_click_intent_signal"],
            "mean_attention_signal": camp_info["mean_attention_signal"],
            "most_useful_mentions": pos_m,
            "least_useful_mentions": neg_m,
            "net_interview_mentions": pos_m - neg_m,
            "by_lever": camp_info.get("by_lever", []),
            "interview_by_lever": c_op.get("by_lever", []),
            "top_asset": c_assets[0]["asset_id"] if c_assets else "",
            "bottom_asset": c_assets[-1]["asset_id"] if c_assets else "",
            "quant_budget_15d_eur": round(tot_budget_base, 2),
            "quant_expected_clicks_15d": round(tot_clicks_scen, 1),
            "quant_mean_ectr_pct": round(mean_ectr, 3),
            "quant_mean_ecpm_eur": round(mean_ecpm, 2),
        })

    ext_bt = {b["cutoff"]: b for b in (val.get("reported_external") or {}).get("backtest", [])}
    folds_out = []
    for idx, f in enumerate(val.get("folds", []), 1):
        bt = ext_bt.get(f["cutoff"], {}).get("annunci", {})
        baseline = f.get("baseline") or bt.get("baseline") or f.get("metrics", {})
        timestral = f.get("timestral") or bt.get("timestral_adjusted") or f.get("metrics", {})
        folds_out.append({
            "fold": f.get("fold", idx),
            "cutoff": f["cutoff"],
            "start": f["start"],
            "end": f["end"],
            "rows": f["rows"],
            "cold_start_rows": f.get("cold_start_rows", 0),
            "baseline": baseline,
            "timestral": timestral,
        })

    report_md = ""
    if report_md_path and Path(report_md_path).exists():
        report_md = Path(report_md_path).read_text(encoding="utf-8")

    return {
        "meta": {
            "cutoff": manifest.get("cutoff", "2026-11-15"),
            "forecast_method": manifest.get("forecast_source", {}).get("method", "ctr_baseline14d__cpm_timestral28m"),
            "forecast_rows": manifest.get("forecast_rows", 699),
            "audience_cards": manifest.get("audience_cards", 12),
            "decision_rows": manifest.get("decision_rows", 180),
            "calibrated_to_ctr": False,
            "persona_count": len(personas_out),
            "evaluated_assets_t3": summary.get("assets", 0),
            "evaluated_pairs_t3": summary.get("persona_asset_evaluations", 0),
            "input_tokens_t3": summary.get("usage", {}).get("reported_input_tokens") or 0,
            "interviews_count": len(frozen.get("interviews", [])),
        },
        "data_quality": dq,
        "folds": folds_out,
        "adsets": adset_rows,
        "seasonal_summary": seasonal_summary,
        "categorization_summary": {
            "segment_counts": categorization.get("segment_counts", {}),
            "dominant_reason_counts": categorization.get("dominant_reason_counts", {}),
        },
        "campaigns": campaigns_out,
        "assets": assets_out,
        "personas": personas_out,
        "interview_summary": interview_summary,
        "report_md": report_md,
    }


def render_unified_dashboard(payload):
    data_json = json.dumps(payload, ensure_ascii=False, allow_nan=False).replace("<", "\\u003c")
    return HTML_TEMPLATE.replace("__DATA_JSON__", data_json)


HTML_TEMPLATE = r'''<!doctype html>
<html lang="it">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Wevion · Dashboard Unificata 600 Personas, Decision 1 &amp; Interviste</title>
  <style>
    :root {
      --bg: #f6f8fb;
      --surface: #ffffff;
      --surface-2: #f1f5f9;
      --border: #dbe3ee;
      --ink: #0f172a;
      --text: #1e293b;
      --muted: #526277;

      --quant: #1d4ed8;
      --quant-bg: #eff6ff;
      --quant-bd: #bfdbfe;

      --synth: #0f766e;
      --synth-bg: #f0fdfa;
      --synth-bd: #99f6e4;

      --warn: #92400e;
      --warn-bg: #fffbeb;
      --warn-bd: #fcd34d;

      --pos: #15803d;
      --pos-bg: #f0fdf4;
      --pos-bd: #bbf7d0;

      --neg: #b91c1c;
      --neg-bg: #fef2f2;
      --neg-bd: #fecaca;

      --shield: #334155;
      --shield-bg: #f1f5f9;
      --shield-bd: #cbd5e1;

      --radius: 12px;
      --shadow: 0 1px 2px rgb(15 23 42 / 0.05), 0 4px 12px rgb(15 23 42 / 0.04);
    }

    * { box-sizing: border-box; }
    body { margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Inter, sans-serif; background: var(--bg); color: var(--text); line-height: 1.5; -webkit-font-smoothing: antialiased; }
    :focus-visible { outline: 2px solid var(--ink); outline-offset: 2px; }
    code { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, monospace; font-size: 0.88em; background: var(--surface-2); padding: 0.1rem 0.35rem; border-radius: 5px; color: var(--ink); overflow-wrap: anywhere; }
    .container { width: 100%; max-width: 1280px; margin: 0 auto; padding: 1rem 1rem 2.5rem; }

    header.hero { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 1.25rem 1.35rem; box-shadow: var(--shadow); margin-bottom: 1rem; min-width: 0; }
    .hero-head { display: flex; flex-wrap: wrap; justify-content: space-between; align-items: flex-start; gap: 0.85rem; }
    .hero-head > * { min-width: 0; }
    .eyebrow { font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; color: var(--muted); margin-bottom: 0.25rem; }
    h1 { margin: 0 0 0.35rem; font-size: clamp(1.25rem, 2.2vw, 1.6rem); color: var(--ink); letter-spacing: -0.02em; line-height: 1.25; overflow-wrap: anywhere; }
    .subtitle { margin: 0; color: var(--muted); max-width: 78ch; font-size: 0.94rem; overflow-wrap: anywhere; }

    .epistemic-banner { margin-top: 0.95rem; padding: 0.75rem 0.95rem; border-radius: 10px; background: var(--warn-bg); border: 1px solid var(--warn-bd); color: #78350f; font-size: 0.87rem; display: flex; flex-wrap: wrap; gap: 0.35rem 0.6rem; align-items: flex-start; min-width: 0; overflow-wrap: anywhere; }
    .epistemic-banner strong { color: #451a03; }

    .decision-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 240px), 1fr)); gap: 0.85rem; margin-top: 1rem; }
    .decision-grid > * { min-width: 0; }
    .decision-card { border: 1px solid var(--border); border-radius: 10px; padding: 0.9rem 1rem; background: var(--surface); min-width: 0; }
    .decision-card.quant-accent { border-top: 3px solid var(--quant); }
    .decision-card.synth-accent { border-top: 3px solid var(--synth); }
    .decision-card.ink-accent { border-top: 3px solid var(--ink); }
    .dc-kicker { font-size: 0.74rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; color: var(--muted); }
    .dc-val { font-size: 1.32rem; font-weight: 800; color: var(--ink); margin: 0.2rem 0; line-height: 1.2; font-variant-numeric: tabular-nums; overflow-wrap: anywhere; }
    .dc-sub { font-size: 0.82rem; color: var(--muted); overflow-wrap: anywhere; }

    .context-strip { display: flex; flex-wrap: wrap; gap: 0.5rem 1.25rem; margin-top: 0.85rem; padding-top: 0.75rem; border-top: 1px solid var(--border); font-size: 0.81rem; color: var(--muted); }
    .context-strip strong { color: var(--text); }

    .tablist { display: flex; flex-wrap: wrap; gap: 0.25rem; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 0.35rem; margin-bottom: 1rem; box-shadow: var(--shadow); }
    .tablist button[role="tab"] { flex: 1 1 auto; appearance: none; background: transparent; border: 0; border-radius: 8px; padding: 0.6rem 0.9rem; font: inherit; font-size: 0.9rem; font-weight: 600; color: var(--muted); cursor: pointer; text-align: center; transition: background 0.15s ease, color 0.15s ease; min-width: 0; }
    .tablist button[role="tab"]:hover { color: var(--ink); background: var(--surface-2); }
    .tablist button[role="tab"][aria-selected="true"] { color: #ffffff; background: var(--ink); }

    .panel-inner { display: grid; grid-template-columns: minmax(0, 1fr); gap: 1rem; }
    .panel-inner > * { min-width: 0; }
    .card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 1.15rem 1.25rem; box-shadow: var(--shadow); min-width: 0; overflow-wrap: anywhere; }
    .card h2 { margin: 0 0 0.35rem; font-size: 1.12rem; color: var(--ink); }
    .card h3 { margin: 0 0 0.35rem; font-size: 0.98rem; color: var(--ink); }
    .muted { color: var(--muted); font-size: 0.89rem; margin: 0 0 0.75rem; }
    .grid-2 { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 300px), 1fr)); gap: 1rem; }
    .grid-2 > * { min-width: 0; }

    .badge { display: inline-flex; align-items: center; padding: 0.15rem 0.5rem; border-radius: 6px; font-size: 0.74rem; font-weight: 600; border: 1px solid var(--border); background: var(--surface-2); color: var(--text); line-height: 1.3; max-width: 100%; }
    .badge.quant { background: var(--quant-bg); color: var(--quant); border-color: var(--quant-bd); }
    .badge.synth { background: var(--synth-bg); color: var(--synth); border-color: var(--synth-bd); }
    .badge.warn { background: var(--warn-bg); color: var(--warn); border-color: var(--warn-bd); }
    .badge.pos { background: var(--pos-bg); color: var(--pos); border-color: var(--pos-bd); }
    .badge.neg { background: var(--neg-bg); color: var(--neg); border-color: var(--neg-bd); }
    .badge.shield { background: var(--shield-bg); color: var(--shield); border-color: var(--shield-bd); }

    .toolbar { display: flex; flex-wrap: wrap; gap: 0.75rem; align-items: flex-end; margin-bottom: 0.9rem; min-width: 0; }
    .toolbar label { display: grid; gap: 0.25rem; font-size: 0.79rem; font-weight: 600; color: var(--muted); min-width: 0; max-width: 100%; }
    select, input[type="search"] { font: inherit; font-size: 0.88rem; color: var(--ink); background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 0.45rem 0.65rem; min-width: 0; width: 100%; max-width: 100%; }

    .table-x { overflow-x: auto; width: 100%; max-width: 100%; min-width: 0; border: 1px solid var(--border); border-radius: 10px; background: var(--surface); -webkit-overflow-scrolling: touch; }
    table { width: 100%; border-collapse: collapse; font-size: 0.86rem; }
    thead th { background: var(--surface-2); text-align: left; padding: 0.6rem 0.75rem; border-bottom: 1px solid var(--border); font-weight: 700; color: var(--ink); white-space: nowrap; }
    tbody th { text-align: left; padding: 0.6rem 0.75rem; border-bottom: 1px solid var(--border); font-weight: 600; vertical-align: top; }
    tbody td { padding: 0.6rem 0.75rem; border-bottom: 1px solid var(--border); vertical-align: top; }
    tbody tr:last-child td, tbody tr:last-child th { border-bottom: 0; }
    tbody tr:hover td, tbody tr:hover th { background: #f8fafc; }
    .num { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
    .nowrap { white-space: nowrap; }

    details.row-details { margin-top: 0.35rem; }
    details.row-details summary { cursor: pointer; font-size: 0.8rem; font-weight: 600; color: var(--quant); list-style: none; }
    details.row-details summary::-webkit-details-marker { display: none; }
    details.row-details summary::before { content: "▸ "; }
    details.row-details[open] summary::before { content: "▾ "; }
    .detail-box { margin-top: 0.45rem; padding: 0.6rem 0.75rem; border-radius: 8px; background: var(--surface-2); border: 1px solid var(--border); font-size: 0.82rem; color: var(--text); }

    .insight-box { border-radius: 10px; padding: 1rem; border: 1px solid var(--border); min-width: 0; }
    .insight-box.pos { background: var(--pos-bg); border-color: var(--pos-bd); }
    .insight-box.neg { background: var(--neg-bg); border-color: var(--neg-bd); }
    .insight-box.rec { background: var(--quant-bg); border-color: var(--quant-bd); grid-column: 1 / -1; }
    .insight-box ul { margin: 0.4rem 0 0; padding-left: 1.2rem; }
    .insight-box li { margin: 0.35rem 0; font-size: 0.89rem; }

    .persona-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 230px), 1fr)); gap: 0.7rem; margin-top: 0.75rem; }
    .persona-grid > * { min-width: 0; }
    .persona-btn { text-align: left; background: var(--surface); border: 2px solid var(--border); border-radius: 10px; padding: 0.75rem 0.85rem; cursor: pointer; font: inherit; transition: border-color 0.15s ease, background 0.15s ease; min-width: 0; }
    .persona-btn:hover { border-color: #94a3b8; }
    .persona-btn[aria-pressed="true"] { border-color: var(--synth); background: var(--synth-bg); }
    .persona-btn .p-name { font-weight: 700; font-size: 0.95rem; color: var(--ink); display: block; }
    .persona-btn .p-meta { font-size: 0.78rem; color: var(--muted); display: block; margin-top: 0.15rem; }

    .kv-list { display: grid; grid-template-columns: minmax(0, 1fr); gap: 0.55rem; font-size: 0.87rem; }
    .kv-item { background: var(--surface-2); border-radius: 8px; padding: 0.6rem 0.8rem; border: 1px solid var(--border); min-width: 0; overflow-wrap: anywhere; }
    .kv-item strong { display: block; font-size: 0.73rem; text-transform: uppercase; letter-spacing: 0.04em; color: var(--muted); margin-bottom: 0.15rem; }

    .scale-axis { display: grid; grid-template-columns: minmax(140px, 190px) minmax(0, 1fr) 78px; gap: 0.6rem; font-size: 0.72rem; color: var(--muted); margin-bottom: 0.35rem; }
    .scale-ticks { display: flex; justify-content: space-between; border-bottom: 1px dashed var(--border); padding-bottom: 0.15rem; }
    .hbar-row { display: grid; grid-template-columns: minmax(140px, 190px) minmax(0, 1fr) 78px; align-items: center; gap: 0.6rem; font-size: 0.83rem; margin-bottom: 0.4rem; }
    .hbar-row > * { min-width: 0; }
    .hbar-track { background: var(--surface-2); border-radius: 999px; height: 11px; overflow: hidden; border: 1px solid var(--border); }
    .hbar-fill { height: 100%; background: var(--synth); border-radius: 999px; }
    .hbar-fill.neg { background: var(--neg); }

    .stacked-bar { display: flex; height: 14px; border-radius: 999px; overflow: hidden; background: #e2e8f0; min-width: 130px; margin-bottom: 0.25rem; }
    .seg-scroll { background: #cbd5e1; }
    .seg-glance { background: #94a3b8; }
    .seg-stop { background: #334155; }
    .seg-click { background: #0f766e; }
    .action-inline { font-size: 0.76rem; color: var(--muted); font-variant-numeric: tabular-nums; }

    .btn { appearance: none; border: 1px solid var(--border); background: var(--surface); color: var(--ink); padding: 0.45rem 0.85rem; border-radius: 8px; font: inherit; font-size: 0.84rem; font-weight: 600; cursor: pointer; }
    .btn:hover { background: var(--surface-2); }
    .btn.primary { background: var(--ink); border-color: var(--ink); color: #fff; }
    .btn.xs { padding: 0.25rem 0.55rem; font-size: 0.76rem; }

    .feed-box { border: 1px solid var(--border); border-radius: 10px; padding: 0.8rem; background: var(--surface-2); min-width: 0; }
    .feed-item { padding: 0.55rem 0.7rem; border-radius: 8px; background: var(--surface); border: 1px solid var(--border); margin-bottom: 0.45rem; font-size: 0.84rem; overflow-wrap: anywhere; }
    .feed-item:last-child { margin-bottom: 0; }
    .feed-item.sponsored { border: 1.5px solid var(--synth); background: var(--synth-bg); }

    .report-rendered { font-size: 0.9rem; line-height: 1.6; color: var(--text); min-width: 0; }
    .report-rendered h2 { margin-top: 1.25rem; border-bottom: 1px solid var(--border); padding-bottom: 0.3rem; }
    pre.report-pre { white-space: pre-wrap; overflow-wrap: anywhere; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 0.82rem; background: var(--surface-2); border: 1px solid var(--border); border-radius: 10px; padding: 1rem; overflow-x: auto; max-width: 100%; }
    .sr-only { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0,0,0,0); white-space: nowrap; border: 0; }

    @media (max-width: 640px) {
      .container { padding: 0.65rem 0.65rem 2rem; }
      header.hero, .card { padding: 0.9rem; }
      .decision-grid, .grid-2, .persona-grid { grid-template-columns: minmax(0, 1fr); }
      .toolbar label { width: 100%; }
      .tablist button[role="tab"] { flex: 1 1 calc(50% - 0.25rem); font-size: 0.84rem; padding: 0.55rem 0.6rem; }
      .scale-axis { display: none; }
      .hbar-row { grid-template-columns: minmax(0, 1fr); gap: 0.2rem; }
      .stacked-bar { min-width: 0; width: 100%; }
    }

    @media print {
      body { background: #fff; }
      .container { max-width: none; padding: 0; }
      .tablist, .toolbar, .btn, #copy-status { display: none !important; }
      section[role="tabpanel"] { display: block !important; margin-bottom: 1.5rem; }
      section[role="tabpanel"][hidden] { display: block !important; }
      .card, header.hero { box-shadow: none; break-inside: avoid; }
    }
  </style>
</head>
<body>
  <div class="container">
    <header class="hero">
      <div class="hero-head">
        <div>
          <div class="eyebrow">Wevion · Analisi Campagne, Segnali Simulati &amp; Piano Budget</div>
          <h1>Wevion · Dashboard Unificata (Personas, Decision 1 &amp; Interviste)</h1>
          <p class="subtitle">
            Sintesi decisionale per le 3 campagne (<code>NDL-C1</code> Beauty, <code>CDF-C1</code> Pet, <code>FGR-C1</code> Abbigliamento) che affianca scenari quantitativi di budget alle valutazioni probabilistiche Decision 1 e interviste cieche.
          </p>
        </div>
        <div>
          <span class="badge warn">Segnali simulati · Calibrazione CTR non applicata</span>
        </div>
      </div>

      <div class="epistemic-banner" role="note" aria-label="Origine e limiti dei dati">
        <span><strong>Avvertenza metodologica:</strong></span>
        <span>
          Le reazioni Decision 1 e le interviste cieche provengono da profili sintetici (metà <code>unbiased</code>, metà <code>in-target</code> critici) su opzioni chiuse o testuali: esprimono <strong>probabilità e attriti simulati</strong>, non click o acquisti reali, e non alterano i CTR previsti dal modello quantitativo.
        </span>
      </div>

      <div class="decision-grid" id="hero-decisions"></div>
      <div class="context-strip" id="hero-context"></div>
    </header>

    <nav class="tablist" role="tablist" aria-label="Sezioni della dashboard unificata">
      <button type="button" role="tab" id="tab-campaigns" aria-controls="panel-campaigns" aria-selected="true">Sintesi Campagne &amp; Insights</button>
      <button type="button" role="tab" id="tab-quant" aria-controls="panel-quant" aria-selected="false">Piano Budget &amp; Forecast</button>
      <button type="button" role="tab" id="tab-personas" aria-controls="panel-personas" aria-selected="false">Esplora Personas &amp; Interviste</button>
      <button type="button" role="tab" id="tab-workflow" aria-controls="panel-workflow" aria-selected="false">Metodo, Confini &amp; Report</button>
    </nav>

    <!-- PANEL 1: CAMPAIGNS & INTERVIEW INSIGHTS -->
    <section role="tabpanel" id="panel-campaigns" aria-labelledby="tab-campaigns" tabindex="0">
      <div class="panel-inner">
        <div class="card">
          <h2>Filtro per Campagna, Coorte &amp; Leva</h2>
          <p class="muted">Confronta le campagne e isola le reazioni simulate tra campione generalista (<em>unbiased</em>) e coorte interessata (<em>in-target</em>).</p>
          <div class="toolbar">
            <label>Campagna
              <select id="camp-filter">
                <option value="ALL">Tutte le campagne</option>
              </select>
            </label>
            <label>Coorte Personas
              <select id="cohort-filter">
                <option value="all">Tutte (unbiased + in-target)</option>
                <option value="unbiased">Solo unbiased</option>
                <option value="category_conditioned">Solo in-target critiche</option>
              </select>
            </label>
            <label>Leva
              <select id="lever-filter">
                <option value="ALL">Tutte le leve</option>
                <option value="scarcity">Scarsità</option>
                <option value="urgency">Urgenza</option>
                <option value="black_friday">Black Friday</option>
              </select>
            </label>
          </div>
        </div>

        <div class="card">
          <h2>Confronto Sintetico Campagne (Decision 1 + Interviste + Quantitativo)</h2>
          <p class="muted">I segnali simulati (Decision 1 / interviste) e le medie quantitative (eCTR/eCPM nel contesto AdSet) misurano dimensioni diverse e vanno letti insieme come ipotesi operative.</p>
          <div class="table-x">
            <table>
              <thead>
                <tr>
                  <th>Campagna &amp; Settore</th>
                  <th class="num">Apertura Sim. (D1)</th>
                  <th class="num">Saldo Interviste</th>
                  <th>Top Asset D1</th>
                  <th class="num">eCTR / eCPM Quant.</th>
                </tr>
              </thead>
              <tbody id="campaigns-tbody"></tbody>
            </table>
          </div>
        </div>

        <div class="card" id="insights-card">
          <h2>Punti Chiave Estratti dalle Interviste (Istanza Separata Hydrogen Low)</h2>
          <p class="muted" id="insights-meta"></p>
          <div class="grid-2" id="insights-grid"></div>
        </div>

        <div class="grid-2">
          <div class="card">
            <h2>Distribuzione Segmenti Comportamentali (Scala 0–100%)</h2>
            <p class="muted">Quota delle personas filtrate per profilo di reazione medio stimato sui 12 annunci.</p>
            <div class="scale-axis" aria-hidden="true"><span></span><div class="scale-ticks"><span>0%</span><span>25%</span><span>50%</span><span>75%</span><span>100%</span></div><span></span></div>
            <div id="segments-bars"></div>
          </div>
          <div class="card">
            <h2>Motivi Dominanti di Scelta o Attrito (Scala 0–100%)</h2>
            <p class="muted">Motivo con probabilità media più alta per persona nel campione selezionato.</p>
            <div class="scale-axis" aria-hidden="true"><span></span><div class="scale-ticks"><span>0%</span><span>25%</span><span>50%</span><span>75%</span><span>100%</span></div><span></span></div>
            <div id="reasons-bars"></div>
          </div>
        </div>

        <div class="card">
          <h2>Classifica Annunci Filtrata (Segnali Simulati + Interviste + Forecast)</h2>
          <p class="muted">Ordine per probabilità simulata di apertura nella coorte selezionata; espandi ogni riga per leggere testi e visual completi.</p>
          <div class="table-x">
            <table>
              <thead>
                <tr>
                  <th>Campagna &amp; Annuncio</th>
                  <th class="num">Apertura Sim.</th>
                  <th class="num">Attenzione Sim.</th>
                  <th class="num">Saldo Interviste</th>
                  <th class="num">eCTR Quant.</th>
                </tr>
              </thead>
              <tbody id="assets-tbody"></tbody>
            </table>
          </div>
        </div>
      </div>
    </section>

    <!-- PANEL 2: QUANTITATIVE & BUDGET -->
    <section role="tabpanel" id="panel-quant" aria-labelledby="tab-quant" hidden>
      <div class="panel-inner">
        <div class="card">
          <h2>12 Ad Set Unificati: Previsioni &amp; Riallocazione Budget ±20% (16–30 Nov)</h2>
          <p class="muted">Riallocazione condizionale a budget totale di campagna invariato. Espandi una riga per ispezionare CTR storico, eCTR/eCPM e ipotesi di pubblico.</p>
          <div class="table-x">
            <table>
              <thead>
                <tr>
                  <th>AdSet &amp; Settore</th>
                  <th class="num">Budget Base → Scen.</th>
                  <th class="num">Click Attesi Base → Scen.</th>
                  <th>Asset &amp; Ipotesi Segmento</th>
                </tr>
              </thead>
              <tbody id="adsets-tbody"></tbody>
            </table>
          </div>
        </div>

        <div class="grid-2">
          <div class="card">
            <h2>Validazione Modelli Forecasting (Fold 1 Selezione &amp; Fold 2 Verifica)</h2>
            <div class="table-x">
              <table>
                <thead><tr><th>Finestra</th><th>Target</th><th class="num">Baseline 14g</th><th class="num">Timestral-28M</th><th>Esito</th></tr></thead>
                <tbody id="folds-tbody"></tbody>
              </table>
            </div>
          </div>
          <div class="card">
            <h2>Qualità Dati &amp; Scenari Stagionali</h2>
            <div id="dq-box" class="kv-list" style="margin-bottom:0.85rem;"></div>
            <div class="table-x">
              <table>
                <thead><tr><th>Settore</th><th>Scenario</th><th class="num">CTR Medio</th><th class="num">CPM Medio</th></tr></thead>
                <tbody id="seasonal-tbody"></tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- PANEL 3: PERSONAS EXPLORER -->
    <section role="tabpanel" id="panel-personas" aria-labelledby="tab-personas" hidden>
      <div class="panel-inner">
        <div class="card">
          <h2>Esplora Personas, Feed Simulato, Decision 1 &amp; Interviste Cieche</h2>
          <div class="toolbar">
            <label>Campagna
              <select id="p-camp-filter">
                <option value="ALL">Tutte</option>
              </select>
            </label>
            <label>Coorte
              <select id="p-cohort-filter">
                <option value="ALL">Tutte</option>
                <option value="unbiased">Generalista (unbiased)</option>
                <option value="category_conditioned">In-target critica</option>
              </select>
            </label>
            <label>Segmento
              <select id="p-seg-filter">
                <option value="ALL">Tutti i segmenti</option>
                <option value="high_intent">Alta intenzione (click ≥ 15%)</option>
                <option value="attentive_hesitant">Attentivo ma esitante</option>
                <option value="skeptical_resistant">Scettico / Offerta debole</option>
                <option value="low_need_scroll">Basso bisogno / Non pertinente</option>
              </select>
            </label>
            <label>Cerca nome / ID / lavoro
              <input type="search" id="p-search" placeholder="Es. P001, idraulico, Giulia...">
            </label>
            <div style="display:flex; gap:0.4rem; align-items:center;">
              <button type="button" class="btn" id="p-prev">Precedente</button>
              <span class="muted" style="margin:0;" id="p-page-info"></span>
              <button type="button" class="btn" id="p-next">Successivo</button>
            </div>
          </div>
          <div class="persona-grid" id="persona-selector" role="group" aria-label="Elenco profili"></div>
          <div id="persona-live-status" class="sr-only" aria-live="polite"></div>
        </div>
        <div id="persona-detail"></div>
      </div>
    </section>

    <!-- PANEL 4: METHOD, BOUNDARY & REPORT -->
    <section role="tabpanel" id="panel-workflow" aria-labelledby="tab-workflow" hidden>
      <div class="panel-inner">
        <div class="card">
          <h2>Isolamento tra Decision 1, Interviste Cieche e Riassunto Separato</h2>
          <p class="muted">Nessun risultato di Decision 1 entra mai nei prompt delle interviste. Le interviste girano su istanze singole <code>gemini-4-hydrogen (low)</code> e il riassunto finale è prodotto da un'istanza separata dopo il congelamento.</p>
          <div class="table-x">
            <table>
              <thead><tr><th>Attore / Istanza</th><th>Input Visibili</th><th>Confine Informativo (Input Esclusi)</th><th>Output</th></tr></thead>
              <tbody>
                <tr><th>Persona Writer (T3)</th><td>Slot stratificati (seed 2026) + settore</td><td><span class="badge shield">Senza annunci, CTR, CPM, forecast</span></td><td>Schede persona v2.0 (unbiased + in-target critiche)</td></tr>
                <tr><th>Decision 1 Worker</th><td>1 persona + feed testuale controllato + 1 creatività</td><td><span class="badge shield">Senza altre persone, CTR, forecast</span></td><td>Distribuzioni probabilità su 12 coppie azione×motivo</td></tr>
                <tr><th>Intervistato (Hydrogen Low)</th><td>Propria scheda, feed, annunci anonimi (C01–C12), 6 domande neutrali</td><td><span class="badge shield">Senza punteggi Decision 1, altre persone, KPI</span></td><td>Interviste congelate in <code>frozen.json</code></td></tr>
                <tr><th>Riassunto (Hydrogen Low separato)</th><td>Interviste congelate aggregate per campagna e asset</td><td><span class="badge shield">Non altera interviste né forecast numerici</span></td><td>Sintesi positiva/negativa e raccomandazioni</td></tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="card">
          <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.75rem; margin-bottom:0.75rem;">
            <div>
              <h2 style="margin:0;">Report Finale &amp; Provenienza</h2>
              <p class="muted" style="margin:0.2rem 0 0;">Documentazione verificabile di Decision 1, interviste cieche e istanza riassunto dedicata.</p>
            </div>
            <div style="display:flex; flex-wrap:wrap; gap:0.5rem; align-items:center;">
              <button type="button" class="btn" id="toggle-raw-btn">Mostra Markdown grezzo</button>
              <button type="button" class="btn primary" id="copy-report-btn">Copia Markdown</button>
              <button type="button" class="btn" id="print-btn">Stampa / PDF</button>
              <span id="copy-status" class="muted" style="margin:0;" aria-live="polite"></span>
            </div>
          </div>
          <div id="receipts-summary" class="kv-list" style="margin-bottom:0.85rem;"></div>
          <div id="report-rendered" class="report-rendered"></div>
          <pre class="report-pre" id="report-pre" hidden></pre>
        </div>
      </div>
    </section>
  </div>

  <script>
    const DATA = __DATA_JSON__;
    const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
    const nf0 = new Intl.NumberFormat('it-IT', { maximumFractionDigits: 0 });
    const nf1 = new Intl.NumberFormat('it-IT', { minimumFractionDigits: 1, maximumFractionDigits: 1 });
    const nf2 = new Intl.NumberFormat('it-IT', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    const nf4 = new Intl.NumberFormat('it-IT', { minimumFractionDigits: 4, maximumFractionDigits: 4 });
    const fmtEur0 = v => nf0.format(Math.round(v)) + ' €';
    const fmtEur2 = v => nf2.format(v) + ' €';
    const fmtPct1 = v => nf1.format(v) + '%';
    const fmtPct2 = v => nf2.format(v) + '%';

    const VERTICAL_LABELS = { beauty_skincare: 'Beauty & Skincare', abbigliamento: 'Abbigliamento', pet_ecommerce: 'Pet E-commerce' };
    const LEVER_LABELS = { scarcity: 'Scarsità', urgency: 'Urgenza', black_friday: 'Black Friday' };
    const COHORT_LABELS = { unbiased: 'Generalista (unbiased)', category_conditioned: 'In-target critica' };
    const REASON_LABELS = {
      irrelevant: 'Non pertinente', low_need: 'Basso bisogno', skeptical: 'Scetticismo',
      weak_offer: 'Offerta debole', interested: 'Interesse', curiosity: 'Curiosità',
      visual: 'Impatto visivo', more_info: 'Vuole più info', trust_check: 'Verifica fiducia',
      busy: 'Di fretta', offer: 'Attratto da offerta', utility: 'Utilità pratica'
    };
    const NEG_REASONS = new Set(['irrelevant', 'low_need', 'skeptical', 'weak_offer', 'busy']);
    const SEGMENT_LABELS = {
      high_intent: 'Alta intenzione (click ≥ 15%)',
      attentive_hesitant: 'Attentivo ma esitante (att. ≥ 50%)',
      skeptical_resistant: 'Scettico / Offerta debole',
      low_need_scroll: 'Basso bisogno / Non pertinente'
    };

    // Accessible Tabs
    const tabs = Array.from(document.querySelectorAll('[role="tab"]'));
    const panels = Array.from(document.querySelectorAll('[role="tabpanel"]'));
    function selectTab(tab, focusTab = false) {
      const targetId = tab.getAttribute('aria-controls');
      tabs.forEach(t => { const a = t === tab; t.setAttribute('aria-selected', a ? 'true' : 'false'); t.tabIndex = a ? 0 : -1; });
      panels.forEach(p => { const a = p.id === targetId; if (a) { p.removeAttribute('hidden'); p.setAttribute('tabindex', '0'); } else { p.setAttribute('hidden', ''); p.removeAttribute('tabindex'); } });
      if (focusTab) tab.focus();
    }
    tabs.forEach((tab, idx) => {
      tab.tabIndex = idx === 0 ? 0 : -1;
      tab.addEventListener('click', () => selectTab(tab));
      tab.addEventListener('keydown', e => {
        let nextIdx = null;
        if (e.key === 'ArrowRight') nextIdx = (idx + 1) % tabs.length;
        else if (e.key === 'ArrowLeft') nextIdx = (idx - 1 + tabs.length) % tabs.length;
        else if (e.key === 'Home') nextIdx = 0;
        else if (e.key === 'End') nextIdx = tabs.length - 1;
        if (nextIdx !== null) { e.preventDefault(); selectTab(tabs[nextIdx], true); }
      });
    });

    // Hero Decision Strip
    const topCamp = DATA.campaigns[0];
    const totBudget = DATA.adsets.reduce((s, a) => s + a.budget_base_eur, 0);
    const totCB = DATA.adsets.reduce((s, a) => s + a.expected_clicks_base, 0);
    const totCS = DATA.adsets.reduce((s, a) => s + a.expected_clicks_scenario, 0);
    const dC = totCS - totCB;
    document.getElementById('hero-decisions').innerHTML = `
      <div class="decision-card quant-accent">
        <div class="dc-kicker">Scenario Budget (±20% a Budget Invariato)</div>
        <div class="dc-val">${dC >= 0 ? '+' : ''}${nf0.format(Math.round(dC))} click stimati</div>
        <div class="dc-sub">Da ${nf0.format(Math.round(totCB))} a ${nf0.format(Math.round(totCS))} click su ${fmtEur0(totBudget)} di budget invariato (assunzione what-if non causale).</div>
      </div>
      <div class="decision-card synth-accent">
        <div class="dc-kicker">Miglior Segnale Simulato (Decision 1)</div>
        <div class="dc-val">${topCamp ? esc(topCamp.campaign_id) + ' · ' + fmtPct2(topCamp.mean_click_intent_signal * 100) : '—'}</div>
        <div class="dc-sub">${topCamp ? 'Saldo interviste: ' + (topCamp.net_interview_mentions >= 0 ? '+' : '') + topCamp.net_interview_mentions + ' · Top asset: ' + esc(topCamp.top_asset) : 'In attesa risultati'}</div>
      </div>
      <div class="decision-card ink-accent">
        <div class="dc-kicker">Copertura Simulazione &amp; Interviste</div>
        <div class="dc-val">${nf0.format(DATA.meta.persona_count)} profili · ${nf0.format(DATA.meta.interviews_count)} interviste</div>
        <div class="dc-sub">${nf0.format(DATA.meta.evaluated_pairs_t3)} valutazioni su ${DATA.meta.evaluated_assets_t3} asset (non calibrate su CTR).</div>
      </div>
    `;
    document.getElementById('hero-context').innerHTML = `
      <span><strong>Orizzonte:</strong> 16–30 nov 2026 (${nf0.format(DATA.meta.forecast_rows)} righe)</span>
      <span><strong>Cutoff storico:</strong> ${esc(DATA.meta.cutoff)}</span>
      <span><strong>Input token D1:</strong> ${nf0.format(DATA.meta.input_tokens_t3 || 0)}</span>
      <span><strong>Calibrazione CTR:</strong> Non applicata</span>
    `;

    // Populate campaign selects
    const campSel = document.getElementById('camp-filter');
    const pCampSel = document.getElementById('p-camp-filter');
    DATA.campaigns.forEach(c => {
      const label = `${c.campaign_id} · ${c.campaign_name} (${c.n_personas}p)`;
      campSel.add(new Option(label, c.campaign_id));
      pCampSel.add(new Option(label, c.campaign_id));
    });

    function renderCampaignsTab() {
      const cid = document.getElementById('camp-filter').value;
      const cohort = document.getElementById('cohort-filter').value;
      const lever = document.getElementById('lever-filter').value;

      const campsToShow = cid === 'ALL' ? DATA.campaigns : DATA.campaigns.filter(c => c.campaign_id === cid);
      document.getElementById('campaigns-tbody').innerHTML = campsToShow.map(c => {
        const net = c.net_interview_mentions;
        const netTag = net > 0 ? `<span class="badge pos">+${net}</span>` : net < 0 ? `<span class="badge neg">${net}</span>` : `<span class="badge">0</span>`;
        return `<tr>
          <th><code>${esc(c.campaign_id)}</code> · ${esc(c.campaign_name)}<br><span class="muted" style="font-weight:400;">${esc(VERTICAL_LABELS[c.vertical] || c.vertical)} · ${c.n_personas} profili</span></th>
          <td class="num"><strong>${fmtPct2(c.mean_click_intent_signal * 100)}</strong><br><span class="muted" style="font-size:0.78rem;">Att. ${fmtPct1(c.mean_attention_signal * 100)}</span></td>
          <td class="num">${netTag}<br><span class="muted" style="font-size:0.78rem;">+${c.most_useful_mentions} / -${c.least_useful_mentions}</span></td>
          <td><code>${esc(c.top_asset)}</code></td>
          <td class="num">${fmtPct2(c.quant_mean_ectr_pct)}<br><span class="muted" style="font-size:0.78rem;">${fmtEur2(c.quant_mean_ecpm_eur)}</span></td>
        </tr>`;
      }).join('');

      const ins = DATA.interview_summary || {};
      const metaEl = document.getElementById('insights-meta');
      const gridEl = document.getElementById('insights-grid');
      if (ins && (ins.overall || ins.campaigns)) {
        const rec = ins.receipt ? `Ricevuta istanza riassunto: ${ins.receipt.providerInstanceId || 'antigravity'} / ${ins.receipt.model || 'gemini-4-hydrogen (low)'} · task ${ins.receipt.taskId || ''}` : 'Istanza separata Gemini 4 Hydrogen (thinking low)';
        const campIns = cid === 'ALL' ? (ins.overall || {}) : ((ins.campaigns || {})[cid] || ins.overall || {});
        metaEl.textContent = (campIns.headline || ins.executive_verdict || '') + ' — ' + rec;
        const positives = campIns.positive_highlights || campIns.positives || [];
        const negatives = campIns.negative_highlights || campIns.negatives || [];
        const recs = campIns.recommendations || [];
        gridEl.innerHTML = `
          <div class="insight-box pos">
            <h3>Punti a Favore (Cosa ha convinto)</h3>
            <ul>${positives.map(x => `<li>${esc(x)}</li>`).join('') || '<li>Nessun punto positivo registrato.</li>'}</ul>
          </div>
          <div class="insight-box neg">
            <h3>Punti di Attrito (Cosa ha frenato)</h3>
            <ul>${negatives.map(x => `<li>${esc(x)}</li>`).join('') || '<li>Nessun attrito registrato.</li>'}</ul>
          </div>
          ${recs.length ? `<div class="insight-box rec"><h3>Sintesi Strategica &amp; Azioni Raccomandate</h3><ul>${recs.map(x => `<li>${esc(x)}</li>`).join('')}</ul></div>` : ''}
        `;
      } else {
        metaEl.textContent = 'Riassunto qualitativo non ancora generato.';
        gridEl.innerHTML = '';
      }

      const filteredPersonas = DATA.personas.filter(p => (cid === 'ALL' || p.campaign_id === cid) && (cohort === 'all' || p.cohort === cohort));
      const segCounts = {};
      const reasonCounts = {};
      filteredPersonas.forEach(p => {
        segCounts[p.segment] = (segCounts[p.segment] || 0) + 1;
        if (p.dominant_reason) reasonCounts[p.dominant_reason] = (reasonCounts[p.dominant_reason] || 0) + 1;
      });
      const nP = Math.max(1, filteredPersonas.length);
      document.getElementById('segments-bars').innerHTML = Object.entries(segCounts).sort((a,b) => b[1]-a[1]).map(([k, v]) => `
        <div class="hbar-row">
          <span>${esc(SEGMENT_LABELS[k] || k)}</span>
          <div class="hbar-track"><div class="hbar-fill ${k==='skeptical_resistant'||k==='low_need_scroll'?'neg':''}" style="width:${(v*100/nP).toFixed(1)}%"></div></div>
          <span class="num">${v} (${nf0.format(Math.round(v*100/nP))}%)</span>
        </div>
      `).join('');
      const sortedReasons = Object.entries(reasonCounts).sort((a,b) => b[1]-a[1]);
      const topReasons = sortedReasons.slice(0, 8);
      const restReasons = sortedReasons.slice(8);
      const renderReasonItem = ([k, v]) => `
        <div class="hbar-row">
          <span>${esc(REASON_LABELS[k] || k)}</span>
          <div class="hbar-track"><div class="hbar-fill ${NEG_REASONS.has(k)?'neg':''}" style="width:${(v*100/nP).toFixed(1)}%"></div></div>
          <span class="num">${v} (${nf0.format(Math.round(v*100/nP))}%)</span>
        </div>
      `;
      document.getElementById('reasons-bars').innerHTML = topReasons.map(renderReasonItem).join('') + (restReasons.length
        ? `<details class="row-details" style="margin-top:0.45rem;"><summary>Mostra altri ${restReasons.length} motivi (top ${topReasons.length} su ${sortedReasons.length})</summary><div style="margin-top:0.4rem;">${restReasons.map(renderReasonItem).join('')}</div></details>`
        : '');

      const filteredAssets = DATA.assets.filter(a => (cid === 'ALL' || a.campaign_id === cid) && (lever === 'ALL' || a.leva === lever))
        .map(a => {
          const stats = (a.by_cohort && a.by_cohort[cohort]) || {click_intent_signal: a.click_intent_signal, attention_signal: a.attention_signal};
          return {...a, view_click: stats.click_intent_signal, view_attn: stats.attention_signal};
        })
        .sort((a, b) => b.view_click - a.view_click);
      document.getElementById('assets-tbody').innerHTML = filteredAssets.map(a => {
        const net = a.net_interview_mentions;
        const netTag = net > 0 ? `<span class="badge pos">+${net}</span>` : net < 0 ? `<span class="badge neg">${net}</span>` : `<span class="badge">0</span>`;
        return `<tr>
          <td>
            <code>${esc(a.campaign_id)}</code> · <strong><code>${esc(a.asset_id)}</code></strong>
            <span class="badge">${esc(LEVER_LABELS[a.leva] || a.leva)} · ${esc(a.formato)}</span>
            <div style="margin-top:0.2rem;"><strong>${esc(a.headline)}</strong></div>
            <details class="row-details">
              <summary>Copy, CTA e descrizione visuale</summary>
              <div class="detail-box">
                <div><strong>Testo:</strong> ${esc(a.testo_principale)}</div>
                <div><strong>CTA:</strong> ${esc(a.call_to_action)}</div>
                <div><strong>Visual:</strong> ${esc(a.descrizione_visual)}</div>
              </div>
            </details>
          </td>
          <td class="num"><strong>${fmtPct2(a.view_click * 100)}</strong></td>
          <td class="num">${fmtPct1(a.view_attn * 100)}</td>
          <td class="num">${netTag}<br><span class="muted" style="font-size:0.78rem;">+${a.most_useful_count} / -${a.least_useful_count}</span></td>
          <td class="num">${a.forecast ? fmtPct2(a.forecast.avg_ctr_pct) : '—'}</td>
        </tr>`;
      }).join('');
    }
    ['camp-filter', 'cohort-filter', 'lever-filter'].forEach(id => document.getElementById(id).addEventListener('change', renderCampaignsTab));
    renderCampaignsTab();

    // Personas Explorer (focus-preserving pagination + live announcement)
    let pPage = 0;
    const PAGE_SIZE = 18;
    let selectedPersonaId = DATA.personas[0]?.persona_id;
    const liveStatusEl = document.getElementById('persona-live-status');

    function getFilteredPersonas() {
      const cid = document.getElementById('p-camp-filter').value;
      const coh = document.getElementById('p-cohort-filter').value;
      const seg = document.getElementById('p-seg-filter').value;
      const q = document.getElementById('p-search').value.trim().toLowerCase();
      return DATA.personas.filter(p =>
        (cid === 'ALL' || p.campaign_id === cid) &&
        (coh === 'ALL' || p.cohort === coh) &&
        (seg === 'ALL' || p.segment === seg) &&
        (!q || (p.name + ' ' + p.persona_id + ' ' + p.occupation + ' ' + (p.interests || []).join(' ')).toLowerCase().includes(q))
      );
    }

    function renderPersonaSelector(preserveFocusPid = null) {
      const list = getFilteredPersonas();
      const maxPage = Math.max(0, Math.ceil(list.length / PAGE_SIZE) - 1);
      if (pPage > maxPage) pPage = maxPage;
      const slice = list.slice(pPage * PAGE_SIZE, (pPage + 1) * PAGE_SIZE);
      if (!slice.some(p => p.persona_id === selectedPersonaId) && slice.length) selectedPersonaId = slice[0].persona_id;
      document.getElementById('p-page-info').textContent = `${nf0.format(list.length)} profili · pag. ${pPage + 1}/${maxPage + 1}`;
      const selBox = document.getElementById('persona-selector');
      selBox.innerHTML = slice.map(p => `
        <button type="button" class="persona-btn" aria-pressed="${p.persona_id === selectedPersonaId}" data-pid="${esc(p.persona_id)}">
          <span class="p-name">${esc(p.name)} (${esc(p.age_years)} anni)</span>
          <span class="p-meta"><code>${esc(p.persona_id)}</code> · <span class="badge">${esc(COHORT_LABELS[p.cohort] || p.cohort)}</span></span>
          <span class="p-meta">Apertura sim.: <strong>${fmtPct1(p.avg_actions.click * 100)}</strong> · ${esc(SEGMENT_LABELS[p.segment] || p.segment)}</span>
        </button>
      `).join('');
      selBox.querySelectorAll('.persona-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          selectedPersonaId = btn.dataset.pid;
          selBox.querySelectorAll('.persona-btn').forEach(b => b.setAttribute('aria-pressed', b.dataset.pid === selectedPersonaId ? 'true' : 'false'));
          const chosen = DATA.personas.find(x => x.persona_id === selectedPersonaId);
          if (chosen) liveStatusEl.textContent = `Profilo selezionato: ${chosen.name}`;
          renderPersonaDetail();
        });
      });
      if (preserveFocusPid) {
        const targetBtn = selBox.querySelector(`.persona-btn[data-pid="${CSS.escape(preserveFocusPid)}"]`);
        if (targetBtn) targetBtn.focus();
      }
      renderPersonaDetail();
    }

    function renderPersonaDetail() {
      const p = DATA.personas.find(x => x.persona_id === selectedPersonaId);
      const el = document.getElementById('persona-detail');
      if (!p) { el.innerHTML = ''; return; }
      const feedItems = (p.feed.items || []).map((it, i) => it.kind === 'sponsored'
        ? `<div class="feed-item sponsored"><strong>Pos. ${i+1} · SPONSORIZZATO</strong><br>Slot testuale riservato alla singola creatività in valutazione</div>`
        : `<div class="feed-item"><strong>Pos. ${i+1} · ${esc(it.author)}</strong><br>${esc(it.text)}</div>`
      ).join('');
      const intv = p.interview;
      const intvByAsset = {};
      if (intv) (intv.answers || []).forEach(a => { intvByAsset[a.asset_id] = a; });
      const mostSet = new Set(intv ? (intv.most_useful || []) : []);
      const leastSet = new Set(intv ? (intv.least_useful || []) : []);
      const evalRows = p.evaluations.map(ev => {
        const ia = intvByAsset[ev.asset_id];
        const s = ev.actions.scroll * 100, g = (ev.actions.glance || 0) * 100, st = ev.actions.stop * 100, c = ev.actions.click * 100;
        let opCell = '—';
        if (ia) {
          opCell = `<span class="badge pos">+</span> ${esc(ia.positive)}<br><span class="badge neg">-</span> ${esc(ia.negative)}`;
        } else if (intv) {
          if (mostSet.has(ev.asset_id)) opCell = `<span class="badge pos">Tra i più utili</span>`;
          else if (leastSet.has(ev.asset_id)) opCell = `<span class="badge neg">Tra i meno utili</span>`;
        }
        return `<tr>
          <th><code>${esc(ev.asset_id)}</code><br><span class="badge">${esc(LEVER_LABELS[ev.leva] || ev.leva)}</span></th>
          <td>
            <div class="stacked-bar" aria-label="Salta ${fmtPct1(s)}, Occhiata ${fmtPct1(g)}, Stop ${fmtPct1(st)}, Apre ${fmtPct1(c)}">
              <div class="seg-scroll" style="width:${s.toFixed(1)}%"></div>
              <div class="seg-glance" style="width:${g.toFixed(1)}%"></div>
              <div class="seg-stop" style="width:${st.toFixed(1)}%"></div>
              <div class="seg-click" style="width:${c.toFixed(1)}%"></div>
            </div>
            <div class="action-inline">Salta ${nf0.format(Math.round(s))}% · Occ. ${nf0.format(Math.round(g))}% · Stop ${nf0.format(Math.round(st))}% · <strong>Apre ${fmtPct1(c)}</strong></div>
          </td>
          <td><code>${esc(ev.top_pair)}</code> (${fmtPct1(ev.top_pair_prob * 100)})</td>
          <td>${opCell}</td>
        </tr>`;
      }).join('');
      el.innerHTML = `
        <div class="grid-2">
          <div class="card">
            <h2>${esc(p.name)} (${esc(p.age_years)} anni) · <code>${esc(p.persona_id)}</code></h2>
            <p class="muted">${esc(p.persona_summary)}</p>
            <div class="kv-list">
              <div class="kv-item"><strong>Attributi &amp; Coorte</strong>${esc(p.campaign_id)} · ${esc(COHORT_LABELS[p.cohort] || p.cohort)} · ${esc(p.gender_identity)} · Motivazione: ${esc(p.motivation)} · Interesse: ${esc(p.interest_in_category)}</div>
              <div class="kv-item"><strong>Occupazione &amp; Contesto</strong>${esc(p.occupation)} — ${esc(p.economic_context)}</div>
              <div class="kv-item"><strong>Routine &amp; Decisioni</strong>${esc(p.daily_routine)} ${esc(p.decision_habits)}</div>
              <div class="kv-item"><strong>Fiducia, Timori &amp; Contraddizione</strong>${esc(p.trust_requirements)} | Timori: ${esc(p.concerns)} | Contraddizione: ${esc(p.contradiction)}</div>
            </div>
          </div>
          <div class="card">
            <h2>Feed &amp; Sintesi Intervista Cieca</h2>
            <p class="muted">${esc(p.feed.platform)} ore ${esc(p.feed.hour)}:00 · pos. annuncio ${esc(p.feed.ad_position)}</p>
            <div class="feed-box">${feedItems}</div>
            ${intv ? `<div class="kv-list" style="margin-top:0.8rem;">
              ${intv.punti_a_favore ? `<div class="kv-item"><strong>Punti a favore (${esc(p.name)})</strong>${esc(intv.punti_a_favore)}</div>` : `<div class="kv-item"><strong>Sintesi Intervista (${esc(p.name)})</strong>${esc(intv.summary)}</div>`}
              ${intv.perche_si_allontana && intv.perche_si_allontana.toLowerCase() !== 'nulla' ? `<div class="kv-item"><strong>Freno principale</strong>${esc(intv.perche_si_allontana)}</div>` : ''}
              <div class="kv-item"><strong>Più utili / Meno utili dichiarati</strong><span class="badge pos">Più utili: ${esc((intv.most_useful || []).join(', ') || 'nessuno')}</span> <span class="badge neg">Meno utili: ${esc((intv.least_useful || []).join(', ') || 'nessuno')}</span></div>
            </div>` : ''}
          </div>
        </div>
        <div class="card" style="margin-top:1rem;">
          <h2>Probabilità Simulate Decision 1 &amp; Risposte Intervista sui 12 Annunci</h2>
          <div class="table-x">
            <table>
              <thead><tr><th>Asset</th><th>Distribuzione Probabilità (Salta / Occ. / Stop / Apre)</th><th>Coppia Prevalente D1</th><th>Opinione nell'Intervista (+ / -)</th></tr></thead>
              <tbody>${evalRows}</tbody>
            </table>
          </div>
        </div>
      `;
    }
    ['p-camp-filter', 'p-cohort-filter', 'p-seg-filter'].forEach(id => document.getElementById(id).addEventListener('change', () => { pPage = 0; renderPersonaSelector(); }));
    document.getElementById('p-search').addEventListener('input', () => { pPage = 0; renderPersonaSelector(); });
    document.getElementById('p-prev').addEventListener('click', () => { if (pPage > 0) { pPage--; renderPersonaSelector(); } });
    document.getElementById('p-next').addEventListener('click', () => { pPage++; renderPersonaSelector(); });
    renderPersonaSelector();

    // Quantitative Tab
    const foldsRows = [];
    DATA.folds.forEach(f => {
      foldsRows.push(`<tr><th>Fold ${f.fold} <span class="nowrap">(${esc(f.start)} → ${esc(f.end)})</span></th><td>CTR (pp)</td><td class="num"><strong>${nf4.format(f.baseline.wmae_ctr_pp)}</strong></td><td class="num">${nf4.format(f.timestral.wmae_ctr_pp)}</td><td>${f.fold===1?'<span class="badge quant">Baseline 14g</span>':'Verifica'}</td></tr>`);
      foldsRows.push(`<tr><th>Fold ${f.fold} <span class="nowrap">(${nf0.format(f.rows)} righe)</span></th><td>CPM (€)</td><td class="num">${nf4.format(f.baseline.wmae_cpm_eur)}</td><td class="num"><strong>${nf4.format(f.timestral.wmae_cpm_eur)}</strong></td><td>${f.fold===1?'<span class="badge quant">Timestral-28M</span>':'Verifica'}</td></tr>`);
    });
    document.getElementById('folds-tbody').innerHTML = foldsRows.join('');
    const dq = DATA.data_quality;
    document.getElementById('dq-box').innerHTML = `<div class="kv-item"><strong>Volumi &amp; Cold-Start</strong>${nf0.format(dq.history_rows)} righe storiche · ${nf0.format(dq.future_rows)} righe future · ${nf0.format(dq.cold_start_rows)} cold-start</div>`;
    document.getElementById('seasonal-tbody').innerHTML = DATA.seasonal_summary.map(s => `<tr><th>${esc(VERTICAL_LABELS[s.vertical] || s.vertical)}</th><td><code>${esc(s.scenario)}</code></td><td class="num">${fmtPct2(s.avg_ctr_pct)}</td><td class="num">${fmtEur2(s.avg_cpm_eur)}</td></tr>`).join('');
    document.getElementById('adsets-tbody').innerHTML = DATA.adsets.map(a => `
      <tr>
        <th><code>${esc(a.adset_id)}</code><br><span class="muted" style="font-weight:400;">${esc(VERTICAL_LABELS[a.vertical] || a.vertical)}</span></th>
        <td class="num">${fmtEur0(a.budget_base_eur)} → <strong>${fmtEur0(a.budget_scenario_eur)}</strong></td>
        <td class="num">${nf0.format(Math.round(a.expected_clicks_base))} → <strong>${nf0.format(Math.round(a.expected_clicks_scenario))}</strong></td>
        <td>
          <code>${esc(a.recommended_asset_id)}</code>
          <details class="row-details">
            <summary>Metriche e ipotesi segmento</summary>
            <div class="detail-box">
              <div><strong>Metriche:</strong> CTR stor. ${fmtPct2(a.ctr_storico_pct)} · eCTR prev. ${fmtPct2(a.ectr_pct)} · eCPM prev. ${fmtEur2(a.ecpm_eur)}</div>
              <div style="margin-top:0.25rem;"><strong>Ipotesi segmento:</strong> ${esc(a.segmento_ipotizzato)}</div>
            </div>
          </details>
        </td>
      </tr>
    `).join('');

    // Report Tab (Formatted + Raw toggle + Safe Clipboard + Print)
    const reportMd = DATA.report_md || '';
    document.getElementById('report-pre').textContent = reportMd;
    document.getElementById('report-rendered').innerHTML = reportMd
      .split('\n\n')
      .map(block => {
        const b = block.trim();
        if (!b) return '';
        if (b.startsWith('# ')) return `<h2>${esc(b.slice(2))}</h2>`;
        if (b.startsWith('## ')) return `<h3>${esc(b.slice(3))}</h3>`;
        return `<p>${esc(b).replace(/\n/g, '<br>')}</p>`;
      }).join('');
    const insRec = (DATA.interview_summary || {}).receipt;
    if (insRec) {
      document.getElementById('receipts-summary').innerHTML = `<div class="kv-item"><strong>Ricevuta Istanza Riassunto (separata dalle interviste)</strong>Provider: <code>${esc(insRec.providerInstanceId)}</code> · Modello: <code>${esc(insRec.model)}</code> (thinking low) · Task: <code>${esc(insRec.taskId)}</code></div>`;
    }
    const toggleRawBtn = document.getElementById('toggle-raw-btn');
    toggleRawBtn.addEventListener('click', () => {
      const pre = document.getElementById('report-pre');
      const rend = document.getElementById('report-rendered');
      if (pre.hasAttribute('hidden')) { pre.removeAttribute('hidden'); rend.setAttribute('hidden', ''); toggleRawBtn.textContent = 'Mostra vista formattata'; }
      else { pre.setAttribute('hidden', ''); rend.removeAttribute('hidden'); toggleRawBtn.textContent = 'Mostra Markdown grezzo'; }
    });
    document.getElementById('copy-report-btn').addEventListener('click', async () => {
      const statusEl = document.getElementById('copy-status');
      try {
        if (navigator.clipboard && navigator.clipboard.writeText) await navigator.clipboard.writeText(reportMd);
        else {
          const ta = document.createElement('textarea');
          ta.value = reportMd; ta.style.position = 'fixed'; ta.style.opacity = '0';
          document.body.appendChild(ta); ta.select();
          const ok = document.execCommand('copy');
          ta.remove();
          if (!ok) throw new Error('execCommand copy returned false');
        }
        statusEl.textContent = 'Markdown copiato negli appunti.';
      } catch (e) {
        statusEl.textContent = 'Copia automatica non disponibile: usa «Mostra Markdown grezzo».';
      }
      setTimeout(() => { statusEl.textContent = ''; }, 3500);
    });
    function expandDetails() {
      document.querySelectorAll('details.row-details').forEach(d => {
        if (!d.hasAttribute('open')) {
          d.setAttribute('open', '');
          d.setAttribute('data-print-opened', '1');
        }
      });
    }
    function restoreDetails() {
      document.querySelectorAll('details.row-details[data-print-opened="1"]').forEach(d => {
        d.removeAttribute('open');
        d.removeAttribute('data-print-opened');
      });
    }
    window.addEventListener('beforeprint', expandDetails);
    window.addEventListener('afterprint', restoreDetails);
    document.getElementById('print-btn').addEventListener('click', () => { expandDetails(); window.print(); });
  </script>
</body>
</html>
'''
