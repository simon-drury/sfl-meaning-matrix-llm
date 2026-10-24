# Meaning-state dashboard verification

## Scope

Verified the interactive dashboard in `index.html`. The separate `meaning-state.html` research figure was not changed. Both transposed tables and their shared row-major coordinate mapping remain intact; no row, column, or diagonal totals are enforced.

## Automated coverage

`node --test tests/meaning-dashboard.test.js` — **5 tests passed, 0 failed, 0 skipped**.

- Sanitization: absent entries, non-arrays, `null`, strings, `NaN`, infinities, negatives, and values above 1; verifies the existing upper clamp and initial-distribution zero-vector fallback.
- Slider redistribution: preserves the edited coordinate, redistributes remaining mass, and tests all nine one-hot states when the selected coordinate is moved to zero.
- Reset and Normalize State: verifies unit-sum state and synchronized output.
- Deterministic randomized sequence: 1,500 programmatic setter and slider updates; checks every coordinate, total, both table views, vector, slider, and label after every update.
- Headless Chromium interaction/render check: exercises the public setter, a real slider input event, both table views, vector and label readouts, total, reset, and nonzero dashboard layout.

An independent verifier inspected the actual diff and ran a separate inline Node/VM adversarial harness (`node <<'NODE'`) for **50,000 deterministic setter/slider transitions**, also checking malformed values, typed arrays, zero and all one-hot states, and synchronized rendering. It reports no remaining findings. The verifier's full dashboard suite, including Chromium, passed as well.

## Tooling, limitations, and findings

- `git diff --check` passed.
- The Chromium smoke test uses local files, disables background networking, and blocks external Google font hosts. It verifies DOM interactions and element layout, not external font loading, screenshot-level styling, or other browser engines.
- No coverage instrumentation or JavaScript package/test runner existed; the reported coverage is the explicit case and transition coverage above, not a percentage.
- The independent verifier attempted `python test_pipeline.py`, but it could not run because `torch` is unavailable in the environment. That pipeline is unrelated to the dashboard changes.
- CodeQL initially flagged the test's lowercase-only script-tag extractor. It was made case-insensitive; the subsequent CodeQL run reported **0 alerts**.
