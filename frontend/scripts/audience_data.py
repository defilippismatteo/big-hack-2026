"""Prepare aggregate audience inputs from existing Market Mirror artifacts."""
from collections import Counter
import math

ACTIONS = ("scroll", "glance", "stop", "click")


def population(cards):
    ids = set()
    groups = Counter()
    for card in cards:
        person_id = card["persona_id"]
        if card["data_kind"] != "synthetic" or not person_id or person_id in ids:
            raise ValueError("Profilo sintetico non valido o duplicato")
        ids.add(person_id)
        groups[card["vertical"], card.get("age_band") or "Non specificata",
               card.get("gender_identity") or "Non specificato"] += 1
    return {
        "count": len(cards),
        "age": dict(Counter(card.get("age_band") or "Non specificata" for card in cards)),
        "gender": dict(Counter(card.get("gender_identity") or "Non specificato" for card in cards)),
        "groups": [[*group, count] for group, count in sorted(groups.items())],
    }


def reactions(summary, asset_ids):
    if summary["data_kind"] != "simulated_decision" or summary["calibrated_to_ctr"] is not False:
        raise ValueError("Provenienza delle reazioni non verificabile")
    result = {}
    for row in summary["ranking"]:
        asset_id = row["asset_id"]
        actions = row["actions"]
        if (asset_id not in asset_ids or asset_id in result or row["n_personas"] <= 0
                or row.get("coverage") != 1 or set(actions) != set(ACTIONS)
                or any(not math.isfinite(v) or not 0 <= v <= 1 for v in actions.values())
                or not math.isclose(sum(actions.values()), 1, abs_tol=1e-5)):
            raise ValueError(f"Reazione incompatibile: {asset_id}")
        reasons = row["reason_distribution"]
        if (any(not math.isfinite(v) or not 0 <= v <= 1 for v in reasons.values())
                or not math.isclose(sum(reasons.values()), 1, abs_tol=1e-5)):
            raise ValueError(f"Distribuzione dei motivi incompatibile: {asset_id}")
        result[asset_id] = {key: row[key] for key in ("vertical", "n_personas", "actions", "reason_distribution", "model", "run_id")}
    return result
