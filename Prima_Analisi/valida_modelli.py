"""Valida CatBoost e Timestral sulle stesse finestre e coppie giorno/annuncio."""

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

import catboost
import numpy as np
import pandas as pd
import torch
from timestral import TimestralForecaster

from timestral_pilot import FOLDS, load_data, make_input, predict

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = ROOT / "TEST INIZIALI FATTI DA CHAT GPT DA VERIFICARE " / "Wevion_Validation_Baseline.py"
KEY = ["data", "ad_id"]
METRICS = ("ctr", "cpm")
MODELS = ("baseline", "catboost", "timestral_28m", "mix_50_50")
OUTCOMES = ["click", "impression", "spesa", "ctr", "cpm", "cpc", "copertura", "frequenza"]


def original_script(path):
    spec = importlib.util.spec_from_file_location("catboost_originale", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_plan(data, kit):
    history, future = data["history"], data["future"]
    rows = pd.concat([history, future], ignore_index=True)
    ads = pd.read_csv(kit / "annunci.csv", parse_dates=["data_lancio", "data_fine"])
    days = pd.DataFrame({"data": rows.data.sort_values().unique()})
    plan = days.merge(ads[["ad_id", "data_lancio", "data_fine"]], how="cross")
    active = plan.data.ge(plan.data_lancio) & (plan.data_fine.isna() | plan.data.le(plan.data_fine))
    pd.testing.assert_frame_equal(plan.loc[active, KEY].sort_values(KEY).reset_index(drop=True),
                                  rows[KEY].sort_values(KEY).reset_index(drop=True))
    budgets = rows.merge(data["budget"], on=["data", "adset_id"], how="left", validate="many_to_one")
    np.testing.assert_array_equal(budgets.budget_giornaliero_adset, budgets.budget_giornaliero_eur)


def catboost_inputs(original, history, start, end):
    past = history[history.data < start]
    holdout = history[history.data.between(start, end)]
    train, forecast, lag_columns = original.group_features(past, holdout)
    columns = original.CATS + original.BASE + lag_columns
    for frame in (train, forecast):
        for column in original.CATS:
            frame[column] = frame[column].astype(str).fillna("missing")
        for column in original.BASE + lag_columns:
            frame[column] = pd.to_numeric(frame[column], errors="coerce").fillna(-1.0)
    realigned = train.set_index(KEY).loc[pd.MultiIndex.from_frame(past[KEY])]
    pd.testing.assert_frame_equal(realigned[OUTCOMES].reset_index(drop=True),
                                  past[OUTCOMES].reset_index(drop=True))
    return train, forecast, columns


def verify_no_leakage(original, prepared, data, start, end, cutoff, train, holdout, columns):
    # Modifica tutti i risultati dopo il cutoff, lasciando intatti calendario e budget.
    altered = prepared.copy()
    altered.loc[altered.data > cutoff, OUTCOMES] = 0
    other_train, other_holdout, other_columns = catboost_inputs(original, altered, start, end)
    if columns != other_columns or set(columns).intersection(OUTCOMES):
        raise ValueError("Colonne CatBoost incoerenti o con outcome contemporanei")
    pd.testing.assert_frame_equal(train[KEY + columns], other_train[KEY + columns])
    pd.testing.assert_frame_equal(holdout[KEY + columns], other_holdout[KEY + columns])

    # Verifica che nemmeno gli esiti dello stesso giorno entrino nelle feature di training.
    for day in (train.data.min(), train.data.max()):
        perturbed_day = prepared.copy()
        perturbed_day.loc[perturbed_day.data == day, ["click", "spesa"]] = 0
        modified_train, _, _ = catboost_inputs(original, perturbed_day, start, end)
        pd.testing.assert_frame_equal(train.loc[train.data == day, KEY + columns],
                                      modified_train.loc[modified_train.data == day, KEY + columns])

    modified_data = {**data, "history": altered}
    context = make_input(data, cutoff, holdout.data.nunique())
    modified_context = make_input(modified_data, cutoff, holdout.data.nunique())
    for actual, expected in zip(context, modified_context):
        np.testing.assert_array_equal(actual, expected)


def fit_catboost(original, train, holdout, columns):
    result = holdout[KEY].copy()
    target = {
        "ctr": np.log((train.click + 0.5) / (train.impression - train.click + 0.5)),
        "cpm": np.log(train.cpm),
    }
    for metric in METRICS:
        model = catboost.CatBoostRegressor(
            iterations=550, depth=5, learning_rate=0.045, l2_leaf_reg=8,
            loss_function="RMSE", verbose=False, thread_count=4, random_seed=17,
            allow_writing_files=False,
        )
        model.fit(train[columns], target[metric], cat_features=original.CATS)
        estimate = model.predict(holdout[columns])
        result[f"{metric}_catboost"] = 100 / (1 + np.exp(-estimate)) if metric == "ctr" else np.exp(estimate)
    return result


def score(frame):
    result = {"righe": len(frame), "impression": int(frame.impression.sum())}
    for method in MODELS:
        for metric in METRICS:
            error = (frame[f"{metric}_{method}"] - frame[f"{metric}_osservato_kit"]).abs()
            result[f"{metric}_{method}"] = {
                "mae": round(float(error.mean()), 6),
                "wmae": round(float(np.average(error, weights=frame.impression)), 6),
            }
    return result


def run_fold(original, prepared, data, forecaster, start, end):
    cutoff = pd.Timestamp(start) - pd.Timedelta(days=1)
    train, holdout, columns = catboost_inputs(original, prepared, start, end)
    verify_no_leakage(original, prepared, data, start, end, cutoff, train, holdout, columns)
    target = data["history"][data["history"].data.between(start, end)]
    pd.testing.assert_frame_equal(holdout[KEY].reset_index(drop=True),
                                  target.sort_values(KEY)[KEY].reset_index(drop=True))
    metrics = {
        "ctr_baseline_pct": "ctr_baseline", "cpm_baseline_eur": "cpm_baseline",
        "ctr_predetto_pct": "ctr_timestral_28m", "cpm_predetto_eur": "cpm_timestral_28m",
    }
    timestral = predict(data, target, cutoff, forecaster)[KEY + list(metrics)].rename(columns=metrics)
    cb = fit_catboost(original, train, holdout, columns)
    frame = target[KEY + ["adset_id", "vertical", "impression"]].copy()
    frame["ctr_osservato_kit"] = 100 * target.click / target.impression
    frame["cpm_osservato_kit"] = 1000 * target.spesa / target.impression
    frame = frame.merge(timestral, on=KEY, how="left", validate="one_to_one")
    frame = frame.merge(cb, on=KEY, how="left", validate="one_to_one")
    if not np.isfinite(frame.select_dtypes("number").to_numpy()).all():
        raise ValueError("Previsioni mancanti o non finite")

    naive = original.heuristic(prepared[prepared.data <= cutoff], holdout)
    baseline_aligned = frame.set_index(KEY).loc[pd.MultiIndex.from_frame(holdout[KEY])]
    for metric in METRICS:
        np.testing.assert_allclose(naive[f"pred_{metric}"], baseline_aligned[f"{metric}_baseline"])
        frame[f"{metric}_mix_50_50"] = (frame[f"{metric}_catboost"] + frame[f"{metric}_timestral_28m"]) / 2
    frame["nuovo_annuncio"] = ~frame.ad_id.isin(train.ad_id)
    frame["cutoff"] = cutoff.date().isoformat()
    return frame.sort_values(KEY), len(train)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kit", type=Path, required=True, help="Cartella dati/ estratta")
    parser.add_argument("--model-28m", type=Path, required=True)
    parser.add_argument("--catboost-script", type=Path, default=ORIGINAL)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    torch.set_num_threads(2)
    original = original_script(args.catboost_script)
    prepared, _ = original.setup(args.kit)
    data = load_data(args.kit)
    verify_plan(data, args.kit)
    forecaster = TimestralForecaster.from_pretrained(args.model_28m, device="cpu", local_files_only=True)
    args.output.mkdir(parents=True, exist_ok=True)
    folds, predictions = [], []
    for start, end in FOLDS:
        print(f"Validazione {start} – {end}", flush=True)
        frame, train_rows = run_fold(original, prepared, data, forecaster, start, end)
        folds.append({"dal": start, "al": end, "righe_train": train_rows,
                      "tutti": score(frame), "annunci_nuovi": score(frame[frame.nuovo_annuncio]),
                      "annunci_gia_visti": score(frame[~frame.nuovo_annuncio])})
        predictions.append(frame)
    combined = pd.concat(predictions, ignore_index=True)
    with (args.model_28m / "model.safetensors").open("rb") as file:
        weights = hashlib.file_digest(file, "sha256").hexdigest()
    report = {
        "catboost_versione": catboost.__version__,
        "numpy_versione": np.__version__,
        "pandas_versione": pd.__version__,
        "pytorch_versione": torch.__version__,
        "timestral_28m_sha256": weights,
        "catboost_originale_sha256": hashlib.sha256(args.catboost_script.read_bytes()).hexdigest(),
        "verifiche": ["stesse chiavi", "calendario annunci e budget coerenti",
                     "baseline equivalente", "outcome dopo cutoff alterati",
                     "outcome dello stesso giorno alterati alle estremità del training"],
        "fold": folds, "aggregato": score(combined),
    }
    for (start, _), frame in zip(FOLDS, predictions):
        frame.to_csv(args.output / f"previsioni_{start}.csv", index=False, float_format="%.8f")
    (args.output / "metriche.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Verificate {len(combined)} righe. Risultati in {args.output}")


if __name__ == "__main__":
    main()
