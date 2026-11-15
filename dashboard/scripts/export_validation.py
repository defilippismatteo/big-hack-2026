#!/usr/bin/env python3
"""Check published backtest metrics and project the sector breakdown."""
import argparse
from collections import defaultdict
from datetime import date, timedelta
import json
import math
from pathlib import Path
import re

from export_overview import csv_rows, index, json_read, metric

MODELS = ("baseline", "catboost", "timestral_28m", "mix_50_50")


def summarize(rows):
    weights = [metric(row["impression"], lower=1) for row in rows]
    result = {"righe": len(rows), "impression": int(sum(weights))}
    for target in ("ctr", "cpm"):
        observed = [metric(row[f"{target}_osservato_kit"], upper=100 if target == "ctr" else math.inf) for row in rows]
        for model in MODELS:
            key = f"{target}_{model}"
            errors = [abs(actual - metric(row[key], upper=100 if target == "ctr" else math.inf))
                      for row, actual in zip(rows, observed)]
            result[key] = {"mae": sum(errors) / len(errors),
                           "wmae": sum(error * weight for error, weight in zip(errors, weights)) / sum(weights)}
    return result


def checked(rows, published):
    actual = summarize(rows)
    for key, value in actual.items():
        if isinstance(value, dict):
            if any(not math.isclose(result, published[key][metric], abs_tol=1e-6) for metric, result in value.items()):
                raise ValueError(f"La metrica pubblicata diverge dalle righe: {key}")
        elif value != published[key]:
            raise ValueError(f"La copertura pubblicata diverge dalle righe: {key}")
    return published


def segments(rows):
    partitions = defaultdict(list)
    for row in rows:
        partitions[row["vertical"]].append(row)
    return {key: summarize(items) for key, items in sorted(partitions.items())}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--metrics", type=Path, required=True)
    p.add_argument("--folds", nargs=2, type=Path, required=True)
    p.add_argument("--source-ref", required=True)
    p.add_argument("--out", type=Path, default=Path("public/data/model-validation.json"))
    a = p.parse_args()
    if not re.fullmatch(r"[a-f0-9]{40}", a.source_ref):
        p.error("Serve lo SHA completo del ramo pilota")
    data = json_read(a.metrics)
    folds, pooled = [], []
    if len(data["fold"]) != len(a.folds):
        raise ValueError("Numero di finestre inatteso")
    for fold, path in zip(data["fold"], a.folds):
        rows = csv_rows(path)
        index(rows, ("data", "ad_id"))
        cutoff = (date.fromisoformat(fold["dal"]) - timedelta(days=1)).isoformat()
        if (any(row["cutoff"] != cutoff or row["nuovo_annuncio"] not in ("True", "False")
                or not fold["dal"] <= row["data"] <= fold["al"] or row["data"] > "2026-11-15" for row in rows)
                or min(row["data"] for row in rows) != fold["dal"] or max(row["data"] for row in rows) != fold["al"]):
            raise ValueError("Cutoff o finestra incompatibili")
        pooled.extend(rows)
        for value, key in (("True", "annunci_nuovi"), ("False", "annunci_gia_visti")):
            checked([r for r in rows if r["nuovo_annuncio"] == value], fold[key])
        folds.append({**fold, "cutoff": cutoff, "tutti": checked(rows, fold["tutti"]), "settori": segments(rows)})
    index(pooled, ("data", "ad_id"))
    result = {"commit": a.source_ref, "folds": folds, "combined": checked(pooled, data["aggregato"]),
              "versions": {"CatBoost": data["catboost_versione"], "PyTorch": data["pytorch_versione"]},
              "modelHash": data["timestral_28m_sha256"]}
    a.out.write_text(json.dumps(result, ensure_ascii=False, allow_nan=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
