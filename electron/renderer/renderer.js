const API = 'http://127.0.0.1:8787';

const el = (q) => document.querySelector(q);
const files = [];
let lastOutputDir = '';

// Fallback formats if backend suggestion is unavailable
const DEFAULT_FORMATS = ['pdf','jpg','png','txt','csv','mp3','mp4','zip'];

function parseFormatsResponse(data) {
  if (!data) return [];
  if (Array.isArray(data)) return data;
  if (Array.isArray(data.formats)) return data.formats;
  if (typeof data === 'object') {
    const vals = Object.values(data).flatMap(v => Array.isArray(v) ? v : []);
    if (vals.length) return vals;
  }
  return [];
}

function setFormats(list, preferred) {
  const formatSel = el('#format');
  formatSel.innerHTML = '';
  const placeholder = document.createElement('option');
  placeholder.value = '';
  placeholder.textContent = '— Sélectionnez un format —';
  placeholder.disabled = true;
  placeholder.selected = true;
  formatSel.appendChild(placeholder);

  const uniq = [...new Set((list || []).map(f => String(f).toLowerCase()))];
  uniq.forEach(f => {
    const opt = document.createElement('option');
    opt.value = f;
    opt.textContent = f.toUpperCase();
    formatSel.appendChild(opt);
  });

  if (preferred && uniq.includes(preferred)) formatSel.value = preferred;
}

function refreshFiles() {
  const list = el('#filesList');
  list.innerHTML = '';
  files.forEach(f => {
    const chip = document.createElement('div');
    chip.className = 'file-chip';
    chip.textContent = f.split('/').pop();
    list.appendChild(chip);
  });
  const disableConvert = files.length === 0 || !el('#format').value || !el('#output').value;
  el('#btnConvert').disabled = disableConvert;
  el('#btnOpenOutput').disabled = !el('#output').value;
}

async function checkBackend(timeoutMs = 4000) {
  const ctl = new AbortController();
  const t = setTimeout(() => ctl.abort(), timeoutMs);
  try {
    const r = await fetch(`${API}/health`, { signal: ctl.signal });
    clearTimeout(t);
    return r.ok;
  } catch {
    clearTimeout(t);
    return false;
  }
}

function delay(ms) {
  return new Promise(res => setTimeout(res, ms));
}

async function waitBackendReady(maxWaitMs = 8000, stepMs = 400) {
  const start = Date.now();
  while (Date.now() - start < maxWaitMs) {
    if (await checkBackend(Math.min(stepMs, 1000))) return true;
    await delay(stepMs);
  }
  return false;
}

async function suggestFormats() {
  const formatSel = el('#format');
  const current = formatSel.value;
  if (files.length === 0) {
    // If no files yet, keep initial/global formats
    if (!formatSel.options.length) setFormats(DEFAULT_FORMATS);
    return;
  }
  const ext = files[0].split('.').pop();
  try {
    const r = await fetch(`${API}/formats?file_ext=${encodeURIComponent(ext)}`);
    const data = await r.json();
    const list = parseFormatsResponse(data);
    setFormats(list.length ? list : DEFAULT_FORMATS, current);
  } catch (e) {
    console.error(e);
    setFormats(DEFAULT_FORMATS, current);
  }
}

async function loadInitialFormats(preferred) {
  try {
    const r = await fetch(`${API}/formats`);
    const data = await r.json();
    const list = parseFormatsResponse(data);
    setFormats(list.length ? list : DEFAULT_FORMATS, preferred);
  } catch (e) {
    console.error(e);
    setFormats(DEFAULT_FORMATS, preferred);
  }
}

async function loadHistory() {
  try {
    const r = await fetch(`${API}/history/recent?limit=10`);
    const data = await r.json();
    const box = el('#history');
    box.innerHTML = '';
    (data.items || []).forEach(it => {
      const d = document.createElement('div');
      d.className = 'item';
      d.innerHTML = `<strong>${(it.output_format||'').toUpperCase()}</strong> • ${ (it.input_file||'').split('/').pop() }<br/><span class="muted">${it.timestamp?.slice(0,19)} — ${it.success? '✓ OK':'✗ Échec'}</span>`;
      box.appendChild(d);
    });
  } catch (e) { console.error(e); }
}

async function startConvert() {
  const outputDir = el('#output').value;
  const outputFmt = el('#format').value;
  if (!files.length || !outputDir || !outputFmt) return;

  el('#status').textContent = 'Démarrage...';
  el('#progressBar').style.width = '0%';

  // Wait for backend to be ready (gives it time to spawn)
  if (!(await waitBackendReady())) {
    el('#status').textContent = "Impossible de joindre le service de conversion (backend).";
    return;
  }

  let job_id = null;
  try {
    const resp = await fetch(`${API}/convert`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ files, output_format: outputFmt, output_dir: outputDir })
    });
    if (!resp.ok) {
      const txt = await resp.text();
      throw new Error(txt || `Erreur HTTP ${resp.status}`);
    }
    const data = await resp.json();
    job_id = data.job_id;
  } catch (e) {
    console.error('convert error', e);
    el('#status').textContent = `Erreur de démarrage: ${e?.message || e}`;
    return;
  }

  let failures = 0;
  const timer = setInterval(async () => {
    try {
      const r = await fetch(`${API}/jobs/${job_id}`);
      if (!r.ok) throw new Error(`status ${r.status}`);
      const j = await r.json();
      el('#status').textContent = j.message || 'En cours...';
      const pct = j.total ? Math.round((j.processed / j.total) * 100) : 0;
      el('#progressBar').style.width = `${pct}%`;
      if (j.done) {
        clearInterval(timer);
        el('#status').textContent = `Terminé: ${j.success} réussite(s), ${j.failed} échec(s)`;
        lastOutputDir = outputDir;
        loadHistory();
      }
      failures = 0;
    } catch (e) {
      failures += 1;
      if (failures >= 8) { // ~4s
        clearInterval(timer);
        el('#status').textContent = `Perte de connexion au service (jobs).`;
      }
    }
  }, 500);
}

window.addEventListener('DOMContentLoaded', () => {
  // Load prefs
  (async () => {
    try {
    const prefs = JSON.parse(localStorage.getItem('ptitconvert:prefs') || '{}');
    if (prefs.defaultFormat) el('#prefDefaultFormat')?.setAttribute('value', prefs.defaultFormat);
    if (prefs.defaultOutput) {
      const out = el('#prefDefaultOutput');
      if (out) out.setAttribute('value', prefs.defaultOutput);
      el('#output').value = prefs.defaultOutput;
    }
      // Preload formats (all) so the dropdown isn't empty before adding files
      await loadInitialFormats(prefs.defaultFormat?.toLowerCase());
    } catch {}
  })();

  el('#btnAddFiles').addEventListener('click', async () => {
    const picked = await window.ptitconvert.pickFiles();
    if (picked && picked.length) {
      picked.forEach(p => files.push(p));
      await suggestFormats();
      refreshFiles();
    }
  });

  el('#btnAddFolder').addEventListener('click', async () => {
    const dir = await window.ptitconvert.pickFolder();
    if (dir) {
      el('#output').value = dir;
      refreshFiles();
    }
  });

  el('#format').addEventListener('change', refreshFiles);
  el('#output').addEventListener('input', refreshFiles);
  el('#btnConvert').addEventListener('click', startConvert);
  el('#btnOpenOutput').addEventListener('click', async () => {
    const dir = el('#output').value || lastOutputDir;
    if (!dir) return;
    try { await fetch(`${API}/open_folder`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ path: dir }) }); } catch {}
  });

  el('#btnBrowseOutput').addEventListener('click', async () => {
    const d = await window.ptitconvert.pickFolder();
    if (d) {
      el('#output').value = d;
      refreshFiles();
    }
  });

  // Preferences modal
  const prefsModal = el('#prefsModal');
  el('#btnPrefs').addEventListener('click', () => {
    prefsModal.classList.remove('hidden');
  });
  el('#btnClosePrefs').addEventListener('click', () => {
    prefsModal.classList.add('hidden');
  });
  el('#btnPickDefaultOutput').addEventListener('click', async () => {
    const d = await window.ptitconvert.pickFolder();
    if (d) el('#prefDefaultOutput').value = d;
  });
  el('#btnSavePrefs').addEventListener('click', () => {
    const prefs = {
      defaultFormat: el('#prefDefaultFormat').value.trim().toLowerCase(),
      defaultOutput: el('#prefDefaultOutput').value.trim()
    };
    localStorage.setItem('ptitconvert:prefs', JSON.stringify(prefs));
    if (prefs.defaultOutput) el('#output').value = prefs.defaultOutput;
    if (prefs.defaultFormat) {
      const sel = el('#format');
      if (Array.from(sel.options).some(o => o.value === prefs.defaultFormat)) {
        sel.value = prefs.defaultFormat;
      }
    }
    refreshFiles();
    prefsModal.classList.add('hidden');
  });

  // Drag & drop over the whole window
  ['dragenter','dragover','dragleave','drop'].forEach(e => {
    window.addEventListener(e, ev => { ev.preventDefault(); ev.stopPropagation(); });
  });
  window.addEventListener('drop', async (ev) => {
    const paths = [];
    for (const item of ev.dataTransfer.files) {
      paths.push(item.path || item.name);
    }
    if (paths.length) {
      paths.forEach(p => files.push(p));
      await suggestFormats();
      refreshFiles();
    }
  });

  loadHistory();
});
