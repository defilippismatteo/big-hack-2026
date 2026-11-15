"""Conditional budget scenarios with pacing, ad-level delivery shares and bounds."""
import math
import statistics

from .analytics import groups, history_before


def bounded_allocation(budgets, efficiencies, bound=.2):
    """Integer cents preserve campaign totals exactly; not a causal budget optimizer."""
    if not 0 <= bound <= 1 or any(v < 0 or not math.isfinite(v) for v in budgets.values()):
        raise ValueError("Budget o vincoli non validi")
    if set(budgets) != set(efficiencies) or any(not math.isfinite(v) or v < 0 for v in efficiencies.values()):
        raise ValueError("Efficienze non valide")
    base = {k: round(v * 100) for k, v in budgets.items()}
    lower = {k: math.ceil(v * (1 - bound) - 1e-7) for k, v in base.items()}
    upper = {k: math.floor(v * (1 + bound) + 1e-7) for k, v in base.items()}
    out = dict(lower)
    remaining = sum(base.values()) - sum(out.values())
    for key in sorted(base, key=lambda k: (-efficiencies[k], k)):
        amount = min(remaining, upper[key] - out[key])
        out[key] += amount
        remaining -= amount
    if remaining:
        raise ValueError("Vincoli di allocazione non soddisfacibili")
    return {k: v / 100 for k, v in out.items()}


def decisions(history, forecast, budgets, cutoff="2026-11-15", bound=.2):
    train = history_before(history, cutoff, 14)
    planned = {(r["data"], r["adset_id"]): float(r["budget_giornaliero_eur"]) for r in budgets}
    pacing, spend_by_ad, excluded = {}, {}, {}
    for (adset,), records in groups(train, "adset_id").items():
        ratios, over = [], 0
        for (day,), daily in groups(records, "data").items():
            ratio = sum(float(r["spesa"]) for r in daily) / planned[(day, adset)]
            if ratio > 1:
                over += 1
                continue
            ratios.append(ratio)
        pacing[adset] = statistics.median(ratios) if ratios else 1.
        excluded[adset] = over
        # Preserve the original observations; exclusion applies to pacing estimation only.
        spend_by_ad[adset] = {key[0]: sum(float(r["spesa"]) for r in rows)
                              for key, rows in groups(records, "ad_id").items()}
    result, deliveries = [], []
    for (day, campaign), records in sorted(groups(forecast, "data", "campaign_id").items()):
        sets, efficiencies = {}, {}
        for (adset,), ads in groups(records, "adset_id").items():
            mass = sum(spend_by_ad.get(adset, {}).get(r["ad_id"], 0.) for r in ads)
            # Reserve 10% across all active ads. New creatives get a positive exploratory share.
            shares = {r["ad_id"]: (.1 / len(ads) + .9 * spend_by_ad.get(adset, {}).get(r["ad_id"], 0.) / mass)
                      if mass else 1 / len(ads) for r in ads}
            value = sum(shares[r["ad_id"]] * 10 * float(r["ctr_predetto_pct"]) / float(r["cpm_predetto_eur"]) for r in ads)
            inverse_cpm = sum(shares[r["ad_id"]] / float(r["cpm_predetto_eur"]) for r in ads)
            best = max(ads, key=lambda r: (10 * float(r["ctr_predetto_pct"]) / float(r["cpm_predetto_eur"]), r["ad_id"]))
            sets[adset] = {"ads": ads, "shares": shares, "value": value, "best": best,
                           "ctr": value / inverse_cpm / 10, "cpm": 1 / inverse_cpm}
            efficiencies[adset] = value * pacing.get(adset, 1.)
        base = {adset: planned[(day, adset)] for adset in sets}
        proposed = bounded_allocation(base, efficiencies, bound)
        for adset, info in sorted(sets.items()):
            factor, best = pacing.get(adset, 1.), info["best"]
            result.append({"data": day, "campaign_id": campaign, "vertical": best["vertical"],
                           "adset_id": adset, "budget_base_eur": base[adset],
                           "budget_scenario_eur": proposed[adset], "budget_delta_eur": proposed[adset] - base[adset],
                           "pacing": factor, "pacing_excluded_overspend_days": excluded.get(adset, 0),
                           "effective_spend_base_eur": base[adset] * factor,
                           "effective_spend_scenario_eur": proposed[adset] * factor,
                           "ectr_pct": info["ctr"], "ecpm_eur": info["cpm"],
                           "expected_clicks_base": base[adset] * efficiencies[adset],
                           "expected_clicks_scenario": proposed[adset] * efficiencies[adset],
                           "recommended_ad_id": best["ad_id"], "recommended_asset_id": best["asset_id"],
                           "recommended_lever": best["leva"], "recommended_format": best["formato"],
                           "reason": "Ranking per click attesi/€; budget assegnato entro campagna con pacing storico e quote delivery congelate",
                           "uncertainty": "Alta: scenario condizionale, intervalli non calibrati; domanda, aste e risposta al budget possono cambiare",
                           "scenario_kind": "conditional_what_if_not_causal", "cutoff": cutoff})
            for ad in info["ads"]:
                share = info["shares"][ad["ad_id"]]
                spend = proposed[adset] * factor * share
                deliveries.append({"data": day, "adset_id": adset, "ad_id": ad["ad_id"],
                                   "asset_id": ad["asset_id"], "delivery_share": share,
                                   "effective_spend_scenario_eur": spend,
                                   "expected_impressions_scenario": spend * 1000 / float(ad["cpm_predetto_eur"]),
                                   "expected_clicks_scenario": spend * 10 * float(ad["ctr_predetto_pct"]) / float(ad["cpm_predetto_eur"]),
                                   "allocation_assumption": "90% historical active-ad spend share + 10% equal exploration"})
    return {"schema_version": "1.0", "cutoff": cutoff, "budget_bound": bound,
            "transfer_scope": "within_campaign_same_day", "rows": result, "ad_delivery": deliveries}
