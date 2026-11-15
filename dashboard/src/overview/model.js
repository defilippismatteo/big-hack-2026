const integer = new Intl.NumberFormat('it-IT');
const decimal = new Intl.NumberFormat('it-IT', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const euro = new Intl.NumberFormat('it-IT', { style: 'currency', currency: 'EUR', maximumFractionDigits: 2 });
const dayFormat = new Intl.DateTimeFormat('it-IT', { day: 'numeric', month: 'short', timeZone: 'UTC' });
export const whole = (value) => integer.format(Math.round(value));
export const fixed = (value) => decimal.format(value);
export const pct = (value) => value == null ? '—' : decimal.format(value) + '%';
export const money = (value) => value == null ? '—' : euro.format(value);
export const shortDate = (value) => dayFormat.format(new Date(value + 'T00:00:00Z'));
export const verticalNames = { abbigliamento: 'Abbigliamento', beauty_skincare: 'Beauty & skincare', pet_ecommerce: 'Pet e-commerce' };
export const leverNames = { scarcity: 'Scarsità', urgency: 'Urgenza', black_friday: 'Black Friday' };
export const modelNames = { ctr_baseline14d__cpm_timestral28m: 'CTR baseline 14 giorni · CPM Timestral-28M', weighted_hierarchical_14d_v1: 'Baseline gerarchica a 14 giorni' };
const sum = (items, pick) => items.reduce((total, item) => total + pick(item), 0);
const keyedSum = (items, pickKey, pickValue) => {
  const result = new Map();
  for (const item of items) {
    const key = pickKey(item);
    result.set(key, (result.get(key) ?? 0) + pickValue(item));
  }
  return result;
};
const order = (items, score, id) => [...items].sort((a, b) => score(b) - score(a) || id(a).localeCompare(id(b)));
const rates = (impressions, clicks, spend) => ({
  ctr: impressions > 0 ? 100 * clicks / impressions : null,
  cpm: impressions > 0 ? 1000 * spend / impressions : null,
});

export function overviewModel(data, campaign, adset) {
  const adsets = data.adsets.filter((item) => !campaign || item.campaignId === campaign);
  const filtered = adsets.filter((item) => !adset || item.id === adset);
  const ids = new Set(filtered.map((item) => item.id));
  const history = filtered.map((item) => data.observed[item.id]).filter(Boolean);
  const observed = rates(sum(history, (r) => r[0]), sum(history, (r) => r[1]), sum(history, (r) => r[2]) / 100);
  const rows = data.forecast.filter((r) => ids.has(data.ads[r[1]][0]));
  const scenario = data.budgetScenario.filter((r) => ids.has(r[1]));
  const seriesFor = (items, [spend, impressions, clicks]) => {
    const dateRows = new Map();
    for (const row of items) {
      if (!dateRows.has(row[0])) dateRows.set(row[0], []);
      dateRows.get(row[0]).push(row);
    }
    return data.dates.filter((day) => dateRows.has(day)).map((day) => {
      const daily = dateRows.get(day);
      return { day, ...rates(sum(daily, (r) => r[impressions]), sum(daily, (r) => r[clicks]),
        sum(daily, (r) => r[spend])) };
    });
  };
  const timeline = seriesFor(scenario, [4, 5, 6]);
  const seasonal = seriesFor((data.seasonalScenario?.rows ?? []).filter((r) => ids.has(r[1])), [2, 3, 4]);
  const friday = Object.keys(data.events).find((day) => data.events[day] === 'Black Friday');
  const candidates = rows.filter((r) => r[0] === friday).map(([, id, ctr, cpm]) => {
    const [adsetId, assetId, headline, lever, format, coldStart] = data.ads[id];
    return { id, adsetId, assetId, headline, lever, format, coldStart, ctr, cpm, efficiency: 10 * ctr / cpm };
  });
  const best = order(candidates, (r) => r.efficiency, (r) => r.id)[0];
  const hypotheses = order(data.hypotheses.filter((r) => ids.has(r.adsetId)), (r) => r.ctr, (r) => r.adsetId);
  const variations = keyedSum(scenario, (r) => r[1], (r) => r[3] - r[2]);
  const moves = [...variations].map(([id, delta]) => ({ id, delta }));
  const positive = order(moves.filter((r) => r.delta > 0), (r) => r.delta, (r) => r.id)[0];
  const negative = order(moves.filter((r) => r.delta < 0), (r) => -r.delta, (r) => r.id)[0];
  const budget = {
    original: sum(scenario, (r) => r[2]), proposed: sum(scenario, (r) => r[3]),
    baseClicks: sum(scenario, (r) => r[6]), scenarioClicks: sum(scenario, (r) => r[7]),
    reallocated: sum(moves.filter((r) => r.delta > 0), (r) => r.delta), positive, negative,
  };
  return { adsets, campaignCount: new Set(filtered.map((item) => item.campaignId)).size,
    adsetCount: filtered.length, predictionCount: rows.length, observed, timeline, seasonal, best, hypotheses, budget };
}
