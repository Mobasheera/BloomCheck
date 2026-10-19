(() => {
  'use strict';
  const $ = (id) => document.getElementById(id);
  const button = $('run-benchmark');
  const resultsRoot = $('benchmark-results');
  const names = { linear: 'Linear scan', sqlite: 'SQLite exact lookup', bloom: 'Bloom + exact verify' };

  async function api(url, options = {}) {
    const response = await fetch(url, { headers: { 'Content-Type': 'application/json' }, ...options });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'The request failed.');
    return result;
  }
  function addCell(row, text, tag = 'td') { const node = document.createElement(tag); node.textContent = text; row.appendChild(node); return node; }

  function render(data) {
    $('bench-records').textContent = data.record_count.toLocaleString('en-US');
    $('bench-queries').textContent = data.query_count.toLocaleString('en-US');
    const values = data.results;
    const max = Math.max(...values.map(item => item.average_ms), 0.001);
    resultsRoot.replaceChildren();
    const summary = document.createElement('div');
    summary.className = 'bench-summary';
    values.forEach(item => {
      const card = document.createElement('article');
      card.className = 'bench-result-card';
      const heading = document.createElement('h3'); heading.textContent = names[item.method];
      const number = document.createElement('div'); number.className = 'bench-number'; number.textContent = `${item.average_ms.toFixed(3)} ms`;
      const note = document.createElement('p'); note.textContent = `${item.average_us_per_query.toFixed(3)} µs/query average`;
      card.append(heading, number, note); summary.appendChild(card);
    });
    resultsRoot.appendChild(summary);

    const bars = document.createElement('div'); bars.className = 'bench-bars';
    const title = document.createElement('h3'); title.textContent = 'Average total batch time'; bars.appendChild(title);
    values.forEach(item => {
      const row = document.createElement('div'); row.className = 'bench-bar-row';
      const label = document.createElement('span'); label.textContent = names[item.method];
      const track = document.createElement('div'); track.className = 'bench-bar-track';
      const fill = document.createElement('div'); fill.className = `bench-bar ${item.method}`; fill.style.width = `${Math.max(0.5, item.average_ms / max * 100)}%`; track.appendChild(fill);
      const value = document.createElement('span'); value.className = 'bench-bar-value'; value.textContent = `${item.average_ms.toFixed(3)} ms`;
      row.append(label, track, value); bars.appendChild(row);
    });
    resultsRoot.appendChild(bars);

    const table = document.createElement('table'); table.className = 'bench-detail';
    const head = document.createElement('thead'); const headRow = document.createElement('tr');
    ['Strategy', 'Average total', 'Average/query', 'Trial times'].forEach(text => addCell(headRow, text, 'th'));
    head.appendChild(headRow); table.appendChild(head);
    const body = document.createElement('tbody');
    values.forEach(item => {
      const row = document.createElement('tr');
      addCell(row, names[item.method]);
      addCell(row, `${item.average_ms.toFixed(3)} ms`);
      addCell(row, `${item.average_us_per_query.toFixed(3)} µs`);
      addCell(row, item.trial_ms.map(ms => ms.toFixed(3)).join(' · ') + ' ms');
      body.appendChild(row);
    });
    table.appendChild(body); resultsRoot.appendChild(table);
    const note = document.createElement('p'); note.className = 'bench-note';
    note.textContent = `${data.note} ${data.trials} measured trials were run after warm-up; results are measurements from this run, not hardcoded claims.`;
    resultsRoot.appendChild(note);
  }

  async function init() {
    try {
      const stats = await api('/api/stats');
      $('bench-records').textContent = stats.actual_count.toLocaleString('en-US');
      $('bench-queries').textContent = '500';
    } catch { /* API error will be displayed on run. */ }
  }
  button.addEventListener('click', async () => {
    $('bench-error').hidden = true;
    button.disabled = true;
    button.textContent = 'Measuring…';
    resultsRoot.innerHTML = '<div class="empty-benchmark"><span>⌁</span><h3>Running trials…</h3><p>All three strategies are processing the same deterministic query list.</p></div>';
    try {
      const data = await api('/api/benchmark', { method: 'POST', body: JSON.stringify({ query_count: Number($('query-count').value), trials: Number($('trial-count').value) }) });
      render(data);
    } catch (error) {
      $('bench-error').textContent = error.message;
      $('bench-error').hidden = false;
      resultsRoot.innerHTML = '<div class="empty-benchmark"><h3>Experiment could not run</h3><p>Check that the Flask application is running, then retry.</p></div>';
    } finally { button.disabled = false; button.innerHTML = 'Run experiment <span aria-hidden="true">→</span>'; }
  });
  init();
})();
