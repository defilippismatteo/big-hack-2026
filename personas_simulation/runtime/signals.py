"""Validate official ChoiceAnswer fields and export uncalibrated asset signals."""
import math
import random

from .contracts import digest, validate_distribution


def aggregate(plan, raw):
    if digest(plan["request"]) != plan["request_sha256"] or raw["request_sha256"] != plan["request_sha256"]:
        raise ValueError("Risposta associata a una richiesta differente")
    answers = raw["response"].get("answers", {})
    questions = plan["request"]["questions"]
    if set(answers) != set(questions) or set(plan["assignments"]) != set(questions):
        raise ValueError("Risposte mancanti o inattese: nessuna imputazione silenziosa")
    if raw["data_kind"] not in ("simulated_decision", "mock_not_model"):
        raise ValueError("Provenienza risposta non supportata")
    if raw["data_kind"] == "simulated_decision" and raw["model"] != plan["request"]["model"]:
        raise ValueError("Modello risposta diverso dal piano")
    per_person = []
    weighted_actions = dict.fromkeys(["scroll", "glance", "stop", "click"], 0.)
    reasons = {}
    weights = [a["sampling_weight"] for a in plan["assignments"].values()]
    if not weights or any(not math.isfinite(w) or w <= 0 for w in weights):
        raise ValueError("Pesi campionamento non validi")
    total_weight = sum(weights)
    for qid, answer in answers.items():
        probabilities = answer["probabilities"]
        validate_distribution(probabilities, questions[qid]["criteria"])
        best = max(probabilities.values())
        if (answer.get("type") != "choice" or answer.get("choice") not in probabilities or
            not math.isclose(probabilities[answer["choice"]], best, abs_tol=1e-5) or
            not math.isclose(answer.get("confidence", -1), best, abs_tol=1e-5)):
            raise ValueError("Choice/confidence incoerenti con le probabilità")
        assignment = plan["assignments"][qid]
        actions = dict.fromkeys(weighted_actions, 0.)
        for code, value in probabilities.items():
            action, reason = code.split("__", 1)
            actions[action] += value
            reasons[reason] = reasons.get(reason, 0.) + value * assignment["sampling_weight"] / total_weight
        for action, value in actions.items():
            weighted_actions[action] += value * assignment["sampling_weight"] / total_weight
        rng = random.Random(int(digest([plan["seed"], assignment["persona_id"]])[:16], 16))
        ordered = sorted(probabilities)
        sampled = rng.choices(ordered, [probabilities[k] for k in ordered], k=1)[0]
        per_person.append({"persona_id": assignment["persona_id"], "probabilities": probabilities,
                           "actions": actions, "confidence": answer["confidence"],
                           "sampled_outcome_for_demo": sampled, "persona_sha256": assignment["persona_sha256"]})
    return {"schema_version": "1.0", "data_kind": raw["data_kind"], "calibrated_to_ctr": False,
            "asset_id": plan["asset_id"], "vertical": plan["vertical"], "seed": plan["seed"],
            "scenario": plan["scenario"], "provider": raw["provider"], "model": raw["model"],
            "request_sha256": plan["request_sha256"], "run_id": digest([plan, raw])[:16],
            "n_personas": len(per_person), "coverage": 1.0,
            "attention_signal": 1 - weighted_actions["scroll"],
            "click_intent_signal": weighted_actions["click"], "actions": weighted_actions,
            "reason_distribution": reasons, "per_person": per_person,
            "uncertainty": "Closed-set model scores; no calibrated human-population interval"}
