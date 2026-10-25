(() => {
  'use strict';
  const $ = (id) => document.getElementById(id);
  const defaults = window.PHISHGUARD_CONFIG || {};
  const storageKey = 'phishguard-appearance-v2';
  let saved = {};
  try { saved = JSON.parse(localStorage.getItem(storageKey) || '{}') || {}; } catch (_) {}
  let config = { ...defaults, theme: saved.theme ?? defaults.theme, grid: typeof saved.grid === 'boolean' ? saved.grid : defaults.grid };
  let lenis = null;
  let animationTimer = null;
  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const gsapReady = () => typeof window.gsap !== 'undefined';
  const css = (name, value) => document.documentElement.style.setProperty(name, value);
  const safeHex = (v) => /^#[0-9a-fA-F]{6}$/.test(v) ? v : '#466457';

  function persist() {
    localStorage.setItem(storageKey, JSON.stringify({ theme: config.theme, grid: config.grid }));
  }
  function updateLenis() {
    if (lenis) { lenis.destroy(); lenis = null; }
    if (config.smoothScroll && !reducedMotion && window.Lenis) {
      lenis = new window.Lenis({ autoRaf: true, duration: 1.15, smoothWheel: true });
    }
  }
  function applySettings({ initialize = false } = {}) {
    document.body.dataset.theme = ['paper','noir','acid'].includes(config.theme) ? config.theme : 'paper';
    css('--accent', safeHex(config.accent));
    css('--motion', Math.max(0, Math.min(1, Number(config.motion) / 100)));
    // Trusted local settings only: never insert user-submitted URLs or API content as HTML.
    $('heroTitle').innerHTML = config.headline || defaults.headline;
    $('gridField').hidden = !config.grid;
    document.querySelector('.grain').hidden = !config.grain;
    $('cursorOrb').hidden = !config.cursor || reducedMotion;
    $('themeSelect').value = config.theme;
    $('gridToggle').checked = !!config.grid;
    if (!initialize) { updateLenis(); document.dispatchEvent(new Event('phishguard:theme')); }
  }
  function openSettings() {
    $('settingsPanel').hidden = false;
    $('settingsBackdrop').hidden = false;
    document.body.style.overflow = 'hidden';
    $('settingsClose').focus();
  }
  function closeSettings() {
    $('settingsPanel').hidden = true;
    $('settingsBackdrop').hidden = true;
    document.body.style.overflow = '';
    $('settingsOpen').focus();
  }
  $('settingsOpen').addEventListener('click', openSettings);
  $('settingsClose').addEventListener('click', closeSettings);
  $('settingsBackdrop').addEventListener('click', closeSettings);
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && !$('settingsPanel').hidden) closeSettings(); });
  $('themeSelect').addEventListener('change', (event) => {
    config.theme = event.target.value;
    applySettings();
    persist();
  });
  $('gridToggle').addEventListener('change', (event) => {
    config.grid = event.target.checked;
    applySettings();
    persist();
  });

  // Cursor halo + interactive generative light on dot grid. Never blocks clicks.
  let mouseX = -1000, mouseY = -1000, currentX = -1000, currentY = -1000;
  document.addEventListener('pointermove', (e) => {
    if (e.pointerType === 'touch') return;
    mouseX = e.clientX; mouseY = e.clientY;
    const bounds = $('gridField').getBoundingClientRect();
    $('gridField').style.setProperty('--mouse-x', `${e.clientX - bounds.left}px`);
    $('gridField').style.setProperty('--mouse-y', `${e.clientY - bounds.top}px`);
    if (config.cursor && !reducedMotion) $('cursorOrb').style.opacity = '1';
  }, { passive: true });
  function tickCursor() {
    const k = .08 + Number(config.motion) / 100 * .13;
    currentX += (mouseX - currentX) * k;
    currentY += (mouseY - currentY) * k;
    $('cursorOrb').style.left = `${currentX}px`;
    $('cursorOrb').style.top = `${currentY}px`;
    requestAnimationFrame(tickCursor);
  }
  if (!reducedMotion) tickCursor();

  function initMotion() {
    if (!gsapReady() || reducedMotion || Number(config.motion) === 0) return;
    window.gsap.from('.topbar > *', { opacity: 0, y: -18, duration: .8, stagger: .09, ease: 'power3.out' });
    window.gsap.from('.hero-title-wrap', { opacity: 0, y: 60, duration: 1.15, delay: .15, ease: 'power4.out' });
    window.gsap.from('.hero-description, #scanForm', { opacity: 0, y: 22, duration: .8, delay: .6, stagger: .12 });
    if (window.ScrollTrigger) {
      window.gsap.registerPlugin(window.ScrollTrigger);
      document.querySelectorAll('[data-reveal]:not(.hero-title-wrap)').forEach((node) => {
        window.gsap.from(node, { opacity: 0, y: 45, duration: 1.0, ease: 'power3.out', scrollTrigger: { trigger: node, start: 'top 88%', once: true } });
      });
    }
  }

  function setBusy(busy) {
    $('checkButton').disabled = busy;
    $('checkLabel').textContent = busy ? 'READING' : 'CHECK';
    $('urlInput').disabled = busy;
  }
  function addItems(id, items, emptyText) {
    const root = $(id);
    root.replaceChildren();
    const values = Array.isArray(items) && items.length ? items : [emptyText];
    for (const text of values) {
      const li = document.createElement('li');
      li.textContent = String(text);
      root.appendChild(li);
    }
  }
  function renderResult(data) {
    const rawScore = Number(data.risk_score);
    const score = Number.isFinite(rawScore) ? Math.max(0, Math.min(100, Math.round(rawScore))) : null;
    $('riskNumber').textContent = score === null ? '—' : score;
    $('riskPill').textContent = `${String(data.risk_level || 'UNRATED').toUpperCase()} / RISK`;
    $('verdictText').textContent = data.prediction === 1 ? 'Potential phishing.' : data.prediction === 0 ? 'Predicted legitimate.' : 'Assessment unavailable.';
    $('reportUrl').textContent = data.url || '';
    $('reportModel').textContent = `MODEL / ${data.model_name || 'UNKNOWN'}`;
    $('reportMode').textContent = `MODE / ${data.analysis_mode || 'URL-ONLY'}`;
    $('resultTimestamp').textContent = `GENERATED / ${new Date().toLocaleString()}`;
    addItems('indicatorList', data.indicators, 'No rule-based indicators flagged. This does not guarantee safety.');
    addItems('recommendationList', data.recommendations, 'Verify the destination independently before sharing sensitive information.');
    const features = $('featureList'); features.replaceChildren();
    for (const [name, value] of Object.entries(data.features || {})) {
      const cell = document.createElement('div'); cell.className = 'feature-cell';
      const label = document.createElement('span'); label.textContent = name.replaceAll('_', ' ').toUpperCase();
      const number = document.createElement('strong'); number.textContent = String(value);
      cell.append(label, number); features.appendChild(cell);
    }
    $('resultSection').hidden = false;
    if (gsapReady() && !reducedMotion && Number(config.motion) > 0) {
      window.gsap.from('#resultSection .result-main > *', { opacity: 0, y: 25, stagger: .12, duration: .75, ease: 'power2.out' });
    }
    $('resultSection').scrollIntoView({ behavior: reducedMotion ? 'instant' : 'smooth', block: 'start' });
  }
  function startScanAnimation() {
    $('scanOverlay').hidden = false;
    $('scanProgress').style.width = '0%';
    requestAnimationFrame(() => { $('scanProgress').style.width = '90%'; });
    let i = 0;
    const phrases = Array.isArray(config.scanPhrases) && config.scanPhrases.length ? config.scanPhrases : defaults.scanPhrases;
    $('scanPhrase').textContent = phrases[0];
    animationTimer = setInterval(() => { i = (i + 1) % phrases.length; $('scanPhrase').textContent = phrases[i]; }, 650);
  }
  function stopScanAnimation() {
    clearInterval(animationTimer);
    $('scanProgress').style.width = '100%';
    $('scanOverlay').hidden = true;
  }
  async function requestAnalysis(url) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 20000);
    try {
      const endpoint = String(config.apiEndpoint || '/analyze').trim();
      const response = await fetch(endpoint, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ url }), signal: controller.signal });
      let payload;
      try { payload = await response.json(); } catch (_) { throw new Error('The server returned an unreadable response.'); }
      if (!response.ok) throw new Error(typeof payload.detail === 'string' ? payload.detail : `Server error (${response.status})`);
      if (typeof payload !== 'object' || !payload || !('prediction' in payload)) throw new Error('The response does not match the expected PhishGuard API.');
      return payload;
    } catch (error) {
      if (error.name === 'AbortError') throw new Error('The request timed out. Check the backend server.');
      if (error instanceof TypeError) throw new Error('Cannot reach the API. Start FastAPI and open this site through the same server.');
      throw error;
    } finally { clearTimeout(timeout); }
  }
  $('scanForm').addEventListener('submit', async (event) => {
    event.preventDefault();
    $('errorMessage').hidden = true;
    const url = $('urlInput').value.trim();
    try {
      const parsed = new URL(url);
      if (!['http:', 'https:'].includes(parsed.protocol) || !parsed.hostname) throw new Error('Enter a complete HTTP or HTTPS URL.');
      if (url.length > 4096) throw new Error('This URL is too long.');
    } catch (error) {
      $('errorMessage').textContent = error instanceof TypeError ? 'Enter a complete URL beginning with https:// or http://.' : error.message;
      $('errorMessage').hidden = false;
      return;
    }
    setBusy(true); $('resultSection').hidden = true;
    startScanAnimation();
    const started = performance.now();
    try {
      const report = await requestAnalysis(url);
      const minimum = reducedMotion ? 0 : Number(config.scanMinDurationMs || 0);
      await new Promise((resolve) => setTimeout(resolve, Math.max(0, minimum - (performance.now() - started))));
      stopScanAnimation();
      renderResult(report);
    } catch (error) {
      stopScanAnimation();
      $('errorMessage').textContent = error.message || 'Analysis failed.';
      $('errorMessage').hidden = false;
    } finally { setBusy(false); }
  });
  $('scanAgain').addEventListener('click', () => { $('urlInput').value = ''; $('resultSection').hidden = true; $('scanner').scrollIntoView({ behavior: reducedMotion ? 'instant' : 'smooth' }); $('urlInput').focus({ preventScroll: true }); });
  // Creative interaction 01: particle grid that bends toward the pointer.
  function initSignalGrid() {
    const canvas = $('signalGrid');
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    let w = 0, h = 0, dpr = 1;
    let px = -1000, py = -1000;
    const field = $('gridField');
    function resize() {
      const r = field.getBoundingClientRect();
      w = r.width; h = r.height;
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = Math.round(w * dpr);
      canvas.height = Math.round(h * dpr);
      canvas.style.width = w + 'px'; canvas.style.height = h + 'px';
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      draw();
    }
    function draw() {
      ctx.clearRect(0, 0, w, h);
      if (!config.grid) return;
      const color = getComputedStyle(document.body).getPropertyValue('--ink').trim();
      const accent = getComputedStyle(document.body).getPropertyValue('--accent').trim();
      const step = w < 600 ? 32 : 29;
      for (let y = step / 2; y < h; y += step) {
        for (let x = step / 2; x < w; x += step) {
          const dx = x - px, dy = y - py, dist = Math.hypot(dx, dy);
          const reach = 185, influence = Math.max(0, 1 - dist / reach);
          const offset = influence * influence * 15;
          const ox = dist ? dx / dist * offset : 0;
          const oy = dist ? dy / dist * offset : 0;
          ctx.beginPath();
          ctx.arc(x + ox, y + oy, 1 + influence * 2.1, 0, Math.PI * 2);
          ctx.fillStyle = influence > .25 ? accent : color;
          ctx.globalAlpha = .12 + influence * .53;
          ctx.fill();
        }
      }
      ctx.globalAlpha = 1;
    }
    document.addEventListener('pointermove', (e) => {
      if (e.pointerType === 'touch' || !config.grid) return;
      const r = field.getBoundingClientRect();
      px = e.clientX - r.left; py = e.clientY - r.top;
      draw();
    }, { passive: true });
    window.addEventListener('resize', resize, { passive: true });
    document.addEventListener('phishguard:theme', draw);
    resize();
  }

  // Creative interaction 02: restrained water ripples following hover/focus on the scanner.
  function initWater() {
    const wrap = $('inputWrap');
    let last = 0;
    function ripple(e) {
      if (reducedMotion || performance.now() - last < 95) return;
      last = performance.now();
      const rect = wrap.getBoundingClientRect();
      const x = e.clientX - rect.left, y = e.clientY - rect.top;
      const ring = document.createElement('span');
      ring.className = 'water-ring';
      ring.style.left = x + 'px'; ring.style.top = y + 'px';
      $('waterLayer').appendChild(ring);
      ring.addEventListener('animationend', () => ring.remove(), { once: true });
    }
    wrap.addEventListener('pointermove', (e) => { if (e.pointerType !== 'touch') ripple(e); }, { passive: true });
  }

  // Creative interaction 03: ASCII-style input monitor, based on actual entered characters.
  function initAscii() {
    const input = $('urlInput');
    const output = $('asciiMonitor');
    function update() {
      const raw = input.value;
      const symbols = ' .:+=*#%@';
      const length = 52;
      let line = '';
      for (let i = 0; i < length; i++) {
        if (i >= raw.length) { line += '·'; continue; }
        line += symbols[raw.charCodeAt(i) % symbols.length];
      }
      output.textContent = line;
    }
    input.addEventListener('input', update);
    $('scanAgain').addEventListener('click', update);
    update();
  }

  // Creative interaction 04: hanging assessment panel with gentle pointer parallax.
  function initHangingCard() {
    const card = $('scoreCard');
    if (reducedMotion) return;
    card.addEventListener('pointermove', (e) => {
      if (e.pointerType === 'touch') return;
      const r = card.getBoundingClientRect();
      const tilt = ((e.clientX - r.left) / r.width - .5) * 5;
      card.style.setProperty('--card-tilt', tilt.toFixed(2) + 'deg');
    }, { passive: true });
    card.addEventListener('pointerleave', () => card.style.setProperty('--card-tilt', '0deg'));
  }

  applySettings({ initialize: true });
  initSignalGrid();
  initWater();
  initAscii();
  initHangingCard();
  updateLenis();
  initMotion();
})();
