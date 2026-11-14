#!/usr/bin/env python3
"""Adapt published modeling exports to the verified baseline keys."""
import argparse
import json
import math
import re
from pathlib import Path

from export_overview import csv_rows, index, json_read, metric


def forecasts(base, selected, seasonal):
    expected = {(day, ad): (ctr, cpm) for day, ad, ctr, cpm in base["forecast"]}
    variants = [index(csv_rows(p), ("data", "ad_id")) for p in (selected, seasonal)]
    if len(expected) != 699 or any(rows.keys() != expected.keys() for rows in variants):
        raise ValueError("L’export deve coprire le 699 chiavi della baseline")
    adsets = {r["id"]: r["campaignId"] for r in base["adsets"]}
    sectors = {r["id"]: r["vertical"] for r in base["campaigns"]}
    result = []
    for (day, ad), (ctr, cpm) in sorted(expected.items()):
        metadata = base["ads"][ad]
        chosen, enriched = [rows[day, ad] for rows in variants]
        for row in (chosen, enriched):
            fields = [row["adset_id"], row["asset_id"], row["leva"], row["formato"]]
            if (fields != [metadata[i] for i in (0, 1, 3, 4)]
                    or row["vertical"] != sectors[adsets[metadata[0]]]
                    or (row["nuovo_annuncio"] == "True") != metadata[5]
                    or not math.isclose(float(row["ctr_baseline"]), ctr, abs_tol=1e-6)
                    or not math.isclose(float(row["cpm_baseline"]), cpm, abs_tol=1e-6)
                    or row["modello_ctr"] != "baseline_14g"
                    or row["modello_cpm"] != "mix_50_50_catboost_timestral28m"):
                raise ValueError(f"Provenienza o mapping incoerenti: {day} {ad}")
        for k in ("ctr_scelto_pct", "cpm_scelto_eur"):
            if chosen[k] != enriched[k]:
                raise ValueError(f"Lo scenario e il forecast divergono sul riferimento: {day} {ad}")
        if not math.isclose(float(chosen["ctr_scelto_pct"]), ctr, abs_tol=1e-6):
            raise ValueError("CTR selezionato diverso dalla baseline")
        result.append([day, ad, metric(chosen["cpm_scelto_eur"], lower=1e-9),
                       metric(enriched["ctr_arricchito_pct"], upper=100),
                       metric(enriched["cpm_arricchito_eur"], lower=1e-9)])
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--overview", type=Path, default=Path("public/data/overview.json"))
    p.add_argument("--selected", type=Path, required=True)
    p.add_argument("--seasonal", type=Path, required=True)
    p.add_argument("--source-ref", required=True)
    p.add_argument("--out", type=Path, default=Path("public/data/pilot-forecast.json"))
    a = p.parse_args()
    if not re.fullmatch(r"[a-f0-9]{40}", a.source_ref):
        p.error("Serve lo SHA completo del ramo pilota")
    base = json_read(a.overview)
    data = {"commit": a.source_ref, "cutoff": base["source"]["cutoff"],
            "rows": forecasts(base, a.selected, a.seasonal)}
    a.out.write_text(json.dumps(data, ensure_ascii=False, allow_nan=False, separators=(",", ":")) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
