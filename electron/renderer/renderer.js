const API = 'http://127.0.0.1:8787';

const el = (q) => document.querySelector(q);
const files = [];
let lastOutputDir = '';

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

async function suggestFormats() {
  const formatSel = el('#format');
  formatSel.innerHTML = '';
  if (files.length === 0) return;
  const ext = files[0].split('.').pop();
  try {
    const r = await fetch(`${API}/formats?file_ext=${encodeURIComponent(ext)}`);
    const data = await r.json();
    data.formats.forEach(f => {
      const opt = document.createElement('option');
      opt.value = f.toLowerCase();
      opt.textContent = f;
      formatSel.appendChild(opt);
    });
  } catch (e) {
    console.error(e);
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
  const resp = await fetch(`${API}/convert`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ files, output_format: outputFmt, output_dir: outputDir })
  });
  const { job_id } = await resp.json();

  const timer = setInterval(async () => {
    const r = await fetch(`${API}/jobs/${job_id}`);
    const j = await r.json();
    el('#status').textContent = j.message || '';
    const pct = j.total ? Math.round((j.processed / j.total) * 100) : 0;
    el('#progressBar').style.width = `${pct}%`;
    if (j.done) {
      clearInterval(timer);
      el('#status').textContent = `Terminé: ${j.success} réussite(s), ${j.failed} échec(s)`;
      lastOutputDir = outputDir;
      loadHistory();
    }
  }, 500);
}

window.addEventListener('DOMContentLoaded', () => {
  // Load prefs
  try {
    const prefs = JSON.parse(localStorage.getItem('ptitconvert:prefs') || '{}');
    if (prefs.defaultFormat) el('#prefDefaultFormat')?.setAttribute('value', prefs.defaultFormat);
    if (prefs.defaultOutput) {
      const out = el('#prefDefaultOutput');
      if (out) out.setAttribute('value', prefs.defaultOutput);
      el('#output').value = prefs.defaultOutput;
    }
  } catch {}

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
      // Select if exists
      const sel = el('#format');
      const opt = Array.from(sel.options).find(o => o.value === prefs.defaultFormat);
      if (opt) sel.value = prefs.defaultFormat;
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
