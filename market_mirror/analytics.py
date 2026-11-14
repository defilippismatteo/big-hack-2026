"""Wevion v4: historical evidence and auditable, behavioral audience hypotheses."""
import csv
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path


def read_csv(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path, records):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)


def groups(records, *keys):
    result = defaultdict(list)
    for row in records:
        result[tuple(row[k] for k in keys)].append(row)
    return result


def rates(records):
    impressions = sum(float(r["impression"]) for r in records)
    clicks = sum(float(r["click"]) for r in records)
    spend = sum(float(r["spesa"]) for r in records)
    if impressions <= 0:
        raise ValueError("Impression aggregate non positive")
    return {"rows": len(records), "impressions": impressions, "clicks": clicks,
            "spend_eur": spend, "ctr_pct": 100 * clicks / impressions,
            "cpm_eur": 1000 * spend / impressions}


def history_before(history, cutoff, window=None):
    lower = (date.fromisoformat(cutoff) - timedelta(days=window - 1)).isoformat() if window else ""
    return [r for r in history if lower <= r["data"] <= cutoff]


def evidence(history, cutoff):
    train = history_before(history, cutoff)
    recent = history_before(train, cutoff, 14)
    campaign = groups(train, "campaign_id")
    result = []
    for (adset_id,), rows in sorted(groups(train, "adset_id").items()):
        current = [r for r in recent if r["adset_id"] == adset_id]
        overall = rates(rows)
        comparison = []
        # Match both asset and day. Peers belong to the same campaign only.
        peers = groups([r for r in campaign[(rows[0]["campaign_id"],)] if r["adset_id"] != adset_id],
                       "data", "asset_id")
        own_matched, peer_matched = [], []
        for key, own in groups(rows, "data", "asset_id").items():
            if key in peers:
                own_matched.extend(own)
                peer_matched.extend(peers[key])
        if own_matched:
            own_rate, peer_rate = rates(own_matched), rates(peer_matched)
            comparison.append({"own_ctr_pct": own_rate["ctr_pct"], "peer_ctr_pct": peer_rate["ctr_pct"],
                               "delta_ctr_pp": own_rate["ctr_pct"] - peer_rate["ctr_pct"],
                               "matched_own_rows": len(own_matched),
                               "method": "same campaign, asset and day; observational, delivery not controlled"})
        by_lever = [{"lever": key[0], **rates(value)} for key, value in groups(rows, "leva").items()]
        by_format = [{"format": key[0], **rates(value)} for key, value in groups(rows, "formato").items()]
        # Weight reported daily frequency; reach cannot be summed as unique people across days.
        frequency = sum(float(r["frequenza"]) * float(r["impression"]) for r in rows) / overall["impressions"]
        result.append({"adset_id": adset_id, "campaign_id": rows[0]["campaign_id"],
                       "vertical": rows[0]["vertical"], "cutoff": cutoff, "data_kind": "observed",
                       "overall": overall, "recent_14d": rates(current) if current else None,
                       "impression_weighted_reported_frequency": frequency,
                       "by_lever": sorted(by_lever, key=lambda r: -r["ctr_pct"]),
                       "by_format": sorted(by_format, key=lambda r: -r["ctr_pct"]),
                       "matched_asset_day_comparison": comparison})
    return {"schema_version": "1.0", "cutoff": cutoff,
            "source": "organizer simulated campaign history; observed means supplied labels", "adsets": result}


def audiences(evidence_payload):
    result = []
    interpretations = {
        "scarcity": "Persone plausibilmente sensibili alla disponibilità limitata, quando il prodotto è già pertinente",
        "urgency": "Persone plausibilmente disponibili a decidere entro una scadenza chiara",
        "black_friday": "Persone plausibilmente orientate a confrontare promozioni e convenienza stagionale",
    }
    for ev in evidence_payload["adsets"]:
        lever, fmt = ev["by_lever"][0], ev["by_format"][0]
        recent = ev["recent_14d"]
        result.append({"schema_version": "1.0", "adset_id": ev["adset_id"],
                       "campaign_id": ev["campaign_id"], "vertical": ev["vertical"],
                       "cutoff": ev["cutoff"], "data_kind": "hypothesis", "method": "evidence_rules_v1",
                       "segmento_ipotizzato": interpretations[lever["lever"]],
                       "ipotesi": [interpretations[lever["lever"]],
                                   f"Il formato {fmt['format']} merita un test controllato su questo gruppo"],
                       "segnali_osservati": {"ctr_storico_pct": ev["overall"]["ctr_pct"],
                                              "cpm_storico_eur": ev["overall"]["cpm_eur"],
                                              "ctr_recente_pct": recent["ctr_pct"] if recent else None,
                                              "leva_con_ctr_piu_alto": lever,
                                              "formato_con_ctr_piu_alto": fmt,
                                              "confronto_stesso_asset_giorno": ev["matched_asset_day_comparison"]},
                       "alternative": ["Il divario può dipendere da contenuto specifico, calendario, costo d'asta o selezione della delivery, senza riflettere un diverso pubblico",
                                        "CTR alto può indicare curiosità: mancano conversioni per dimostrare acquisti o redditività"],
                       "confidence": "bassa", "demografia": "Non identificabile dai dati forniti",
                       "strategie": f"Testare {lever['lever']} e {fmt['format']} entro budget; scegliere i giorni dal forecast, non dal solo CTR storico",
                       "caution": "Associazione osservazionale; ranking di leve/formati non corretto causalmente per il mix di asset e periodi"})
    return {"schema_version": "1.0", "cutoff": evidence_payload["cutoff"], "data_kind": "hypothesis",
            "provider": "deterministic_evidence_rules", "adsets": result}


def quality_audit(data):
    history, future = data["history"], data["future"]
    historical_ads = {r["ad_id"] for r in history}
    anomalies = []
    budgets = {(r["data"], r["adset_id"]): float(r["budget_giornaliero_eur"]) for r in data["budgets"]}
    for key, records in groups(history, "data", "adset_id").items():
        spend = sum(float(r["spesa"]) for r in records)
        if spend > budgets[key]:
            anomalies.append({"data": key[0], "adset_id": key[1], "spend_eur": spend,
                              "budget_eur": budgets[key], "action": "flagged; source rows preserved"})
    return {"schema_version": "1.0", "history_rows": len(history), "future_rows": len(future),
            "new_ad_ids": sorted({r["ad_id"] for r in future} - historical_ads),
            "cold_start_rows": sum(r["ad_id"] not in historical_ads for r in future),
            "over_budget_days": anomalies, "zero_click_rows": sum(float(r["click"]) == 0 for r in history),
            "future_outcomes_present": sorted(set(future[0]) & {"click", "impression", "spesa", "ctr", "cpm"})}


def load_kit(path):
    path = Path(path)
    return {"history": read_csv(path / "storico_giornaliero.csv"),
            "future": read_csv(path / "da_prevedere.csv"),
            "budgets": read_csv(path / "budget_giornaliero.csv"),
            "market": read_csv(path / "benchmark_mercato_settimanale_2025.csv"),
            "assets": [r for p in sorted((path / "asset_creativi").glob("*.csv")) for r in read_csv(p)]}
