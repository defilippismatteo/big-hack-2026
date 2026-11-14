"""Google Decisions only. Persona writing uses T3/Antigravity, not a Google API."""
import os

from .contracts import digest
from .starter import ROOT


def settings():
    # Optional offline: stdlib only. Live: installs the official SDK and dotenv.
    if (ROOT / ".env").exists():
        try:
            from dotenv import load_dotenv
        except ImportError as exc:
            raise RuntimeError("Installa requirements-market-mirror.txt per caricare .env") from exc
        load_dotenv(ROOT / ".env", override=False)
    return {"persona_model": os.getenv("MM_PERSONA_MODEL", "gemini-4-hydrogen"),
            "decision_model": os.getenv("MM_DECISION_MODEL", "gemini-decision-1"),
            "seed": int(os.getenv("MM_SEED", "2026")),
            "data_dir": os.getenv("WEVION_DATA_DIR", str(ROOT / "info fornite dagli organizzatori " / "dati")),
            "forecast_csv": os.getenv("MM_FORECAST_CSV", "")}


def client():
    settings()
    key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not key:
        raise RuntimeError("Inserisci GEMINI_API_KEY nel file .env alla root")
    try:
        from google import genai
    except ImportError as exc:
        raise RuntimeError("Installa requirements-market-mirror.txt") from exc
    return genai.Client(api_key=key, vertexai=False,
                        http_options={"api_version": "v1beta", "timeout": 60000,
                                      "retry_options": {"attempts": 1}})


def decide(plan, api=None):
    req = plan["request"]
    if digest(req) != plan["request_sha256"]:
        raise ValueError("Hash richiesta non corrispondente")
    if api is None:
        # Deliberately constant: plumbing fixture, not a behavioral model.
        answers = {}
        for qid, question in req["questions"].items():
            keys = list(question["criteria"])
            probs = dict.fromkeys(keys, 0.0)
            probs["scroll__irrelevant"] = 0.70
            probs["glance__visual"] = 0.20
            probs["stop__curiosity"] = 0.08
            probs["click__more_info"] = 0.02
            answers[qid] = {"type": "choice", "choice": "scroll__irrelevant",
                            "confidence": .70, "probabilities": probs}
        response = {"answers": answers}
    else:
        if any(a["persona_data_kind"] != "synthetic" for a in plan["assignments"].values()):
            raise ValueError("Il probe live richiede schede live, non fixture offline")
        if not hasattr(api, "decisions"):
            raise RuntimeError("SDK senza Decisions: serve google-genai>=3.2")
        response = api.decisions.create(**req).model_dump(mode="json", exclude_none=True)
    return {"schema_version": "1.0", "data_kind": "simulated_decision" if api else "mock_not_model",
            "provider": "google" if api else "offline", "model": req["model"] if api else "fixture-v1",
            "request_sha256": plan["request_sha256"], "response": response}


def decision_preflight(plan):
    """Validate a frozen T3 plan, including SDK schema, without a Google client."""
    from .signals import aggregate
    req = plan['request']
    if not 1 <= len(req['questions']) <= 4:
        raise ValueError('Il primo probe usa da 1 a 4 persone')
    if any(a['persona_data_kind'] != 'synthetic' for a in plan['assignments'].values()):
        raise ValueError('Servono schede effettivamente generate prima del preflight Decision')
    for a in plan['assignments'].values():
        feed = a['feed']
        positions = [i for i, item in enumerate(feed['items']) if item.get('kind') == 'sponsored']
        if len(feed['items']) != 4 or positions != [feed['ad_position'] - 1]:
            raise ValueError('Feed incompleto o posizione annuncio incoerente')
    try:
        from google.genai.decisions import CreateDecisionRequest
    except ImportError as exc:
        raise RuntimeError('Installa lo SDK Decisions con requirements-market-mirror.txt') from exc
    CreateDecisionRequest.model_validate(req)
    aggregate(plan, decide(plan))  # Local fixture only; no response saved as a model result.
    return {'schema_version': '1.0', 'request_sha256': plan['request_sha256'],
            'offline_preflight': 'passed', 'n_personas': len(req['questions']),
            'api_calls': 0, 'fixture_used_only_for_parser_check': True,
            'live_access_verified': False,
            'decision_key_present': bool(os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY'))}
