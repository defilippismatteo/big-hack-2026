(() => {
  const data = window.ADERA_DATA;
  const italianNumber = new Intl.NumberFormat("it-IT", { useGrouping: "always" });
  const decimal = (number, digits = 2) =>
    Number(number).toLocaleString("it-IT", { minimumFractionDigits: digits, maximumFractionDigits: digits });
  const dayMonth = day => day.slice(8) + "/" + day.slice(5, 7);

  document.querySelector("#record-count").textContent = italianNumber.format(data.records);
  document.querySelector("#kit-rows").innerHTML = data.table.map(([day, ad, impressions, clicks, cpm]) =>
    "<tr><td>" + dayMonth(day) + "</td><td>" + ad + "</td><td>" +
    italianNumber.format(impressions) + "</td><td>" + clicks + "</td><td>" + decimal(cpm) + "</td></tr>"
  ).join("");
  document.querySelector("#calendar").innerHTML = data.events.map(([day, label], index) =>
    '<article class="event-tile card' + (index === 1 ? " feature" : "") + '"><b>' + day.slice(8) +
    '</b><span>' + (index === 0 ? "Black Week" : label) + "</span></article>"
  ).join("");
  const fold = data.validation[1];
  document.querySelector("#model-numbers").textContent =
    decimal(fold.timestral, 3) + " / " + decimal(fold.catboost, 3) + " €";

  // Isolate each illustrated subject from the transparent source plate.
  const avatars = [
    ["sheet-ten-grid", 75, 29, 365, 390],
    ["sheet-ten-grid", 457, 24, 349, 391],
    ["sheet-ten-grid", 812, 23, 390, 393],
    ["sheet-ten-grid", 3, 429, 329, 372],
    ["sheet-ten-grid", 632, 434, 310, 372],
    ["sheet-ten-grid", 944, 432, 306, 374],
    ["sheet-ten-grid", 49, 831, 394, 376],
    ["chiara-hero", 142, 91, 972, 1069, true],
    ["sheet-ten-grid", 443, 817, 387, 389],
    ["portrait-glasses", 117, 57, 1020, 1131]
  ];
  document.querySelector(".cast").innerHTML = avatars.map(([asset, x, y, width, height, hero]) => {
    const factor = Math.min(266 / width, 241 / height);
    return '<div class="cast-card' + (hero ? " hero-cast" : "") + '"><div class="portrait" style="width:' +
      width * factor + "px;height:" + height * factor + "px;--w:" + 1254 * factor + "px;--h:" +
      1254 * factor + "px;--x:" + (-x * factor) + "px;--y:" + (-y * factor) +
      'px"><img src="assets/avatars/' + asset + '.png" alt=""></div></div>';
  }).join("");

  const chart = document.querySelector("#cpm-chart");
  const dateIndex = Object.fromEntries([...data.observed, ...data.forecast].map(([day], index) => [day, index]));
  const chartX = day => 112 + dateIndex[day] * 63;
  const chartY = cpm => 427 - (cpm - 6) * 97;
  const points = rows => rows.map(([day, cpm]) => chartX(day) + "," + chartY(cpm)).join(" ");
  const cutoffX = (chartX(data.cutoff) + chartX(data.forecast[0][0])) / 2;
  const [lastDay, lastCpm] = data.forecast.at(-1);
  const first = data.forecast[0];
  const markerDates = [...data.observed.filter((_, i) => [0, 6].includes(i)).map(([day]) => day), ...data.events.map(([day]) => day)];
  chart.innerHTML =
    '<rect x="' + cutoffX + '" y="48" width="' + (1513 - cutoffX) + '" height="379" rx="12" fill="#483063" opacity=".43"/>' +
    '<text class="period" x="112" y="34">STORICO</text><text class="period" x="' + (cutoffX + 25) + '" y="34">PREVISIONE</text>' +
    [6, 7, 8, 9, 10].map(value => {
      const y = chartY(value);
      return '<line class="axis" x1="112" x2="1513" y1="' + y + '" y2="' + y +
        '"/><text x="92" y="' + (y + 8) + '" text-anchor="end">' + value + ' €</text>';
    }).join("") +
    '<line class="cutoff" x1="' + cutoffX + '" x2="' + cutoffX + '" y1="50" y2="427"/>' +
    markerDates.map(day => {
      const x = chartX(day);
      return '<g class="chart-date"><line class="event-guide" x1="' + x + '" x2="' + x + '" y1="57" y2="427"/>' +
        '<text class="date-caption" x="' + x + '" y="474" text-anchor="middle">' + dayMonth(day) + '</text></g>';
    }).join("") +
    '<polyline class="chart-line historical" points="' + points(data.observed) + '"/>' +
    '<polyline class="chart-line predicted" points="' + points(data.forecast) + '"/>' +
    '<circle class="chart-runner" cx="' + chartX(first[0]) + '" cy="' + chartY(first[1]) + '" r="9" fill="#e3d1ff"/>' +
    '<g class="chart-tip" transform="translate(' + chartX(lastDay) + ' ' + (chartY(lastCpm) - 30) + ')">' +
      '<rect x="-64" y="-40" width="128" height="43" rx="12" fill="#e9dcff"/>' +
      '<text class="tip-value" x="0" y="-10" text-anchor="middle">' + decimal(lastCpm) + ' €</text></g>';
  const historyLine = chart.querySelector(".historical");
  const forecastLine = chart.querySelector(".predicted");
  const dashLength = forecastLine.getTotalLength();
  for (const line of [historyLine, forecastLine]) {
    line.style.strokeDasharray = line.getTotalLength();
    line.style.strokeDashoffset = line.getTotalLength();
  }

  window.__timelines = window.__timelines || {};
  const tl = gsap.timeline({ paused: true });
  window.__timelines["adera"] = tl;
  const scenes = [
    ["question", 0], ["brand", 9, "zoom"], ["dataset", 16],
    ["forecast", 27], ["events", 44], ["agents", 53, "vertical"],
    ["persona", 65, "fade"], ["feed", 76], ["audience", 95, "zoom"],
    ["signals", 104], ["interview", 112, "vertical"], ["dashboard", 127],
    ["end", 144, "fade"]
  ];
  for (const [i, [id, start, transition]] of scenes.entries()) {
    tl.addLabel(id, start);
    tl.fromTo("#" + id + " .orbit", { x: -35, y: 25, scale: .97 }, {
      x: 38, y: -20, scale: 1.04, duration: (scenes[i + 1]?.[1] ?? 150) - start, ease: "sine.inOut"
    }, start);
    if (!i) continue;
    const old = "#" + scenes[i - 1][0];
    const next = "#" + id;
    const ease = "power3.inOut";
    if (transition === "fade") {
      tl.fromTo(next, { opacity: 0, scale: 1.045 }, {
        opacity: 1, scale: 1, duration: .72, ease: "sine.inOut", immediateRender: false
      }, start);
      tl.set(old, { opacity: 0 }, start + .72);
    } else if (transition === "zoom") {
      tl.to(old, { scale: 1.14, duration: .66, ease }, start);
      tl.fromTo(next, { scale: .91, opacity: 0 }, { scale: 1, opacity: 1, duration: .66, ease, immediateRender: false }, start);
      tl.set(old, { opacity: 0 }, start + .66);
    } else {
      const axis = transition === "vertical" ? "yPercent" : "xPercent";
      tl.to(old, { [axis]: -100, duration: .55, ease }, start);
      tl.fromTo(next, { [axis]: 100, opacity: 1 }, { [axis]: 0, opacity: 1, duration: .55, ease, immediateRender: false }, start);
      tl.set(old, { opacity: 0 }, start + .55);
    }
  }

  // Entrances settle into the static layout; later movements carry the narrative.
  const reveal = (selector, at, motion, duration = .64, ease = "power3.out") =>
    tl.from(selector, { opacity: 0, duration, ease, ...motion }, at);
  const enterCopy = (id, at) => {
    reveal("#" + id + " .eyebrow", at + .17, { x: -36 }, .49, "sine.out");
    reveal("#" + id + " h2", at + .35, { y: 52 }, .8, "power4.out");
  };
  const brand = (id, at) => {
    reveal("#" + id + " .logo-symbol", at + .16, { y: 50, scale: .82 }, .91, "expo.out");
    reveal("#" + id + " .logo-type", at + .55, { y: 26 }, .72, "power3.out");
    reveal("#" + id + " .signature", at + 1.05, { scale: .96, y: 20 }, .85, "sine.out");
  };
  tl.from(".opening h1 span:first-child", { opacity: .87, y: 27, duration: .72, ease: "power4.out" }, .16);
  reveal(".opening h1 span:not(:first-child)", .64, { y: 76, stagger: .48 }, .79, "power4.out");
  reveal(".back-card", .81, { x: 150, rotation: 29, scale: .93 }, 1.02, "expo.out");
  reveal(".mid-card", 1.2, { x: 93, y: 118, rotation: -23 }, .92, "power3.out");
  reveal(".front-card", 1.61, { y: 142, rotation: 8 }, .92, "back.out(1.25)");
  tl.to(".open-deck", { y: -16, rotation: 2.2, duration: 3, ease: "sine.inOut" }, 3.9);
  tl.fromTo(".shimmer-sweep-target", { "--shimmer-pos": "-20%" }, {
    "--shimmer-pos": "120%", duration: 1.45, ease: "power2.inOut"
  }, 4.55);
  brand("brand", 9);
  tl.to("#brand .logo", { scale: 1.055, duration: 2.6, ease: "sine.inOut" }, 12.8);

  enterCopy("dataset", 16);
  reveal(".data-table", 16.5, { x: 85 }, .85, "expo.out");
  reveal("#kit-rows tr", 17.0, { x: 28, stagger: .23 }, .48, "power2.out");
  reveal(".row-count", 18.2, { y: 30, scale: .975 }, .75, "back.out(1.15)");
  tl.to(".data-table", { scale: .97, y: -8, duration: .85, ease: "sine.inOut" }, 22.5);
  tl.to("#kit-rows tr", { backgroundColor: "#f0e8ff", stagger: .12, duration: .43, ease: "power2.out" }, 22.58);
  reveal(".data-strip", 23.1, { y: 43, scaleX: .87 }, .78, "expo.out");
  tl.to(".data-strip strong", { x: 7, duration: .48, repeat: 1, yoyo: true, ease: "sine.inOut" }, 24.8);

  enterCopy("forecast", 27);
  reveal(".chart-plate", 27.45, { y: 58 }, .84, "expo.out");
  reveal(".legend span", 28.4, { x: 32, stagger: .27 }, .52, "sine.out");
  tl.to(historyLine, { strokeDashoffset: 0, duration: 2.05, ease: "power1.inOut" }, 28.8);
  tl.to(".chart-camera", { scale: 1.24, x: 89, y: 0, duration: 1.2, ease: "power2.inOut" }, 30.3);
  const trace = { fraction: 0 };
  tl.to(trace, { fraction: 1, duration: 6, ease: "none", onUpdate() {
    const point = forecastLine.getPointAtLength(trace.fraction * dashLength);
    const runner = chart.querySelector(".chart-runner");
    runner.setAttribute("cx", point.x);
    runner.setAttribute("cy", point.y);
    forecastLine.style.strokeDashoffset = dashLength * (1 - trace.fraction);
  } }, 31.5);
  tl.to(".chart-camera", { x: -123, duration: 6, ease: "none" }, 31.5);
  reveal(".chart-tip", 37.43, { y: 16, scale: .88 }, .55, "back.out(1.35)");
  tl.to(".chart-camera", { scale: 1, x: 0, y: 0, duration: 1.42, ease: "power3.inOut" }, 38.7);
  tl.from(".chart-date", { opacity: .35, stagger: .23, duration: .66, ease: "sine.out" }, 40.1);

  enterCopy("events", 44);
  reveal(".event-tile", 44.55, { y: 88, scale: .95, stagger: .34 }, .78, "expo.out");
  reveal(".model-row .model", 47.35, { x: 44, stagger: .25 }, .65, "power2.out");
  tl.to(".event-tile.feature", { y: -12, duration: .51, repeat: 1, yoyo: true, ease: "sine.inOut" }, 50.25);

  enterCopy("agents", 53);
  reveal(".agent-hub", 53.6, { scale: .74, y: -35 }, .86, "back.out(1.4)");
  reveal("#agents .bodycopy", 54.35, { x: -32 }, .64, "sine.out");
  const link = document.querySelector(".network-lines path");
  const linkLength = link.getTotalLength();
  link.style.strokeDasharray = linkLength;
  link.style.strokeDashoffset = linkLength;
  tl.to(link, { strokeDashoffset: 0, duration: 1.55, ease: "power2.inOut" }, 55.0);
  reveal(".network-lines circle", 55.41, { scale: .1, transformOrigin: "50% 50%" }, .55, "back.out(1.5)");
  reveal(".agent", 56.0, { y: 58, stagger: .58 }, .71, "expo.out");
  tl.to(".agent", { y: -12, stagger: .51, duration: .62, repeat: 1, yoyo: true, ease: "sine.inOut" }, 60.1);

  enterCopy("persona", 65);
  reveal(".persona-plate", 65.5, { x: 80, scale: .935 }, .92, "expo.out");
  reveal(".hero-portrait", 66.08, { y: 90 }, .91, "power4.out");
  reveal(".persona-meta > *", 67.02, { y: 23, stagger: .28 }, .62, "sine.out");
  tl.to(".hero-portrait", { scale: 1.08, y: 11, duration: 4.25, ease: "sine.inOut" }, 69.6);

  enterCopy("feed", 76);
  reveal(".feed-frame", 76.5, { x: 91, rotation: 5 }, .91, "back.out(1.15)");
  reveal(".ad-promo > *", 77.06, { y: 30, stagger: .19 }, .65, "power2.out");
  reveal(".feed-note:nth-child(1)", 78.95, { x: -35 }, .6, "sine.out");
  function swipe(card, nextCard, progress, time, direction) {
    const cue = document.querySelector(".swipe-cue");
    tl.fromTo(cue, { opacity: 0, x: -44 * direction, y: 25, scale: .72 }, {
      opacity: 1, x: 11 * direction, y: 0, scale: 1, duration: .36, ease: "power2.out", immediateRender: false
    }, time - .37);
    tl.fromTo(nextCard, { scale: .91, y: 21 }, { scale: 1, y: 0, duration: .68, ease: "power2.out", immediateRender: false }, time);
    tl.to(card, { x: 530 * direction, y: -63, rotation: 21 * direction, duration: .68, ease: "power3.inOut" }, time);
    tl.set(card, { opacity: 0 }, time + .68);
    tl.to(cue, { opacity: 0, x: 90 * direction, y: -30, duration: .5, ease: "power2.in" }, time);
    tl.to(".feed-progress i", { backgroundColor: "#c7b5e0", duration: .24 }, time);
    tl.to(".feed-progress i:nth-child(" + progress + ")", { backgroundColor: "#7046ce", duration: .24 }, time + .24);
    reveal(".feed-note:nth-child(" + progress + ")", time + .25, { x: -35 }, .61, "sine.out");
  }
  swipe(".ad-promo", ".ad-discount", 2, 82.5, 1);
  tl.to(".feed-frame", { rotation: -2, duration: 1.35, ease: "sine.inOut" }, 85.3);
  swipe(".ad-discount", ".ad-scarcity", 3, 88.45, -1);
  tl.to(".feed-frame", { scale: 1.028, y: -9, duration: 2.55, ease: "sine.inOut" }, 91.4);

  enterCopy("audience", 95);
  const heroCast = ".hero-cast";
  tl.from(".cast", { scale: 2.05, x: -270, y: -139, duration: 2.35, ease: "power3.inOut" }, 95.4);
  reveal(heroCast, 95.32, { scale: .86 }, .68, "back.out(1.35)");
  reveal(".cast-card:not(.hero-cast)", 96.11, { y: 42, scale: .93, stagger: { amount: 1.12, from: 6 } }, .69, "expo.out");
  tl.to(".cast", { y: -12, scale: 1.025, duration: 2.4, ease: "sine.inOut" }, 100.8);

  enterCopy("signals", 104);
  reveal(".doc", 105.45, { scale: .65, y: 48 }, .86, "expo.out");
  reveal(".doc-fold", 105.85, { scale: .4, transformOrigin: "100% 0" }, .67, "back.out(1.25)");
  const chipPositions = [[-174,-125], [360,-143], [-169,155], [364,155]];
  chipPositions.forEach(([x, y], i) => {
    const chip = ".signal-chip:nth-of-type(" + (i + 2) + ")";
    const start = 104.61 + i * .15;
    tl.fromTo(chip, { x, y: y + 34, scale: .58, opacity: 0 }, {
      x, y, scale: 1, opacity: 1, duration: .49, ease: "back.out(1.1)"
    }, start);
    tl.to(chip, { x: 107, y: -35 + i * 24, scale: .28, opacity: 0, duration: .68, ease: "power3.in" }, 106.12 + i * .22);
  });
  reveal(".signal-rows > div", 106.85, { x: 29, stagger: .23 }, .65, "sine.out");
  tl.to(".doc", { y: -11, duration: 1.05, ease: "sine.inOut" }, 109.15);

  enterCopy("interview", 112);
  reveal(".interview-marks span", 113.65, { y: 24, stagger: .22 }, .64, "back.out(1.2)");
  reveal(".lead-question", 114.17, { x: 67, scale: .97 }, .75, "expo.out");
  tl.to(".conversation", { x: 12, duration: 1.15, ease: "sine.inOut" }, 116.35);
  reveal(".follow-question:nth-child(2)", 118.1, { x: -54 }, .76, "power3.out");
  tl.to(".conversation", { x: 0, duration: 1.15, ease: "sine.inOut" }, 120.2);
  reveal(".follow-question:nth-child(3)", 122.1, { y: 49, scale: .96 }, .81, "power3.out");
  tl.to(".conversation", { y: -13, duration: 1.4, ease: "sine.inOut" }, 124.3);

  enterCopy("dashboard", 127);
  reveal(".dash-viewport", 127.65, { y: 77, scale: .98 }, .94, "expo.out");
  reveal(".pan-arrow", 128.19, { x: 35 }, .65, "back.out(1.2)");
  for (const [time, x] of [[132.0, -925], [137.8, -1865]]) {
    tl.to(".pan-arrow", { x: -22, duration: .37, repeat: 1, yoyo: true, ease: "sine.inOut" }, time - .37);
    tl.to(".dash-reel", { x, duration: 1.22, ease: "power3.inOut" }, time);
  }
  tl.to(".dash-frame:nth-child(2) img", { scale: 1.038, transformOrigin: "35% 20%", duration: 2.3, ease: "sine.inOut" }, 134.5);
  tl.to(".dash-frame:nth-child(3) img", { scale: 1.037, transformOrigin: "50% 20%", duration: 2.4, ease: "sine.inOut" }, 140.65);
  brand("end", 144);
  tl.to("#end .logo", { scale: 1.035, duration: 2.9, ease: "sine.inOut" }, 146.5);
})();
