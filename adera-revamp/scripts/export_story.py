"""Export synthetic persona examples and the acquired 600-interview qualitative recap."""
from pathlib import Path
import hashlib
import json

root = Path(__file__).resolve().parents[2]
source = root / "artifacts/personas_t3_600/persona_cards.json"
frozen_path = root / "artifacts/personas_t3_600/interviews/frozen.json"
opinions_path = root / "artifacts/personas_t3_600/interviews/campaign_opinions.json"
summary_path = root / "artifacts/personas_t3_600/interviews/interview_summary.json"

raw = source.read_bytes()
cards = json.loads(raw)["personas"]
frozen_raw = frozen_path.read_bytes()
frozen = json.loads(frozen_raw)
opinions_raw = opinions_path.read_bytes()
opinions = json.loads(opinions_raw)
summary_raw = summary_path.read_bytes()
int_summary = json.loads(summary_raw)

frozen_by_pid = {}
for item in frozen.get("interviews", []):
    pid = item["persona_id"]
    mapping = item.get("mapping", {})
    resp = item.get("response", {})
    overall = resp.get("overall", {})
    punti = resp.get("punti_a_favore")
    freno = resp.get("perche_si_allontana")
    if not punti:
        pos_list = [a["positive"] for a in resp.get("answers", []) if a.get("positive", "").lower() != "nulla"]
        punti = " | ".join(pos_list[:2]) if pos_list else overall.get("summary", "")
    if not freno:
        neg_list = [a["negative"] for a in resp.get("answers", []) if a.get("negative", "").lower() != "nulla"]
        freno = " | ".join(neg_list[:2]) if neg_list else "nulla"
    frozen_by_pid[pid] = {
        "mode": resp.get("mode", "full"),
        "punti_a_favore": punti,
        "perche_si_allontana": freno,
        "most_useful": [mapping.get(s, s) for s in overall.get("most_useful", [])],
        "least_useful": [mapping.get(s, s) for s in overall.get("least_useful", [])],
        "summary": overall.get("summary", ""),
        "receipt_model": item.get("receipt", {}).get("model", "gemini-4-hydrogen"),
    }

examples = {}
used_names = set()
for p in cards:
    vert = p["vertical"]
    if vert not in examples and p.get("name") not in used_names:
        pid = p["persona_id"]
        used_names.add(p.get("name"))
        examples[vert] = {
            **{
                k: p.get(k)
                for k in [
                    "persona_id",
                    "name",
                    "vertical",
                    "age_years",
                    "occupation",
                    "persona_summary",
                    "interests",
                    "concerns",
                    "trust_requirements",
                    "decision_habits",
                    "ad_avoidance",
                    "provider",
                    "model",
                ]
            },
            "interview": frozen_by_pid.get(pid),
        }

camp_by_vertical = {c["vertical"]: c for c in opinions.get("campaigns", [])}
reports = {}
for vert, camp in sorted(camp_by_vertical.items()):
    cid = camp["campaign_id"]
    c_sum = int_summary.get("campaigns", {}).get(cid, {})
    c_assets = camp.get("assets", [])
    top_assets = [
        {
            "asset_id": a["asset_id"],
            "headline": a["headline"],
            "leva": a["leva"],
            "formato": a["formato"],
            "most_useful_count": a["most_useful_count"],
            "least_useful_count": a["least_useful_count"],
            "net_mentions": a["most_useful_count"] - a["least_useful_count"],
            "decision_click_intent": a["decision_click_intent"],
        }
        for a in c_assets[:4]
    ]
    least_assets = [
        {
            "asset_id": a["asset_id"],
            "headline": a["headline"],
            "leva": a["leva"],
            "formato": a["formato"],
            "most_useful_count": a["most_useful_count"],
            "least_useful_count": a["least_useful_count"],
            "net_mentions": a["most_useful_count"] - a["least_useful_count"],
            "decision_click_intent": a["decision_click_intent"],
        }
        for a in c_assets[-3:]
    ]
    unb_v = [v for v in camp.get("persona_summaries", []) if v.get("cohort") == "unbiased"][:3]
    cat_v = [v for v in camp.get("persona_summaries", []) if v.get("cohort") != "unbiased"][:3]
    voices = [
        {
            "persona_id": v["persona_id"],
            "name": v["name"],
            "age_years": v["age_years"],
            "occupation": v["occupation"],
            "cohort": v["cohort"],
            "punti_a_favore": v["punti_a_favore"],
            "perche_si_allontana": v["perche_si_allontana"],
            "most_useful": v["most_useful"],
            "least_useful": v["least_useful"],
        }
        for v in (unb_v + cat_v)
    ]
    recs = c_sum.get("recommendations", [])
    reports[vert] = {
        "campaign_id": cid,
        "campaign_name": camp["campaign_name"],
        "n_interviews": camp["n_interviews"],
        "headline": c_sum.get("headline", f"{cid} · {camp['n_interviews']} interviste cieche"),
        "positive": c_sum.get("positive_highlights", [])[:3],
        "negative": c_sum.get("negative_highlights", [])[:3],
        "next": recs[0] if recs else "",
        "recommendations": recs,
        "by_lever": camp.get("by_lever", []),
        "top_assets": top_assets,
        "least_assets": least_assets,
        "voices": voices,
    }

asset_interviews = {}
for a in opinions.get("assets", []):
    aid = a["asset_id"]
    sample_ops = []
    for op in a.get("opinions", []):
        if op.get("positive") or op.get("negative"):
            sample_ops.append({
                "persona_id": op["persona_id"],
                "name": op["name"],
                "cohort": op["cohort"],
                "positive": op.get("positive", ""),
                "negative": op.get("negative", ""),
            })
        if len(sample_ops) >= 4:
            break
    asset_interviews[aid] = {
        "asset_id": aid,
        "campaign_id": a["campaign_id"],
        "most_useful_count": a["most_useful_count"],
        "least_useful_count": a["least_useful_count"],
        "net_mentions": a["most_useful_count"] - a["least_useful_count"],
        "n_responses": a["n_responses"],
        "sample_opinions": sample_ops,
    }

# Full profiles and verbatim answers live in a separate, on-demand dataset.
profiles = []
for card in cards:
    item = next((i for i in frozen.get("interviews", []) if i["persona_id"] == card["persona_id"]), None)
    interview = frozen_by_pid.get(card["persona_id"])
    answers = []
    if item:
        for answer in item.get("response", {}).get("answers", []):
            answers.append({**answer, "asset_id": item.get("mapping", {}).get(answer["stimulus_id"], answer["stimulus_id"])})
    profiles.append({**card, "interview": interview, "answers": answers})
(root / "adera-revamp/public/data/persona-library.json").write_text(
    json.dumps({"schemaVersion": 1, "kind": "synthetic", "personas": profiles,
                "assets": [{k: a.get(k) for k in ("asset_id", "vertical", "headline", "formato", "leva")}
                           for a in opinions.get("assets", [])]}, ensure_ascii=False) + "\n", encoding="utf-8")

out = {
    "schemaVersion": 1,
    "examplesKind": "synthetic",
    "examplesSource": {
        "path": str(source.relative_to(root)),
        "sha256": hashlib.sha256(raw).hexdigest(),
    },
    "examples": examples,
    "reportsKind": "synthetic_interviews",
    "reportsSource": {
        "frozenPath": str(frozen_path.relative_to(root)),
        "frozenSha256": hashlib.sha256(frozen_raw).hexdigest(),
        "summaryPath": str(summary_path.relative_to(root)),
        "summarySha256": hashlib.sha256(summary_raw).hexdigest(),
        "nInterviews": frozen and len(frozen.get("interviews", [])),
        "nAssets": len(asset_interviews),
    },
    "reportsStatus": "Recap finale acquisito da 600 interviste cieche congelate (200 per campagna) e confrontato con 7.200 valutazioni Decision 1.",
    "overallSummary": {
        "executive_verdict": int_summary.get("executive_verdict", ""),
        **int_summary.get("overall", {}),
    },
    "reports": reports,
    "assetInterviews": asset_interviews,
}
(root / "adera-revamp/public/data/product-story.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(f"Exported product-story.json: {len(frozen.get('interviews', []))} interviews, {len(asset_interviews)} assets")

