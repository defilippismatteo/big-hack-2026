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


def validate_response_and_receipt(job, response, receipt):
    if receipt.get("status") != "completed" or receipt.get("providerInstanceId") != "antigravity":
        raise ValueError("Ricevuta incompleta o provider inatteso")
    if not receipt.get("taskId") or not receipt.get("link"):
        raise ValueError("Ricevuta T3 mancante")
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
        most_assets = [r["mapping"][s] for s in r["response"]["overall"]["most_useful"]]
        least_assets = [r["mapping"][s] for s in r["response"]["overall"]["least_useful"]]
        c_bucket["most_useful"].update(most_assets)
        c_bucket["least_useful"].update(least_assets)
        c_bucket["persona_summaries"].append({
            "persona_id": pid,
            "name": card.get("name", pid),
            "cohort": cohort,
            "interest_in_category": card.get("interest_in_category"),
            "most_useful": most_assets,
            "least_useful": least_assets,
            "summary": r["response"]["overall"]["summary"],
        })

        for ans in r["response"]["answers"]:
            aid = r["mapping"][ans["stimulus_id"]]
            cr = creatives.get(aid, {})
            dec = decision_by_asset.get(aid, {})
            ab = by_asset.setdefault(aid, {
                "asset_id": aid,
                "campaign_id": cid,
                "campaign_name": camp["campaign_name"],
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


def report(out, cards, summary, analyst_notes, catalog=None, max_transcript_pairs=120):
    """Join only frozen interviews to saved Decision results, for the analyst."""
    out = Path(out).resolve()
    frozen = read(out / "frozen.json")
    people = {p["persona_id"]: p for p in cards["personas"]}
    positive, negative = Counter(), Counter()
    pairs = []
    decision_by_asset = {a["asset_id"]: a for a in summary["ranking"]}
    for r in frozen["interviews"]:
        for key, counter in (("most_useful", positive), ("least_useful", negative)):
            counter.update(r["mapping"][s] for s in r["response"]["overall"][key])
        for a in r["response"]["answers"]:
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
    n_assets = len({p["asset_id"] for p in pairs})
    n_pairs = len(pairs)
    n_answers = n_pairs * len(QUESTIONS)
    lines = ["# Interviste indipendenti dopo Decision — report", "",
             f"{n_people} persone sintetiche, {n_assets} asset, {n_pairs} valutazioni qualitative e {n_answers} risposte aperte. "
             "Provider T3 Antigravity, modello richiesto/configurato Gemini 4 Hydrogen, thinking low. "
             "Nessuna nuova chiamata Decisions e nessuna API generativa Google.", "",
             "## Risultati e interpretazione (riassunto da istanza dedicata)", "", analyst_notes, "",
             "## Protocollo e visibilità", "",
             "La selezione locale include tutte le coppie completate, indipendentemente da punteggi o esiti. "
             "Le domande sono identiche e neutrali. Ogni colloquio è un nuovo subagente con il solo task inline, "
             "senza storia del coordinatore, e vede una sola scheda più i propri 12 stimoli in ordine "
             "mescolato con seed stabile. Il feed per persona conserva piattaforma, ora e posizione del test. "
             "I codici C01–C12 sono locali alla singola intervista; la mappatura asset_id resta al coordinatore.", "",
             "| Ruolo | Input visibile | Input escluso |", "|---|---|---|",
             "| Persona intervistata | Propria biografia, feed, descrizioni testuali degli annunci, sei domande | Decision, azioni campionate, score, ranking, altre persone/risposte, pesi, KPI, audience inferite, forecast |",
             "| Coordinatore | Repository e registri, payload e ricevute | Nessuna esclusione OS dichiarata |",
             "| Istanza riassunto (dopo congelamento) | Interviste congelate e metriche per campagna/asset | Non influenza le interviste né modifica numeri/CTR |", "",
             "L'intervista è una riesposizione riflessiva a più annunci, non ricordo spontaneo né spiegazione "
             "del comportamento di una sessione. Non sono stati comunicati scroll/click della simulazione. "
             "I risultati sono `synthetic`; Decision resta `simulated_decision`; trend e suggerimenti sono "
             "`hypothesis`. Nessuna fixture `mock_not_model` entra nel confronto.", "",
             "## Preferenze dichiarate per campagna e asset", "",
             "Conteggi non pesati di persone che includono un asset tra massimo tre più/meno utili; "
             "erano ammesse liste vuote. Non sono voti di qualità assoluta, percentuali di clienti o CTR.", ""]
    for camp in campaign_opinions["campaigns"]:
        lines += [f"### {camp['campaign_id']} — {camp['campaign_name']} ({camp['n_interviews']} interviste)", "",
                  "| Asset | Leva | Formato | Più utili | Meno utili | Saldo | Click Intent (Decision) |",
                  "|---|---|---|---:|---:|---:|---:|"]
        for a in camp["assets"]:
            net = a["most_useful_count"] - a["least_useful_count"]
            ci = f"{a['decision_click_intent']:.4f}" if a["decision_click_intent"] is not None else "n/d"
            lines.append(f"| {a['asset_id']} | {a['leva']} | {a['formato']} | {a['most_useful_count']} | {a['least_useful_count']} | {net:+d} | {ci} |")
        lines.append("")
    lines += ["## Sintesi per persona (estratto) e ricevute", ""]
    for r in frozen["interviews"][:60]:
        pid = r["persona_id"]
        lines += [f"### {people[pid].get('name', pid)} — {pid}", "", r["response"]["overall"]["summary"], "",
                  "Più utili: " + (", ".join(r["mapping"][s] for s in r["response"]["overall"]["most_useful"]) or "nessuno") + ".",
                  "", "Meno utili: " + (", ".join(r["mapping"][s] for s in r["response"]["overall"]["least_useful"]) or "nessuno") + ".", "",
                  r["receipt"]["link"], "",
                  f"[Prompt completo]({out}/jobs/{pid}.prompt.txt) · [Risposta JSON]({out}/responses/{pid}.json) · [Ricevuta]({out}/responses/{pid}.receipt.json)", ""]
    if n_people > 60:
        lines += [f"*Nota: mostrati i primi 60 profili di {n_people}; tutte le sintesi e risposte integrali sono in `{out}/frozen.json` e `{out}/campaign_opinions.json`.*", ""]
    lines += ["## Trascrizioni integrali e confronto per coppia", "",
              "Le citazioni seguenti sono parole generate dal modello in ruolo, non testimonianze umane. "
              "Le probabilità provengono esclusivamente dalle risposte Decision già salvate; "
              "il massimo della distribuzione non è un'azione realmente compiuta.", ""]
    for pair in pairs[:max_transcript_pairs]:
        a, d = pair["interview"], pair["decision"]
        lines += [f"### {people[pair['persona_id']].get('name', pair['persona_id'])} · {pair['asset_id']}", "",
                  "Decision — " + "; ".join(f"{k}: {v:.3f}" for k, v in d["actions"].items()) + ".", "",
                  "Distribuzione completa azione/motivo: " + json.dumps(d["probabilities"], ensure_ascii=False) + ".", ""]
        for key, question in QUESTIONS.items():
            lines += [f"**{question}**", "", "> " + a[key].replace("\n", "\n> "), ""]
    if len(pairs) > max_transcript_pairs:
        lines += [f"*Mostrate le prime {max_transcript_pairs} coppie su {len(pairs)} totali; il dataset completo è in `{out}/comparison.json` e `{out}/frozen.json`.*", ""]
    lines += ["## Artefatti e riproducibilità", "",
              f"[Manifest e hash degli input]({out}/manifest.json) · [Interviste congelate]({out}/frozen.json) · "
              f"[Opinioni per campagna]({out}/campaign_opinions.json) · "
              f"[Confronto strutturato]({out}/comparison.json) · [Grafico]({out}/preferences.html)", ""]
    (out / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    assets = sorted({p["asset_id"] for p in pairs})
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
