"""V4 invariants: chronology, exact keys, money conservation and honest provenance."""
import copy
import tempfile
import unittest
from pathlib import Path

from market_mirror.analytics import audiences, evidence, groups, load_kit, quality_audit, rates
from market_mirror.delivery import deliver
from market_mirror.forecast import baseline, metrics, validate_forecast
from market_mirror.marketing import bounded_allocation, decisions
from market_mirror.starter import ROOT


class DeliveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_kit(ROOT / "info fornite dagli organizzatori " / "dati")
        cls.pred = baseline(cls.data['history'], cls.data['future'], '2026-11-15')
        cls.decision = decisions(cls.data['history'], cls.pred, cls.data['budgets'])

    def test_weighted_rates(self):
        result = rates([{'click': 100, 'impression': 1000, 'spesa': 10},
                        {'click': 90, 'impression': 9000, 'spesa': 90}])
        self.assertAlmostEqual(result['ctr_pct'], 1.9)
        self.assertAlmostEqual(result['cpm_eur'], 10.)

    def test_exact_699_keys_and_cold_start(self):
        validate_forecast(self.pred, self.data['future'])
        self.assertEqual(len(self.pred), 699)
        self.assertEqual(sum(r['cold_start'] for r in self.pred), 114)
        self.assertEqual(len({r['ad_id'] for r in self.pred if r['cold_start']}), 12)

    def test_invalid_or_duplicate_forecast_rejected(self):
        for changes in ('duplicate', 'mapping', 'nonfinite'):
            rows = copy.deepcopy(self.pred)
            if changes == 'duplicate': rows[-1] = rows[0]
            if changes == 'mapping': rows[0]['asset_id'] = 'WRONG'
            if changes == 'nonfinite': rows[0]['ctr_predetto_pct'] = float('nan')
            with self.subTest(change=changes), self.assertRaises(ValueError):
                validate_forecast(rows, self.data['future'])

    def test_future_labels_cannot_change_baseline_or_audience(self):
        cutoff = '2026-11-01'
        target = [r for r in self.data['history'] if r['data'] > cutoff]
        changed = copy.deepcopy(self.data['history'])
        for row in changed:
            if row['data'] > cutoff:
                row['click'], row['impression'], row['spesa'], row['frequenza'] = '999999', '1', '999999', '999'
        self.assertEqual(baseline(self.data['history'], target, cutoff), baseline(changed, target, cutoff))
        self.assertEqual(evidence(self.data['history'], cutoff), evidence(changed, cutoff))

    def test_twelve_evidence_backed_audiences(self):
        result = audiences(evidence(self.data['history'], '2026-11-15'))
        self.assertEqual(len(result['adsets']), 12)
        for card in result['adsets']:
            self.assertEqual(card['data_kind'], 'hypothesis')
            self.assertTrue(card['alternative'])
            self.assertTrue(card['segnali_osservati']['confronto_stesso_asset_giorno'])
            self.assertEqual(card['confidence'], 'bassa')

    def test_daily_campaign_budget_conserved_with_bounds(self):
        for rows in groups(self.decision['rows'], 'data', 'campaign_id').values():
            self.assertAlmostEqual(sum(r['budget_base_eur'] for r in rows), sum(r['budget_scenario_eur'] for r in rows))
            for row in rows:
                self.assertLessEqual(abs(row['budget_delta_eur']), .2 * row['budget_base_eur'] + 1e-8)
                self.assertLessEqual(row['effective_spend_scenario_eur'], row['budget_scenario_eur'])
        for rows in groups(self.decision['rows'], 'data').values():
            self.assertAlmostEqual(sum(r['budget_scenario_eur'] for r in rows), 1130.)

    def test_ad_delivery_does_not_duplicate_adset_budget(self):
        sets = {(r['data'], r['adset_id']): r for r in self.decision['rows']}
        for key, records in groups(self.decision['ad_delivery'], 'data', 'adset_id').items():
            self.assertAlmostEqual(sum(r['delivery_share'] for r in records), 1.)
            self.assertTrue(all(r['delivery_share'] > 0 for r in records))
            self.assertAlmostEqual(sum(r['effective_spend_scenario_eur'] for r in records), sets[key]['effective_spend_scenario_eur'])
            self.assertAlmostEqual(sum(r['expected_clicks_scenario'] for r in records), sets[key]['expected_clicks_scenario'])

    def test_clicks_scenario_uses_weighted_group_ctr_cpm(self):
        for row in self.decision['rows']:
            estimated = row['effective_spend_scenario_eur'] * 10 * row['ectr_pct'] / row['ecpm_eur']
            self.assertAlmostEqual(estimated, row['expected_clicks_scenario'])

    def test_budget_rounding_and_no_move_when_bound_zero(self):
        budgets = {'A': 80.01, 'B': 110.03, 'C': 90.99}
        out = bounded_allocation(budgets, {'A': 2., 'B': 1., 'C': 3.})
        self.assertEqual(round(sum(out.values()) * 100), round(sum(budgets.values()) * 100))
        self.assertEqual(budgets, bounded_allocation(budgets, dict.fromkeys(budgets, 1.), 0))

    def test_overspending_anomaly_is_flagged(self):
        result = quality_audit(self.data)
        anomaly = next(r for r in result['over_budget_days'] if r['data'] == '2026-10-21' and r['adset_id'] == 'FGR-AS1')
        self.assertAlmostEqual(anomaly['spend_eur'], 397.55)
        self.assertEqual(anomaly['budget_eur'], 100.)

    def test_full_delivery_runs_without_models(self):
        with tempfile.TemporaryDirectory() as folder:
            result = deliver(ROOT / 'info fornite dagli organizzatori ' / 'dati', Path(folder))
            self.assertEqual(result['forecast_rows'], 699)
            self.assertEqual(result['audience_cards'], 12)
            self.assertEqual(result['decision_rows'], 180)
            self.assertFalse(result['persona_simulation_required'])
            for file in ['viewer.html', 'forecasts_2026-11-16_30.csv', 'persona_adset.json', 'decisions.csv', 'validation_metrics.json']:
                self.assertTrue((Path(folder) / file).exists())


if __name__ == '__main__':
    unittest.main()
