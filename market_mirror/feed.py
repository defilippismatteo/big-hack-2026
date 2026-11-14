"""A controlled textual feed: independent single exposures, no social propagation."""
import json
import random

from .contracts import CREATIVE_FIELDS, DETAIL_FIELDS, SLOT_FIELDS, T3_FIELDS, digest, project, validate_card
from .starter import OUTCOMES

ORGANIC = (
    {"author": "Elena (fittizia)", "text": "Passeggiata al parco questa mattina."},
    {"author": "Luca (fittizio)", "text": "Una foto del panorama durante il viaggio."},
    {"author": "Sara (fittizia)", "text": "Oggi provo una nuova ricetta per cena."},
)


def exposure(persona, seed):
    # No asset in the RNG key: paired comparisons retain layout, platform and time.
    rng = random.Random(int(digest([persona["persona_id"], seed])[:16], 16))
    organic = [dict(p) for p in ORGANIC]
    rng.shuffle(organic)
    pos = rng.randrange(1, len(organic))
    organic.insert(pos, {"kind": "sponsored", "content": "creatività nell'input condiviso"})
    habit = persona["social_habit"]
    return {"platform": habit if habit in ("instagram", "facebook") else rng.choice(["instagram", "facebook"]),
            "hour": rng.choice([8, 13, 18, 21]), "exposure_number": 1,
            "items": organic, "ad_position": pos + 1,
            "visual_mode": "organizer_text_description_only"}


def build_plan(catalog, cards, asset_id, n=4, seed=2026, model="gemini-decision-1"):
    if not 1 <= n <= 1000:
        raise ValueError("Occorrono da 1 a 1000 persone")
    asset = next((a for a in catalog["creatives"] if a["asset_id"] == asset_id), None)
    if asset is None:
        raise ValueError(f"Asset sconosciuto: {asset_id}")
    people = [p for p in cards["personas"] if p["vertical"] == asset["vertical"]][:n]
    if len(people) != n or len({p['persona_id'] for p in people}) != n:
        raise ValueError("Persone insufficienti o duplicate per il settore richiesto")
    questions, assignments = {}, {}
    for i, p in enumerate(people):
        validate_card(p)
        qid = f"p{i:04d}"
        feed = exposure(p, seed)
        visible = project(p, tuple(k for k in SLOT_FIELDS if k not in
                                  ("persona_id", "sampling_weight", "seed", "vertical")) + DETAIL_FIELDS + T3_FIELDS)
        instructions = (
            "Valuta solo questa persona fittizia durante la singola esposizione nel feed. "
            "Le descrizioni visual sono testo, non immagini viste. Non inventare prezzi, "
            "landing page o commenti non forniti. Scegli il comportamento finale più plausibile; "
            "click include l'attenzione precedente, stop implica fermarsi senza cliccare, "
            "glance una breve occhiata senza fermarsi, scroll ignorare. "
            + json.dumps({"persona": visible, "feed": feed}, ensure_ascii=False)
        )
        questions[qid] = {"type": "choice", "instructions": instructions, "criteria": dict(OUTCOMES)}
        assignments[qid] = {"persona_id": p["persona_id"], "sampling_weight": p["sampling_weight"],
                            "persona_sha256": digest(p), "persona_data_kind": p["data_kind"],
                            "feed": feed}
    request = {"model": model,
               "input": "Annuncio sponsorizzato Meta. " + json.dumps(project(asset, CREATIVE_FIELDS), ensure_ascii=False),
               "questions": questions}
    return {"schema_version": "1.0", "asset_id": asset_id, "vertical": asset["vertical"],
            "seed": seed, "scenario": "single_exposure_text_feed_v1",
            "request_sha256": digest(request), "assignments": assignments, "request": request}
