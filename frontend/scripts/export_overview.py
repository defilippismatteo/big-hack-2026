#!/usr/bin/env python3
"""Project Wevion kit + existing Market Mirror exports into the static Overview dataset."""
import argparse
import csv
import json
import math
import re
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path

from audience_data import population, reactions


def csv_rows(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def json_read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def index(rows, keys):
    result = {tuple(row[k] for k in keys): row for row in rows}
    if len(result) != len(rows):
        raise ValueError(f"Chiavi duplicate: {keys}")
    return result


def metric(value, lower=0.0, upper=math.inf):
    result = float(value)
    if not math.isfinite(result) or not lower <= result <= upper:
        raise ValueError(f"Metrica fuori intervallo: {value}")
    return result


def cents(value):
    amount = Decimal(value) * 100
    if not amount.is_finite() or amount < 0 or amount != round(amount):
        raise ValueError(f"Budget non valido: {value}")
    return int(amount)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kit", type=Path, required=True)
    parser.add_argument("--artifacts", type=Path, required=True)
    parser.add_argument("--source-ref", required=True, help="SHA completo del runtime Market Mirror")
    parser.add_argument("--personas", type=Path, help="Export opzionale persona_cards.json di T3")
    parser.add_argument("--simulations", type=Path, help="Summary.json di Market Mirror Decision")
    parser.add_argument("--out", type=Path, default=Path("public/data/overview.json"))
    args = parser.parse_args()
    if not re.fullmatch(r"[a-f0-9]{40}", args.source_ref):
        parser.error("--source-ref deve essere uno SHA Git completo")

    manifest = json_read(args.artifacts / "manifest.json")
    if manifest["workspace_base_commit"] not in (None, args.source_ref):
        raise ValueError("Il commit dichiarato non coincide con il manifest")
    targets = index(csv_rows(args.kit / "da_prevedere.csv"), ("data", "ad_id"))
    forecasts = index(csv_rows(args.artifacts / "forecasts_2026-11-16_30.csv"), ("data", "ad_id"))
    if forecasts.keys() != targets.keys() or len(targets) != manifest["forecast_rows"]:
        raise ValueError("Previsioni e righe attese non coincidono")
    catalog = index([row for p in sorted((args.kit / "asset_creativi").glob("*.csv"))
                     for row in csv_rows(p)], ("asset_id",))
    ads = {}
    forecast = []
    dates = sorted({day for day, _ in targets})
    adset_days = set()

    for (day, ad), row in sorted(forecasts.items()):
        target = targets[day, ad]
        fields = ("adset_id", "asset_id", "vertical", "campaign_id", "leva", "formato")
        if any(row[key] != target[key] for key in fields):
            raise ValueError(f"Metadati previsione incoerenti: {(day, ad)}")
        asset = catalog[row["asset_id"],]
        meta = [row["adset_id"], row["asset_id"], asset["headline"], row["leva"],
                row["formato"], row["cold_start"] == "True"]
        if not meta[2] or ads.setdefault(ad, meta) != meta:
            raise ValueError(f"Annuncio incoerente: {ad}")
        forecast.append([day, ad, metric(row["ctr_predetto_pct"], upper=100),
                         metric(row["cpm_predetto_eur"], lower=1e-9)])
        adset_days.add((day, row["adset_id"]))

    planned = index(csv_rows(args.kit / "budget_giornaliero.csv"), ("data", "adset_id"))
    decision_rows = index(csv_rows(args.artifacts / "decisions.csv"), ("data", "adset_id"))
    if (decision_rows.keys() != adset_days or len(decision_rows) != manifest["decision_rows"]
            or {key for key in planned if key[0] in dates} != adset_days):
        raise ValueError("Copertura dello scenario budget diversa dal forecast o dal kit")

    campaigns = csv_rows(args.kit / "campagne.csv")
    adsets = csv_rows(args.kit / "adset.csv")
    campaign_ids = {row["campaign_id"] for row in campaigns}
    adset_campaign = {r["adset_id"]: r["campaign_id"] for r in adsets}
    if len(adset_campaign) != len(adsets) or len(campaign_ids) != len(campaigns):
        raise ValueError("Identificativi duplicati nel catalogo campagne o ad set")
    budget_bound = metric(manifest["decision_budget_bound"], upper=1)
    scenario = []
    totals = Counter()
    for (day, adset), row in sorted(decision_rows.items()):
        campaign = row["campaign_id"]
        if adset_campaign.get(adset) != campaign or campaign not in campaign_ids:
            raise ValueError(f"Campagna incoerente per {adset}")
        original = cents(row["budget_base_eur"])
        scenario_cents = cents(row["budget_scenario_eur"])
        if (original != cents(planned[day, adset]["budget_giornaliero_eur"])
                or abs(scenario_cents - original) > original * budget_bound + 1e-7
                or row["scenario_kind"] != "conditional_what_if_not_causal"):
            raise ValueError(f"Scenario budget fuori vincoli: {(day, adset)}")
        totals[day, campaign] += scenario_cents - original
        ecpm = metric(row["ecpm_eur"], lower=1e-9)
        spend = metric(row["effective_spend_base_eur"])
        impressions = 1000 * spend / ecpm
        clicks = metric(row["expected_clicks_base"])
        if not math.isclose(clicks, impressions * metric(row["ectr_pct"], upper=100) / 100, abs_tol=1e-6):
            raise ValueError(f"CTR, impression e clic non coerenti: {(day, adset)}")
        scenario.append([day, adset, original, scenario_cents, spend, impressions, clicks,
                         metric(row["expected_clicks_scenario"])])

    if any(totals.values()):
        raise ValueError("Totale scenario non conservato per campagna e giorno")

    seasonal = index([r for r in csv_rows(args.artifacts / "seasonal_scenarios.csv")
                      if r["scenario"] == "central"], ("data", "ad_id"))
    delivery = index(csv_rows(args.artifacts / "ad_delivery.csv"), ("data", "ad_id"))
    if seasonal.keys() != forecasts.keys() or delivery.keys() != forecasts.keys():
        raise ValueError("Scenario stagionale o quote di pubblicazione incompleti")
    ad_weights = {}
    seasonal_totals = defaultdict(lambda: [0.0, 0.0, 0.0])
    shares = defaultdict(float)
    seasonal_method = None
    for (day, ad), row in seasonal.items():
        adset = forecasts[day, ad]["adset_id"]
        allocation = delivery[day, ad]
        if (row["calibrated_interval"] != "False" or allocation["adset_id"] != adset
                or row["vertical"] != forecasts[day, ad]["vertical"]
                or allocation["asset_id"] != forecasts[day, ad]["asset_id"]):
            raise ValueError(f"Scenario stagionale incoerente: {(day, ad)}")
        seasonal_method = seasonal_method or row["method"]
        if row["method"] != seasonal_method:
            raise ValueError("Metodo stagionale non uniforme")
        share = metric(allocation["delivery_share"], upper=1)
        shares[day, adset] += share
        spend = metric(decision_rows[day, adset]["effective_spend_base_eur"]) * share
        ad_weights[day, ad] = spend
        cpm = metric(row["cpm_scenario_eur"], lower=1e-9)
        impressions = 1000 * spend / cpm
        clicks = impressions * metric(row["ctr_scenario_pct"], upper=100) / 100
        totals_for_set = seasonal_totals[day, adset]
        for i, amount in enumerate((spend, impressions, clicks)):
            totals_for_set[i] += amount
    if any(not math.isclose(share, 1, abs_tol=1e-8) for share in shares.values()):
        raise ValueError("Quote di pubblicazione incoerenti")

    observed = defaultdict(lambda: [0, 0, 0])
    for row in csv_rows(args.kit / "storico_giornaliero.csv"):
        if row["data"] > manifest["cutoff"]:
            continue
        if adset_campaign.get(row["adset_id"]) != row["campaign_id"]:
            raise ValueError("Mapping campagna incoerente nello storico")
        aggregate = observed[row["adset_id"]]
        aggregate[0] += int(row["impression"])
        aggregate[1] += int(row["click"])
        aggregate[2] += cents(row["spesa"])

    hypotheses = json_read(args.artifacts / "persona_adset.json")
    if hypotheses["data_kind"] != "hypothesis" or hypotheses["cutoff"] != manifest["cutoff"]:
        raise ValueError("Tipo di dati o cutoff incoerente nelle ipotesi")
    if (len(hypotheses["adsets"]) != manifest["audience_cards"]
            or index(hypotheses["adsets"], ("adset_id",)).keys() != {(adset,) for adset in adset_campaign}):
        raise ValueError("Copertura incoerente delle ipotesi per ad set")

    profiles = population(json_read(args.personas)["personas"]) if args.personas else None
    simulated = reactions(json_read(args.simulations), {key[0] for key in catalog}) if args.simulations else {}

    events = {row["data"]: row["evento"].replace(" (venerdi)", "")
              for row in csv_rows(args.kit / "calendario.csv") if row["data"] in dates and row["evento"]}
    payload = {
        "schemaVersion": 1,
        "source": {"commit": args.source_ref, "kitSha256": manifest["kit_sha256"],
                   "cutoff": manifest["cutoff"], "method": manifest["forecast_source"]["method"],
                   "budgetBound": budget_bound},
        "campaigns": [{"id": r["campaign_id"], "name": r["campaign_name"], "vertical": r["vertical"]} for r in campaigns],
        "adsets": [{"id": r["adset_id"], "campaignId": r["campaign_id"], "name": r["adset_name"]} for r in adsets],
        "observed": dict(observed),
        "dates": dates,
        "events": events,
        "ads": ads,
        "assetDetails": {asset_id: {"body": row["testo_principale"], "cta": row["call_to_action"],
                                    "visual": row["descrizione_visual"]}
                         for (asset_id,), row in sorted(catalog.items())},
        "forecast": forecast,
        "forecastSpend": [ad_weights[row[0], row[1]] for row in forecast],
        "hypotheses": [{"adsetId": r["adset_id"], "description": r["segmento_ipotizzato"],
                        "ctr": r["segnali_osservati"]["ctr_storico_pct"],
                        "confidence": r["confidence"], "evidence": r["segnali_osservati"],
                        "alternatives": r["alternative"], "strategy": r["strategie"]} for r in hypotheses["adsets"]],
        "synthetic": profiles,
        "simulatedDecision": simulated,
        "budgetScenario": scenario,
        "seasonalScenario": {"method": seasonal_method, "rows": [[day, adset, *amounts]
                             for (day, adset), amounts in sorted(seasonal_totals.items())]},
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, ensure_ascii=False, allow_nan=False, separators=(",", ":")) + "\n",
                        encoding="utf-8")
    print(f"{args.out}: {len(forecast)} previsioni · {len(scenario)} righe scenario · {len(hypotheses['adsets'])} ipotesi")


if __name__ == "__main__":
    main()
