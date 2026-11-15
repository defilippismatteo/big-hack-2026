import copy
import tempfile
import unittest
from pathlib import Path

from personas_simulation.runtime.contracts import DETAIL_FIELDS, write
from personas_simulation.runtime.interviews import QUESTIONS, freeze, prepare

class InterviewTests(unittest.TestCase):
    def test_decision_scores_and_other_people_cannot_change_individual_prompt(self):
        card = {"persona_id": "test-P001", "vertical": "test", "country": "IT",
                "age_band": "25-34", "gender_identity": "non dichiarato",
                "motivation": "test", "social_habit": "facebook", "risk_attitude": "test",
                "interest_in_category": "low", "sampling_weight": 1, "seed": 2026,
                "schema_version": "1.0", "data_kind": "synthetic",
                "provider": "test-only", "model": "test-only",
                **{k: "test-only" for k in DETAIL_FIELDS}}
        cards = {"personas": [card, {**card, "persona_id": "test-P002"}]}
        catalog = {"creatives": [{"asset_id": "test-A001", "vertical": "test",
                                  "headline": "Test stimulus", "secret_kpi": "SECRET_ASSET_KPI"}]}
        pid = cards["personas"][0]["persona_id"]
        asset = next(a["asset_id"] for a in catalog["creatives"]
                     if a["vertical"] == cards["personas"][0]["vertical"])
        summary = {"ranking": [{"asset_id": asset, "per_person": [{"persona_id": pid}],
                                "click_intent_signal": "SECRET_DECISION_SCORE"}]}
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "interviews"
            write(out.parent / "analyses/summary.json", summary)
            prepare(catalog, cards, out)
            prompt = (out / "jobs" / f"{pid}.prompt.txt").read_text()
            self.assertNotIn("SECRET_DECISION_SCORE", prompt)
            self.assertNotIn("sampling_weight", prompt)
            self.assertNotIn("SECRET_ASSET_KPI", prompt)
            changed = copy.deepcopy(cards)
            changed["personas"][1]["persona_summary"] = "SECRET_OTHER_PERSON"
            summary["ranking"][0]["click_intent_signal"] = 999
            write(out.parent / "analyses/summary.json", summary)
            prepare(catalog, changed, out)
            self.assertEqual(prompt, (out / "jobs" / f"{pid}.prompt.txt").read_text())
            response = {"answers": [{"stimulus_id": "C01", **{k: "nulla" for k in QUESTIONS}}],
                        "overall": {"most_useful": [], "least_useful": [], "summary": "nulla"}}
            write(out / "responses" / f"{pid}.json", response)
            write(out / "responses" / f"{pid}.receipt.json", {
                "status": "completed", "providerInstanceId": "antigravity",
                "taskId": "test-only", "link": "test-only"})
            self.assertEqual(len(freeze(out)), 1)
            response["answers"].append(response["answers"][0])
            write(out / "responses" / f"{pid}.json", response)
            with self.assertRaises(ValueError):
                freeze(out)


if __name__ == "__main__":
    unittest.main()
