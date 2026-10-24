const assert = require('node:assert/strict');
const { execFileSync, spawnSync } = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');

const repository = path.resolve(__dirname, '..');
const pagePath = path.join(repository, 'index.html');
const html = fs.readFileSync(pagePath, 'utf8');
const script = html.match(/<script>([\s\S]*?)<\/script>/)[1];
const initial = [0.25, 0.10, 0.05, 0.15, 0.20, 0.05, 0.05, 0.05, 0.10];

function createDashboard() {
  const elements = new Map();
  const sliders = [];
  const makeElement = () => ({
    textContent: '',
    value: '',
    style: { setProperty() {} },
    listeners: {},
    addEventListener(type, callback) {
      this.listeners[type] = callback;
    },
    dispatch(type) {
      this.listeners[type]({ target: this });
    }
  });

  for (let index = 0; index < 9; index += 1) {
    for (const prefix of ['cell-m0-', 'cell-m1-']) {
      const cell = makeElement();
      cell.valueElement = makeElement();
      elements.set(`${prefix}${index}`, cell);
    }
    for (const prefix of ['vec-', 'sval-', 'slider-']) {
      elements.set(`${prefix}${index}`, makeElement());
    }
    sliders.push(elements.get(`slider-${index}`));
  }
  for (const id of ['total-potential', 'btn-normalize', 'btn-reset']) {
    elements.set(id, makeElement());
  }

  const document = {
    getElementById(id) {
      return elements.get(id);
    },
    querySelector(selector) {
      const match = selector.match(/^#(cell-m[01]-\d) \.cell-value$/);
      return match && elements.get(match[1]).valueElement;
    },
    querySelectorAll(selector) {
      return selector === '.lumi-slider' ? sliders : [];
    }
  };
  const window = {};
  vm.runInNewContext(script, { document, window, Array, Number, Math });
  return { document, elements, window, sliders };
}

function assertState(state) {
  assert.equal(state.length, 9);
  for (const value of state) {
    assert.equal(Number.isFinite(value), true);
    assert.ok(value >= 0 && value <= 1, `coordinate ${value} outside [0, 1]`);
  }
  assert.ok(Math.abs(state.reduce((sum, value) => sum + value, 0) - 1) < 1e-12);
}

function assertValuesClose(actual, expected) {
  assert.equal(actual.length, expected.length);
  actual.forEach((value, index) => {
    assert.ok(Math.abs(value - expected[index]) < 1e-12, `coordinate ${index}: ${value}`);
  });
}

function assertRendered(dashboard, state) {
  assert.equal(
    dashboard.elements.get('total-potential').textContent,
    state.reduce((sum, value) => sum + value, 0).toFixed(4)
  );
  state.forEach((value, index) => {
    const rendered = value.toFixed(3);
    assert.equal(dashboard.elements.get(`cell-m0-${index}`).valueElement.textContent, rendered);
    assert.equal(dashboard.elements.get(`cell-m1-${index}`).valueElement.textContent, rendered);
    assert.equal(dashboard.elements.get(`vec-${index}`).textContent, rendered);
    assert.equal(dashboard.elements.get(`sval-${index}`).textContent, rendered);
    assert.equal(Number(dashboard.elements.get(`slider-${index}`).value), value);
  });
}

test('setter sanitizes, clamps, normalizes, and uses the initial zero-vector fallback', () => {
  const dashboard = createDashboard();
  assertState(dashboard.window.setMeaningState([2, -1, 0, 0, 0, 0, 0, 0, 0]));
  assertState(dashboard.window.setMeaningState([0, 0, 0, 0, 0, 0, 0, 0, 0]));
  assert.deepEqual(
    Array.from(dashboard.window.setMeaningState([0, 0, 0, 0, 0, 0, 0, 0, 0])),
    initial
  );

  const sanitized = dashboard.window.setMeaningState([
    Number.NaN, Number.POSITIVE_INFINITY, Number.NEGATIVE_INFINITY, -2, 2, null, '0.2'
  ]);
  assertState(sanitized);
  assertValuesClose(Array.from(sanitized), Array.from(dashboard.window.setMeaningState([
    0.25, 0.1, 0.05, 0, 1, 0.05, 0.05, 0.05, 0.1
  ])));
  assertValuesClose(Array.from(dashboard.window.setMeaningState(null)), initial);
});

test('slider edits preserve the dragged coordinate, redistribute mass, and handle one-hot states', () => {
  const dashboard = createDashboard();
  for (let index = 0; index < 9; index += 1) {
    const oneHotInput = Array(9).fill(0);
    oneHotInput[index] = 1;
    const oneHot = dashboard.window.setMeaningState(oneHotInput);
    assert.deepEqual(Array.from(oneHot), oneHotInput);

    oneHotInput[index] = 0;
    const redistributed = dashboard.window.setMeaningState(oneHotInput, index);
    assert.equal(redistributed[index], 0);
    assertState(redistributed);
  }

  dashboard.sliders[4].value = '0.73';
  dashboard.sliders[4].dispatch('input');
  let state = dashboard.sliders.map(slider => Number(slider.value));
  assert.equal(state[4], 0.73);
  assertState(state);
  assertRendered(dashboard, state);

  dashboard.sliders[4].value = '1';
  dashboard.sliders[4].dispatch('input');
  state = dashboard.sliders.map(slider => Number(slider.value));
  assert.deepEqual(Array.from(state), [0, 0, 0, 0, 1, 0, 0, 0, 0]);

  dashboard.sliders[4].value = '0.3';
  dashboard.sliders[4].dispatch('input');
  state = dashboard.sliders.map(slider => Number(slider.value));
  assert.equal(state[4], 0.3);
  assertState(state);
  assertRendered(dashboard, state);
});

test('reset and normalize actions always commit a synchronized unit-sum state', () => {
  const dashboard = createDashboard();
  dashboard.window.setMeaningState([0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09]);
  dashboard.elements.get('btn-normalize').dispatch('click');
  let state = dashboard.sliders.map(slider => Number(slider.value));
  assertState(state);
  assertRendered(dashboard, state);

  dashboard.window.setMeaningState([0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]);
  dashboard.elements.get('btn-reset').dispatch('click');
  state = dashboard.sliders.map(slider => Number(slider.value));
  assertValuesClose(state, initial);
  assertState(state);
  assertRendered(dashboard, state);
  assert.doesNotMatch(html, /auto-norm-toggle|Auto-normalize/);
});

test('randomized setter and slider sequences preserve the invariant and every rendered view', () => {
  const dashboard = createDashboard();
  let seed = 0x51f15e;
  const random = () => {
    seed = (seed * 1664525 + 1013904223) >>> 0;
    return seed / 0x100000000;
  };

  for (let step = 0; step < 1500; step += 1) {
    let state;
    if (step % 3 === 0) {
      const values = Array.from({ length: Math.floor(random() * 13) }, () => {
        const choice = Math.floor(random() * 12);
        if (choice === 0) return Number.NaN;
        if (choice === 1) return Number.POSITIVE_INFINITY;
        if (choice === 2) return null;
        if (choice === 3) return 'invalid';
        return random() * 4 - 1.5;
      });
      state = dashboard.window.setMeaningState(values);
    } else {
      const index = Math.floor(random() * 9);
      dashboard.sliders[index].value = String(random() * 1.4 - 0.2);
      dashboard.sliders[index].dispatch('input');
      state = dashboard.window.setMeaningState(
        dashboard.sliders.map(slider => Number(slider.value))
      );
    }
    assertState(state);
    assertRendered(dashboard, state);
  }
});

test('dashboard interactions and rendering work in headless Chromium', { skip: !findChromium() }, () => {
  const chromium = findChromium();
  const temporaryDirectory = fs.mkdtempSync('/tmp/meaning-dashboard-');
  const harnessPath = path.join(temporaryDirectory, 'browser-test.html');
  const pageUrl = `file://${pagePath}`;
  fs.writeFileSync(harnessPath, `<!doctype html>
    <iframe id="dashboard" src="${pageUrl}" style="width:100%;height:1200px;border:0"></iframe>
    <pre id="result">waiting</pre>
    <script>
      const frame = document.getElementById('dashboard');
      frame.addEventListener('load', () => {
        try {
          const page = frame.contentWindow;
          const doc = page.document;
          const check = (condition, message) => { if (!condition) throw new Error(message); };
          const values = page.setMeaningState([1, 0, 0, 0, 0, 0, 0, 0, 0]);
          check(values[0] === 1 && values.slice(1).every(value => value === 0), 'one-hot setter');
          const slider = doc.getElementById('slider-4');
          slider.value = '0.4';
          slider.dispatchEvent(new page.Event('input', { bubbles: true }));
          const edited = page.setMeaningState(Array.from({ length: 9 }, (_, i) =>
            Number(doc.getElementById('slider-' + i).value)));
          check(Math.abs(edited[4] - 0.4) < 1e-12, 'slider preserves dragged coordinate');
          check(Math.abs(edited.reduce((sum, value) => sum + value, 0) - 1) < 1e-12, 'slider sum');
          check(doc.querySelector('#cell-m0-4 .cell-value').textContent ===
            doc.querySelector('#cell-m1-4 .cell-value').textContent, 'transposed matrix sync');
          check(doc.getElementById('vec-4').textContent === doc.getElementById('sval-4').textContent,
            'vector and label sync');
          check(doc.getElementById('total-potential').textContent === '1.0000', 'total readout');
          const card = doc.querySelector('.sfl-card').getBoundingClientRect();
          check(card.width > 0 && card.height > 0, 'dashboard has visible layout');
          doc.getElementById('btn-reset').click();
          check(doc.getElementById('total-potential').textContent === '1.0000', 'reset total');
          document.getElementById('result').textContent = 'PASS: slider, setter, matrices, readouts, reset, and layout';
        } catch (error) {
          document.getElementById('result').textContent = 'FAIL: ' + error.stack;
        }
      });
    </script>`);

  try {
    const output = execFileSync(chromium, [
      '--headless', '--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage',
      '--disable-background-networking',
      '--host-resolver-rules=MAP fonts.googleapis.com ~NOTFOUND,MAP fonts.gstatic.com ~NOTFOUND',
      '--allow-file-access-from-files', '--dump-dom', '--virtual-time-budget=2000',
      `file://${harnessPath}`
    ], { encoding: 'utf8', timeout: 15000, stdio: ['ignore', 'pipe', 'pipe'] });
    assert.match(output, /PASS: slider, setter, matrices, readouts, reset, and layout/);
  } finally {
    fs.rmSync(temporaryDirectory, { recursive: true, force: true });
  }
});

function findChromium() {
  for (const candidate of ['chromium', 'chromium-browser', 'google-chrome']) {
    const result = spawnSync('sh', ['-c', `command -v ${candidate}`], { encoding: 'utf8' });
    if (result.status === 0) return result.stdout.trim();
  }
  return null;
}
