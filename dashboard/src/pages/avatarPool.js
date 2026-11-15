const BACKGROUNDS = ['#eee7ff', '#e0f1ed', '#fbe9d9'];

const WOMEN = [
  '/avatars/chiara-hero.png',
  '/avatars/portrait-glasses.png',
  '/avatars/five-grid-01.png',
  '/avatars/five-grid-04.png',
  '/avatars/five-grid-05.png',
  '/avatars/five-row-03.png',
  '/avatars/five-row-04.png',
  '/avatars/ten-grid-01.png',
  '/avatars/ten-grid-04.png',
  '/avatars/ten-grid-05.png',
  '/avatars/ten-grid-10.png',
];

const WOMEN_SENIOR = [
  '/avatars/five-row-03.png',
  '/avatars/five-grid-05.png',
  '/avatars/portrait-glasses.png',
  '/avatars/ten-grid-01.png',
  '/avatars/chiara-hero.png',
];

const MEN = [
  '/avatars/five-grid-02.png',
  '/avatars/five-grid-03.png',
  '/avatars/five-row-05.png',
  '/avatars/ten-grid-02.png',
  '/avatars/ten-grid-03.png',
  '/avatars/ten-grid-06.png',
  '/avatars/ten-grid-07.png',
  '/avatars/ten-grid-08.png',
  '/avatars/ten-grid-09.png',
];

const MEN_SENIOR = [
  '/avatars/ten-grid-08.png',
  '/avatars/ten-grid-03.png',
  '/avatars/five-grid-03.png',
  '/avatars/ten-grid-06.png',
  '/avatars/five-grid-02.png',
];

const NEUTRAL = [
  '/avatars/five-grid-02.png',
  '/avatars/ten-grid-07.png',
  '/avatars/ten-grid-09.png',
  '/avatars/five-row-05.png',
  '/avatars/ten-grid-02.png',
  '/avatars/ten-grid-04.png',
  '/avatars/five-grid-05.png',
  '/avatars/portrait-glasses.png',
];

export const ALL_AVATARS = [...new Set([...WOMEN, ...MEN, ...NEUTRAL])];

export function avatarFor(persona) {
  const id = persona?.persona_id ?? '';
  const seed = [...id].reduce((acc, ch, i) => acc + ch.charCodeAt(0) * (i + 1), 0);
  const bg = BACKGROUNDS[seed % BACKGROUNDS.length];

  if (id === 'abbigliamento-P001') {
    return { src: '/avatars/chiara-hero.png', bg };
  }

  const senior = Number(persona?.age_years) >= 65;
  let pool = NEUTRAL;
  if (persona?.gender_identity === 'donna') {
    pool = senior ? WOMEN_SENIOR : WOMEN;
  } else if (persona?.gender_identity === 'uomo') {
    pool = senior ? MEN_SENIOR : MEN;
  }

  return { src: pool[seed % pool.length], bg };
}
