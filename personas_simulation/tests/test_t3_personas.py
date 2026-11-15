import copy
import unittest
from unittest.mock import patch

from personas_simulation.runtime.contracts import DETAIL_FIELDS
from personas_simulation.runtime.feed import build_plan
from personas_simulation.runtime.starter import ROOT, build_context, build_catalog, generate_slots
from personas_simulation.runtime.t3_personas import apply_cohort_split, build_jobs, import_response
from personas_simulation.runtime.providers import decision_preflight


class T3PersonaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        d = ROOT / "data" / "challenge_kit" / "dati"
        cls.context = build_context(d)
        cls.slots = generate_slots(cls.context)
        cls.catalog = build_catalog(d)
        cls.receipt = {'providerInstanceId': 'antigravity', 'executedModel': 'gemini-4-hydrogen',
                       'link': 'fixture-only', 'taskId': 'fixture-only'}

    def response(self, job):
        return {'personas': [{'persona_id': s['persona_id'], 'name': 'Nome fittizio',
                              'interests': ['montagna', 'libri', 'cucina'],
                              **{k: s['persona_id'] + ' fixture' for k in DETAIL_FIELDS}} for s in job['slots']]}

    def test_ages_and_jobs_are_repeatable(self):
        jobs = build_jobs(self.context, self.slots)
        self.assertEqual(jobs, build_jobs(self.context, self.slots))
        self.assertEqual(len(jobs), 18)
        for j in jobs:
            for s in j['slots']:
                low, high = (65,80) if s['age_band'] == '65+' else map(int, s['age_band'].split('-'))
                self.assertLessEqual(low, s['age_years'])
                self.assertLessEqual(s['age_years'], high)

    def test_import_preserves_slots_and_uses_actual_receipt(self):
        job = build_jobs(self.context, self.slots)[0]
        cards = import_response(job, self.response(job), self.receipt)
        for source, card in zip(job['slots'], cards['personas']):
            for k,v in source.items(): self.assertEqual(v, card[k])
            self.assertEqual(card['provider'], 't3:antigravity')
        plan = build_plan(self.catalog, cards, 'NDL-S1')
        prompt = plan['request']['questions']['p0000']['instructions']
        self.assertIn('age_years', prompt)
        self.assertIn('interests', prompt)

    def test_missing_duplicate_and_unexpected_personas_fail(self):
        job = build_jobs(self.context, self.slots)[0]
        for kind in ['missing', 'duplicate', 'unexpected']:
            r = self.response(job)
            if kind == 'missing': r['personas'].pop()
            if kind == 'duplicate': r['personas'][-1] = r['personas'][0]
            if kind == 'unexpected': r['personas'][0]['persona_id'] = 'wrong'
            with self.subTest(kind=kind), self.assertRaises(ValueError): import_response(job, r, self.receipt)

    def test_changed_slots_and_fake_provider_rejected(self):
        job = build_jobs(self.context, self.slots)[0]
        r = self.response(job)
        edited = copy.deepcopy(job)
        edited['slots'][0]['age_years'] += 1
        with self.assertRaises(ValueError): import_response(edited, r, self.receipt)
        with self.assertRaises(ValueError): import_response(job, r, {**self.receipt,'providerInstanceId':'codex'})

    def test_model_cannot_override_age_or_metrics(self):
        job = build_jobs(self.context, self.slots)[0]
        for field in ['age_years', 'ctr', 'adset_id']:
            r = self.response(job)
            r['personas'][0][field] = 99
            with self.subTest(field=field), self.assertRaises(ValueError): import_response(job, r, self.receipt)

    def test_decision_preflight_never_constructs_api_client(self):
        try:
            from google import genai
        except ImportError:
            self.skipTest('SDK Decisions opzionale assente')
        job = build_jobs(self.context, self.slots)[0]
        cards = import_response(job, self.response(job), self.receipt)
        plan = build_plan(self.catalog, cards, 'NDL-S1')
        with patch.object(genai, 'Client', side_effect=AssertionError('No API client in preflight')):
            report = decision_preflight(plan)
        self.assertEqual(report['api_calls'], 0)
        self.assertFalse(report['live_access_verified'])

    def test_cohort_split_50_50_for_600_personas(self):
        slots = apply_cohort_split(generate_slots(self.context, n=200, seed=2026), biased_share=0.5, seed=2026)
        self.assertEqual(len(slots['slots']), 600)
        jobs = build_jobs(self.context, slots, batch_size=25)
        self.assertEqual(len(jobs), 24)
        for v in ('beauty_skincare', 'pet_ecommerce', 'abbigliamento'):
            vs = [s for s in slots['slots'] if s['vertical'] == v]
            unbiased = [s for s in vs if s['cohort'] == 'unbiased']
            conditioned = [s for s in vs if s['cohort'] == 'category_conditioned']
            self.assertEqual(len(unbiased), 100)
            self.assertEqual(len(conditioned), 100)
            self.assertTrue(all(s['interest_in_category'] in ('high', 'medium') for s in conditioned))
            self.assertTrue(all(s['motivation'] != 'indifferenza' for s in conditioned))
        cards = import_response(jobs[-1], self.response(jobs[-1]), self.receipt)
        self.assertEqual(len(cards['personas']), 25)
        plan = build_plan(self.catalog, cards, 'FGR-S1', n=25)
        self.assertNotIn('cohort', plan['request']['questions']['p0000']['instructions'])
