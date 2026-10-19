(() => {
  'use strict';
  const $ = (id) => document.getElementById(id);
  const state = { bits: [], capacity: 10000, hashCount: 7, positions: [], bitValues: [], changedPositions: [] };
  const checkForm = $('check-form');
  const emailInput = $('email-input');
  const checkButton = $('check-button');

  function formatNumber(value) { return Number(value || 0).toLocaleString('en-US'); }
  function formatPercent(value, digits = 2) { return `${Number(value || 0).toFixed(digits)}%`; }
  function safeText(value) { return String(value ?? ''); }

  async function api(url, options = {}) {
    const response = await fetch(url, { headers: { 'Content-Type': 'application/json', ...(options.headers || {}) }, ...options });
    let payload;
    try { payload = await response.json(); } catch { throw new Error('The server returned an unreadable response.'); }
    if (!response.ok) throw new Error(payload.error || 'The request could not be completed.');
    return payload;
  }

  function setBackend(connected) {
    const badge = $('backend-status');
    badge.classList.toggle('offline', !connected);
    badge.innerHTML = `<span></span>${connected ? 'Connected' : 'Connection issue'}`;
  }

  async function loadStats() {
    try {
      const stats = await api('/api/stats');
      setBackend(true);
      state.capacity = stats.capacity;
      state.hashCount = stats.hash_count;
      $('intro-record-count').textContent = formatNumber(stats.actual_count);
      $('intro-capacity').textContent = formatNumber(stats.capacity);
      $('intro-hashes').textContent = formatNumber(stats.hash_count);
      $('metric-capacity').textContent = formatNumber(stats.capacity);
      $('metric-set-bits').textContent = formatNumber(stats.set_bits);
      $('metric-set-foot').textContent = `${formatNumber(stats.unset_bits)} bits still 0`;
      $('metric-occupancy').textContent = formatPercent(stats.occupancy_percent, 1);
      $('occupancy-bar').style.width = `${Math.min(100, stats.occupancy_percent)}%`;
      $('metric-fpr').textContent = formatPercent(stats.estimated_false_positive_percent, 2);
      $('map-range').textContent = `${formatNumber(stats.capacity)} bits`;
      if (!stats.synchronized) {
        setBackend(false);
        showFormError('The filter and reference database are out of sync. Restart the app to rebuild the filter.');
      }
    } catch (error) {
      setBackend(false);
      showFormError(`Cannot reach the local backend. Make sure Flask is running. ${error.message}`);
    }
  }

  async function loadFilter() {
    try {
      const data = await api('/api/filter');
      state.bits = data.bits;
      state.capacity = data.capacity;
      renderBitMap();
    } catch (error) {
      $('bit-map').innerHTML = '<span class="map-placeholder">Could not load the bit array. Check the local server.</span>';
      setBackend(false);
    }
  }

  function currentWindowStart() {
    if (!state.positions.length) return 0;
    const middle = Math.min(...state.positions);
    return Math.max(0, Math.min(state.capacity - 1000, middle - 500));
  }

  function renderBitMap() {
    const map = $('bit-map');
    if (!state.bits.length) return;
    const sampleSize = 1000;
    const start = state.capacity <= sampleSize ? 0 : currentWindowStart();
    const end = Math.min(state.capacity, start + sampleSize);
    const fragment = document.createDocumentFragment();
    for (let i = start; i < end; i += 1) {
      const cell = document.createElement('span');
      const selected = state.positions.includes(i);
      const changed = state.changedPositions.includes(i);
      cell.className = `bit-cell${state.bits[i] ? ' set' : ''}${selected ? ' queried' : ''}${changed ? ' changed' : ''}`;
      cell.title = `Bit ${i}: ${state.bits[i]}${selected ? ' · queried' : ''}${changed ? ' · changed during insertion simulation' : ''}`;
      cell.setAttribute('aria-hidden', 'true');
      fragment.appendChild(cell);
    }
    map.replaceChildren(fragment);
    $('map-sampled').textContent = state.capacity > sampleSize ? `Showing bits ${formatNumber(start)}–${formatNumber(end - 1)} of ${formatNumber(state.capacity)}` : `Showing all ${formatNumber(state.capacity)} bits`;
  }

  function renderPositions(positions, values, changed = []) {
    state.positions = positions || [];
    state.bitValues = values || [];
    state.changedPositions = changed || [];
    const list = $('hash-position-list');
    list.replaceChildren();
    if (!state.positions.length) {
      list.innerHTML = '<p class="trace-placeholder">Check an email to reveal its positions.</p>';
      $('trace-count').textContent = `${state.hashCount} positions`;
      $('query-trace-meta').textContent = 'Waiting for a check';
      renderBitMap();
      return;
    }
    state.positions.forEach((position, index) => {
      const bit = state.bitValues[index];
      const chip = document.createElement('div');
      chip.className = `position-chip ${bit ? 'bit-one' : 'bit-zero'}${state.changedPositions.includes(position) ? ' changed-bit' : ''}`;
      const number = document.createElement('strong');
      number.textContent = String(position);
      const caption = document.createElement('small');
      caption.textContent = `BIT = ${bit === undefined ? '?' : bit}`;
      chip.append(number, caption);
      list.appendChild(chip);
    });
    $('trace-count').textContent = `${state.positions.length} positions`;
    $('query-trace-meta').textContent = 'Actual backend trace';
    renderBitMap();
  }

  function setResult(status, title, description, overline) {
    const card = $('result-card');
    card.className = `result-card result-${status}`;
    $('result-title').textContent = title;
    $('result-description').textContent = description;
    $('result-overline').textContent = overline;
    const symbols = { available: '✓', registered: '!', false_positive: '≈', invalid: '!', loading: '…', empty: '⌕' };
    $('result-symbol').textContent = symbols[status] || '•';
  }

  function showFormError(message) {
    const error = $('form-error');
    error.textContent = message;
    error.hidden = !message;
  }

  function setStep(id, text, label, className = '') {
    const item = $(id);
    item.className = `decision-step ${className}`.trim();
    item.querySelector('p').textContent = text;
    item.querySelector('.step-state').textContent = label;
  }

  function renderDecision(result) {
    const badge = $('decision-badge');
    const bloomPositive = result.preliminary_result === 'possibly_present';
    badge.textContent = bloomPositive ? 'Possible match' : 'Definitely absent';
    badge.className = `decision-badge ${bloomPositive ? 'positive' : 'good'}`;
    setStep('step-bloom', bloomPositive ? 'All queried bits were 1; membership is possible, not certain.' : 'At least one queried bit was 0, so this synchronized filter excludes the address.', bloomPositive ? 'Possible' : 'Negative', bloomPositive ? 'alert' : 'done');
    if (result.exact_verification_performed) {
      setStep('step-database', result.exact_registered ? 'SQLite found this normalized address in the reference dataset.' : 'SQLite did not find this normalized address in the reference dataset.', result.exact_registered ? 'Found' : 'Not found', result.exact_registered ? 'done' : 'alert');
    } else {
      setStep('step-database', 'Skipped: a zero bit already established that the address is absent.', 'Skipped', '');
    }
    const finalClass = result.status === 'available' ? 'done' : result.status === 'false_positive' ? 'alert' : 'fail';
    setStep('step-final', result.explanation, result.title, finalClass);
    badge.className = `decision-badge ${result.status === 'available' ? 'good' : result.status === 'false_positive' ? 'warning' : 'bad'}`;
    badge.textContent = result.status === 'available' ? 'Absent confirmed' : result.status === 'registered' ? 'Registered confirmed' : 'False positive';
  }

  function renderHistory(items) {
    const root = $('history-list');
    root.replaceChildren();
    if (!items || !items.length) {
      const note = document.createElement('p');
      note.className = 'empty-note';
      note.textContent = 'Your recent checks will show up here.';
      root.appendChild(note);
      return;
    }
    items.slice(0, 8).forEach((item) => {
      const button = document.createElement('button');
      button.className = 'history-item';
      button.type = 'button';
      button.title = `Run this check again: ${item.email}`;
      const email = document.createElement('span');
      email.className = 'history-email';
      email.textContent = item.email;
      const status = document.createElement('span');
      status.className = `history-status ${item.status}`;
      status.setAttribute('aria-label', item.title || item.status);
      button.append(email, status);
      button.addEventListener('click', () => { emailInput.value = item.email; checkEmail(item.email); });
      root.appendChild(button);
    });
  }

  async function refreshHistory() {
    try { const data = await api('/api/history'); renderHistory(data.history); }
    catch { /* The last visible history is harmless if the server drops temporarily. */ }
  }

  async function checkEmail(value) {
    showFormError('');
    const email = value ?? emailInput.value;
    if (!email.trim()) {
      showFormError('Enter an email address to check.');
      emailInput.focus();
      return;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())) {
      setResult('invalid', 'That email doesn’t look right', 'Check the address format and try again, for example name@example.com.', 'INPUT NEEDS ATTENTION');
      showFormError('Enter a valid email address, such as name@example.com.');
      emailInput.focus();
      return;
    }
    checkButton.disabled = true;
    checkButton.querySelector('.button-label').textContent = 'Checking…';
    setResult('loading', 'Checking your address', 'Calculating hash positions and reading the live bit array…', 'PLEASE WAIT');
    try {
      const result = await api('/api/check', { method: 'POST', body: JSON.stringify({ email }) });
      renderPositions(result.positions, result.bit_values);
      setResult(result.status, result.title, result.explanation, result.status === 'available' ? 'FILTER EXCLUDED ADDRESS' : result.status === 'registered' ? 'EXACT MATCH CONFIRMED' : 'FALSE POSITIVE DETECTED');
      renderDecision(result);
      await Promise.all([loadStats(), loadFilter(), refreshHistory()]);
    } catch (error) {
      setResult('invalid', 'Could not complete the check', error.message, 'REQUEST ERROR');
      showFormError(error.message);
    } finally {
      checkButton.disabled = false;
      checkButton.querySelector('.button-label').textContent = 'Check availability';
    }
  }

  checkForm.addEventListener('submit', (event) => { event.preventDefault(); checkEmail(); });
  $('clear-input').addEventListener('click', () => { emailInput.value = ''; emailInput.focus(); showFormError(''); });
  $('clear-visualization').addEventListener('click', async () => {
    emailInput.value = '';
    showFormError('');
    renderPositions([], []);
    setResult('empty', 'Your result will appear here', 'Enter an email address above to inspect its hash positions and bit values.', 'READY WHEN YOU ARE');
    $('decision-badge').textContent = 'Awaiting query';
    $('decision-badge').className = 'decision-badge neutral';
    setStep('step-bloom', 'The filter checks the bit at each calculated position.', '—');
    setStep('step-database', 'Only a possible match needs an exact lookup.', '—');
    setStep('step-final', 'The final result is based on the synchronized reference data.', '—');
  });

  $('insert-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    const input = $('insert-input');
    const output = $('insert-output');
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(input.value.trim())) { output.textContent = 'Enter a valid email address to simulate insertion.'; return; }
    output.textContent = 'Simulating insertion against a temporary copy of the filter…';
    try {
      const result = await api('/api/demo/insert', { method: 'POST', body: JSON.stringify({ email: input.value }) });
      state.bits = result.bits;
      renderPositions(result.positions, result.after, result.changed_positions);
      $('query-trace-meta').textContent = 'Insertion simulation · temporary copy';
      output.replaceChildren();
      const title = document.createElement('strong');
      title.textContent = `${result.changed_positions.length} bit(s) changed · ${result.already_set_positions.length} already set`;
      const detail = document.createElement('p');
      detail.textContent = `Positions: ${result.positions.join(', ')}. ${result.note}`;
      detail.style.margin = '5px 0 0';
      output.append(title, detail);
    } catch (error) { output.textContent = error.message; }
  });

  $('false-positive-button').addEventListener('click', async () => {
    const button = $('false-positive-button');
    const output = $('false-positive-output');
    button.disabled = true;
    button.textContent = 'Searching candidates…';
    output.textContent = 'Checking synthetic non-members against the actual filter and SQLite…';
    try {
      const result = await api('/api/demo/false-positive', { method: 'POST', body: '{}' });
      if (!result.found) { output.textContent = result.message; return; }
      emailInput.value = result.email;
      renderPositions(result.positions, result.bit_values);
      setResult('false_positive', result.title, result.explanation, 'FALSE POSITIVE DEMONSTRATION');
      renderDecision(result);
      output.replaceChildren();
      const title = document.createElement('strong');
      title.textContent = 'Verified genuine false positive';
      const detail = document.createElement('p');
      detail.textContent = `${result.email} · bits: ${result.positions.join(', ')} · SQLite says not registered.`;
      detail.style.margin = '5px 0 0';
      output.append(title, detail);
      await Promise.all([loadStats(), loadFilter(), refreshHistory()]);
    } catch (error) { output.textContent = error.message; }
    finally { button.disabled = false; button.innerHTML = 'Find a false positive <span aria-hidden="true">→</span>'; }
  });

  async function initialize() {
    await loadStats();
    await loadFilter();
    await refreshHistory();
    $('trace-count').textContent = `${state.hashCount} positions`;
  }
  initialize();
})();
