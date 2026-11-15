"""Critical boundaries and joins; no model calls or external service required."""
import copy
import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from personas_simulation.runtime.contracts import DETAIL_FIELDS, digest
from personas_simulation.runtime.feed import build_plan, exposure
from personas_simulation.runtime.handoff import join_forecast
from personas_simulation.runtime.personas import make_cards, writer_payload
from personas_simulation.runtime.providers import decide
from personas_simulation.runtime.t3_personas import build_jobs, import_response, task_prompt
from personas_simulation.runtime.signals import aggregate
from personas_simulation.runtime.starter import ROOT, build_catalog, build_context, generate_slots

DATA = ROOT / "data" / "challenge_kit" / "dati"


class RuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context = build_context(DATA)
        cls.slots = generate_slots(cls.context, 24, 2026)
        cls.cards = make_cards(cls.context, cls.slots)
        cls.catalog = build_catalog(DATA)

    def plan(self):
        return build_plan(self.catalog, self.cards, "NDL-S1")

    def test_balanced_repeatable_pool(self):
        self.assertEqual(self.slots, generate_slots(self.context, 24, 2026))
        self.assertEqual(len(self.cards["personas"]), 72)
        for vertical in {p['vertical'] for p in self.cards['personas']}:
            people = [p for p in self.cards['personas'] if p['vertical'] == vertical]
            self.assertEqual(len({p['age_band'] for p in people}), 6)
            self.assertAlmostEqual(sum(p['sampling_weight'] for p in people), 1)

    def test_writer_projects_injected_metrics_and_creatives(self):
        context = copy.deepcopy(self.context)
        for v in context['verticals']:
            v['ctr'] = 'DO_NOT_PASS_OUTCOMES'
            v['audience_hypothesis'] = 'DO_NOT_PASS_AUDIENCE'
        slot = {**self.slots['slots'][0], 'headline': 'DO_NOT_PASS_AD', 'adset_id': 'AS99'}
        payload = json.dumps(writer_payload(context, slot))
        self.assertNotIn('DO_NOT_PASS', payload)
        self.assertNotIn('AS99', payload)

    def test_request_visibility_and_persona_independence(self):
        plan = self.plan()
        self.assertEqual(len(plan['request']['questions']), 4)
        shared = plan['request']['input']
        self.assertNotIn('persona', shared)
        self.assertNotIn('asset_id', shared)
        self.assertNotIn('leva', shared)
        first = plan['request']['questions']['p0000']['instructions']
        self.assertNotIn('sampling_weight', first)
        self.assertNotIn('persona_id', first)
        changed = copy.deepcopy(self.cards)
        changed['personas'][1]['persona_summary'] = 'A_DIFFERENT_PERSON'
        other = build_plan(self.catalog, changed, 'NDL-S1')
        self.assertEqual(plan['request']['questions']['p0000'], other['request']['questions']['p0000'])
        self.assertNotIn('A_DIFFERENT_PERSON', other['request']['questions']['p0000']['instructions'])

    def test_paired_feed_is_stable_across_creatives(self):
        a = self.plan()
        asset = next(c for c in self.catalog['creatives'] if c['vertical'] == a['vertical'] and c['asset_id'] != a['asset_id'])
        b = build_plan(self.catalog, self.cards, asset['asset_id'])
        self.assertEqual(a['assignments'], b['assignments'])
        self.assertEqual(exposure(self.cards['personas'][0], 2026), exposure(self.cards['personas'][0], 2026))

    def test_missing_personas_rejected(self):
        with self.assertRaises(ValueError):
            build_plan(self.catalog, self.cards, 'NDL-S1', n=25)

    def test_fixture_provenance_and_probability_marginals(self):
        p = self.plan()
        result = aggregate(p, decide(p))
        self.assertEqual(result['data_kind'], 'mock_not_model')
        self.assertFalse(result['calibrated_to_ctr'])
        self.assertAlmostEqual(result['click_intent_signal'], .02)
        self.assertAlmostEqual(result['attention_signal'], .30)
        self.assertAlmostEqual(sum(result['reason_distribution'].values()), 1)
        self.assertEqual(result, aggregate(p, decide(p)))

    def test_missing_response_rejected(self):
        p = self.plan()
        raw = decide(p)
        raw['response']['answers'].pop('p0000')
        with self.assertRaises(ValueError):
            aggregate(p, raw)

    def test_invalid_probabilities_rejected(self):
        for value in [float('nan'), -1, 2, .5]:
            with self.subTest(value=value):
                p = self.plan()
                raw = decide(p)
                raw['response']['answers']['p0000']['probabilities']['scroll__irrelevant'] = value
                with self.assertRaises(ValueError):
                    aggregate(p, raw)

    def test_response_cannot_be_reused_for_another_request(self):
        p = self.plan()
        raw = decide(p)
        p['request']['input'] += ' ALTERED'
        with self.assertRaises(ValueError):
            aggregate(p, raw)

    def test_inconsistent_choice_rejected(self):
        p = self.plan()
        raw = decide(p)
        raw['response']['answers']['p0000']['choice'] = 'click__offer'
        with self.assertRaises(ValueError):
            aggregate(p, raw)

    def test_live_rejects_mock_personas_before_request(self):
        api = Mock()
        with self.assertRaises(ValueError):
            decide(self.plan(), api)
        api.decisions.create.assert_not_called()

    def test_writer_task_contains_only_projected_input(self):
        context = copy.deepcopy(self.context)
        context['verticals'][0]['ctr'] = 'FORBIDDEN_OUTCOME'
        slots = copy.deepcopy(self.slots)
        slots['slots'][0]['forecast'] = 'FORBIDDEN_FORECAST'
        job = build_jobs(context, slots)[0]
        prompt = task_prompt(job)
        self.assertNotIn('FORBIDDEN', prompt)
        self.assertEqual(len(job['slots']), 4)
        self.assertTrue(all('age_years' in s for s in job['slots']))

    def test_writer_extra_fields_rejected(self):
        job = build_jobs(self.context, self.slots)[0]
        response = {'personas': [{'persona_id': s['persona_id'], 'name': 'Persona',
                                 'interests': ['A','B','C'], **{k: s['persona_id'] for k in DETAIL_FIELDS}, 'ctr': 2}
                                for s in job['slots']]}
        receipt = {'providerInstanceId': 'antigravity', 'executedModel': 'gemini-4-hydrogen',
                   'link': 'test-only', 'taskId': 'test-only'}
        with self.assertRaises(ValueError):
            import_response(job, response, receipt)

    def test_official_sdk_schema_without_network(self):
        try:
            from google.genai.decisions import CreateDecisionRequest, CreateDecisionResponse
        except ImportError:
            self.skipTest('SDK opzionale non installato')
        p = self.plan()
        CreateDecisionRequest.model_validate(p['request'])
        CreateDecisionResponse.model_validate(decide(p)['response'])

    def csv_file(self, folder, name, records):
        path = Path(folder) / name
        with path.open('w', newline='') as handle:
            w = csv.DictWriter(handle, fieldnames=list(records[0]))
            w.writeheader()
            w.writerows(records)
        return path

    def test_analytics_join_preserves_forecast_and_rejects_mock(self):
        with tempfile.TemporaryDirectory() as folder:
            row = {'data': '2026-11-16', 'ad_id': 'A', 'asset_id': 'NDL-S1', 'adset_id': 'S',
                   'ctr_predetto_pct': '1.25', 'cpm_predetto_eur': '8.30'}
            f = self.csv_file(folder, 'forecast.csv', [row])
            t = self.csv_file(folder, 'target.csv', [{k: row[k] for k in ['data', 'ad_id', 'asset_id', 'adset_id']}])
            joined = join_forecast(f, t, [])
            self.assertEqual(joined['rows'][0]['ctr_predetto_pct'], '1.25')
            self.assertEqual(joined['rows'][0]['simulation_status'], 'not_run')
            with self.assertRaises(ValueError):
                join_forecast(f, t, [aggregate(self.plan(), decide(self.plan()))])
            self.csv_file(folder, 'forecast.csv', [row, row])
            with self.assertRaises(ValueError):
                join_forecast(f, t, [])

    def test_analytics_join_rejects_wrong_asset_and_nonfinite_forecast(self):
        with tempfile.TemporaryDirectory() as folder:
            row = {'data': '2026-11-16', 'ad_id': 'A', 'asset_id': 'NDL-S1', 'adset_id': 'S',
                   'ctr_predetto_pct': '1.25', 'cpm_predetto_eur': '8.30'}
            t = self.csv_file(folder, 'target.csv', [row])
            for replacement in [{'asset_id': 'WRONG'}, {'ctr_predetto_pct': 'nan'}, {'cpm_predetto_eur': '0'}]:
                with self.subTest(replacement=replacement):
                    f = self.csv_file(folder, 'forecast.csv', [{**row, **replacement}])
                    with self.assertRaises(ValueError):
                        join_forecast(f, t, [])


if __name__ == '__main__':
    unittest.main()
