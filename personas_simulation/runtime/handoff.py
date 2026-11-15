"""Analytics-side join. This module is never called by the persona/decision workers."""
import csv
import math
from pathlib import Path


def rows(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def join_forecast(forecast_path, target_path, signals):
    forecast, target = rows(forecast_path), rows(target_path)
    key = lambda r: (r["data"], r["ad_id"])
    keys = [key(r) for r in forecast]
    if len(keys) != len(set(keys)) or set(keys) != {key(r) for r in target} or len(keys) != len(target):
        raise ValueError("Chiavi forecast diverse da da_prevedere o duplicate")
    target_index = {key(r): r for r in target}
    by_asset = {}
    for signal in signals:
        if signal["data_kind"] != "simulated_decision" or signal["calibrated_to_ctr"] is not False:
            raise ValueError("Il join Analytics accetta solo segnali di modello dichiarati non calibrati")
        if signal["asset_id"] in by_asset:
            raise ValueError("Segnali duplicati per asset: scegli uno scenario/run")
        by_asset[signal["asset_id"]] = signal
    result = []
    for row in forecast:
        ctr, cpm = float(row["ctr_predetto_pct"]), float(row["cpm_predetto_eur"])
        if not math.isfinite(ctr) or not math.isfinite(cpm) or not 0 <= ctr <= 100 or cpm <= 0:
            raise ValueError("CTR/CPM del forecast non validi")
        expected = target_index[key(row)]
        if any(row.get(k) != expected[k] for k in ("asset_id", "adset_id")):
            raise ValueError("Mappatura annuncio/asset/adset incoerente con il kit")
        signal = by_asset.get(expected["asset_id"])
        result.append({**row,
                       "simulation_status": "available" if signal else "not_run",
                       "simulation_attention_signal": signal["attention_signal"] if signal else None,
                       "simulation_click_intent_signal": signal["click_intent_signal"] if signal else None,
                       "simulation_run_id": signal["run_id"] if signal else None})
    return {"schema_version": "1.0", "forecast_source": str(forecast_path),
            "notice": "Simulation columns are explanatory. Forecast values are unchanged.",
            "n_rows": len(result), "rows": result}
