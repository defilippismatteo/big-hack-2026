const keyOf = (day, id) => day + '/' + id;

export function forecastSelection(data, pilot, { campaign, adset, ad, variant, dates }) {
  const sets = new Map(data.adsets.map((item) => [item.id, item.campaignId]));
  const alternatives = new Map((pilot?.rows ?? []).map(([day, id, ...values]) => [keyOf(day, id), values]));
  return data.forecast.flatMap(([day, id, ctr, cpm], i) => {
    const [set] = data.ads[id];
    if ((campaign && sets.get(set) !== campaign) || (adset && set !== adset) ||
        (ad && id !== ad) || (dates && !dates.includes(day))) return [];
    const extra = alternatives.get(keyOf(day, id));
    if (variant !== 'baseline' && !extra) return [];
    const metrics = variant === 'enriched' ? extra.slice(1) : variant === 'pilot' ? [ctr, extra[0]] : [ctr, cpm];
    return [{ day, id, ctr: metrics[0], cpm: metrics[1], spend: data.forecastSpend?.[i] ?? null }];
  });
}

export function dailyForecast(rows, dates) {
  const groups = new Map();
  for (const row of rows) {
    const values = groups.get(row.day) ?? { spend: 0, impressions: 0, clicks: 0 };
    const impressions = row.spend == null ? 0 : 1000 * row.spend / row.cpm;
    values.spend += row.spend ?? 0;
    values.impressions += impressions;
    values.clicks += impressions * row.ctr / 100;
    groups.set(row.day, values);
  }
  return dates.map((day) => {
    const values = groups.get(day);
    const hasEstimate = values?.impressions > 0;
    return { day, ctr: hasEstimate ? 100 * values.clicks / values.impressions : null,
      cpm: hasEstimate ? 1000 * values.spend / values.impressions : null };
  });
}
