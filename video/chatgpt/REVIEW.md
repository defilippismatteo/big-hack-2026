# ADERA — final review

Implementation: gpt-6.1-sol, low reasoning. Reanimate local workflow; 2 implementation rounds. No delegated agent, HeyGen, Reverse service, HyperFrames command or model API.

## Delivered film

`ADERA-150s.mp4`: 150.000 seconds, 1920×1080, 30 fps, 4500 frames, H.264/yuv420p; no audio and no subtitle track. Standalone editable HTML and all local assets accompany it.

## Fidelity verdict: mixed, PARTIAL overall

Full reference sheet and detailed opening/persona/feed/ending sheets inspected. Sequence roles, alternating backgrounds, left typography / right card compositions and report progression inform this adaptation. ADERA adds forecast, orchestration, swipe, signal convergence, interviews and dashboard. The film is not a globally timing-identical or pixel-identical clone.

Opening reference 0–2.1s → ADERA 0–2.1s is the quantitatively verified microsequence. Native 30 fps images supply five normalized ink curves; the clone reproduces those curves over different phrases. Independent clone screenshot glyph masks verify the rendered result. Thresholds: 5%/95% ink progress; ±80 ms start/end/duration; curve RMSE ≤0.05. One frame is 33.33 ms, so a measured 0 ms is equality at this sampling resolution, not sub-frame proof. Masks exclude line-box overlap (24px top, 20px bottom); an initial false early onset from a neighbouring line was corrected in the measurement crop, without changing the animation or threshold.

| ADERA phrase | timing error start/end/duration | normalized ink RMSE | result |
|---|---|---|---|
| E se | 0 / 0 / 0 ms | 0.000437 | pass |
| potessi testare | 0 / 0 / 0 ms | 0.000538 | pass |
| una campagna | 0 / 0 / 0 ms | 0.000582 | pass |
| prima di | 0 / 0 / 0 ms | 0.000342 | pass |
| investirci? | 0 / 0 / 0 ms | 0.000509 | pass |

All five have correct order and frame-level gaps. Easing is a sampled measured ink curve, not an assumed named CSS family. Reference text remains stationary; clone text remains stationary. This pass covers opacity/sequence only. Font, phrase widths, line breaks and title layout are intentionally adapted and are not a proof of identical composition.

Raw whole-frame mismatch for this opening is 7.54% at 384×216 with a 10% channel-difference threshold. This diagnostic includes different content, layout, colours and reference subtitles. It is not a pass criterion or a claim of film similarity.

## Residuals and limitations

- Right campaign card uses a 400ms ease-out, +70px Y entrance mapped around reference 2.4s; exact reference travel/easing was not recovered, so no ±80ms pass is claimed.
- Persona, feed, report and final brand scenes preserve broad reference roles; their internal stagger/easing and normalized travel distances were not independently tracked. They remain unverified, not passed. Reference persona 20–25s → ADERA 65–76s; reference feed 28–32s → ADERA 76–95s; reference report 34–40s → ADERA 104–127s; reference ending 54–57s → ADERA 144–150s.
- New scene durations and reading holds differ substantially from the 60.7s reference. Swipe, camera-follow chart, zoom-out and signal convergence are ADERA additions, not claimed reference clones.
- Chart uses saved FGR-AD09 CPM forecast 16–30 Nov. No supported daily history is plotted and no historical gap or peak is invented. Event labels mark calendar dates; they do not cause the curve.
- Ads are HTML reconstructions from kit descriptions, clearly labelled illustrative; these are not original stimuli. Chiara probabilities shown only for FGR-U3: 46.75% scroll, 26.21% glance, 16.97% stop, 10.08% click. No action draw is represented as a recorded user event.
- Ten distinct illustration crops are illustrative, not identities inferred from appearance. Eight faint repeated crops indicate a larger pool; count 600 comes from the saved library. Alpha is real in the used source; magenta edge cleanup is heuristic and cannot guarantee perfect hair edges under every background.
- Interview question is editorial; its two quoted replies are literal saved excerpts, not newly generated answers. Synthetic nature is stated in primary scene labels. No footer disclaimer.
- Dashboard is a real offline capture of current preview.html overview. It is a screenshot in the video, not an interactive dashboard inside the film.
- Skill setup could not use Bun because it is absent. Local Playwright/ffmpeg and Python/Pillow/NumPy implement capture/build/verify/render instead. No persistent server was launched.

## Evidence

- `.reanimate/adera-sol61-low/spec.md`: scope before capture, maps and timeline.
- `reference-sheet.jpg`, `reference-opening.jpg`, `reference-persona-feed.jpg`, `reference-ending.jpg`: inspected reference sheets.
- `ref-opening/`: 63 native 30 fps reference frames.
- `clone-1/sheet.jpg`: first visual round; `clone-1/*.png` were refreshed by final render for scene checks.
- `clone-2/frames/`, `clone-2/track.json`: final opening capture and DOM opacity track.
- `compare-2/comparison-01.jpg` through `comparison-03.jpg`, `compare-2/report.json`: same-time side-by-side evidence and measurements.
- `final-filmstrip.jpg`, `final-probe.json`, `browser-errors.json`: final film QC. Browser errors: zero.

Source paths, SHA-256 hashes, actual model and processing notes are in `manifest.json`. All writes were confined to the two assigned directories; pre-existing changes elsewhere were left alone.

Final QC: full H.264 decode completed with exit 0; final contact sheet inspected. Metadata confirmed 150.000s, 1920×1080, 30/1 fps, 4500 frames and exactly one video stream. MP4 SHA-256: `83144ea7991259778c0ba8eb4a317364f7409ddce1e96b4f8bdf774d49b424ac`.
