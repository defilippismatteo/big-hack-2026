#!/usr/bin/env python3
"""Wevion Timestral-28M pilot: 12 ad sets, temporal backtests, 699 ad/day predictions."""
from __future__ import annotations

import argparse
import io
import json
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

FOLDS = [("2026-10-19", "2026-11-01"), ("2026-11-02", "2026-11-15")]
FINAL_START, FINAL_END = "2026-11-16", "2026-11-30"
CUTOFF = pd.Timestamp("2026-11-15")
MODEL = "mistralai/Timestral-28M"
COVARIATES = ["budget_adset", "market_ctr_2025", "market_cpm_2025",
              "weekend", "black_week", "black_friday", "cyber_monday"]
META = ["data", "giorno_settimana", "piattaforma", "vertical", "campaign_id",
        "adset_id", "ad_id", "asset_id", "leva", "formato", "budget_giornaliero_adset"]
EPS = 1e-3


def read_csv(source: Path, filename: str, **kwargs) -> pd.DataFrame:
    if source.is_dir():
        for path in (source / filename, source / "dati" / filename):
            if path.is_file():
                return pd.read_csv(path, **kwargs)
        raise FileNotFoundError(f"Missing {filename} in {source}")
    with zipfile.ZipFile(source) as archive:
        matches = [n for n in archive.namelist()
                   if n == f"dati/{filename}" or n.endswith(f"/dati/{filename}")]
        if len(matches) != 1:
            raise ValueError(f"Expected exactly one dati/{filename} in ZIP, found {matches}")
        return pd.read_csv(io.BytesIO(archive.read(matches[0])), **kwargs)


def load_data(source: Path) -> dict:
    if not source.exists():
        raise FileNotFoundError(source)
    d = {
        "history": read_csv(source, "storico_giornaliero.csv", parse_dates=["data"]),
        "future": read_csv(source, "da_prevedere.csv", parse_dates=["data"]),
        "budget": read_csv(source, "budget_giornaliero.csv", parse_dates=["data"]),
        "market": read_csv(source, "benchmark_mercato_settimanale_2025.csv",
                           parse_dates=["settimana_dal"]),
        "adset": read_csv(source, "adset.csv"),
        "campaign": read_csv(source, "campagne.csv"),
    }
    h, f, b, m = (d[k] for k in ("history", "future", "budget", "market"))
    for name, frame, keys in [
        ("history", h, ["data", "ad_id"]), ("future", f, ["data", "ad_id"]),
        ("budget", b, ["data", "adset_id"]),
        ("market", m, ["vertical", "settimana_dal"]),
    ]:
        if frame.duplicated(keys).any():
            raise ValueError(f"Duplicate {name} keys: {keys}")
    if len(h) != 1879 or len(f) != 699 or f.data.min() != pd.Timestamp(FINAL_START) or f.data.max() != pd.Timestamp(FINAL_END):
        raise ValueError("Unexpected kit dimensions or future dates")
    if h.data.max() != CUTOFF or h.data.min() != pd.Timestamp("2026-08-17"):
        raise ValueError("Unexpected historical dates")
    if (h.impression <= 0).any() or (h.click < 0).any() or (h.click > h.impression).any() or (h.spesa < 0).any():
        raise ValueError("Invalid historical clicks, impressions or spend")
    if h[["click", "impression", "spesa"]].isna().any().any():
        raise ValueError("Null historical inputs")
    if set(f.adset_id) != set(d["adset"].adset_id) or len(d["adset"]) != 12:
        raise ValueError("Expected 12 adsets with future rows")
    vertical = d["adset"][["adset_id", "campaign_id"]].merge(
        d["campaign"][["campaign_id", "vertical"]], on="campaign_id", validate="many_to_one"
    )
    d["vertical"] = dict(zip(vertical.adset_id, vertical.vertical))
    d["adsets"] = sorted(d["adset"].adset_id.tolist())
    return d


def rates(frame: pd.DataFrame, group: str) -> pd.DataFrame:
    aggregated = frame.groupby(group).agg(click=("click", "sum"),
                                           impression=("impression", "sum"), spesa=("spesa", "sum"))
    aggregated = aggregated[aggregated.impression > 0]
    return pd.DataFrame({
        "ctr": 100.0 * aggregated.click / aggregated.impression,
        "cpm": 1000.0 * aggregated.spesa / aggregated.impression
    })


def make_input(d: dict, cutoff: pd.Timestamp, horizon: int):
    """Only target values <= cutoff. Covariates are known before cutoff."""
    if cutoff > CUTOFF or horizon <= 0:
        raise ValueError("Invalid forecast origin/horizon")
    history = d["history"][d["history"].data <= cutoff]
    past_days = pd.date_range(d["history"].data.min(), cutoff, freq="D")
    dates = pd.date_range(past_days[0], periods=len(past_days) + horizon, freq="D")
    hist = history.groupby(["adset_id", "data"], as_index=False).agg(
        click=("click", "sum"), impression=("impression", "sum"), spesa=("spesa", "sum")
    )
    hist["ctr"] = 100.0 * hist.click / hist.impression
    hist["cpm"] = 1000.0 * hist.spesa / hist.impression
    context = np.full((12, 2, len(past_days)), np.nan, dtype=np.float32)
    known = np.zeros((12, len(COVARIATES), len(dates)), dtype=np.float32)
    weeks = (dates - pd.Timedelta(days=364)).to_period("W-SUN").start_time
    for i, aid in enumerate(d["adsets"]):
        t = hist[hist.adset_id == aid].set_index("data").reindex(past_days)
        context[i, 0] = t["ctr"].to_numpy(dtype=np.float32)
        context[i, 1] = t["cpm"].to_numpy(dtype=np.float32)
        if not np.isfinite(context[i]).any(axis=1).all():
            raise ValueError(f"All historical values missing for {aid}")
        budget = d["budget"][d["budget"].adset_id == aid].set_index("data")
        v = d["vertical"][aid]
        market = d["market"][d["market"].vertical == v].set_index("settimana_dal")
        season = market.reindex(weeks)
        cov = [
            budget.reindex(dates).budget_giornaliero_eur.to_numpy(dtype=float),
            season.indice_ctr.to_numpy(dtype=float) / 100.0,
            season.indice_cpm.to_numpy(dtype=float) / 100.0,
            (dates.dayofweek >= 5).astype(float),
            ((dates >= "2026-11-20") & (dates <= "2026-11-30")).astype(float),
            (dates == "2026-11-27").astype(float),
            (dates == "2026-11-30").astype(float),
        ]
        known[i] = np.asarray(cov, dtype=np.float32)
        if not np.isfinite(known[i]).all():
            raise ValueError(f"Missing known future data for {aid}")
    return context, known


def baseline(history: pd.DataFrame, rows: pd.DataFrame, cutoff: pd.Timestamp) -> pd.DataFrame:
    history = history[history.data <= cutoff]
    if history.empty:
        raise ValueError("No history before forecast cutoff")
    recent = history[history.data >= cutoff - pd.Timedelta(days=13)]
    result = pd.DataFrame(index=rows.index, data={"ctr": np.nan, "cpm": np.nan})
    for group in ("ad_id", "asset_id", "adset_id", "vertical"):
        r = rates(recent, group)
        for measure in ("ctr", "cpm"):
            result[measure] = result[measure].fillna(rows[group].map(r[measure]))
    for measure in ("ctr", "cpm"):
        fallback = (100.0 * history.click.sum() / history.impression.sum() if measure == "ctr"
                    else 1000.0 * history.spesa.sum() / history.impression.sum())
        result[measure] = result[measure].fillna(fallback)
    return result


def predict(d: dict, rows: pd.DataFrame, cutoff: pd.Timestamp, forecaster) -> pd.DataFrame:
    """Output has one row per requested ad/day. No observed outcomes passed to model."""
    rows = rows[META].copy().reset_index(drop=True)
    unique_dates = pd.DatetimeIndex(sorted(rows.data.unique()))
    horizon = len(unique_dates)
    if not unique_dates.equals(pd.date_range(cutoff + pd.Timedelta(days=1), periods=horizon)):
        raise ValueError("Prediction dates must immediately follow cutoff without gaps")
    context, known = make_input(d, cutoff, horizon)
    fc = forecaster.forecast(context, prediction_length=horizon, known_covariates=known)
    predictions = {
        "p10": np.asarray(fc.quantile(0.1)),
        "p50": np.asarray(fc.median),
        "p90": np.asarray(fc.quantile(0.9)),
    }
    records = []
    for p, x in predictions.items():
        if x.shape != (12, 2, horizon) or not np.isfinite(x).all():
            raise ValueError(f"Invalid Timestral output for {p}, shape={x.shape}")
    for i, aid in enumerate(d["adsets"]):
        for j, date in enumerate(unique_dates):
            record = {"adset_id": aid, "data": date}
            for p, x in predictions.items():
                record[f"as_ctr_{p}"] = float(np.clip(x[i, 0, j], 0, 100))
                record[f"as_cpm_{p}"] = float(max(x[i, 1, j], EPS))
            records.append(record)
    out = rows.merge(pd.DataFrame(records), on=["data", "adset_id"], how="left", validate="many_to_one")
    h = d["history"][d["history"].data <= cutoff]
    b = baseline(h, rows, cutoff)
    out["ctr_baseline_pct"] = b.ctr.to_numpy()
    out["cpm_baseline_eur"] = b.cpm.to_numpy()
    recent = h[h.data >= cutoff - pd.Timedelta(days=13)]
    adset_recent, adset_full = rates(recent, "adset_id"), rates(h, "adset_id")
    for target in ("ctr", "cpm"):
        adset_ref = out.adset_id.map(adset_recent[target]).fillna(out.adset_id.map(adset_full[target]))
        ref = np.maximum(adset_ref.to_numpy(dtype=float), EPS)
        for p in ("p10", "p50", "p90"):
            # Fixed safety bounds; not calibrated or optimized on the holdouts.
            factor = np.clip(out[f"as_{target}_{p}"].to_numpy() / ref, 0.25, 4.0)
            base = out["ctr_baseline_pct" if target == "ctr" else "cpm_baseline_eur"].to_numpy()
            value = base * factor
            out[f"{target}_timestral_{p}"] = (np.clip(value, 0, 100) if target == "ctr"
                                             else np.maximum(value, EPS))
    out["ctr_predetto_pct"] = out["ctr_timestral_p50"]
    out["cpm_predetto_eur"] = out["cpm_timestral_p50"]
    return out


def evaluate(pred: pd.DataFrame, actual: pd.DataFrame) -> dict:
    joined = pred.merge(actual[["data", "ad_id", "click", "impression", "spesa"]],
                        on=["data", "ad_id"], validate="one_to_one")
    if len(joined) != len(actual):
        raise ValueError("Incomplete validation join")
    y_ctr = 100.0 * joined.click / joined.impression
    y_cpm = 1000.0 * joined.spesa / joined.impression
    score = {}
    for name, c, m in [
        ("baseline", "ctr_baseline_pct", "cpm_baseline_eur"),
        ("timestral_direct_adset", "as_ctr_p50", "as_cpm_p50"),
        ("timestral_adjusted", "ctr_predetto_pct", "cpm_predetto_eur"),
    ]:
        ec, em = abs(joined[c] - y_ctr), abs(joined[m] - y_cpm)
        score[name] = {
            "mae_ctr_pp": round(float(ec.mean()), 4),
            "mae_cpm_eur": round(float(em.mean()), 4),
            "wmae_ctr_pp": round(float(np.average(ec, weights=joined.impression)), 4),
            "wmae_cpm_eur": round(float(np.average(em, weights=joined.impression)), 4),
        }
    score["q10_q90_coverage_unadjusted_for_calibration"] = {
        "ctr": round(float(y_ctr.between(joined.ctr_timestral_p10, joined.ctr_timestral_p90).mean()), 4),
        "cpm": round(float(y_cpm.between(joined.cpm_timestral_p10, joined.cpm_timestral_p90).mean()), 4),
    }
    return score


def validate_forecast(pred: pd.DataFrame, future: pd.DataFrame) -> None:
    if len(pred) != 699 or pred.duplicated(["data", "ad_id"]).any():
        raise ValueError("Expected exactly 699 unique prediction keys")
    key = lambda x: set(map(tuple, x[["data", "ad_id"]].itertuples(index=False, name=None)))
    if key(pred) != key(future):
        raise ValueError("Prediction keys do not match da_prevedere.csv")
    if not np.isfinite(pred[["ctr_predetto_pct", "cpm_predetto_eur"]].to_numpy()).all():
        raise ValueError("Nonfinite predictions")
    if not pred.ctr_predetto_pct.between(0, 100).all() or not (pred.cpm_predetto_eur > 0).all():
        raise ValueError("Out of range CTR or CPM")


def execute(d: dict, mode: str, output: Path, model=None) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    manifest = {"model": MODEL, "mode": mode, "known_covariates": COVARIATES,
                "caution": "2025 indices are seasonal priors, not observed outcomes for 2026",
                "windows": {}}
    for start, end in FOLDS + [(FINAL_START, FINAL_END)]:
        cutoff = pd.Timestamp(start) - pd.Timedelta(days=1)
        days = (pd.Timestamp(end) - pd.Timestamp(start)).days + 1
        context, known = make_input(d, cutoff, days)
        manifest["windows"][start] = {"cutoff": str(cutoff.date()), "days": days,
                                      "context_shape": list(context.shape),
                                      "known_covariates_shape": list(known.shape),
                                      "missing_context_entries": int(np.isnan(context).sum())}
    (output / "preparation.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    if mode == "prepare":
        return manifest
    if model is None:
        raise ValueError("Model required for inference")
    if mode in ("backtest", "all"):
        results = []
        for start, end in FOLDS:
            cutoff = pd.Timestamp(start) - pd.Timedelta(days=1)
            hold = d["history"][d["history"].data.between(start, end)].copy()
            pred = predict(d, hold, cutoff, model)
            seen = set(d["history"].loc[d["history"].data <= cutoff, "ad_id"])
            new = set(hold.ad_id) - seen
            report = {"start": start, "end": end, "cutoff": str(cutoff.date()),
                      "rows": len(hold), "new_ad_ids": len(new),
                      "metrics": evaluate(pred, hold)}
            if new:
                report["cold_start"] = {
                    "rows": int(hold.ad_id.isin(new).sum()),
                    "metrics": evaluate(pred[pred.ad_id.isin(new)], hold[hold.ad_id.isin(new)]),
                }
            pred.to_csv(output / f"backtest_{start}_{end}.csv", index=False, date_format="%Y-%m-%d")
            results.append(report)
        (output / "backtest_metrics.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
        manifest["backtest"] = results
    if mode in ("forecast", "all"):
        pred = predict(d, d["future"], CUTOFF, model)
        validate_forecast(pred, d["future"])
        pred.to_csv(output / "forecast_2026-11-16_30.csv", index=False, date_format="%Y-%m-%d")
        manifest["forecast"] = {"rows": len(pred),
                                "new_ad_ids": len(set(d["future"].ad_id) - set(d["history"].ad_id))}
    (output / "run_summary.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kit", type=Path, required=True,
                        help="Official kit ZIP, extracted kit root or extracted data directory")
    parser.add_argument("--mode", choices=("prepare", "backtest", "forecast", "all"), default="prepare")
    parser.add_argument("--model", default=MODEL)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--output", type=Path, default=Path(__file__).parent / "outputs")
    args = parser.parse_args()
    d = load_data(args.kit)
    model = None
    if args.mode != "prepare":
        try:
            from timestral import TimestralForecaster
        except ImportError as ex:
            parser.error("Missing Timestral: install Test_Timestral/requirements.txt")
            raise AssertionError from ex
        model = TimestralForecaster.from_pretrained(
            args.model, device=args.device, local_files_only=args.offline
        )
    result = execute(d, args.mode, args.output, model)
    result["model"] = args.model
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
