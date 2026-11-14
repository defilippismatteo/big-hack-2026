"""Blind qualitative re-exposure after Decision; no Decision output in child jobs."""
import json
import random
from collections import Counter
from datetime import datetime, timezone
from html import escape
from pathlib import Path

from .contracts import (CREATIVE_FIELDS, DETAIL_FIELDS, SLOT_FIELDS, T3_FIELDS,
                        digest, project, read, validate_card, write)
from .feed import exposure

QUESTIONS = {
    "first_impression": "Quale impressione ti dà il messaggio e che cosa capisci venga proposto?",
    "positive": "C'è qualcosa che ti interessa o apprezzi? Puoi rispondere nulla; spiega riferendoti al testo fornito.",
    "negative": "C'è qualcosa che ti lascia indifferente, non convince o allontana? Puoi rispondere nulla; spiega riferendoti al testo fornito.",
    "missing": "Quali informazioni ti servirebbero, se presenti, per valutarlo meglio? Non supporre che manchino nella pagina di destinazione, che non vedi.",
    "next_step": "In questa situazione che cosa pensi faresti, e perché? Non devi giustificare un comportamento già avvenuto.",
    "change": "Cambieresti qualcosa per renderlo utile per te, oppure non ne senti il bisogno? Non inventare caratteristiche del prodotto.",
}
RULES = """Intervista simulata: rispondi in prima persona come l'unica persona fittizia sotto.
Usa esclusivamente il JSON inline. Non leggere repository, file, storia o strumenti;
non avviare subagenti, non usare API. Nessuna risposta altrui è disponibile.
Non conosci esiti comportamentali precedenti e non devi inventarli o giustificarli.
I materiali sono descrizioni testuali, non immagini o video visti. Non inventare
prezzi, ingredienti, certificazioni, landing page o prove non fornite. Distingui
ciò che leggi da aspettative personali e da ciò che non puoi determinare.
Questa è una nuova esposizione qualitativa riflessiva a più annunci, ciascuno
valutato separatamente nel feed indicato; non è ricordo spontaneo di una sessione.
Rispondi alle stesse sei domande per OGNI stimolo, con 1-2 frasi per campo.
Non forzare positività, negatività o acquisto; 'nulla' e 'non determinabile' sono validi.
Alla fine indica fino a tre stimoli più utili e meno utili per te (anche nessuno).
Restituisci SOLO JSON: {"answers":[{"stimulus_id":"C01","first_impression":"...",
"positive":"...","negative":"...","missing":"...","next_step":"...","change":"..."}],
"overall":{"most_useful":["C01"],"least_useful":[],"summary":"..."}}.
"""


def prepare(catalog, cards, out, seed=2026):
    """Select the completed panel locally, then project allowlisted stimuli only."""
    out = Path(out)
    # Completion controls eligibility, never the wording or ordering of questions.
    summary = read(out.parent / "analyses/summary.json")
    completed = {a["asset_id"]: {p["persona_id"] for p in a["per_person"]}
                 for a in summary["ranking"]}
    jobs = []
    for p in cards["personas"]:
        validate_card(p)
        if p["data_kind"] != "synthetic":
            raise ValueError("Le interviste richiedono schede synthetic, non fixture offline")
        assets = [a for a in catalog["creatives"] if a["vertical"] == p["vertical"]
                  and p["persona_id"] in completed.get(a["asset_id"], set())]
        if not assets:
            continue
        random.Random(int(digest([p["persona_id"], seed, "interview"])[:16], 16)).shuffle(assets)
        visible = project(p, tuple(k for k in SLOT_FIELDS if k not in
                          ("persona_id", "sampling_weight", "seed", "vertical")) + DETAIL_FIELDS + T3_FIELDS)
        stimuli = [{"stimulus_id": f"C{i+1:02d}", "creative": project(a, CREATIVE_FIELDS),
                    "feed": exposure(p, seed)} for i, a in enumerate(assets)]
        payload = {"persona": visible, "questions": QUESTIONS, "stimuli": stimuli}
        prompt = RULES + "\n" + json.dumps(payload, ensure_ascii=False)
        pid = p["persona_id"]
        job = {"persona_id": pid, "persona_sha256": digest(p),
               "payload": payload, "payload_sha256": digest(payload),
               "prompt_sha256": digest(prompt),
               "mapping": {s["stimulus_id"]: a["asset_id"] for s, a in zip(stimuli, assets)}}
        write(out / "jobs" / f"{pid}.json", job)
        (out / "jobs" / f"{pid}.prompt.txt").write_text(prompt, encoding="utf-8")
        jobs.append({k: v for k, v in job.items() if k != "payload"})
    write(out / "manifest.json", {"schema_version": "1.0", "data_kind": "synthetic",
          "method": "blind_reflective_reexposure", "jobs": jobs,
          "decision_outputs_visible_to_interviewees": False,
          "decision_api_calls": 0, "os_sandbox": False,
          "visibility_enforcement": "inline projection and no-tool instructions; not OS isolation"})
    return jobs


CONCISE_BATCH_RULES = """Intervista sintetica in batch: valuta ciascuna persona fittizia in `personas` separatamente in prima persona.
Usa esclusivamente il JSON inline. Non leggere repository, file, storia o strumenti;
non avviare subagenti, non usare API. Ogni persona risponde in modo indipendente senza
influenzarsi con le altre e riflettendo la propria età, lavoro, bisogni e diffidenze reali.
Nessuna persona conosce esiti comportamentali precedenti.
I materiali sono descrizioni testuali, non immagini o video visti. Non inventare prezzi,
ingredienti, certificazioni, landing page o prove non fornite.
Per OGNI persona indica:
- `punti_a_favore`: 1-2 frasi brevi e personalizzate su cosa apprezza negli annunci (oppure 'nulla'),
- `perche_si_allontana`: 1 frase breve e concreta sul freno principale dal punto di vista del suo profilo (oppure 'nulla'),
- `most_useful` e `least_useful`: fino a 3 codici stimolo (C01-C12) più utili e meno utili (anche liste vuote).
Restituisci SOLO JSON valido:
{"interviews":[{"persona_id":"...","punti_a_favore":"...","perche_si_allontana":"...","most_useful":["C01"],"least_useful":["C05"]}]}.
"""


def _validate_concise_response(job, response):
    punti = response.get("punti_a_favore")
    if not isinstance(punti, str) or not punti.strip():
        raise ValueError("Campo punti_a_favore mancante")
    freno = response.get("perche_si_allontana", "nulla")
    if not isinstance(freno, str) or not freno.strip():
        raise ValueError("Campo perche_si_allontana non valido")
    overall = response.get("overall")
    if not isinstance(overall, dict):
        raise ValueError("Campo overall mancante")
    summary_txt = overall.get("summary")
    if not isinstance(summary_txt, str) or not summary_txt.strip():
        raise ValueError("Sintesi mancante")
    valid_ids = set(job["mapping"])
    for key in ("most_useful", "least_useful"):
        selected = overall.get(key)
        if not isinstance(selected, list) or len(selected) > 3 or len(set(selected)) != len(selected) or not set(selected) <= valid_ids:
            raise ValueError("Preferenza non valida")


def validate_response_and_receipt(job, response, receipt):
    if receipt.get("status") != "completed" or receipt.get("providerInstanceId") != "antigravity":
        raise ValueError("Ricevuta incompleta o provider inatteso")
    if not receipt.get("taskId") or not receipt.get("link"):
        raise ValueError("Ricevuta T3 mancante")
    if response.get("mode") == "concise":
        _validate_concise_response(job, response)
        return
    ids = [a["stimulus_id"] for a in response["answers"]]
    if len(ids) != len(set(ids)) or set(ids) != set(job["mapping"]):
        raise ValueError("Stimoli mancanti, duplicati o inattesi")
    for answer in response["answers"]:
        if set(answer) != {"stimulus_id", *QUESTIONS} or any(
            not isinstance(answer[k], str) or not answer[k].strip() for k in QUESTIONS):
            raise ValueError("Risposta intervista incompleta")
    overall = response["overall"]
    if not isinstance(overall["summary"], str) or not overall["summary"].strip():
        raise ValueError("Sintesi mancante")
    for key in ("most_useful", "least_useful"):
        selected = overall[key]
        if not isinstance(selected, list) or len(selected) > 3 or len(set(selected)) != len(selected) or not set(selected) <= set(ids):
            raise ValueError("Preferenza non valida")


def _extract_json_object(raw):
    if isinstance(raw, dict):
        return raw
    text = str(raw or "").strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end > start:
            return json.loads(text[start : end + 1])
        raise


def save_interview_result(out, pid, raw_response, receipt):
    """Parse, validate, and save a single blind interview response + receipt."""
    out = Path(out)
    job = read(out / "jobs" / f"{pid}.json")
    response = _extract_json_object(raw_response)
    validate_response_and_receipt(job, response, receipt)
    write(out / "responses" / f"{pid}.json", response)
    write(out / "responses" / f"{pid}.receipt.json", receipt)
    return response


def pending_jobs(out):
    """Return list of persona_ids whose interview response/receipt is missing or invalid."""
    out = Path(out)
    manifest = read(out / "manifest.json")
    pending = []
    for entry in manifest["jobs"]:
        pid = entry["persona_id"]
        resp_p = out / "responses" / f"{pid}.json"
        rec_p = out / "responses" / f"{pid}.receipt.json"
        if not resp_p.exists() or not rec_p.exists():
            pending.append(pid)
            continue
        try:
            job = read(out / "jobs" / f"{pid}.json")
            validate_response_and_receipt(job, read(resp_p), read(rec_p))
        except Exception:
            pending.append(pid)
    return pending


def prepare_concise_batches(catalog, cards, out, seed=2026, batch_size=20, skip_completed=True):
    """Prepare blind concise-interview batches (~15-20 personas per call) over completed Decision 1 personas."""
    out = Path(out)
    if batch_size < 1:
        raise ValueError("batch_size deve essere >= 1")
    prepare(catalog, cards, out, seed)
    manifest = read(out / "manifest.json")
    eligible = set(pending_jobs(out)) if skip_completed else {j["persona_id"] for j in manifest["jobs"]}
    summary = read(out.parent / "analyses/summary.json")
    completed = {a["asset_id"]: {p["persona_id"] for p in a["per_person"]}
                 for a in summary["ranking"]}

    by_vertical = {}
    for p in cards["personas"]:
        pid = p["persona_id"]
        if pid not in eligible:
            continue
        assets = [a for a in catalog["creatives"] if a["vertical"] == p["vertical"]
                  and pid in completed.get(a["asset_id"], set())]
        if not assets:
            continue
        by_vertical.setdefault(p["vertical"], []).append((p, assets))

    batch_jobs = []
    batch_dir = out / "batch_jobs"
    batch_dir.mkdir(parents=True, exist_ok=True)
    visible_fields = tuple(k for k in SLOT_FIELDS if k not in
                           ("persona_id", "sampling_weight", "seed", "vertical")) + DETAIL_FIELDS + T3_FIELDS

    for vertical, items in sorted(by_vertical.items()):
        for idx in range(0, len(items), batch_size):
            chunk = items[idx : idx + batch_size]
            batch_id = f"{vertical}-B{idx // batch_size + 1:02d}"
            # All personas in the same vertical share the completed creative pool; shuffle per batch deterministically.
            assets = list(chunk[0][1])
            random.Random(int(digest([batch_id, seed, "concise_batch"])[:16], 16)).shuffle(assets)
            stimuli = [{"stimulus_id": f"C{i+1:02d}", "creative": project(a, CREATIVE_FIELDS)}
                       for i, a in enumerate(assets)]
            mapping = {s["stimulus_id"]: a["asset_id"] for s, a in zip(stimuli, assets)}
            personas_payload = [
                {
                    "persona_id": p["persona_id"],
                    "persona": project(p, visible_fields),
                    "feed": exposure(p, seed),
                }
                for p, _ in chunk
            ]
            payload = {"vertical": vertical, "stimuli": stimuli, "personas": personas_payload}
            prompt = CONCISE_BATCH_RULES + "\n" + json.dumps(payload, ensure_ascii=False)
            job = {
                "batch_id": batch_id,
                "vertical": vertical,
                "persona_ids": [p["persona_id"] for p, _ in chunk],
                "mapping": mapping,
                "payload_sha256": digest(payload),
                "prompt_sha256": digest(prompt),
            }
            write(batch_dir / f"{batch_id}.json", job)
            (batch_dir / f"{batch_id}.prompt.txt").write_text(prompt, encoding="utf-8")
            batch_jobs.append(job)

    write(out / "batch_manifest.json", {
        "schema_version": "1.0",
        "data_kind": "synthetic",
        "method": "blind_concise_batch_reexposure",
        "batch_size": batch_size,
        "batches": batch_jobs,
    })
    return batch_jobs


def pending_batch_jobs(out):
    """Return batch_ids whose personas still have any pending interview."""
    out = Path(out)
    bman = read(out / "batch_manifest.json")
    pending_pids = set(pending_jobs(out))
    return [b["batch_id"] for b in bman["batches"] if any(pid in pending_pids for pid in b["persona_ids"])]


def save_concise_batch(out, batch_id, raw_response, receipt):
    """Validate and save all concise persona interviews from one T3 batch response."""
    out = Path(out)
    bjob = read(out / "batch_jobs" / f"{batch_id}.json")
    parsed = _extract_json_object(raw_response)
    items = parsed.get("interviews")
    if not isinstance(items, list):
        raise ValueError("Campo 'interviews' mancante nella risposta batch")
    expected = bjob["persona_ids"]
    by_pid = {}
    for item in items:
        pid = item.get("persona_id")
        if not pid or pid in by_pid:
            raise ValueError(f"persona_id mancante o duplicato nel batch {batch_id}: {pid}")
        by_pid[pid] = item
    if set(by_pid) != set(expected):
        missing = sorted(set(expected) - set(by_pid))
        extra = sorted(set(by_pid) - set(expected))
        raise ValueError(f"Mismatch persona_id nel batch {batch_id}: mancanti={missing}, extra={extra}")

    saved = []
    batch_to_asset = bjob["mapping"]
    for pid in expected:
        item = by_pid[pid]
        pjob = read(out / "jobs" / f"{pid}.json")
        asset_to_psid = {aid: psid for psid, aid in pjob["mapping"].items()}
        punti = str(item.get("punti_a_favore", "")).strip() or "nulla"
        freno = str(item.get("perche_si_allontana", "nulla")).strip() or "nulla"

        def _remap(raw_list):
            if not isinstance(raw_list, list):
                raise ValueError("most_useful/least_useful deve essere una lista")
            out_sids = []
            for bsid in raw_list[:3]:
                if bsid not in batch_to_asset:
                    raise ValueError(f"Stimolo {bsid} non valido nel batch {batch_id}")
                aid = batch_to_asset[bsid]
                psid = asset_to_psid.get(aid)
                if psid and psid not in out_sids:
                    out_sids.append(psid)
            return out_sids

        resp = {
            "mode": "concise",
            "punti_a_favore": punti,
            "perche_si_allontana": freno,
            "overall": {
                "most_useful": _remap(item.get("most_useful", [])),
                "least_useful": _remap(item.get("least_useful", [])),
                "summary": punti if freno.lower() == "nulla" else f"{punti} Freno: {freno}",
            },
        }
        pid_receipt = {**receipt, "batch_id": batch_id}
        validate_response_and_receipt(pjob, resp, pid_receipt)
        write(out / "responses" / f"{pid}.json", resp)
        write(out / "responses" / f"{pid}.receipt.json", pid_receipt)
        saved.append(pid)
    return saved


def freeze(out):
    """Validate complete responses and receipts before any cross-person synthesis."""
    out = Path(out)
    manifest = read(out / "manifest.json")
    records = []
    for entry in manifest["jobs"]:
        pid = entry["persona_id"]
        job = read(out / "jobs" / f"{pid}.json")
        if digest(job["payload"]) != entry["payload_sha256"]:
            raise ValueError("Input intervista alterato")
        if digest((out / "jobs" / f"{pid}.prompt.txt").read_text()) != entry["prompt_sha256"]:
            raise ValueError("Prompt intervista alterato")
        response = read(out / "responses" / f"{pid}.json")
        receipt = read(out / "responses" / f"{pid}.receipt.json")
        validate_response_and_receipt(job, response, receipt)
        records.append({"persona_id": pid, "data_kind": "synthetic",
                        "payload_sha256": entry["payload_sha256"],
                        "response_sha256": digest(response), "receipt_sha256": digest(receipt),
                        "response": response, "mapping": job["mapping"], "receipt": receipt})
    write(out / "frozen.json", {"data_kind": "synthetic", "calibrated_to_ctr": False,
          "method": manifest["method"], "interviews": records,
          "notice": "Qualitative model role-play, not observed human interviews or explanations of sampled Decision outcomes."})
    return records


CAMPAIGN_BY_VERTICAL = {
    "beauty_skincare": {"campaign_id": "NDL-C1", "campaign_name": "NDL | Vendite | Skincare"},
    "pet_ecommerce": {"campaign_id": "CDF-C1", "campaign_name": "CDF | Vendite | Cani e gatti"},
    "abbigliamento": {"campaign_id": "FGR-C1", "campaign_name": "FGR | Vendite | Autunno-Inverno"},
}


def build_campaign_opinions(out, cards, summary, catalog=None):
    """Aggregate frozen blind interviews by campaign, asset, lever, and cohort without altering raw verbatim."""
    out = Path(out).resolve()
    frozen = read(out / "frozen.json")
    people = {p["persona_id"]: p for p in cards["personas"]}
    creatives = {c["asset_id"]: c for c in (catalog or {}).get("creatives", [])}
    decision_by_asset = {a["asset_id"]: a for a in summary.get("ranking", [])}

    by_campaign = {}
    by_asset = {}

    def _ensure_asset(aid, vertical, cid, camp_name):
        cr = creatives.get(aid, {})
        dec = decision_by_asset.get(aid, {})
        return by_asset.setdefault(aid, {
            "asset_id": aid,
            "campaign_id": cid,
            "campaign_name": camp_name,
            "vertical": vertical,
            "leva": cr.get("leva", ""),
            "formato": cr.get("formato", ""),
            "headline": cr.get("headline", ""),
            "decision_click_intent": dec.get("click_intent_signal"),
            "decision_attention": dec.get("attention_signal"),
            "most_useful_count": 0,
            "least_useful_count": 0,
            "n_responses": 0,
            "opinions": [],
        })

    for r in frozen["interviews"]:
        pid = r["persona_id"]
        card = people.get(pid, {})
        vertical = card.get("vertical", "")
        camp = CAMPAIGN_BY_VERTICAL.get(vertical, {"campaign_id": vertical or "UNKNOWN", "campaign_name": vertical or "Unknown"})
        cid = camp["campaign_id"]
        cohort = card.get("cohort", "unbiased")

        c_bucket = by_campaign.setdefault(cid, {
            "campaign_id": cid,
            "campaign_name": camp["campaign_name"],
            "vertical": vertical,
            "n_interviews": 0,
            "cohorts": Counter(),
            "most_useful": Counter(),
            "least_useful": Counter(),
            "persona_summaries": [],
            "assets": {},
        })
        c_bucket["n_interviews"] += 1
        c_bucket["cohorts"][cohort] += 1
        resp = r["response"]
        most_assets = [r["mapping"][s] for s in resp["overall"]["most_useful"]]
        least_assets = [r["mapping"][s] for s in resp["overall"]["least_useful"]]
        c_bucket["most_useful"].update(most_assets)
        c_bucket["least_useful"].update(least_assets)

        for aid in r["mapping"].values():
            _ensure_asset(aid, vertical, cid, camp["campaign_name"])

        if resp.get("mode") == "concise":
            punti = resp["punti_a_favore"]
            freno = resp.get("perche_si_allontana", "nulla")
            c_bucket["persona_summaries"].append({
                "persona_id": pid,
                "name": card.get("name", pid),
                "age_years": card.get("age_years"),
                "occupation": card.get("occupation", ""),
                "cohort": cohort,
                "interest_in_category": card.get("interest_in_category"),
                "mode": "concise",
                "punti_a_favore": punti,
                "perche_si_allontana": freno,
                "most_useful": most_assets,
                "least_useful": least_assets,
                "summary": resp["overall"]["summary"],
            })
            for aid in most_assets:
                ab = _ensure_asset(aid, vertical, cid, camp["campaign_name"])
                ab["most_useful_count"] += 1
                ab["n_responses"] += 1
                ab["opinions"].append({
                    "persona_id": pid,
                    "name": card.get("name", pid),
                    "cohort": cohort,
                    "positive": punti,
                    "negative": freno,
                    "missing": "",
                    "next_step": "",
                    "change": "",
                })
            for aid in least_assets:
                if aid in most_assets:
                    continue
                ab = _ensure_asset(aid, vertical, cid, camp["campaign_name"])
                ab["least_useful_count"] += 1
                ab["n_responses"] += 1
                ab["opinions"].append({
                    "persona_id": pid,
                    "name": card.get("name", pid),
                    "cohort": cohort,
                    "positive": "",
                    "negative": freno,
                    "missing": "",
                    "next_step": "",
                    "change": "",
                })
        else:
            pos_list = [a["positive"] for a in resp["answers"] if a["positive"].lower() != "nulla"]
            neg_list = [a["negative"] for a in resp["answers"] if a["negative"].lower() != "nulla"]
            c_bucket["persona_summaries"].append({
                "persona_id": pid,
                "name": card.get("name", pid),
                "age_years": card.get("age_years"),
                "occupation": card.get("occupation", ""),
                "cohort": cohort,
                "interest_in_category": card.get("interest_in_category"),
                "mode": "full",
                "punti_a_favore": " | ".join(pos_list[:2]) if pos_list else "nulla",
                "perche_si_allontana": " | ".join(neg_list[:2]) if neg_list else "nulla",
                "most_useful": most_assets,
                "least_useful": least_assets,
                "summary": resp["overall"]["summary"],
            })
            for ans in resp["answers"]:
                aid = r["mapping"][ans["stimulus_id"]]
                ab = _ensure_asset(aid, vertical, cid, camp["campaign_name"])
                ab["n_responses"] += 1
                if aid in most_assets:
                    ab["most_useful_count"] += 1
                if aid in least_assets:
                    ab["least_useful_count"] += 1
                ab["opinions"].append({
                    "persona_id": pid,
                    "name": card.get("name", pid),
                    "cohort": cohort,
                    "positive": ans["positive"],
                    "negative": ans["negative"],
                    "missing": ans["missing"],
                    "next_step": ans["next_step"],
                    "change": ans["change"],
                })

    campaigns_out = []
    for cid, cb in sorted(by_campaign.items()):
        c_assets = sorted(
            [a for a in by_asset.values() if a["campaign_id"] == cid],
            key=lambda x: (-(x["most_useful_count"] - x["least_useful_count"]), -(x["decision_click_intent"] or 0), x["asset_id"]),
        )
        by_lever = {}
        for a in c_assets:
            lv = a["leva"] or "unknown"
            lb = by_lever.setdefault(lv, {"leva": lv, "most_useful": 0, "least_useful": 0, "n_assets": 0, "click_sum": 0.0})
            lb["most_useful"] += a["most_useful_count"]
            lb["least_useful"] += a["least_useful_count"]
            lb["n_assets"] += 1
            lb["click_sum"] += (a["decision_click_intent"] or 0.0)
        lever_rows = [
            {
                "leva": lv,
                "n_assets": v["n_assets"],
                "most_useful_mentions": v["most_useful"],
                "least_useful_mentions": v["least_useful"],
                "net_mentions": v["most_useful"] - v["least_useful"],
                "mean_decision_click_intent": round(v["click_sum"] / max(1, v["n_assets"]), 6),
            }
            for lv, v in sorted(by_lever.items())
        ]
        campaigns_out.append({
            "campaign_id": cid,
            "campaign_name": cb["campaign_name"],
            "vertical": cb["vertical"],
            "n_interviews": cb["n_interviews"],
            "cohorts": dict(cb["cohorts"]),
            "most_useful_mentions": dict(cb["most_useful"]),
            "least_useful_mentions": dict(cb["least_useful"]),
            "by_lever": sorted(lever_rows, key=lambda x: -x["net_mentions"]),
            "assets": [{k: v for k, v in a.items() if k != "opinions"} for a in c_assets],
            "persona_summaries": cb["persona_summaries"],
        })

    result = {
        "schema_version": "1.0",
        "data_kind": "synthetic",
        "calibrated_to_ctr": False,
        "n_interviews": len(frozen["interviews"]),
        "campaigns": campaigns_out,
        "assets": list(by_asset.values()),
    }
    write(out / "campaign_opinions.json", result)
    return result


def report(out, cards, summary, analyst_notes, catalog=None, max_transcript_pairs=0):
    """Join only frozen interviews to saved Decision results, for the analyst (concise executive report)."""
    out = Path(out).resolve()
    frozen = read(out / "frozen.json")
    people = {p["persona_id"]: p for p in cards["personas"]}
    positive, negative = Counter(), Counter()
    pairs = []
    all_assets = set()
    decision_by_asset = {a["asset_id"]: a for a in summary["ranking"]}
    for r in frozen["interviews"]:
        all_assets.update(r["mapping"].values())
        for key, counter in (("most_useful", positive), ("least_useful", negative)):
            counter.update(r["mapping"][s] for s in r["response"]["overall"][key])
        for a in r["response"].get("answers", []):
            asset_id = r["mapping"][a["stimulus_id"]]
            decision = decision_by_asset[asset_id]
            person_decision = next(p for p in decision["per_person"] if p["persona_id"] == r["persona_id"])
            pairs.append({"persona_id": r["persona_id"], "asset_id": asset_id,
                          "interview": a, "decision": person_decision})
    write(out / "comparison.json", {"schema_version": "1.0", "data_kind": "hypothesis",
          "created_utc": datetime.now(timezone.utc).isoformat(),
          "frozen_interviews_sha256": digest(frozen), "decision_summary_sha256": digest(summary),
          "notice": "Comparison of synthetic statements and simulated_decision probabilities; no observed behavior or CTR.",
          "most_useful_mentions": dict(positive), "least_useful_mentions": dict(negative),
          "pairs": pairs})
    campaign_opinions = build_campaign_opinions(out, cards, summary, catalog)
    n_people = len(frozen["interviews"])
    n_assets = len(all_assets)
    lines = ["# Interviste sintetiche post-Decision — sintesi esecutiva", "",
             f"{n_people} persone sintetiche su {n_assets} asset (provider T3 Antigravity, Gemini 4 Hydrogen thinking low; nessuna chiamata Decision in intervista).", "",
             "## Risultati chiave e punti a favore (istanza riassunto separata)", "", analyst_notes, "",
             "## Classifica annunci per campagna (menzioni più/meno utili + Decision 1)", ""]
    for camp in campaign_opinions["campaigns"]:
        lines += [f"### {camp['campaign_id']} — {camp['campaign_name']} ({camp['n_interviews']} interviste)", "",
                  "| Asset | Leva | Formato | Più utili | Meno utili | Saldo | Click Intent (D1) |",
                  "|---|---|---|---:|---:|---:|---:|"]
        for a in camp["assets"]:
            net = a["most_useful_count"] - a["least_useful_count"]
            ci = f"{a['decision_click_intent']:.4f}" if a["decision_click_intent"] is not None else "n/d"
            lines.append(f"| {a['asset_id']} | {a['leva']} | {a['formato']} | {a['most_useful_count']} | {a['least_useful_count']} | {net:+d} | {ci} |")
        lines.append("")
    lines += ["## Estratto voci per campagna (nome, età, punti a favore e freni)", ""]
    for camp in campaign_opinions["campaigns"]:
        lines.append(f"### {camp['campaign_id']}")
        for ps in camp["persona_summaries"][:4]:
            age = f", {ps['age_years']} anni" if ps.get("age_years") else ""
            most_lbl = ", ".join(ps["most_useful"]) or "nessuno"
            freno = ps.get("perche_si_allontana", "nulla")
            lines.append(f"- **{ps['name']}{age}** (`{ps['persona_id']}`, {ps['cohort']}) — Più utili: {most_lbl}. **A favore:** {ps['punti_a_favore']} | **Freno:** {freno}")
        lines.append("")
    lines += [f"*Dataset completo e ricevute T3 in `{out}/frozen.json`, `{out}/campaign_opinions.json` e `{out}/preferences.html`.*", ""]
    (out / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    assets = sorted(all_assets)
    denom = max(1, max([positive[a] for a in assets] + [negative[a] for a in assets] + [1]))
    rows = "".join(f'<div class="row"><span>{escape(aid)}</span><div class="bars">'
                   f'<div class="bar pos" style="width:{positive[aid] * 100 / denom:.1f}%"></div>'
                   f'<div class="bar neg" style="width:{negative[aid] * 100 / denom:.1f}%"></div></div>'
                   f'<span>{positive[aid]} / {negative[aid]}</span></div>' for aid in assets)
    html = '''<!doctype html><html lang="it"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Preferenze del panel sintetico</title><style>
body{margin:0;color:var(--foreground);font-family:var(--font-sans,system-ui);font-size:14px}
p{margin:8px 0}.muted{color:var(--muted-foreground);font-size:12px}.chart{display:flex;flex-direction:column;gap:6px}
.row{display:grid;grid-template-columns:75px 1fr 70px;gap:12px;align-items:center;font-size:12px}.bars{height:23px}.bar{height:9px;margin:2px 0;border-radius:2px;min-width:0}
.pos{background:var(--chart-1,#9277ee)}.neg{background:var(--chart-2,#eeaa55)}
.legend{display:flex;gap:16px}.key{display:inline-block;width:10px;height:10px;margin-right:4px}</style>
<body><p><strong>Annunci citati tra i più e i meno utili</strong></p>
<p class="muted">''' + str(n_people) + ''' persone sintetiche; massimo tre scelte per categoria, anche nessuna. Conteggi non pesati, non CTR.</p>
<div class="legend"><span><i class="key pos"></i>Più utili</span><span><i class="key neg"></i>Meno utili</span></div>
<div class="chart" role="img" aria-label="Preferenze dichiarate del panel: conteggi più utili e meno utili per asset">''' + rows + '''</div>
<p class="muted">Nessuna citazione non equivale a neutralità. Le persone non hanno visto score o risposte Decision. Tutti i materiali sono descrizioni testuali.</p></body></html>'''
    (out / "preferences.html").write_text(html, encoding="utf-8")


def build_summarizer_packets(out, cards, summary, catalog=None):
    """Prepare compact per-campaign qualitative + Decision packets for a separate summarizer instance."""
    out = Path(out).resolve()
    opinions = build_campaign_opinions(out, cards, summary, catalog)
    packets_dir = out / "summarizer_packets"
    packets_dir.mkdir(parents=True, exist_ok=True)
    assets_by_cid = {}
    for a in opinions["assets"]:
        assets_by_cid.setdefault(a["campaign_id"], []).append(a)
    written = []
    for camp in opinions["campaigns"]:
        cid = camp["campaign_id"]
        c_assets = assets_by_cid.get(cid, [])
        compact_assets = []
        for a in sorted(c_assets, key=lambda x: (-(x["most_useful_count"] - x["least_useful_count"]), -(x["decision_click_intent"] or 0))):
            compact_assets.append({
                "asset_id": a["asset_id"],
                "leva": a["leva"],
                "formato": a["formato"],
                "headline": a["headline"],
                "decision_click_intent": a["decision_click_intent"],
                "decision_attention": a["decision_attention"],
                "most_useful_count": a["most_useful_count"],
                "least_useful_count": a["least_useful_count"],
                "net_mentions": a["most_useful_count"] - a["least_useful_count"],
                "opinions": [
                    {
                        "pid": o["persona_id"],
                        "cohort": o["cohort"],
                        "pos": o["positive"],
                        "neg": o["negative"],
                        "missing": o["missing"],
                        "change": o["change"],
                    }
                    for o in a["opinions"]
                ],
            })
        packet = {
            "campaign_id": cid,
            "campaign_name": camp["campaign_name"],
            "vertical": camp["vertical"],
            "n_interviews": camp["n_interviews"],
            "cohorts": camp["cohorts"],
            "by_lever": camp["by_lever"],
            "persona_summaries": camp["persona_summaries"],
            "assets": compact_assets,
        }
        dest = packets_dir / f"{cid}.json"
        write(dest, packet)
        written.append(str(dest))
    return written
