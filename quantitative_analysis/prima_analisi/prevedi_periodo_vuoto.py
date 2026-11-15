"""Prevede il periodo vuoto (16-30 novembre 2026) con i modelli validati sui dati del kit."""

import argparse
import hashlib
import json
from pathlib import Path

import catboost
import numpy as np
import pandas as pd
import torch
from timestral import TimestralForecaster

from timestral_pilot import load_data, predict, validate_forecast
from valida_modelli import (
    KEY,
    METRICS,
    ORIGINAL,
    OUTCOMES,
    fit_catboost,
    original_script,
    verify_plan,
)

CUTOFF = pd.Timestamp("2026-11-15")
BLACK_WEEK_START = pd.Timestamp("2026-11-20")


def prepare_future_inputs(original, history, future):
    """Costruisce le feature CatBoost per il periodo futuro senza data leakage."""
    train, forecast, lag_columns = original.group_features(history, future)
    columns = original.CATS + original.BASE + lag_columns
    for frame in (train, forecast):
        for column in original.CATS:
            frame[column] = frame[column].astype(str).fillna("missing")
        for column in original.BASE + lag_columns:
            frame[column] = pd.to_numeric(frame[column], errors="coerce").fillna(-1.0)
    realigned = train.set_index(KEY).loc[pd.MultiIndex.from_frame(history[KEY])]
    pd.testing.assert_frame_equal(
        realigned[OUTCOMES].reset_index(drop=True),
        history[OUTCOMES].reset_index(drop=True),
    )
    return train, forecast, columns


def summarize_group(frame):
    """Calcola statistiche descrittive (mediana, media, min, max) per un sottoinsieme."""
    return {
        "righe": int(len(frame)),
        "annunci_distinti": int(frame["ad_id"].nunique()),
        "ctr_scelto_mediana_pct": round(float(frame["ctr_scelto_pct"].median()), 4),
        "ctr_scelto_media_pct": round(float(frame["ctr_scelto_pct"].mean()), 4),
        "cpm_scelto_mediana_eur": round(float(frame["cpm_scelto_eur"].median()), 4),
        "cpm_scelto_media_eur": round(float(frame["cpm_scelto_eur"].mean()), 4),
        "cpm_catboost_mediana_eur": round(float(frame["cpm_catboost"].median()), 4),
        "cpm_timestral_28m_mediana_eur": round(float(frame["cpm_timestral_28m"].median()), 4),
    }


def build_summary(frame, kit, model_28m, catboost_script):
    """Costruisce il riepilogo JSON delle previsioni e delle verifiche."""
    with (model_28m / "model.safetensors").open("rb") as file:
        weights_sha256 = hashlib.file_digest(file, "sha256").hexdigest()

    by_vertical = {
        vertical: summarize_group(group)
        for vertical, group in frame.groupby("vertical", sort=True)
    }
    by_period = {
        "pre_black_week_16_19_nov": summarize_group(frame[frame["data"] < BLACK_WEEK_START]),
        "black_week_e_eventi_20_30_nov": summarize_group(frame[frame["data"] >= BLACK_WEEK_START]),
    }
    by_cold_start = {
        "annunci_gia_visti": summarize_group(frame[~frame["nuovo_annuncio"]]),
        "annunci_nuovi": summarize_group(frame[frame["nuovo_annuncio"]]),
    }

    return {
        "cutoff": CUTOFF.date().isoformat(),
        "dal": frame["data"].min().date().isoformat(),
        "al": frame["data"].max().date().isoformat(),
        "fonte_dati": "Solo dati forniti dagli organizzatori (senza moltiplicatori esterni Black Friday)",
        "strategia_modelli": {
            "ctr": "baseline_14g",
            "cpm": "mix_50_50_catboost_timestral28m",
        },
        "versioni": {
            "catboost": catboost.__version__,
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "pytorch": torch.__version__,
        },
        "timestral_28m_sha256": weights_sha256,
        "catboost_originale_sha256": hashlib.sha256(catboost_script.read_bytes()).hexdigest(),
        "verifiche": [
            "699 chiavi esattamente corrispondenti a da_prevedere.csv",
            "calendario annunci e budget coerenti",
            "baseline equivalente tra CatBoost script e Timestral pilot",
            "valori finiti, CTR in [0, 100], CPM > 0",
        ],
        "totale": summarize_group(frame),
        "per_vertical": by_vertical,
        "per_periodo": by_period,
        "per_stato_annuncio": by_cold_start,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kit", type=Path, required=True, help="Cartella dati/ estratta")
    parser.add_argument("--model-28m", type=Path, required=True)
    parser.add_argument("--catboost-script", type=Path, default=ORIGINAL)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    torch.set_num_threads(2)
    original = original_script(args.catboost_script)
    history, future = original.setup(args.kit)
    data = load_data(args.kit)
    verify_plan(data, args.kit)

    train, forecast, columns = prepare_future_inputs(original, history, future)
    forecaster = TimestralForecaster.from_pretrained(
        args.model_28m, device="cpu", local_files_only=True
    )

    ts_cols = {
        "ctr_baseline_pct": "ctr_baseline",
        "cpm_baseline_eur": "cpm_baseline",
        "ctr_predetto_pct": "ctr_timestral_28m",
        "cpm_predetto_eur": "cpm_timestral_28m",
    }
    timestral_pred = predict(data, data["future"], CUTOFF, forecaster)[
        KEY + list(ts_cols)
    ].rename(columns=ts_cols)
    cb_pred = fit_catboost(original, train, forecast, columns)

    meta_cols = [
        "adset_id",
        "asset_id",
        "vertical",
        "leva",
        "formato",
        "budget_giornaliero_adset",
        "is_black_week",
        "is_black_friday",
        "is_cyber_monday",
    ]
    frame = future[KEY + meta_cols].copy()
    frame = frame.merge(timestral_pred, on=KEY, how="left", validate="one_to_one")
    frame = frame.merge(cb_pred, on=KEY, how="left", validate="one_to_one")

    # Verifica coerenza baseline tra heuristic() di CatBoost e baseline() di Timestral pilot
    naive = original.heuristic(history, forecast)
    aligned = frame.set_index(KEY).loc[pd.MultiIndex.from_frame(forecast[KEY])]
    for metric in METRICS:
        np.testing.assert_allclose(naive[f"pred_{metric}"], aligned[f"{metric}_baseline"])
        frame[f"{metric}_mix_50_50"] = (
            frame[f"{metric}_catboost"] + frame[f"{metric}_timestral_28m"]
        ) / 2.0

    # Selezione vincente da Validazione_Modelli: CTR = baseline 14g, CPM = Media 50/50
    frame["ctr_scelto_pct"] = frame["ctr_baseline"]
    frame["cpm_scelto_eur"] = frame["cpm_mix_50_50"]
    frame["modello_ctr"] = "baseline_14g"
    frame["modello_cpm"] = "mix_50_50_catboost_timestral28m"
    frame["nuovo_annuncio"] = ~frame["ad_id"].isin(history["ad_id"])

    # Validazione formale sul contratto di output atteso da validate_forecast
    check_df = frame[KEY + ["ctr_scelto_pct", "cpm_scelto_eur"]].rename(
        columns={"ctr_scelto_pct": "ctr_predetto_pct", "cpm_scelto_eur": "cpm_predetto_eur"}
    )
    validate_forecast(check_df, data["future"])
    if not np.isfinite(frame.select_dtypes("number").to_numpy()).all():
        raise ValueError("Previsioni mancanti o non finite")

    frame = frame.sort_values(KEY).reset_index(drop=True)
    args.output.mkdir(parents=True, exist_ok=True)
    frame.to_csv(
        args.output / "previsioni_2026-11-16_30.csv",
        index=False,
        float_format="%.6f",
        date_format="%Y-%m-%d",
    )
    summary = build_summary(frame, args.kit, args.model_28m, args.catboost_script)
    (args.output / "riepilogo.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Generate {len(frame)} previsioni in {args.output}")


if __name__ == "__main__":
    main()
