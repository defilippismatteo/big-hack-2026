(function () {
  const D = window.ADERA_DATA;
  const TOTAL_MS = 150000;

  // --- Cubic-bezier exact solver matching CSS/WAAPI easing curves ---
  function cubicBezier(x1, y1, x2, y2) {
    return function (t) {
      if (t <= 0) return 0;
      if (t >= 1) return 1;
      let lo = 0, hi = 1, u = t;
      for (let i = 0; i < 24; i++) {
        u = (lo + hi) * 0.5;
        const x = 3 * (1 - u) * (1 - u) * u * x1 + 3 * (1 - u) * u * u * x2 + u * u * u;
        if (x < t) lo = u; else hi = u;
      }
      return 3 * (1 - u) * (1 - u) * u * y1 + 3 * (1 - u) * u * u * y2 + u * u * u;
    };
  }

  const EASE = {
    outCirc: cubicBezier(0.075, 0.82, 0.165, 1),   // ref seq1 RMSE 0.012
    outExpo: cubicBezier(0.16, 1, 0.3, 1),        // ref seq2, seq3, seq5, seq6
    outBack: cubicBezier(0.34, 1.56, 0.64, 1),    // ref seq4 Tinder swipe overshoot
    inOutCubic: cubicBezier(0.65, 0, 0.35, 1),    // camera pan/zoom
    linear: (t) => t,
  };

  const clamp01 = (v) => (v < 0 ? 0 : v > 1 ? 1 : v);
  const seg = (t, start, dur, ease = EASE.outExpo) => ease(clamp01((t - start) / dur));
  const lerp = (a, b, p) => a + (b - a) * p;
  const fmtIt = (n, dec = 2) => n.toLocaleString('it-IT', { minimumFractionDigits: dec, maximumFractionDigits: dec });

  // --- Populate dynamic DOM from verified ADERA_DATA ---
  function populateDOM() {
    // Scene 1: kinetic headline words
    const words = [
      { text: 'E', accent: false }, { text: 'se', accent: false }, { text: 'potessi', accent: false },
      { text: 'testare', accent: true }, { text: 'una', accent: false }, { text: 'campagna', accent: true },
      { text: 'prima', accent: false }, { text: 'di', accent: false }, { text: 'investirci?', accent: true }
    ];
    document.getElementById('s1-headline').innerHTML = words
      .map((w, i) => `<span class="word-mask"><span class="word-inner ${w.accent ? 'accent-word' : ''}" id="s1-w-${i}">${w.text}</span></span>`)
      .join('');

    // Scene 3: KPIs + 12 adsets table + bar SVG
    const obs = D.observedTotal;
    document.getElementById('s3-kpis').innerHTML = [
      { label: 'Impression osservate', val: obs.impressions.toLocaleString('it-IT') },
      { label: 'Clic osservati', val: obs.clicks.toLocaleString('it-IT') },
      { label: 'Spesa storica', val: fmtIt(obs.spendEur, 2) + ' €' },
      { label: 'CTR osservato', val: fmtIt(obs.ctrPct, 2) + '%', hi: true },
      { label: 'CPM storico', val: fmtIt(obs.cpmEur, 2) + ' €', hi: true },
    ].map(k => `<div class="s3-kpi ${k.hi ? 'highlight' : ''}"><span>${k.label}</span><strong>${k.val}</strong></div>`).join('');

    const tableRows = D.adsetsObserved.map((a, idx) => {
      const pctW = Math.min(100, (a.ctr / 2.6) * 100).toFixed(1);
      return `<div class="s3-row" id="s3-r-${idx}">
        <strong style="color:var(--action)">${a.id}</strong>
        <span style="color:var(--muted)">${a.campaignId}</span>
        <div class="s3-bar-track"><div class="s3-bar-fill" style="width:${pctW}%"></div></div>
        <span>${a.impr.toLocaleString('it-IT')}</span>
        <span>${a.clicks.toLocaleString('it-IT')}</span>
        <span>${fmtIt(a.ctr, 2)}%</span>
        <span>${fmtIt(a.cpm, 2)} €</span>
      </div>`;
    }).join('');
    document.getElementById('s3-table').innerHTML =
      `<div class="s3-row head"><span>Ad set</span><span>Campagna</span><span>CTR relativo</span><span>Impression</span><span>Clic</span><span>CTR</span><span>CPM</span></div>` + tableRows;

    const bars = D.adsetsObserved.map((a, idx) => {
      const x = 40 + idx * 132;
      const h = Math.round((a.cpm / 12) * 340);
      const y = 395 - h;
      return `<g id="s3-b-${idx}">
        <rect x="${x}" y="${y}" width="84" height="${h}" rx="12" fill="${a.id.startsWith('FGR') ? '#7046CE' : '#A992EB'}" />
        <text x="${x + 42}" y="${y - 12}" text-anchor="middle" font-size="18" font-weight="800" fill="#292339">${fmtIt(a.cpm, 2)} €</text>
        <text x="${x + 42}" y="432" text-anchor="middle" font-size="16" font-weight="700" fill="#625E73">${a.id}</text>
      </g>`;
    }).join('');
    document.getElementById('s3-bars-svg').innerHTML = `<line x1="24" y1="395" x2="1620" y2="395" stroke="#E5E0F2" stroke-width="2"/>${bars}`;

    // Scene 4 & 5: Forecast SVG (observed anchor + temporal gap + 15-day forecast)
    // Y-axis from 0 to 16.5 EUR (540 down to 140) leaving generous room for event popups above
    const yOfCpm = (v) => 540 - (v / 16.5) * 390;
    const obsAnchorY = yOfCpm(obs.cpmEur); // 7.43 EUR
    const pts = D.dailyForecast.map((d, i) => {
      const x = 520 + i * 76; // 520 .. 1584
      const y = yOfCpm(d.cpm);
      return { x, y, ...d };
    });
    const pathD = pts.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x.toFixed(1)} ${p.y.toFixed(1)}`).join(' ');
    const areaD = `${pathD} L ${pts[pts.length - 1].x.toFixed(1)} 540 L ${pts[0].x.toFixed(1)} 540 Z`;

    const yGrid = [0, 4, 8, 12, 16].map(v => {
      const yy = yOfCpm(v);
      return `<line x1="70" y1="${yy}" x2="1610" y2="${yy}" stroke="#ECE7F6" stroke-width="2" />
              <text x="52" y="${yy + 6}" text-anchor="end" font-size="18" font-weight="700" fill="#625E73">${v} €</text>`;
    }).join('');

    const xTicks = pts.map((p, i) => {
      const hi = p.event ? 'fill="#7046CE" font-weight="800"' : 'fill="#625E73" font-weight="650"';
      return `<text x="${p.x}" y="582" text-anchor="middle" font-size="16" ${hi}>${p.label}</text>`;
    }).join('');

    const evLines = pts.filter(p => p.event).map(p =>
      `<g class="ev-marker" data-day="${p.day}" opacity="0">
        <line x1="${p.x}" y1="95" x2="${p.x}" y2="540" stroke="#8861E8" stroke-width="3" stroke-dasharray="8 6" />
        <circle cx="${p.x}" cy="${p.y}" r="9" fill="#FFFFFF" stroke="#7046CE" stroke-width="4" />
      </g>`
    ).join('');

    document.getElementById('s4-svg').innerHTML = `
      <defs>
        <linearGradient id="fcAreaGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#8861E8" stop-opacity="0.28"/>
          <stop offset="100%" stop-color="#8861E8" stop-opacity="0.02"/>
        </linearGradient>
      </defs>
      ${yGrid}
      <!-- Observed historical zone (1..15 nov) -->
      <rect x="80" y="100" width="330" height="440" rx="16" fill="#F4F1FA" />
      <text x="245" y="142" text-anchor="middle" font-size="18" font-weight="800" fill="#625E73">STORICO OSSERVATO (FINO AL 15/11)</text>
      <line x1="105" y1="${obsAnchorY.toFixed(1)}" x2="390" y2="${obsAnchorY.toFixed(1)}" stroke="#625E73" stroke-width="5" stroke-linecap="round" />
      <circle cx="390" cy="${obsAnchorY.toFixed(1)}" r="8" fill="#625E73" />
      <text x="245" y="${(obsAnchorY - 18).toFixed(1)}" text-anchor="middle" font-size="22" font-weight="800" fill="#292339">CPM medio 7,43 € · CTR 1,19%</text>
      <text x="245" y="582" text-anchor="middle" font-size="16" font-weight="700" fill="#625E73">01/11 – 15/11</text>

      <!-- Temporal gap -->
      <rect x="422" y="100" width="84" height="440" fill="repeating-linear-gradient(45deg,#FAF9FD,#FAF9FD 8px,#EFEAFB 8px,#EFEAFB 16px)" opacity="0.6" />
      <line x1="414" y1="100" x2="414" y2="540" stroke="#C5B9E8" stroke-width="2" stroke-dasharray="6 6" />
      <text x="464" y="330" text-anchor="middle" font-size="16" font-weight="800" fill="#7046CE" transform="rotate(-90 464 330)">GAP CUTOFF 15/11</text>

      <!-- Forecast area + curve -->
      <path id="s4-area" d="${areaD}" fill="url(#fcAreaGrad)" opacity="0" />
      <path id="s4-line" d="${pathD}" fill="none" stroke="#7046CE" stroke-width="6" stroke-linecap="round" stroke-linejoin="round" />
      ${evLines}
      <circle id="s4-tip" cx="${pts[0].x}" cy="${pts[0].y}" r="11" fill="#8861E8" stroke="#FFFFFF" stroke-width="4" />
      ${xTicks}
    `;

    // Store geometry for camera tip tracking
    window.__FC_PTS__ = pts;
    const lineEl = document.getElementById('s4-line');
    window.__FC_LEN__ = lineEl.getTotalLength();
    lineEl.style.strokeDasharray = `${window.__FC_LEN__}`;

    // Scene 9: 10 avatars + ghost ring
    document.getElementById('s9-grid').innerHTML = D.tenPersonas.map((p, idx) => `
      <article class="s9-avatar-card ${idx === 0 ? 'hero' : ''}" id="s9-av-${idx}">
        <img src="${idx === 0 ? 'assets/avatars/chiara-hero.png' : p.avatar}" alt="${p.name}" />
        <strong>${p.name}, ${p.age}</strong>
        <span>${p.occupation}</span>
      </article>
    `).join('');

    const ghostCoords = [
      [120, 140], [1760, 130], [80, 520], [1800, 540], [160, 910],
      [1740, 890], [520, 40], [1360, 40], [920, 20], [960, 980]
    ];
    document.getElementById('s9-ghosts').innerHTML = ghostCoords
      .map(([gx, gy]) => `<div class="s9-ghost" style="left:${gx}px;top:${gy}px"></div>`)
      .join('');
  }

  populateDOM();

  const scenes = [
    { id: 's1', start: 0, end: 9000 },
    { id: 's2', start: 9000, end: 16000 },
    { id: 's3', start: 16000, end: 27000 },
    { id: 's4', start: 27000, end: 53000 }, // Scenes 4 + 5 share forecast stage
    { id: 's6', start: 53000, end: 65000 },
    { id: 's7', start: 65000, end: 76000 },
    { id: 's8', start: 76000, end: 95000 },
    { id: 's9', start: 95000, end: 104000 },
    { id: 's10', start: 104000, end: 112000 },
    { id: 's11', start: 112000, end: 127000 },
    { id: 's12', start: 127000, end: 144000 },
    { id: 's13', start: 144000, end: 150000 },
  ];

  // --- Deterministic Timeline Evaluator ---
  function renderAt(tMs) {
    const t = Math.max(0, Math.min(TOTAL_MS, tMs));

    for (const sc of scenes) {
      const el = document.getElementById(sc.id);
      const active = t >= sc.start && (t < sc.end || (sc.id === 's13' && t <= TOTAL_MS));
      el.style.opacity = active ? '1' : '0';
      el.style.zIndex = active ? '2' : '0';
    }

    // --- SCENE 1 (0..9000ms) [CLONED SEQ1] ---
    if (t < 9000) {
      for (let i = 0; i < 9; i++) {
        const w = document.getElementById(`s1-w-${i}`);
        const p = seg(t, 567 + i * 95, 520, EASE.outCirc);
        w.style.transform = `translateY(${lerp(115, 0, p).toFixed(2)}%)`;
        w.style.opacity = clamp01(p * 1.4).toFixed(3);
      }
      const pSub = seg(t, 1200, 600, EASE.outCirc);
      const subEl = document.getElementById('s1-sub');
      subEl.style.transform = `translateY(${lerp(28, 0, pSub).toFixed(2)}px)`;
      subEl.style.opacity = pSub.toFixed(3);

      const cards = [
        { sel: '.s1-card-1', start: 2533, dur: 600, dist: 150 },
        { sel: '.s1-card-2', start: 3600, dur: 533, dist: 140 },
        { sel: '.s1-card-3', start: 4533, dur: 500, dist: 140 },
      ];
      cards.forEach((c) => {
        const el = document.querySelector(c.sel);
        const p = seg(t, c.start, c.dur, EASE.outCirc);
        el.style.transform = `translateY(${lerp(c.dist, 0, p).toFixed(2)}px)`;
        el.style.opacity = p.toFixed(3);
      });

      const exitP = seg(t, 8533, 467, EASE.inOutCubic);
      document.getElementById('s1').style.transform = `translateY(${lerp(0, -100, exitP).toFixed(2)}%)`;
    }

    // --- SCENE 2 (9000..16000ms) [CLONED SEQ2] ---
    if (t >= 9000 && t < 16000) {
      const lt = t - 9000;
      const pw = seg(lt, 0, 267, EASE.outCirc);
      document.getElementById('s2-wipe').style.transform = `scale(${lerp(0.02, 1.45, pw).toFixed(4)})`;

      const ps = seg(lt, 150, 650, EASE.outExpo);
      const sym = document.getElementById('s2-symbol');
      const openOut = seg(lt, 5850, 1150, EASE.inOutCubic);
      sym.style.transform = `scale(${lerp(lerp(0.65, 1, ps), 3.4, openOut).toFixed(4)})`;
      sym.style.opacity = (ps * (1 - openOut * 0.85)).toFixed(3);

      ['s2-bar1', 's2-bar2', 's2-bar3'].forEach((bid, idx) => {
        const pb = seg(lt, 260 + idx * 95, 420, EASE.outExpo);
        document.getElementById(bid).style.opacity = pb.toFixed(3);
      });

      const pwm = seg(lt, 350, 600, EASE.outExpo);
      const wm = document.getElementById('s2-wordmark');
      wm.style.transform = `translateY(${lerp(36, 0, pwm).toFixed(2)}px)`;
      wm.style.opacity = (pwm * (1 - openOut)).toFixed(3);

      const ppay = seg(lt, 550, 600, EASE.outExpo);
      const pay = document.getElementById('s2-payoff');
      pay.style.transform = `translateY(${lerp(28, 0, ppay).toFixed(2)}px)`;
      pay.style.opacity = (ppay * (1 - openOut)).toFixed(3);

      // Right pill card matches ref seq2 3433ms entry
      const ppill = seg(lt, 3433, 400, EASE.outCirc);
      const pill = document.getElementById('s2-pill');
      pill.style.transform = `translateX(${lerp(48, 0, ppill).toFixed(2)}px)`;
      pill.style.opacity = (ppill * (1 - openOut)).toFixed(3);

      document.getElementById('s2').style.backgroundColor = openOut > 0.5 ? '#F6F5F9' : 'transparent';
    }

    // --- SCENE 3 (16000..27000ms) DATI CHALLENGE ---
    if (t >= 16000 && t < 27000) {
      const lt = t - 16000;
      const pk = seg(lt, 0, 700, EASE.outExpo);
      document.getElementById('s3-kpis').style.transform = `translateY(${lerp(26, 0, pk).toFixed(2)}px)`;
      document.getElementById('s3-kpis').style.opacity = pk.toFixed(3);

      const morphP = seg(lt, 5000, 2200, EASE.inOutCubic);
      for (let i = 0; i < 12; i++) {
        const row = document.getElementById(`s3-r-${i}`);
        const enter = seg(lt, 350 + i * 70, 450, EASE.outExpo);
        row.style.transform = `translateY(${lerp(22, 0, enter) - morphP * 24}px) scaleY(${lerp(1, 0.2, morphP).toFixed(3)})`;
        row.style.opacity = (enter * (1 - morphP)).toFixed(3);
      }
      document.getElementById('s3-table').style.opacity = (1 - morphP).toFixed(3);
      const ser = document.getElementById('s3-series');
      ser.style.opacity = morphP.toFixed(3);
      ser.style.transform = `scale(${lerp(0.94, 1, morphP).toFixed(4)})`;
    }

    // --- SCENE 4 & 5 (27000..53000ms) FORECAST + EVENTI & MODELLI ---
    if (t >= 27000 && t < 53000) {
      const lt = t - 27000;
      const pts = window.__FC_PTS__;
      const lineLen = window.__FC_LEN__;
      const lineEl = document.getElementById('s4-line');
      const areaEl = document.getElementById('s4-area');
      const tipEl = document.getElementById('s4-tip');
      const camEl = document.getElementById('s4-camera');

      // Draw progress from 1.5s to 10.5s (28.5s..37.5s master)
      const drawP = seg(lt, 1500, 9000, EASE.linear);
      lineEl.style.strokeDashoffset = (lineLen * (1 - drawP)).toFixed(1);
      areaEl.style.opacity = clamp01(drawP * 1.4).toFixed(3);

      // Tip position along pts
      const fIdx = drawP * (pts.length - 1);
      const i0 = Math.floor(fIdx), i1 = Math.min(pts.length - 1, i0 + 1);
      const frac = fIdx - i0;
      const tipX = lerp(pts[i0].x, pts[i1].x, frac);
      const tipY = lerp(pts[i0].y, pts[i1].y, frac);
      tipEl.setAttribute('cx', tipX.toFixed(1));
      tipEl.setAttribute('cy', tipY.toFixed(1));
      const curPt = pts[Math.round(fIdx)];
      document.getElementById('s4-readout').textContent =
        `${curPt.label} · CPM ${fmtIt(curPt.cpm, 2)} € · CTR ${fmtIt(curPt.ctr, 3)}%`;

      // Camera follows tip (scale 1.75) during draw, then zooms out 10.5s..14.8s
      const zoomInP = seg(lt, 400, 1200, EASE.inOutCubic);
      const zoomOutP = seg(lt, 10500, 4200, EASE.inOutCubic);
      const camScale = lerp(1.0, 1.75, zoomInP) * (1 - zoomOutP) + 1.0 * zoomOutP;
      const targetTx = (830 - tipX) * 0.65;
      const targetTy = (320 - tipY) * 0.55;
      const tx = targetTx * zoomInP * (1 - zoomOutP);
      const ty = targetTy * zoomInP * (1 - zoomOutP);
      camEl.style.transform = `translate(${tx.toFixed(1)}px, ${ty.toFixed(1)}px) scale(${camScale.toFixed(4)})`;

      // Scene 5 starts at lt=17000ms (44s master): Event markers + popups + model dock
      const s5t = lt - 17000;
      const markers = document.querySelectorAll('#s4-svg .ev-marker');
      markers.forEach((m, idx) => {
        const pm = seg(s5t, idx * 450, 500, EASE.outExpo);
        m.setAttribute('opacity', pm.toFixed(3));
      });
      ['pop-bw', 'pop-bf', 'pop-cm'].forEach((pid, idx) => {
        const pp = seg(s5t, 200 + idx * 500, 520, EASE.outBack);
        const pel = document.getElementById(pid);
        pel.style.opacity = clamp01(pp).toFixed(3);
        pel.style.transform = `translateY(${lerp(24, 0, pp).toFixed(1)}px) scale(${lerp(0.9, 1, pp).toFixed(3)})`;
      });

      const modP = seg(s5t, 1800, 750, EASE.outExpo);
      const dock = document.getElementById('s5-models');
      dock.style.opacity = modP.toFixed(3);
      dock.style.transform = `translateY(${lerp(42, 0, modP).toFixed(1)}px)`;

      document.getElementById('s4-title').textContent = s5t > 0
        ? 'Eventi Black Friday & ruoli reali dei modelli.'
        : 'Previsione su 15 giorni, senza picchi artificiali.';
    }

    // --- SCENE 6 (53000..65000ms) ORCHESTRAZIONE [CLONED SEQ5] ---
    if (t >= 53000 && t < 65000) {
      const lt = t - 53000;
      const ph = seg(lt, 33, 567, EASE.outExpo);
      const hub = document.getElementById('s6-hub');
      hub.style.opacity = ph.toFixed(3);
      hub.style.transform = `scale(${lerp(0.84, 1, ph).toFixed(4)})`;

      // Animate dashed lines continuously
      const dashOff = -(lt * 0.045);
      ['s6-p1', 's6-p2', 's6-p3'].forEach((id) => {
        const el = document.getElementById(id);
        el.style.strokeDashoffset = dashOff.toFixed(1);
        el.style.opacity = seg(lt, 500, 700, EASE.linear).toFixed(3);
      });

      // Agents enter at 4167ms + 160ms stagger, dur 500ms easeOutExpo (matches ref seq5!)
      ['s6-a1', 's6-a2', 's6-a3'].forEach((aid, idx) => {
        const pa = seg(lt, 4167 + idx * 160, 500, EASE.outExpo);
        const ael = document.getElementById(aid);
        ael.style.opacity = pa.toFixed(3);
        ael.style.transform = `translateY(${lerp(40, 0, pa).toFixed(1)}px) scale(${lerp(0.84, 1, pa).toFixed(4)})`;
      });
    }

    // --- SCENE 7 (65000..76000ms) PERSONA CHIARA [CLONED SEQ3-PERSONA] ---
    if (t >= 65000 && t < 76000) {
      const lt = t - 65000;
      // Left copy enters immediately (33ms..867ms) matching ref seq3 opening motion
      const pCopy = seg(lt, 33, 833, EASE.outExpo);
      const copyEl = document.querySelector('#s7 .s7-copy');
      copyEl.style.opacity = pCopy.toFixed(3);
      copyEl.style.transform = `translateY(${lerp(42, 0, pCopy).toFixed(1)}px)`;

      // Card enters at 3700ms dur 600ms easeOutExpo (matches ref seq3-persona!)
      const pc = seg(lt, 3700, 600, EASE.outExpo);
      const card = document.getElementById('s7-card');
      card.style.opacity = pc.toFixed(3);
      card.style.transform = `translateY(${lerp(90, 0, pc).toFixed(1)}px)`;

      ['s7-at1', 's7-at2', 's7-at3', 's7-at4', 's7-at5'].forEach((id, idx) => {
        const pa = seg(lt, 3840 + idx * 140, 450, EASE.outExpo);
        const el = document.getElementById(id);
        el.style.opacity = pa.toFixed(3);
        el.style.transform = `translateY(${lerp(20, 0, pa).toFixed(1)}px)`;
      });
    }

    // --- SCENE 8 (76000..95000ms) FEED DECISION 1 [CLONED SEQ4-FEED] ---
    if (t >= 76000 && t < 95000) {
      const lt = t - 76000;
      const pEnter = seg(lt, 33, 500, EASE.outExpo);
      const s8Left = document.querySelector('#s8 .s8-left');
      const s8Phone = document.querySelector('#s8 .s8-phone');
      const s8Right = document.querySelector('#s8 .s8-right');
      s8Left.style.opacity = pEnter.toFixed(3);
      s8Left.style.transform = `translateY(${lerp(28, 0, pEnter).toFixed(1)}px)`;
      s8Phone.style.opacity = pEnter.toFixed(3);
      s8Phone.style.transform = `translateY(${lerp(40, 0, pEnter).toFixed(1)}px)`;

      // Feed/telemetry settle around 2600..3000ms matching ref seq4 mid-scroll burst
      const pTel = seg(lt, 2600, 420, EASE.outExpo);
      s8Right.style.opacity = (0.35 + 0.65 * pTel).toFixed(3);
      s8Right.style.transform = `translateY(${lerp(26, 0, pTel).toFixed(1)}px)`;

      const u3 = document.getElementById('fc-u3');
      const b1 = document.getElementById('fc-b1');
      const s1 = document.getElementById('fc-s1');

      // Swipe 1 (FGR-U3 right @ 4367ms, dur 433ms easeOutBack — matches ref seq4!)
      const sw1 = seg(lt, 4367, 433, EASE.outBack);
      const sw1Exit = seg(lt, 5100, 420, EASE.outExpo);
      const u3x = sw1 * 90 + sw1Exit * 520;
      const u3rot = sw1 * 6 + sw1Exit * 12;
      u3.style.transform = `translateX(${u3x.toFixed(1)}px) rotate(${u3rot.toFixed(2)}deg)`;
      u3.style.opacity = (1 - sw1Exit).toFixed(3);
      document.getElementById('st-u3').style.opacity = clamp01(sw1 * 1.2).toFixed(3);

      // Swipe 2 (FGR-B1 left @ 9200ms, dur 433ms easeOutBack)
      const sw2 = seg(lt, 9200, 433, EASE.outBack);
      const sw2Exit = seg(lt, 9950, 420, EASE.outExpo);
      const b1x = -(sw2 * 90 + sw2Exit * 520);
      const b1rot = -(sw2 * 6 + sw2Exit * 12);
      b1.style.transform = `translateX(${b1x.toFixed(1)}px) rotate(${b1rot.toFixed(2)}deg)`;
      b1.style.opacity = (1 - sw2Exit).toFixed(3);
      document.getElementById('st-b1').style.opacity = clamp01(sw2 * 1.2).toFixed(3);

      // Swipe 3 (FGR-S1 left @ 14000ms, dur 433ms easeOutBack)
      const sw3 = seg(lt, 14000, 433, EASE.outBack);
      s1.style.transform = `translateX(${(-sw3 * 85).toFixed(1)}px) rotate(${(-sw3 * 5).toFixed(2)}deg)`;
      document.getElementById('st-s1').style.opacity = clamp01(sw3 * 1.2).toFixed(3);

      // Subtle human inspection micro-motion between swipes so phone never freezes 4-5s
      const inspectPulse = Math.sin(lt * 0.0022);
      const s8PhoneScale = 1 + 0.012 * Math.sin(lt * 0.0014);
      s8Phone.style.transform = `translateY(${(lerp(40, 0, pEnter) + inspectPulse * 5).toFixed(1)}px) scale(${s8PhoneScale.toFixed(4)})`;

      // Smooth telemetry interpolation across card transitions
      const mix1 = seg(lt, 5000, 650, EASE.inOutCubic);
      const mix2 = seg(lt, 9850, 650, EASE.inOutCubic);
      const a0 = D.feedAssets[0].actions;
      const a1 = D.feedAssets[1].actions;
      const a2 = D.feedAssets[2].actions;
      const curClick = lerp(lerp(a0.click, a1.click, mix1), a2.click, mix2);
      const curStop = lerp(lerp(a0.stop, a1.stop, mix1), a2.stop, mix2);
      const curGlance = lerp(lerp(a0.glance, a1.glance, mix1), a2.glance, mix2);
      const curScroll = lerp(lerp(a0.scroll, a1.scroll, mix1), a2.scroll, mix2);

      // Active asset telemetry
      let activeIdx = 0;
      if (lt >= 10300) activeIdx = 2;
      else if (lt >= 5500) activeIdx = 1;
      const asset = D.feedAssets[activeIdx];
      document.getElementById('s8-counter').textContent = `${activeIdx + 1} / 3`;
      document.getElementById('s8-tel-id').textContent = asset.assetId;
      document.getElementById('s8-asset-status').innerHTML = `Asset attivo: <strong>${asset.assetId}</strong> · ${asset.visualDesc}`;
      document.getElementById('pf-click').style.width = `${(curClick * 2.2).toFixed(2)}%`;
      document.getElementById('pf-stop').style.width = `${(curStop * 2.2).toFixed(2)}%`;
      document.getElementById('pf-glance').style.width = `${(curGlance * 2.2).toFixed(2)}%`;
      document.getElementById('pf-scroll').style.width = `${(curScroll * 2.2).toFixed(2)}%`;
      document.getElementById('pv-click').textContent = fmtIt(curClick, 2) + '%';
      document.getElementById('pv-stop').textContent = fmtIt(curStop, 2) + '%';
      document.getElementById('pv-glance').textContent = fmtIt(curGlance, 2) + '%';
      document.getElementById('pv-scroll').textContent = fmtIt(curScroll, 2) + '%';
      const rightDrift = Math.sin(lt * 0.0017) * 4;
      s8Right.style.transform = `translateY(${(lerp(26, 0, pTel) + rightDrift).toFixed(1)}px)`;

      const toasts = [
        { id: 's8-toast1', start: 4600 },
        { id: 's8-toast2', start: 9450 },
        { id: 's8-toast3', start: 14250 },
      ];
      toasts.forEach((to) => {
        const pt = seg(lt, to.start, 450, EASE.outExpo);
        const tel = document.getElementById(to.id);
        tel.style.opacity = pt.toFixed(3);
        tel.style.transform = `translateX(${lerp(42, 0, pt).toFixed(1)}px)`;
      });
    }

    // --- SCENE 9 (95000..104000ms) SCALA 10 AVATAR -> 600 ---
    if (t >= 95000 && t < 104000) {
      const lt = t - 95000;
      const pz = seg(lt, 400, 4800, EASE.inOutCubic);
      const scale = lerp(2.15, 0.92, pz);
      const tx = lerp(620, 0, pz);
      const ty = lerp(180, -45, pz);
      document.getElementById('s9-camera').style.transform = `translate(${tx.toFixed(1)}px, ${ty.toFixed(1)}px) scale(${scale.toFixed(4)})`;
      document.getElementById('s9-ghosts').style.opacity = clamp01((pz - 0.35) * 1.6).toFixed(3);
      const countVal = Math.round(lerp(1, 600, seg(lt, 1200, 4500, EASE.outExpo)));
      document.getElementById('s9-count').textContent = `${countVal} profili`;
    }

    // --- SCENE 10 (104000..112000ms) MORPH SEGNALI IN DOCUMENTO ---
    if (t >= 104000 && t < 112000) {
      const lt = t - 104000;
      const pConv = seg(lt, 1400, 2600, EASE.inOutCubic);
      const targets = [
        [520, 210], [-520, 210], [520, -210], [-520, -210]
      ];
      ['s10-c1', 's10-c2', 's10-c3', 's10-c4'].forEach((cid, idx) => {
        const el = document.getElementById(cid);
        const [dx, dy] = targets[idx];
        el.style.transform = `translate(${(dx * pConv).toFixed(1)}px, ${(dy * pConv).toFixed(1)}px) scale(${lerp(1, 0.45, pConv).toFixed(3)})`;
        el.style.opacity = (1 - clamp01((pConv - 0.5) * 2.2)).toFixed(3);
      });
      const pDoc = seg(lt, 2600, 1400, EASE.outExpo);
      const doc = document.getElementById('s10-doc');
      doc.style.opacity = pDoc.toFixed(3);
      doc.style.transform = `scale(${lerp(0.84, 1, pDoc).toFixed(4)})`;
    }

    // --- SCENE 11 (112000..127000ms) INTERVISTE ---
    if (t >= 112000 && t < 127000) {
      const lt = t - 112000;
      const pq = seg(lt, 200, 600, EASE.outExpo);
      const qel = document.getElementById('s11-q');
      qel.style.opacity = pq.toFixed(3);
      qel.style.transform = `translateY(${lerp(30, 0, pq).toFixed(1)}px)`;

      const p1 = seg(lt, 1600, 700, EASE.outExpo);
      const c1 = document.getElementById('s11-card1');
      c1.style.opacity = p1.toFixed(3);
      c1.style.transform = `translateY(${lerp(40, 0, p1).toFixed(1)}px)`;

      const p2 = seg(lt, 4200, 700, EASE.outExpo);
      const c2 = document.getElementById('s11-card2');
      c2.style.opacity = p2.toFixed(3);
      c2.style.transform = `translateY(${lerp(40, 0, p2).toFixed(1)}px)`;
    }

    // --- SCENE 12 (127000..144000ms) PAN LEFT -> DASHBOARD SPLIT ---
    if (t >= 127000 && t < 144000) {
      const lt = t - 127000;
      const pulse = Math.sin((lt / 400) * Math.PI) * 18;
      document.getElementById('s12-arrow').style.transform = `translateX(${(-Math.abs(pulse)).toFixed(1)}px)`;

      // Camera pans LEFT following left arrow: track shifts from -1920px (intro on right) to 0px (dashboard on left)
      const panP = seg(lt, 1400, 2600, EASE.inOutCubic);
      document.getElementById('s12-track').style.transform = `translateX(${lerp(-1920, 0, panP).toFixed(1)}px)`;

      const pv1 = seg(lt, 3200, 700, EASE.outExpo);
      const pv2 = seg(lt, 4100, 700, EASE.outExpo);
      document.getElementById('s12-v1').style.opacity = pv1.toFixed(3);
      document.getElementById('s12-v1').style.transform = `translateY(${lerp(36, 0, pv1).toFixed(1)}px)`;
      document.getElementById('s12-v2').style.opacity = pv2.toFixed(3);
      document.getElementById('s12-v2').style.transform = `translateY(${lerp(36, 0, pv2).toFixed(1)}px)`;
    }

    // --- SCENE 13 (144000..150000ms) CHIUSURA [CLONED SEQ6] ---
    if (t >= 144000) {
      const lt = t - 144000;
      const pw = seg(lt, 33, 267, EASE.outExpo);
      const wipe = document.getElementById('s13-wipe');
      wipe.style.transform = `scaleX(${lerp(1, 0, pw).toFixed(4)})`;
      wipe.style.opacity = (1 - pw).toFixed(3);

      const pL = seg(lt, 400, 533, EASE.outExpo);
      const lock = document.getElementById('s13-lockup');
      lock.style.opacity = pL.toFixed(3);
      lock.style.transform = `scale(${lerp(0.92, 1, pL).toFixed(4)})`;

      const pPay = seg(lt, 1000, 600, EASE.outExpo);
      const pay = document.getElementById('s13-payoff');
      pay.style.opacity = pPay.toFixed(3);
      pay.style.transform = `translateY(${lerp(28, 0, pPay).toFixed(1)}px)`;

      const pSub = seg(lt, 3433, 667, EASE.outExpo);
      const sub = document.getElementById('s13-sub');
      sub.style.opacity = pSub.toFixed(3);
      sub.style.transform = `translateY(${lerp(20, 0, pSub).toFixed(1)}px)`;
    }
  }

  // Fit 1920x1080 stage cleanly into any browser window
  function fitStage() {
    const stage = document.getElementById('stage');
    const sx = window.innerWidth / 1920;
    const sy = window.innerHeight / 1080;
    const s = Math.min(sx, sy);
    stage.style.transform = `scale(${s})`;
  }
  window.addEventListener('resize', fitStage);
  fitStage();

  // Query params: ?capture=1&seq=seq1
  const params = new URLSearchParams(window.location.search);
  const seqMap = {
    seq1: 0,
    seq2: 9000,
    seq3: 65000,
    seq4: 76000,
    seq5: 53000,
    seq6: 144000,
  };
  const seqName = params.get('seq');
  const seqOffset = seqName && seqName in seqMap ? seqMap[seqName] : 0;
  const isCapture = params.get('capture') === '1';
  if (isCapture) document.body.classList.add('capture-mode');

  let currentMs = Number(params.get('t') || 0);
  window.__ADERA_SEEK__ = function (tMs) {
    currentMs = tMs;
    renderAt(seqOffset + tMs);
  };

  // Initial render
  window.__ADERA_SEEK__(currentMs);

  // Interactive playback when not in deterministic capture mode
  if (!isCapture) {
    let playing = !window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    let lastTs = performance.now();
    const scrub = document.getElementById('hud-scrub');
    const playBtn = document.getElementById('hud-play');
    const timeLbl = document.getElementById('hud-time');

    const fmtClock = (ms) => {
      const s = ms / 1000;
      const m = Math.floor(s / 60);
      const rem = (s - m * 60).toFixed(1).padStart(4, '0');
      return `${String(m).padStart(2, '0')}:${rem}`;
    };

    playBtn.addEventListener('click', () => {
      playing = !playing;
      playBtn.textContent = playing ? 'Pause' : 'Play';
      lastTs = performance.now();
    });
    scrub.addEventListener('input', () => {
      playing = false;
      playBtn.textContent = 'Play';
      currentMs = Number(scrub.value);
      window.__ADERA_SEEK__(currentMs);
      timeLbl.textContent = `${fmtClock(currentMs)} / 02:30.0`;
    });

    function tick(now) {
      if (playing) {
        currentMs += now - lastTs;
        if (currentMs > TOTAL_MS) currentMs = 0;
        window.__ADERA_SEEK__(currentMs);
        scrub.value = String(Math.round(currentMs));
        timeLbl.textContent = `${fmtClock(currentMs)} / 02:30.0`;
      }
      lastTs = now;
      requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }
})();
