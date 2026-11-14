export function chartDomain(values, zoom = true) {
  const valid = values.filter((v) => Number.isFinite(v));
  if (!valid.length) return { min: 0, max: 1, ticks: [0, .25, .5, .75, 1] };
  const low = Math.min(...valid), high = Math.max(...valid);
  const pad = Math.max((high - low) * .22, high * .008, .0001);
  const min = zoom ? Math.max(0, low - pad) : 0;
  const max = zoom ? high + pad : Math.max(high * 1.15, .01);
  return { min, max, ticks: Array.from({ length: 5 }, (_, i) => min + (max - min) * i / 4) };
}
