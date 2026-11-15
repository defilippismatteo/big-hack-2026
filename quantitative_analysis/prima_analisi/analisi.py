"""Backtest del pilota Timestral e scenari CPM da campagne pubbliche."""

import argparse
import hashlib
import json
import platform
from pathlib import Path
from time import perf_counter

import numpy as np
import pandas as pd
import torch

from timestral import TimestralForecaster
from timestral_pilot import (
    CUTOFF,
    COVARIATES,
    FOLDS,
    evaluate,
    load_data,
    make_input,
    predict,
    rates,
    validate_forecast,
)

HERE = Path(__file__).resolve().parent


def backtest_adset(prediction, holdout, history, cutoff):
    keys = ["data", "adset_id"]
    observed = holdout.groupby(keys, as_index=False)[["click", "impression", "spesa"]].sum()
    direct_cols = ["as_ctr_p10", "as_ctr_p50", "as_ctr_p90",
                   "as_cpm_p10", "as_cpm_p50", "as_cpm_p90"]
    direct = prediction[keys + direct_cols].drop_duplicates()
    joined = observed.merge(direct, on=keys, how="left", validate="one_to_one")
    if joined[direct_cols].isna().any().any():
        raise ValueError("Previsioni dirette mancanti per coppie data/ad set")

    recent = history[history.data.between(cutoff - pd.Timedelta(days=13), cutoff)]
    reference = rates(recent, "adset_id")
    truth = {"ctr": 100 * joined.click / joined.impression,
             "cpm": 1000 * joined.spesa / joined.impression}
    result = {"righe": len(joined)}
    for metric, actual in truth.items():
        base = joined.adset_id.map(reference[metric])
        if base.isna().any():
            raise ValueError("Baseline ad set mancante")
        errors = pd.DataFrame({"baseline": (base - actual).abs(),
                               "timestral": (joined[f"as_{metric}_p50"] - actual).abs()})
        result[metric] = {
            method: {
                "mae": round(float(errors[method].mean()), 4),
                "wmae": round(float(np.average(errors[method], weights=joined.impression)), 4),
            }
            for method in errors
        }
        result[metric]["copertura_q10_q90"] = round(
            float(actual.between(joined[f"as_{metric}_p10"], joined[f"as_{metric}_p90"]).mean()), 4
        )
    return result


def backtest_annunci(prediction, holdout):
    metrics = evaluate(prediction, holdout)
    # Il confronto diretto richiede target aggregati per ad set e giorno.
    del metrics["timestral_direct_adset"]
    return metrics


def scenario_cpm(history, output):
    october = history[history.data.between("2026-10-01", "2026-10-31")]
    october_rates = rates(october, "vertical").reset_index()
    external = pd.read_csv(HERE / "scenari_cpm.csv")
    scenarios = external.merge(october_rates[["vertical", "cpm"]], how="cross")
    scenarios = scenarios.rename(columns={"cpm": "cpm_ottobre_kit_eur"})
    scenarios["cpm_scenario_eur"] = scenarios.cpm_ottobre_kit_eur * scenarios.moltiplicatore_cpm
    scenarios.to_csv(output / "cpm_scenari_evento.csv", index=False, float_format="%.4f")


def run_model(data, model_path, model_id, output):
    started = perf_counter()
    model = TimestralForecaster.from_pretrained(model_path, device="cpu", local_files_only=True)
    history, future = data["history"], data["future"]
    folds = []
    for start, end in FOLDS:
        cutoff = pd.Timestamp(start) - pd.Timedelta(days=1)
        holdout = history[history.data.between(start, end)]
        prediction = predict(data, holdout, cutoff, model)
        cold = ~holdout.ad_id.isin(history.loc[history.data <= cutoff, "ad_id"])
        cold_prediction = prediction[prediction.ad_id.isin(holdout.loc[cold, "ad_id"])]
        context, known = make_input(data, cutoff, holdout.data.nunique())
        folds.append({
            "inizio": start, "fine": end, "cutoff": cutoff.date().isoformat(),
            "context_shape": list(context.shape), "covariates_shape": list(known.shape),
            "righe_annuncio": len(holdout),
            "annunci": backtest_annunci(prediction, holdout),
            "ad_set": backtest_adset(prediction, holdout, history, cutoff),
            "avvio_a_freddo": {
                "annunci": int(holdout.loc[cold, "ad_id"].nunique()),
                "righe": int(cold.sum()),
                "metriche": backtest_annunci(cold_prediction, holdout[cold]) if cold.any() else {},
            },
        })

    prediction = predict(data, future, CUTOFF, model)
    validate_forecast(prediction, future)
    columns = ["data", "vertical", "adset_id", "ad_id", "asset_id",
               "ctr_baseline_pct", "cpm_baseline_eur",
               "ctr_timestral_p10", "ctr_timestral_p50", "ctr_timestral_p90",
               "cpm_timestral_p10", "cpm_timestral_p50", "cpm_timestral_p90"]
    if not np.isfinite(prediction[columns[5:]].to_numpy()).all():
        raise ValueError("Valori non finiti nel CSV delle previsioni")
    for target in ("ctr", "cpm"):
        quantiles = prediction[[f"{target}_timestral_{q}" for q in ("p10", "p50", "p90")]]
        if (np.diff(quantiles, axis=1) < 0).any():
            raise ValueError(f"Quantili non ordinati per {target}")
    filename = f"previsioni_{model_id.lower()}.csv"
    prediction[columns].to_csv(output / filename, index=False, float_format="%.6f")
    with (model_path / "model.safetensors").open("rb") as weights:
        sha256 = hashlib.file_digest(weights, "sha256").hexdigest()
    return {
        "modello": f"mistralai/Timestral-{model_id}",
        "sha256_pesi": sha256,
        "secondi_caricamento_backtest_e_forecast": round(perf_counter() - started, 2),
        "backtest": folds,
        "forecast": {
            "file": filename, "righe": len(prediction),
            "nuovi_annunci": int(future.loc[~future.ad_id.isin(history.ad_id), "ad_id"].nunique()),
            "righe_nuovi_annunci": int((~future.ad_id.isin(history.ad_id)).sum()),
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kit", type=Path, required=True)
    parser.add_argument("--model-5m", type=Path, required=True)
    parser.add_argument("--model-28m", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=HERE)
    args = parser.parse_args()
    torch.set_num_threads(2)
    data = load_data(args.kit)
    args.output.mkdir(parents=True, exist_ok=True)
    scenario_cpm(data["history"], args.output)
    result = {
        "python": platform.python_version(), "torch": torch.__version__,
        "architettura": platform.machine(), "thread_cpu": torch.get_num_threads(),
        "covariate_pilota": COVARIATES,
        "modelli": [
            run_model(data, args.model_5m, "5M", args.output),
            run_model(data, args.model_28m, "28M", args.output),
        ],
    }
    (args.output / "metriche.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
