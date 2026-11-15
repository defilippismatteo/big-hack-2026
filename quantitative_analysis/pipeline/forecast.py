"""Offline baseline, temporal validation and import of another branch's forecasts."""
import csv
import io
import math
import subprocess
from datetime import date, timedelta

from .analytics import groups, history_before, rates
from .contracts import digest

FOLDS = (("2026-10-18", "2026-10-19", "2026-11-01"),
         ("2026-11-01", "2026-11-02", "2026-11-15"))
TARGET_KEYS = ("data", "ad_id", "adset_id", "asset_id", "vertical", "campaign_id", "leva", "formato")


def baseline(history, targets, cutoff):
    train = history_before(history, cutoff)
    recent = history_before(train, cutoff, 14)
    if not train:
        raise ValueError("Storico vuoto al cutoff")
    hierarchy = [(field, groups(recent, field)) for field in ("ad_id", "asset_id", "adset_id", "vertical")]
    seen = {r["ad_id"] for r in train}
    records = []
    for row in targets:
        source, level = train, "global"
        for field, mapping in hierarchy:
            if (row[field],) in mapping:
                source, level = mapping[(row[field],)], field
                break
        value = rates(source)
        records.append({**{k: row[k] for k in TARGET_KEYS},
                        "ctr_predetto_pct": value["ctr_pct"], "cpm_predetto_eur": value["cpm_eur"],
                        "cold_start": row["ad_id"] not in seen, "fallback_level": level,
                        "model_version": "weighted_hierarchical_14d_v1", "cutoff": cutoff,
                        "scenario": "central", "interval_status": "not_calibrated"})
    return records


def metrics(predictions, actual):
    truth = {(r["data"], r["ad_id"]): r for r in actual}
    keys = [(r["data"], r["ad_id"]) for r in predictions]
    if len(keys) != len(set(keys)) or set(keys) != set(truth):
        raise ValueError("Chiavi backtest non corrispondenti")
    if not actual:
        raise ValueError("Holdout vuoto")
    values = {k: 0. for k in ("mae_ctr_pp", "mae_cpm_eur", "wmae_ctr_pp", "wmae_cpm_eur")}
    weight = 0.
    for row in predictions:
        observed = truth[(row["data"], row["ad_id"])]
        imps = float(observed["impression"])
        ctr = 100 * float(observed["click"]) / imps
        cpm = 1000 * float(observed["spesa"]) / imps
        ec, em = abs(float(row["ctr_predetto_pct"]) - ctr), abs(float(row["cpm_predetto_eur"]) - cpm)
        values["mae_ctr_pp"] += ec
        values["mae_cpm_eur"] += em
        values["wmae_ctr_pp"] += ec * imps
        values["wmae_cpm_eur"] += em * imps
        weight += imps
    return {k: value / (weight if k.startswith("wmae") else len(actual)) for k, value in values.items()}


def backtest_baseline(history):
    folds, exports = [], []
    for cutoff, start, end in FOLDS:
        actual = [r for r in history if start <= r["data"] <= end]
        pred = baseline(history, actual, cutoff)
        cold_pred = [r for r in pred if r["cold_start"]]
        cold_keys = {(r["data"], r["ad_id"]) for r in cold_pred}
        folds.append({"cutoff": cutoff, "start": start, "end": end, "rows": len(pred),
                      "metrics": metrics(pred, actual), "cold_start_rows": len(cold_pred),
                      "cold_start_metrics": metrics(cold_pred, [r for r in actual if (r["data"], r["ad_id"]) in cold_keys]) if cold_pred else None})
        truth = {(r["data"], r["ad_id"]): rates([r]) for r in actual}
        exports.extend({**r, "ctr_observed_pct": truth[(r["data"], r["ad_id"])]["ctr_pct"],
                        "cpm_observed_eur": truth[(r["data"], r["ad_id"])]["cpm_eur"]} for r in pred)
    return {"schema_version": "1.0", "model": "weighted_hierarchical_14d_v1", "folds": folds}, exports


def validate_forecast(records, targets):
    keys = lambda rows: [(r["data"], r["ad_id"]) for r in rows]
    got, expected = keys(records), keys(targets)
    if len(got) != len(set(got)) or len(expected) != len(set(expected)) or set(got) != set(expected):
        raise ValueError("Il forecast deve coprire esattamente le chiavi richieste senza duplicati")
    reference = {(r["data"], r["ad_id"]): r for r in targets}
    for row in records:
        target = reference[(row["data"], row["ad_id"])]
        if any(row[k] != target[k] for k in TARGET_KEYS):
            raise ValueError("Mapping del forecast non coerente con le chiavi originali")
        ctr, cpm = float(row["ctr_predetto_pct"]), float(row["cpm_predetto_eur"])
        if not math.isfinite(ctr) or not math.isfinite(cpm) or not 0 <= ctr <= 100 or cpm <= 0:
            raise ValueError("Valori CTR/CPM non validi")


def from_timestral_ref(ref, targets, history):
    # Read immutable blobs, never checkout/merge or alter the other branch.
    commit = subprocess.check_output(["git", "rev-parse", "--verify", f"{ref}^{{commit}}"], text=True).strip()
    prefix = "Prima_Analisi/"
    blob = subprocess.check_output(["git", "show", f"{commit}:{prefix}previsioni_28m.csv"], text=True)
    raw = list(csv.DictReader(io.StringIO(blob)))
    import json
    report = json.loads(subprocess.check_output(["git", "show", f"{commit}:{prefix}metriche.json"], text=True))
    model = next(r for r in report["modelli"] if r["modello"] == "mistralai/Timestral-28M")
    first = model["backtest"][0]["annunci"]
    # Fixed selection rule, evaluated on the earlier fold only, separately for each target.
    use_ctr = first["timestral_adjusted"]["wmae_ctr_pp"] < first["baseline"]["wmae_ctr_pp"]
    use_cpm = first["timestral_adjusted"]["wmae_cpm_eur"] < first["baseline"]["wmae_cpm_eur"]
    source_index = {(r["data"], r["ad_id"]): r for r in raw}
    if len(source_index) != len(raw) or set(source_index) != {(r["data"], r["ad_id"]) for r in targets}:
        raise ValueError("Export Timestral incompleto o con chiavi inattese")
    seen = {r["ad_id"] for r in history}
    local_baseline = {(r["data"], r["ad_id"]): r for r in baseline(history, targets, "2026-11-15")}
    records = []
    for target in targets:
        row = source_index[(target["data"], target["ad_id"])]
        if any(row[k] != target[k] for k in ("asset_id", "adset_id", "vertical")):
            raise ValueError("Mapping export Timestral incoerente")
        reference = local_baseline[(target["data"], target["ad_id"])]
        if (not math.isclose(float(row["ctr_baseline_pct"]), reference["ctr_predetto_pct"], abs_tol=1e-5) or
            not math.isclose(float(row["cpm_baseline_eur"]), reference["cpm_predetto_eur"], abs_tol=1e-5)):
            raise ValueError("La baseline dell'export non coincide con il kit corrente: verificare dati e metodo")
        records.append({**{k: target[k] for k in TARGET_KEYS},
                        "ctr_predetto_pct": float(row["ctr_timestral_p50"] if use_ctr else row["ctr_baseline_pct"]),
                        "cpm_predetto_eur": float(row["cpm_timestral_p50"] if use_cpm else row["cpm_baseline_eur"]),
                        "cold_start": target["ad_id"] not in seen, "fallback_level": "external_pilot",
                        "model_version": f"ctr_{'timestral28m' if use_ctr else 'baseline14d'}__cpm_{'timestral28m' if use_cpm else 'baseline14d'}",
                        "cutoff": "2026-11-15", "scenario": "central", "interval_status": "exploratory_not_calibrated"})
    # Quantiles stay in the source snapshot, not relabeled as calibrated intervals in final CSV.
    return records, {"git_commit": commit, "source_file": prefix + "previsioni_28m.csv",
                     "source_sha256": digest(raw), "selection_metric": "first-fold WMAE per target",
                     "selected_ctr": "timestral28m" if use_ctr else "baseline14d",
                     "selected_cpm": "timestral28m" if use_cpm else "baseline14d",
                     "catboost_comparison": "pending; pilot selection compares only baseline and Timestral",
                     "reported_metrics": model, "raw_forecast": raw}


def seasonal_scenarios(history, targets, market, cutoff):
    lookup = {(r["settimana_dal"], r["vertical"]): r for r in market
              if r["piattaforma"] == "meta" and r["paese"] == "IT"}

    def index(row, target):
        aligned = date.fromisoformat(row["data"]) - timedelta(days=364)
        monday = (aligned - timedelta(days=aligned.weekday())).isoformat()
        return float(lookup[(monday, row["vertical"])][f"indice_{target}"])

    central = baseline(history, targets, cutoff)
    recent = history_before(history, cutoff, 14)
    reference = {}
    for (vertical,), rows in groups(recent, "vertical").items():
        mass = sum(float(r["impression"]) for r in rows)
        reference[vertical] = {k: sum(index(r, k) * float(r["impression"]) for r in rows) / mass for k in ("ctr", "cpm")}
    result = []
    for source, target in zip(central, targets):
        for label, strength in (("conservative", .5), ("central", 1.), ("high_pressure", 1.5)):
            result.append({"data": target["data"], "ad_id": target["ad_id"], "vertical": target["vertical"],
                           "scenario": label,
                           "ctr_scenario_pct": min(100., source["ctr_predetto_pct"] * (index(target, "ctr") / reference[target["vertical"]]["ctr"]) ** strength),
                           "cpm_scenario_eur": source["cpm_predetto_eur"] * (index(target, "cpm") / reference[target["vertical"]]["cpm"]) ** strength,
                           "method": "14d baseline x aligned 2025 index ratio; ex ante assumed strength",
                           "calibrated_interval": False})
    return result
