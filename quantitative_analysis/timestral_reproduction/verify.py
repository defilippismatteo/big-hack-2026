"""Audit della replica: confronto con blob Git, integrità e bande esplorative.

Eseguire con venv/bin/python dalla root della repository. Nessuna chiamata remota.
"""
from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import torch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = HERE / "source"
sys.path.insert(0, str(SOURCE / "Test_Timestral"))
from timestral import TimestralForecaster
from timestral_pilot import CUTOFF, FOLDS, execute, load_data, make_input

COMMIT = "2d8adf033e747e147c401246c07ce656f9f1cfb7"
REVISIONS = {
    "5m": "bdd20cfc15a3fea0e4cb5ccef37f8d3ca7aa335f",
    "28m": "49b26409ac87b5935539a5d8ffe7f397b720db47",
}


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path):
    return json.loads(path.read_text())


def compare_tree(a, b, path=""):
    """Ignore hardware and timing only; all model/fold records must coincide."""
    differences = []
    if isinstance(a, dict):
        assert isinstance(b, dict) and set(a) == set(b), path
        for key in a:
            if key != "secondi_caricamento_backtest_e_forecast":
                differences.extend(compare_tree(a[key], b[key], f"{path}/{key}"))
    elif isinstance(a, list):
        assert len(a) == len(b), path
        for i, (x, y) in enumerate(zip(a, b)):
            differences.extend(compare_tree(x, y, f"{path}/{i}"))
    elif a != b:
        differences.append({"path": path, "reference": a, "local": b})
    return differences


def main():
    torch.set_num_threads(2)
    kit = ROOT / "data" / "challenge_kit" / "dati"
    data = load_data(kit)
    reference = read(SOURCE / "Prima_Analisi/metriche.json")
    local = read(HERE / "results/metriche.json")
    differences = compare_tree(reference["modelli"], local["modelli"])
    assert not differences, differences
    cat_source = SOURCE / "TEST INIZIALI FATTI DA CHAT GPT DA VERIFICARE "
    cat_ref = read(cat_source / "Wevion_validazione_baseline.json")
    cat_local = read(HERE / "catboost/catboost_metrics.json")
    assert cat_ref == cat_local, "CatBoost non coincide con il report iniziale"

    provenance = {
        "verified_utc": datetime.now(timezone.utc).isoformat(),
        "branch_snapshot_commit": COMMIT,
        "timestral_source_commit": "a534bdbd244d64f3d9d743f46c7bf6fc330ed4ff",
        "local_environment": {"python": platform.python_version(), "torch": torch.__version__,
                              "numpy": np.__version__, "pandas": pd.__version__,
                              "architecture": platform.machine(), "device": "cpu", "threads": 2},
        "reference_environment": {k: reference[k] for k in ("python", "torch", "architettura", "thread_cpu")},
        "kit_sha256": {str(p.relative_to(kit)): sha(p) for p in sorted(kit.rglob("*.csv"))},
        "specification_sha256": sha(ROOT / "docs" / "BigHack2026_Wevion_Specifica_Operativa_v4.md"),
        "source_sha256": {str(p.relative_to(SOURCE)): sha(p) for p in sorted(SOURCE.rglob("*.py"))},
        "metric_differences_at_published_precision": differences,
        "catboost_reference_metrics_exact": True,
        "models": [],
    }
    metric_rows, interval_rows = [], []
    for size, ref_model, model_result in zip(("5m", "28m"), reference["modelli"], local["modelli"]):
        path = HERE / "models" / f"timestral-{size}"
        assert sha(path / "model.safetensors") == ref_model["sha256_pesi"]
        ref = pd.read_csv(SOURCE / "Prima_Analisi" / f"previsioni_{size}.csv")
        now = pd.read_csv(HERE / "results" / f"previsioni_{size}.csv")
        keys = ["data", "ad_id"]
        assert not now.duplicated(keys).any()
        a = ref.set_index(keys).sort_index()
        b = now.set_index(keys).sort_index()
        assert a.index.equals(b.index) and len(b) == 699
        numcols = a.select_dtypes("number").columns
        assert a.drop(columns=numcols).equals(b.drop(columns=numcols))
        errors = (a[numcols] - b[numcols]).abs().max()
        # Numerical sanity threshold, not a forecasting accuracy criterion.
        assert (errors <= 0.0005).all(), errors
        model = TimestralForecaster.from_pretrained(path, device="cpu", local_files_only=True)
        # Retain raw fold predictions as well as the reduced report CSVs.
        rawdir = HERE / "raw" / size
        summary = execute(data, "all", rawdir, model)
        summary["model"] = str(path.relative_to(ROOT))
        summary["note"] = "Corrected model provenance in audit wrapper; original execute uses a constant MODEL."
        (rawdir / "run_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
        prep = read(rawdir / "preparation.json")
        prep["model"] = summary["model"]
        (rawdir / "preparation.json").write_text(json.dumps(prep, indent=2) + "\n")
        windows = []
        for fold in model_result["backtest"]:
            for method in ("baseline", "timestral_adjusted"):
                metric_rows.append({"model": size, "start": fold["inizio"], "end": fold["fine"],
                                    "method": method, **fold["annunci"][method]})
            cutoff = pd.Timestamp(fold["cutoff"])
            before, known = make_input(data, cutoff, 14)
            modified = {**data, "history": data["history"].copy()}
            later = modified["history"].data > cutoff
            modified["history"].loc[later, ["click", "impression", "spesa"]] = 999999
            after, after_known = make_input(modified, cutoff, 14)
            assert np.array_equal(before, after, equal_nan=True)
            assert np.array_equal(known, after_known, equal_nan=True)
            prediction = pd.read_csv(rawdir / f"backtest_{fold['inizio']}_{fold['fine']}.csv")
            hold = data["history"][data["history"].data.between(fold["inizio"], fold["fine"])].copy()
            hold["data"] = hold.data.dt.strftime("%Y-%m-%d")
            joined = prediction.merge(hold[keys + ["click", "impression", "spesa"]], on=keys, validate="one_to_one")
            seen = data["history"].loc[data["history"].data <= cutoff, "ad_id"]
            for subset, frame in (("all", joined), ("cold_start", joined[~joined.ad_id.isin(seen)])):
                for target in ("ctr", "cpm"):
                    lo, hi = (frame[f"{target}_timestral_{q}"] for q in ("p10", "p90"))
                    actual = (100 * frame.click / frame.impression if target == "ctr" else 1000 * frame.spesa / frame.impression)
                    interval_rows.append({"model": size, "start": fold["inizio"], "subset": subset,
                                          "target": target, "rows": len(frame),
                                          "coverage": float(actual.between(lo, hi).mean()),
                                          "mean_width": float((hi - lo).mean()),
                                          "median_width": float((hi - lo).median()),
                                          "status": "exploratory_not_calibrated"})
            windows.append({"cutoff": fold["cutoff"], "future_target_mutation_changes_input": False})
        final = pd.read_csv(rawdir / "forecast_2026-11-16_30.csv")
        assert np.allclose(final.ctr_timestral_p50, now.ctr_timestral_p50, atol=0.00000051, rtol=0)
        assert np.allclose(final.cpm_timestral_p50, now.cpm_timestral_p50, atol=0.00000051, rtol=0)
        for target in ("ctr", "cpm"):
            q = final[[f"{target}_timestral_{p}" for p in ("p10", "p50", "p90")]]
            assert np.isfinite(q).all().all() and (np.diff(q, axis=1) >= 0).all()
            assert ((q >= 0) & (q <= 100)).all().all() if target == "ctr" else (q > 0).all().all()
        provenance["models"].append({"model": ref_model["modello"], "hub_revision": REVISIONS[size],
                                     "weight_sha256": sha(path / "model.safetensors"),
                                     "weight_bytes": (path / "model.safetensors").stat().st_size,
                                     "config_sha256": sha(path / "config.json"),
                                     "published_metrics_identical": True,
                                     "forecast_max_abs_deltas_by_column": errors.to_dict(),
                                     "forecast_bitwise_identical": sha(HERE / "results" / f"previsioni_{size}.csv") == sha(SOURCE / "Prima_Analisi" / f"previsioni_{size}.csv"),
                                     "local_timing_seconds": model_result["secondi_caricamento_backtest_e_forecast"],
                                     "validated_rows": len(now), "no_future_target_leak": windows})
    for fold in cat_local["folds"]:
        m = fold["catboost"]
        metric_rows.append({"model": "catboost", "method": "catboost", "start": fold["valid_from"], "end": fold["valid_to"],
                            "mae_ctr_pp": m["ctr_mae_pp"], "mae_cpm_eur": m["cpm_mae_eur"],
                            "wmae_ctr_pp": m["ctr_wmae_pp"], "wmae_cpm_eur": m["cpm_wmae_eur"]})
    pd.DataFrame(metric_rows).to_csv(HERE / "results/method_comparison.csv", index=False)
    pd.DataFrame(interval_rows).to_csv(HERE / "results/interval_diagnostics.csv", index=False)
    # A separate candidate uses the branch's existing rule, without changing published delivery artifacts.
    forecast = pd.read_csv(HERE / "raw/28m/forecast_2026-11-16_30.csv")
    forecast["ctr_predetto_pct"] = forecast.ctr_baseline_pct
    forecast["cpm_predetto_eur"] = forecast.cpm_timestral_p50
    forecast["model_version"] = "ctr_baseline14d__cpm_timestral28m_local_reproduction"
    forecast["interval_status"] = "exploratory_not_calibrated"
    forecast.to_csv(HERE / "results/forecast_candidate_2026-11-16_30.csv", index=False)
    delivery = ROOT / "data/predictions/v4_delivery/forecasts_2026-11-16_30.csv"
    if delivery.exists():
        old = pd.read_csv(delivery).set_index(["data", "ad_id"]).sort_index()
        new = forecast.set_index(["data", "ad_id"]).sort_index()
        assert old.index.equals(new.index)
        provenance["existing_delivery_forecast_max_abs_delta"] = {
            k: float((old[k] - new[k]).abs().max()) for k in ("ctr_predetto_pct", "cpm_predetto_eur")}
    (HERE / "results/verification.json").write_text(json.dumps(provenance, indent=2) + "\n")
    print(json.dumps({"models": provenance["models"], "catboost_reference_metrics_exact": True}, indent=2))


if __name__ == "__main__":
    main()
