"""Explicit projections at the provider boundary; not a filesystem sandbox."""
import hashlib
import json
import math
from pathlib import Path

SLOT_FIELDS = (
    "persona_id", "vertical", "country", "age_band", "gender_identity", "motivation",
    "social_habit", "risk_attitude", "interest_in_category", "sampling_weight", "seed",
)
DETAIL_FIELDS = (
    "occupation", "economic_context", "daily_routine", "decision_habits",
    "trust_requirements", "ad_avoidance", "concerns", "contradiction", "persona_summary",
)
CREATIVE_FIELDS = (
    "vertical", "formato", "durata_video_s", "headline", "testo_principale",
    "call_to_action", "descrizione_visual",
)
T3_FIELDS = ("age_years", "name", "interests")


def project(obj, fields):
    return {k: obj[k] for k in fields if k in obj}


def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False,
                                     allow_nan=False).encode()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
                    encoding="utf-8")


def validate_card(card):
    required = set(SLOT_FIELDS + DETAIL_FIELDS) | {"schema_version", "data_kind", "provider", "model"}
    if card.get("schema_version") == "2.0":
        required.update(T3_FIELDS)
    if not required.issubset(card):
        raise ValueError(f"Persona incompleta: {sorted(required - set(card))}")
    if set(card) - required:
        raise ValueError("Persona contiene campi non previsti dal contratto")
    for key in DETAIL_FIELDS:
        if not isinstance(card[key], str) or not card[key].strip():
            raise ValueError(f"Dettaglio persona non valido: {key}")
    if card.get("schema_version") == "2.0":
        age = card["age_years"]
        band = card["age_band"]
        low, high = (int(band[:-1]), 80) if band.endswith("+") else map(int, band.split("-"))
        if isinstance(age, bool) or not isinstance(age, int) or not low <= age <= high:
            raise ValueError("Età non coerente con lo slot assegnato")
        if not isinstance(card["name"], str) or not card["name"].strip():
            raise ValueError("Nome persona mancante")
        interests = card["interests"]
        if (not isinstance(interests, list) or not 3 <= len(interests) <= 8 or
            any(not isinstance(i, str) or not i.strip() for i in interests) or
            len({i.strip().casefold() for i in interests}) != len(interests)):
            raise ValueError("Servono 3–8 interessi distinti")
    if not math.isfinite(card["sampling_weight"]) or card["sampling_weight"] <= 0:
        raise ValueError("Peso persona non valido")


def validate_distribution(probabilities, options):
    if not isinstance(probabilities, dict) or set(probabilities) != set(options):
        raise ValueError("Opzioni mancanti o inattese nella risposta")
    if any(isinstance(p, bool) or not isinstance(p, (int, float)) or
           not math.isfinite(p) or not 0 <= p <= 1 for p in probabilities.values()):
        raise ValueError("Probabilità non finite o fuori [0,1]")
    if not math.isclose(sum(probabilities.values()), 1, abs_tol=1e-5):
        raise ValueError("La massa delle probabilità non è 1")
