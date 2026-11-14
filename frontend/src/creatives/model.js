import { leverNames, verticalNames } from '../overview/model';

export const sectorTones = {
  abbigliamento: 'purple',
  beauty_skincare: 'pink',
  pet_ecommerce: 'green',
};

export const formatNames = { video: 'Video', immagine: 'Immagine', carosello: 'Carosello' };

export function creativeCatalog(data) {
  const adsets = new Map(data.adsets.map((row) => [row.id, row]));
  const campaigns = new Map(data.campaigns.map((row) => [row.id, row]));
  const catalog = new Map();
  for (const [id, meta] of Object.entries(data.ads)) {
    const [adsetId, assetId, headline, lever, format, coldStart] = meta;
    const campaignId = adsets.get(adsetId).campaignId;
    const vertical = campaigns.get(campaignId).vertical;
    catalog.set(id, {
      id, adsetId, campaignId, assetId, headline, coldStart,
      vertical, sector: verticalNames[vertical] ?? vertical, tone: sectorTones[vertical] ?? 'purple',
      lever: leverNames[lever] ?? lever, format: formatNames[format] ?? format,
      asset: data.assetDetails?.[assetId], series: new Map(),
    });
  }

  for (const [day, id, ctr, cpm] of data.forecast) {
    catalog.get(id).series.set(day, { ctr, cpm, cpc: ctr > 0 ? cpm / (10 * ctr) : null });
  }

  return catalog;
}

export function creativesForDay(catalog, day) {
  return Array.from(catalog.values()).flatMap((creative) => {
    const metrics = creative.series.get(day);
    return metrics ? [{ ...creative, ...metrics }] : [];
  });
}

export function sortCreatives(rows, { key, direction }) {
  return [...rows].sort((a, b) => {
    const left = a[key];
    const right = b[key];
    if (left == null || right == null) {
      return Number(left == null) - Number(right == null) || a.id.localeCompare(b.id);
    }
    const diff = typeof left === 'number' ? left - right : left.localeCompare(right, 'it');
    return diff * direction || a.id.localeCompare(b.id);
  });
}

export function plotLimit(maximum) {
  const estimate = maximum / 4;
  const unit = 10 ** Math.floor(Math.log10(estimate || 1));
  const step = [1, 2, 2.5, 5, 10].map((factor) => factor * unit).find((n) => n >= estimate) ?? 10 * unit;
  return step * 4;
}
