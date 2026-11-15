const bySet = (rows, id) => new Map(rows.filter((row) => row[1] === id).map((row) => [row[0], row[2]]));

export function transferLimit(rows, from, to, bound) {
  if (!from || !to || from === to) return 0;
  const source = bySet(rows, from);
  const target = bySet(rows, to);
  if (!source.size || source.size !== target.size || [...source.keys()].some((day) => !target.has(day))) return 0;
  return Math.min(...[...source].map(([day, budget]) => Math.floor(Math.min(budget, target.get(day)) * bound + 1e-8)));
}

export function budgetAllocation(rows, { mode, from, to, amount, bound }) {
  const transfer = Math.max(0, Math.min(Math.trunc(amount || 0), transferLimit(rows, from, to, bound)));
  return rows.map(([day, id, base, proposed, spend, impressions, clicks]) => {
    const delta = id === to ? transfer : id === from ? -transfer : 0;
    const budget = mode === 'recommended' ? proposed : mode === 'custom' ? base + delta : base;
    const scale = base > 0 ? budget / base : 0;
    return { day, id, base, budget, spend: spend * scale, impressions: impressions * scale, clicks: clicks * scale, baseClicks: clicks };
  });
}

export function budgetTotals(rows) {
  const totals = { base: 0, budget: 0, spend: 0, impressions: 0, clicks: 0, baseClicks: 0 };
  for (const row of rows) for (const key of Object.keys(totals)) totals[key] += row[key];
  return { ...totals, ctr: totals.impressions > 0 ? 100 * totals.clicks / totals.impressions : null,
    cpm: totals.impressions > 0 ? 1000 * totals.spend / totals.impressions : null,
    cpc: totals.clicks > 0 ? totals.spend / totals.clicks : null };
}
