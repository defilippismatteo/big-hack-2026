"""Unit tests do not download Timestral weights."""
import unittest

import numpy as np
import pandas as pd

from quantitative_analysis.timestral_pilot.timestral_pilot import rates, baseline, make_input, predict


class DummyOutput:
    def __init__(self, context, horizon):
        self.median = np.repeat(context[:, :, -1:], horizon, axis=-1)
    def quantile(self, level):
        return self.median * (0.8 if level == .1 else 1.2)


class DummyModel:
    def forecast(self, context, prediction_length, known_covariates):
        if known_covariates.shape[-1] != context.shape[-1] + prediction_length:
            raise AssertionError("Invalid covariate horizon")
        return DummyOutput(context, prediction_length)


def fixture():
    dates = pd.date_range("2026-08-17", periods=10)
    hist = []
    future = []
    budget = []
    market = []
    adsets = [f"AS-{i:02d}" for i in range(12)]
    for aid in adsets:
        for idx, day in enumerate(dates):
            hist.append({"data": day, "adset_id": aid, "ad_id": aid + "-AD",
                         "asset_id": aid + "-S", "vertical": "beauty_skincare",
                         "click": 10 + idx, "impression": 1000, "spesa": 8.0})
        for idx, day in enumerate(pd.date_range("2026-08-17", periods=13)):
            budget.append({"data": day, "adset_id": aid, "budget_giornaliero_eur": 100 + idx})
        future.append({"data": pd.Timestamp("2026-08-27"), "adset_id": aid,
                       "ad_id": aid + "-NEW", "asset_id": aid + "-S",
                       "vertical": "beauty_skincare", "campaign_id": "C1",
                       "piattaforma": "meta", "giorno_settimana": "giovedi",
                       "leva": "urgency", "formato": "immagine",
                       "budget_giornaliero_adset": 110})
    for week in ("2025-08-18", "2025-08-25"):
        market.append({"settimana_dal": pd.Timestamp(week), "vertical": "beauty_skincare",
                       "indice_ctr": 115, "indice_cpm": 125})
    return {"history": pd.DataFrame(hist), "future": pd.DataFrame(future),
            "budget": pd.DataFrame(budget), "market": pd.DataFrame(market),
            "adsets": adsets, "vertical": {a: "beauty_skincare" for a in adsets}}


class PilotTests(unittest.TestCase):
    def test_weighted_aggregation(self):
        x = pd.DataFrame([{"adset_id": "A", "click": 100, "impression": 1000, "spesa": 10},
                          {"adset_id": "A", "click": 90, "impression": 9000, "spesa": 90}])
        self.assertAlmostEqual(float(rates(x, "adset_id").loc["A", "ctr"]), 1.9)
        self.assertAlmostEqual(float(rates(x, "adset_id").loc["A", "cpm"]), 10.0)

    def test_cutoff_no_leakage(self):
        d = fixture()
        cutoff = pd.Timestamp("2026-08-21")
        context, known = make_input(d, cutoff, 2)
        d["history"].loc[d["history"].data > cutoff, "click"] = 999
        other, cov = make_input(d, cutoff, 2)
        np.testing.assert_array_equal(context, other)
        np.testing.assert_array_equal(known, cov)
        self.assertEqual(context.shape, (12, 2, 5))
        self.assertEqual(known.shape, (12, 7, 7))

    def test_new_ad_fallback(self):
        d = fixture()
        b = baseline(d["history"], d["future"].reset_index(drop=True), pd.Timestamp("2026-08-26"))
        self.assertEqual(len(b), 12)
        self.assertAlmostEqual(float(b.iloc[0].cpm), 8.0)

    def test_stub_inference(self):
        d = fixture()
        pred = predict(d, d["future"], pd.Timestamp("2026-08-26"), DummyModel())
        self.assertEqual(len(pred), 12)
        self.assertTrue(pred.ctr_predetto_pct.between(0, 100).all())
        self.assertTrue((pred.cpm_predetto_eur > 0).all())
        self.assertTrue(np.isfinite(pred[["ctr_predetto_pct", "cpm_predetto_eur"]]).all().all())
        self.assertTrue((pred.ctr_timestral_p10 <= pred.ctr_timestral_p90).all())


if __name__ == "__main__":
    unittest.main()
