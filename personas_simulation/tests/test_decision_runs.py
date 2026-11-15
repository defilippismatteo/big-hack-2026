import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from personas_simulation.runtime.contracts import DETAIL_FIELDS, write
from personas_simulation.runtime.decision_runs import Ledger, run_asset, refresh_summary
from personas_simulation.runtime.feed import build_plan
from personas_simulation.runtime.providers import decide
from personas_simulation.runtime.starter import ROOT, build_context, build_catalog, generate_slots
from personas_simulation.runtime.t3_personas import build_jobs, import_response


class FakeDecisionAPI:
    def __init__(self, error=None, invalid=False):
        self.calls = []
        self.error, self.invalid = error, invalid
        self.decisions = self

    def create(self, **kwargs):
        self.calls.append(kwargs)
        if self.error: raise self.error
        answers = {}
        for key, q in kwargs['questions'].items():
            first = next(iter(q['criteria']))
            answers[key] = {'type': 'choice', 'choice': first, 'confidence': 1.,
                            'probabilities': {k: float(k == first) for k in q['criteria']}}
        if self.invalid: answers = {}
        return SimpleNamespace(model_dump=lambda **opts: {'answers': answers})


class DecisionRunTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        data = ROOT / "data" / "challenge_kit" / "dati"
        context = build_context(data)
        job = build_jobs(context, generate_slots(context))[0]
        response = {'personas': [{'persona_id': s['persona_id'], 'name': 'Fixture ' + s['persona_id'],
                                 'interests': ['libri','cucina','sport'],
                                 **{k: 'Fixture ' + s['persona_id'] for k in DETAIL_FIELDS}} for s in job['slots']]}
        cls.cards = import_response(job, response, {'providerInstanceId':'antigravity','executedModel':'gemini-fixture',
                                                  'taskId':'fixture-only','link':'fixture-only'})
        cls.catalog = build_catalog(data)

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.out = Path(self.tmp.name)
        self.ledger = Ledger(self.out / 'ledger.sqlite')
        self.plan = build_plan(self.catalog, self.cards, 'NDL-S1')

    def tearDown(self):
        self.ledger.close()
        self.tmp.cleanup()

    def test_completed_analysis_is_not_sent_twice(self):
        api = FakeDecisionAPI()
        run_asset(self.ledger, self.plan, self.out, api)
        second = run_asset(self.ledger, self.plan, self.out, None)
        self.assertEqual(len(api.calls), 1)
        self.assertEqual(second['api_requests'], 0)
        self.assertEqual(second['reused_questions'], 4)

    def test_extended_panel_sends_only_new_people(self):
        api = FakeDecisionAPI()
        small = build_plan(self.catalog, self.cards, 'NDL-S1', n=2)
        run_asset(self.ledger, small, self.out, api)
        result = run_asset(self.ledger, self.plan, self.out, api)
        self.assertEqual(result['new_questions'], 2)
        self.assertEqual(result['reused_questions'], 2)
        self.assertEqual(len(api.calls[1]['questions']), 2)

    def test_persona_reordering_reuses_answers(self):
        api = FakeDecisionAPI()
        run_asset(self.ledger, self.plan, self.out, api)
        reversed_cards = {**self.cards, 'personas': list(reversed(self.cards['personas']))}
        reordered = build_plan(self.catalog, reversed_cards, 'NDL-S1')
        second = run_asset(self.ledger, reordered, self.out, api)
        self.assertEqual(second['reused_questions'], 4)
        self.assertEqual(len(api.calls), 1)

    def test_uncertain_error_never_retries_automatically(self):
        api = FakeDecisionAPI(error=TimeoutError())
        with self.assertRaises(RuntimeError): run_asset(self.ledger, self.plan, self.out, api)
        with self.assertRaises(ValueError): run_asset(self.ledger, self.plan, self.out, api)
        self.assertEqual(len(api.calls), 1)
        self.assertEqual(self.ledger.export()['requests'][0]['status'], 'ambiguous')

    def test_invalid_response_is_saved_and_never_resent(self):
        api = FakeDecisionAPI(invalid=True)
        with self.assertRaises(RuntimeError): run_asset(self.ledger, self.plan, self.out, api)
        state = self.ledger.export()['requests'][0]
        self.assertTrue(Path(state['raw_path']).exists())
        self.assertEqual(state['status'], 'invalid_response')
        with self.assertRaises(ValueError): run_asset(self.ledger, self.plan, self.out, api)
        self.assertEqual(len(api.calls), 1)

    def test_saved_response_recovers_after_interruption(self):
        raw_path = self.out / 'raw.json'
        _, fragment = self.ledger.claim(self.plan, list(self.plan['request']['questions']), raw_path)
        raw = decide(fragment, FakeDecisionAPI())
        write(raw_path, raw)
        recovered = run_asset(self.ledger, self.plan, self.out, None)
        self.assertEqual(recovered['reused_questions'], 4)
        self.assertEqual(recovered['api_requests'], 0)

    def test_no_live_flag_does_not_cache_fixtures(self):
        with self.assertRaises(ValueError): run_asset(self.ledger, self.plan, self.out, None)
        self.assertEqual(self.ledger.export()['requests'], [])

    def test_partial_summary_keeps_completed_results_after_rejection(self):
        api = FakeDecisionAPI()
        run_asset(self.ledger, self.plan, self.out, api)
        other = build_plan(self.catalog, self.cards, 'NDL-S2')
        rejected = Exception('safe fixture')
        rejected.code = 429
        with self.assertRaises(RuntimeError):
            run_asset(self.ledger, other, self.out, FakeDecisionAPI(error=rejected))
        summary = refresh_summary(self.ledger, self.catalog, self.cards, self.out, 'gemini-decision-1', 2026)
        self.assertEqual(summary['assets'], 1)
        self.assertEqual(summary['persona_asset_evaluations'], 4)
        self.assertEqual(next(s for s in summary['asset_states'] if s['asset_id']=='NDL-S2')['status'], 'rejected')

    def test_rejected_retry_is_explicit_and_completed_answers_still_reused(self):
        rejected = Exception('safe fixture'); rejected.code = 429
        with self.assertRaises(RuntimeError):
            run_asset(self.ledger, self.plan, self.out, FakeDecisionAPI(error=rejected))
        api = FakeDecisionAPI()
        with self.assertRaises(ValueError): run_asset(self.ledger, self.plan, self.out, api)
        done = run_asset(self.ledger, self.plan, self.out, api, retry_rejected=True)
        self.assertEqual(done['new_questions'], 4)
        self.assertEqual(len(self.ledger.export()['requests']), 2)
        run_asset(self.ledger, self.plan, self.out, api)
        self.assertEqual(len(api.calls), 1)

    def test_run_asset_chunks_questions_by_batch_size(self):
        api = FakeDecisionAPI()
        res = run_asset(self.ledger, self.plan, self.out, api, batch_size=2)
        self.assertEqual(res['api_requests'], 2)
        self.assertEqual(res['new_questions'], 4)
        self.assertEqual(len(api.calls), 2)
        self.assertEqual([len(c['questions']) for c in api.calls], [2, 2])
        res2 = run_asset(self.ledger, self.plan, self.out, None, batch_size=2)
        self.assertEqual(res2['reused_questions'], 4)
        self.assertEqual(res2['api_requests'], 0)

    def test_pack_question_chunks_and_parallel_two_keys_with_categorization(self):
        from personas_simulation.runtime.decision_runs import (
            analyze_parallel, build_categorization, estimate_request_tokens, pack_question_chunks
        )
        from personas_simulation.runtime.contracts import read
        qids = list(self.plan['request']['questions'])
        est_one = estimate_request_tokens(self.plan['request']['input'], {qids[0]: self.plan['request']['questions'][qids[0]]})
        self.assertGreater(est_one, 800)
        chunks = pack_question_chunks(self.plan, qids, batch_size=10, max_est_tokens=est_one + 50)
        self.assertEqual(len(chunks), 4)
        api1, api2 = FakeDecisionAPI(), FakeDecisionAPI()
        res = analyze_parallel(
            self.catalog, self.cards, self.out, [('key_1', api1), ('key_2', api2)],
            asset_ids=['NDL-S1', 'NDL-S2'], batch_size=2, min_interval_s=0.0,
            tpm_limit=100000, rpm_limit=60, max_tokens_per_request=40000,
        )
        self.assertEqual(len(res['assets']), 2)
        self.assertEqual(res['api_requests'], 4)
        self.assertGreaterEqual(len(api1.calls) + len(api2.calls), 4)
        cat = read(self.out / 'categorization.json')
        self.assertEqual(cat['n_personas_categorized'], 4)
        self.assertEqual(cat['campaigns'][0]['campaign_id'], 'NDL-C1')
        summary = read(self.out / 'summary.json')
        self.assertEqual(build_categorization(summary, self.cards, self.catalog)['n_assets'], 2)

