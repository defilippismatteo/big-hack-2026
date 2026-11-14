import json
import tempfile
import unittest
from pathlib import Path

from market_mirror.contracts import DETAIL_FIELDS, read, write
from market_mirror.decision_runs import analyze_parallel
from market_mirror.interviews import QUESTIONS, freeze, prepare, report
from market_mirror.starter import ROOT, build_catalog, build_context, generate_slots
from market_mirror.t3_personas import build_jobs, import_response
from market_mirror.design_dashboard import build_dashboard
from market_mirror.unified_dashboard import build_unified_payload, render_unified_dashboard
from tests.test_decision_runs import FakeDecisionAPI


class UnifiedDashboardTests(unittest.TestCase):
    def test_end_to_end_parallel_interviews_opinions_and_dashboard(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = ROOT / "info fornite dagli organizzatori " / "dati"
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
            self.assertEqual(len(ijobs), 6)  # beauty_skincare only (2 NDL assets)
            from market_mirror.interviews import pending_jobs, save_interview_result
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

            write(
                interviews_dir / "interview_summary.json",
                {
                    "executive_verdict": "Sintesi da istanza separata",
                    "overall": {
                        "headline": "Sintesi globale",
                        "positive_highlights": ["Chiarezza offerta"],
                        "negative_highlights": ["Mancano prove sociali"],
                        "recommendations": ["Testare recensioni"],
                    },
                    "campaigns": {
                        "NDL-C1": {
                            "headline": "Skincare NDL-C1",
                            "positive_highlights": ["Beneficio diretto"],
                            "negative_highlights": ["Urgenza percepita forzata"],
                            "recommendations": ["Aggiungere INCI"],
                        }
                    },
                    "receipt": {
                        "providerInstanceId": "antigravity",
                        "model": "gemini-4-hydrogen",
                        "taskId": "summary-task-1",
                    },
                },
            )

            from market_mirror.interviews import build_summarizer_packets
            packets = build_summarizer_packets(interviews_dir, cards, read(analyses_dir / "summary.json"), catalog)
            self.assertEqual(len(packets), 1)
            v4_dir = ROOT / "artifacts" / "wevion_v4"
            payload = build_unified_payload(
                v4_dir,
                cards_path,
                catalog_path,
                analyses_dir,
                interviews_dir,
                interviews_dir / "REPORT.md",
            )
            self.assertEqual(payload["meta"]["persona_count"], 18)
            self.assertEqual(payload["meta"]["interviews_count"], 6)
            self.assertEqual(len(payload["adsets"]), 12)
            self.assertEqual(len(payload["folds"]), 2)
            html = render_unified_dashboard(payload)
            self.assertIn("Wevion · Dashboard Unificata", html)
            self.assertIn("Chiarezza offerta", html)
            self.assertIn("NDL-C1", html)
            self.assertNotIn("__DATA_JSON__", html)

    def test_design_dashboard_renders_all_project_sections(self):
        html = build_dashboard(ROOT)
        self.assertNotIn("__PAYLOAD__", html)
        for token in [
            'id="tab-btn-overview"',
            'id="tab-btn-forecast"',
            'id="tab-btn-audience"',
            'id="tab-btn-creatives"',
            'id="tab-btn-personas"',
            'id="tab-btn-interviews"',
            'id="tab-btn-validation"',
            'id="tab-btn-evidence"',
            'hidden="until-found"',
            'closedby="any"',
            'role="status"',
            "aria-sort",
            "Orizzonte completo a 106 giorni",
            "Pool 600",
            "previsioni_arricchite",
            "NDL-C1",
            "FGR-C1",
            "CDF-C1",
            "abbigliamento-P001",
            "beforematch",
        ]:
            self.assertIn(token, html)

