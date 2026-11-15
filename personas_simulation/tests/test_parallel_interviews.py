import json
import tempfile
import unittest
from pathlib import Path

from personas_simulation.runtime.contracts import DETAIL_FIELDS, read, write
from personas_simulation.runtime.decision_runs import analyze_parallel
from personas_simulation.runtime.interviews import (
    build_summarizer_packets,
    freeze,
    pending_batch_jobs,
    pending_jobs,
    prepare,
    prepare_concise_batches,
    report,
    save_concise_batch,
    save_interview_result,
)
from personas_simulation.runtime.starter import ROOT, build_catalog, build_context, generate_slots
from personas_simulation.runtime.t3_personas import build_jobs, import_response
from personas_simulation.tests.test_decision_runs import FakeDecisionAPI


class ParallelInterviewTests(unittest.TestCase):
    def test_end_to_end_parallel_interviews_and_opinions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = ROOT / "data" / "challenge_kit" / "dati"
            context = build_context(data)
            slots = generate_slots(context, n=6, seed=2026)
            jobs = build_jobs(context, slots, batch_size=6)
            cards = None
            for job in jobs:
                resp = {
                    "personas": [
                        {
                            "persona_id": s["persona_id"],
                            "name": f"Persona {s['persona_id']}",
                            "interests": ["libri", "cucina", "sport"],
                            **{k: f"Dettaglio {s['persona_id']}" for k in DETAIL_FIELDS},
                        }
                        for s in job["slots"]
                    ]
                }
                cards = import_response(
                    job,
                    resp,
                    {
                        "providerInstanceId": "antigravity",
                        "executedModel": "gemini-fixture",
                        "taskId": f"t-{job['job_id']}",
                        "link": "fixture://job",
                    },
                    existing=cards,
                )
            cards_path = root / "persona_cards.json"
            catalog = build_catalog(data)
            catalog_path = root / "creative_catalog.json"
            write(cards_path, cards)
            write(catalog_path, catalog)

            analyses_dir = root / "analyses"
            analyze_parallel(
                catalog,
                cards,
                analyses_dir,
                [("key_1", FakeDecisionAPI()), ("key_2", FakeDecisionAPI())],
                asset_ids=["NDL-S1", "NDL-S2"],
                batch_size=3,
                min_interval_s=0.0,
                tpm_limit=100000,
                rpm_limit=60,
                max_tokens_per_request=40000,
            )

            interviews_dir = root / "interviews"
            ijobs = prepare(catalog, cards, interviews_dir, seed=2026)
            self.assertEqual(len(ijobs), 6)
            self.assertEqual(len(pending_jobs(interviews_dir)), 6)
            for idx, j in enumerate(ijobs):
                pid = j["persona_id"]
                sids = sorted(j["mapping"])
                answers = [
                    {
                        "stimulus_id": sid,
                        "first_impression": "Messaggio chiaro sul testo",
                        "positive": "Offerta esplicita",
                        "negative": "Poca prova sociale",
                        "missing": "Ingredienti e prezzo chiaro",
                        "next_step": "Ci penso prima di cliccare",
                        "change": "Aggiungerei recensioni verificate",
                    }
                    for sid in sids
                ]
                raw_payload = {
                    "answers": answers,
                    "overall": {
                        "most_useful": [sids[0]],
                        "least_useful": [sids[-1]],
                        "summary": "Sintesi cieca coerente con profilo.",
                    },
                }
                raw_input = (
                    f"```json\n{json.dumps(raw_payload)}\n```" if idx % 2 == 0 else raw_payload
                )
                save_interview_result(
                    interviews_dir,
                    pid,
                    raw_input,
                    {
                        "status": "completed",
                        "providerInstanceId": "antigravity",
                        "model": "gemini-4-hydrogen",
                        "taskId": f"task-{pid}",
                        "link": f"t3://task-{pid}",
                    },
                )
            self.assertEqual(pending_jobs(interviews_dir), [])

            frozen = freeze(interviews_dir)
            self.assertEqual(len(frozen), 6)
            report(interviews_dir, cards, read(analyses_dir / "summary.json"), "Note analista separate.", catalog)
            camp_op = read(interviews_dir / "campaign_opinions.json")
            self.assertEqual(camp_op["campaigns"][0]["campaign_id"], "NDL-C1")

            packets = build_summarizer_packets(interviews_dir, cards, read(analyses_dir / "summary.json"), catalog)
            self.assertEqual(len(packets), 1)

    def test_concise_batch_interviews_mixed_with_full(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = ROOT / "data" / "challenge_kit" / "dati"
            context = build_context(data)
            slots = generate_slots(context, n=6, seed=2026)
            jobs = build_jobs(context, slots, batch_size=6)
            cards = None
            for job in jobs:
                resp = {
                    "personas": [
                        {
                            "persona_id": s["persona_id"],
                            "name": f"Persona {s['persona_id']}",
                            "interests": ["libri", "cucina", "sport"],
                            **{k: f"Dettaglio {s['persona_id']}" for k in DETAIL_FIELDS},
                        }
                        for s in job["slots"]
                    ]
                }
                cards = import_response(
                    job,
                    resp,
                    {
                        "providerInstanceId": "antigravity",
                        "executedModel": "gemini-fixture",
                        "taskId": f"t-{job['job_id']}",
                        "link": "fixture://job",
                    },
                    existing=cards,
                )
            cards_path = root / "persona_cards.json"
            catalog = build_catalog(data)
            write(cards_path, cards)

            analyses_dir = root / "analyses"
            analyze_parallel(
                catalog,
                cards,
                analyses_dir,
                [("key_1", FakeDecisionAPI()), ("key_2", FakeDecisionAPI())],
                asset_ids=["NDL-S1", "NDL-S2"],
                batch_size=3,
                min_interval_s=0.0,
                tpm_limit=100000,
                rpm_limit=60,
                max_tokens_per_request=40000,
            )

            interviews_dir = root / "interviews"
            ijobs = prepare(catalog, cards, interviews_dir, seed=2026)
            p0 = ijobs[0]
            sids0 = sorted(p0["mapping"])
            save_interview_result(
                interviews_dir,
                p0["persona_id"],
                {
                    "answers": [
                        {
                            "stimulus_id": sid,
                            "first_impression": "Chiaro",
                            "positive": "Offerta esplicita",
                            "negative": "Poca prova",
                            "missing": "INCI",
                            "next_step": "Valuto",
                            "change": "Più prove",
                        }
                        for sid in sids0
                    ],
                    "overall": {"most_useful": [sids0[0]], "least_useful": [sids0[-1]], "summary": "Intervista completa 1."},
                },
                {"status": "completed", "providerInstanceId": "antigravity", "model": "gemini-4-hydrogen", "taskId": "t-full-1", "link": "t3://full-1"},
            )

            bjobs = prepare_concise_batches(catalog, cards, interviews_dir, seed=2026, batch_size=3, skip_completed=True)
            self.assertEqual(sum(len(b["persona_ids"]) for b in bjobs), 5)
            self.assertEqual(len(pending_batch_jobs(interviews_dir)), len(bjobs))

            for b in bjobs:
                bid = b["batch_id"]
                prompt = (interviews_dir / "batch_jobs" / f"{bid}.prompt.txt").read_text(encoding="utf-8")
                self.assertNotIn("click_intent_signal", prompt)
                bsids = sorted(b["mapping"])
                raw_batch = {
                    "interviews": [
                        {
                            "persona_id": pid,
                            "punti_a_favore": f"Apprezzo la chiarezza su {pid}.",
                            "perche_si_allontana": "Mancano ingredienti dettagliati.",
                            "most_useful": [bsids[0]],
                            "least_useful": [bsids[-1]],
                        }
                        for pid in b["persona_ids"]
                    ]
                }
                save_concise_batch(
                    interviews_dir,
                    bid,
                    raw_batch,
                    {"status": "completed", "providerInstanceId": "antigravity", "model": "gemini-4-hydrogen", "taskId": f"t-{bid}", "link": f"t3://{bid}"},
                )

            self.assertEqual(pending_batch_jobs(interviews_dir), [])
            frozen = freeze(interviews_dir)
            self.assertEqual(len(frozen), 6)
            report(interviews_dir, cards, read(analyses_dir / "summary.json"), "Sintesi concisa separata.", catalog)
            report_txt = (interviews_dir / "REPORT.md").read_text(encoding="utf-8")
            self.assertIn("Apprezzo la chiarezza", report_txt)
            packets = build_summarizer_packets(interviews_dir, cards, read(analyses_dir / "summary.json"), catalog)
            self.assertEqual(len(packets), 1)
