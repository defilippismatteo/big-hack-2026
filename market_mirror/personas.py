"""Slot-to-card expansion. The writer sees no ads, history or audience hypotheses."""
import json

from .contracts import DETAIL_FIELDS, SLOT_FIELDS, digest, project, validate_card


def writer_payload(context, slot):
    sector = next(v for v in context["verticals"] if v["vertical"] == slot["vertical"])
    return {
        "sector": project(sector, ("vertical", "market", "industry_description", "campaign_goal")),
        "slot": project(slot, SLOT_FIELDS),
    }


def make_cards(context, slots):
    """Offline plumbing fixtures only. Real cards are imported from T3 responses."""
    cards = []
    for slot in slots["slots"]:
        # A fixture exercises the contracts; it is not an LLM-authored person.
        details = {
            "occupation": "Occupazione non specificata nella fixture",
            "economic_context": f"Priorità dichiarata: {slot['motivation']}",
            "daily_routine": f"Uso social: {slot['social_habit']}",
            "decision_habits": f"Approccio {slot['risk_attitude']}; verifica condizioni prima di acquistare",
            "trust_requirements": "Prezzi e condizioni comprensibili",
            "ad_avoidance": "Non dedotta dai dati; da sviluppare nella scheda live",
            "concerns": "Non desidera acquisti inutili",
            "contradiction": "Apprezza la praticità ma a volte rimanda la scelta",
            "persona_summary": f"Fixture {slot['persona_id']}, interesse {slot['interest_in_category']}",
        }
        card = {**project(slot, SLOT_FIELDS), **details, "schema_version": "1.0",
                "data_kind": "mock_not_model",
                "provider": "offline", "model": "offline-template-v1"}
        validate_card(card)
        cards.append(card)
    if len({p['persona_id'] for p in cards}) != len(cards):
        raise ValueError("Identificativi persona duplicati")
    return {"schema_version": "1.0", "data_kind": "mock_not_model",
            "input_sha256": digest({"context": context, "slots": slots}), "personas": cards}


def writer_prompt(payload):
    return (
        "Scrivi una persona fittizia italiana coerente con lo slot e il settore. "
        "I dati sono ipotesi, non demografia osservata. Evita stereotipi. "
        "Non inventare annunci né risultati di campagne. Includi una contraddizione plausibile. "
        "Restituisci esclusivamente un oggetto JSON con questi campi stringa: "
        + ", ".join(DETAIL_FIELDS) + ".\n" + json.dumps(payload, ensure_ascii=False)
    )
