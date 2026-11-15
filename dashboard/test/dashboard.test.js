import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import { budgetAllocation, budgetTotals, transferLimit } from '../src/pages/budgetModel.js';
import { dailyForecast, forecastSelection } from '../src/pages/forecastModel.js';
import { creativeCatalog, creativesForDay, sortCreatives } from '../src/creatives/model.js';
import { overviewModel } from '../src/overview/model.js';

const read = (name) => JSON.parse(readFileSync(new URL('../public/data/' + name + '.json', import.meta.url)));
const data = read('overview');

test('all series preserve 699 forecast keys; scoped aggregates respect coverage', () => {
  const pilot = read('pilot-forecast');
  const baseline = forecastSelection(data, pilot, { variant: 'baseline' });
  const keys = (rows) => rows.map(({ day, id }) => day + '/' + id);
  assert.equal(new Set(keys(baseline)).size, 699);
  for (const variant of ['pilot', 'enriched']) {
    const rows = forecastSelection(data, pilot, { variant });
    assert.deepEqual(keys(rows), keys(baseline));
    assert(rows.every(({ ctr, cpm }) => ctr >= 0 && ctr <= 100 && cpm > 0));
  }
  const single = forecastSelection(data, pilot, { variant: 'baseline', ad: 'CDF-AD23' });
  const series = dailyForecast(single, data.dates);
  assert.equal(series[0].ctr, null);
  assert(Math.abs(series.at(-1).ctr - single.at(-1).ctr) < 1e-10);
});

test('budget scenarios conserve campaign/day totals and respect each ad-set bound', () => {
  for (const campaign of data.campaigns) {
    const sets = data.adsets.filter((set) => set.campaignId === campaign.id).map((set) => set.id);
    const rows = data.budgetScenario.filter((row) => sets.includes(row[1]));
    const [from, to] = sets;
    const bound = data.source.budgetBound;
    const limit = transferLimit(rows, from, to, bound);
    assert(limit > 0);
    for (const mode of ['base', 'recommended', 'custom']) {
      const applied = budgetAllocation(rows, { mode, from, to, amount: limit * 2, bound });
      assert(applied.every((row) => Math.abs(row.budget - row.base) <= row.base * bound + 1e-8));
      for (const day of data.dates) {
        const totals = budgetTotals(applied.filter((row) => row.day === day));
        assert.equal(totals.base, totals.budget);
      }
      if (mode === 'recommended') {
        assert(applied.every((row, i) => Math.abs(row.clicks - rows[i][7]) < 1e-6));
      }
      if (mode === 'custom') assert.equal(applied.find((row) => row.id === from).base - applied.find((row) => row.id === from).budget, limit);
    }
  }
});

test('Overview and Creative Explorer agree on the most efficient Black Friday ad', () => {
  const catalog = creativeCatalog(data);
  const day = data.dates.find((date) => data.events[date] === 'Black Friday');
  const best = sortCreatives(creativesForDay(catalog, day), { key: 'efficiency', direction: -1 })[0];
  assert.equal(best.id, overviewModel(data, '', '').best.id);
  assert.equal(best.efficiency, 10 * best.ctr / best.cpm);
});

test('validation windows preserve published coverage and split by sector', () => {
  const validation = read('model-validation');
  assert.equal(validation.folds.reduce((total, fold) => total + fold.tutti.righe, 0), 759);
  assert.equal(validation.combined.righe, 759);
  for (const fold of validation.folds) {
    assert(fold.cutoff < fold.dal && fold.al <= data.source.cutoff);
    assert.equal(Object.values(fold.settori).reduce((total, row) => total + row.righe, 0), fold.tutti.righe);
    assert.equal(fold.annunci_nuovi.righe + fold.annunci_gia_visti.righe, fold.tutti.righe);
  }
});
