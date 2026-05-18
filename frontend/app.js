/* ============================================================
   AI ERP – Frontend Application Logic
   ============================================================ */

const API = '/api';
let currentJobFilter = '';
let pollTimer = null;
let selectedFile = null;

/* ─── Page Navigation ──────────────────────────────────────── */
function showPage(name) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));

  document.getElementById(`page-${name}`).classList.add('active');
  const navEl = document.getElementById(`nav-${name}`);
  if (navEl) navEl.classList.add('active');

  const titles = {
    dashboard: ['Dashboard', 'Genel bakış ve istatistikler'],
    upload: ['Dosya Yükle', 'Excel veya CSV yükleyin, AI analiz etsin'],
    jobs: ['İşler', 'Tüm yükleme ve işleme işleri'],
  };
  const [title, sub] = titles[name] || [name, ''];
  document.getElementById('pageTitle').textContent = title;
  document.getElementById('pageSubtitle').textContent = sub;

  if (name === 'dashboard') loadDashboard();
  if (name === 'jobs') loadJobs();
}

document.querySelectorAll('.nav-item').forEach(el => {
  el.addEventListener('click', e => {
    e.preventDefault();
    showPage(el.dataset.page);
  });
});

/* ─── API helpers ──────────────────────────────────────────── */
async function apiFetch(path, opts = {}) {
  const res = await fetch(API + path, opts);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

/* ─── Health Check ─────────────────────────────────────────── */
async function checkHealth() {
  try {
    const data = await fetch('/health').then(r => r.json());
    const dot = document.getElementById('healthDot');
    const txt = document.getElementById('healthText');
    if (data.status === 'healthy') {
      dot.className = 'health-dot ok';
      txt.textContent = 'Sistem Sağlıklı';
    } else {
      dot.className = 'health-dot warn';
      txt.textContent = 'Kısmi Sorun';
    }
  } catch {
    document.getElementById('healthDot').className = 'health-dot err';
    document.getElementById('healthText').textContent = 'Bağlanamadı';
  }
}

/* ─── Dashboard ────────────────────────────────────────────── */
async function loadDashboard() {
  try {
    const data = await apiFetch('/analytics/dashboard');

    document.getElementById('statJobs').textContent = data.total_jobs.toLocaleString();
    document.getElementById('statRecords').textContent = data.total_records.toLocaleString();
    document.getElementById('statValid').textContent = data.valid_records.toLocaleString();
    document.getElementById('statQuality').textContent =
      data.avg_quality_score > 0 ? `${Math.round(data.avg_quality_score * 100)}%` : '–';

    renderCategories(data.categories);
    renderRecentJobs(data.recent_jobs);
  } catch (e) {
    console.error('Dashboard load error:', e);
  }
}

function renderCategories(cats) {
  const el = document.getElementById('categoriesContainer');
  if (!cats || !cats.length) {
    el.innerHTML = `<div class="empty-state"><p>Henüz kategori verisi yok</p></div>`;
    return;
  }
  const max = Math.max(...cats.map(c => c.count));
  el.innerHTML = cats.map(c => {
    const pct = max > 0 ? (c.count / max) * 100 : 0;
    const label = categoryLabel(c.emission_category);
    return `
      <div class="category-item">
        <span class="category-label">${label}</span>
        <div class="category-bar-wrap">
          <div class="category-bar" style="width:${pct}%"></div>
        </div>
        <span class="category-count">${c.count}</span>
      </div>`;
  }).join('');
}

function renderRecentJobs(jobs) {
  const el = document.getElementById('recentJobsContainer');
  if (!jobs || !jobs.length) {
    el.innerHTML = `<div class="empty-state"><p>Henüz iş yok. <a href="#" onclick="showPage('upload')">Dosya yükleyin</a></p></div>`;
    return;
  }
  el.innerHTML = jobs.map(j => `
    <div class="recent-job-item" onclick="openJobModal('${j.id}')">
      ${statusBadge(j.status)}
      <span class="rj-name">${j.original_filename}</span>
      <span class="rj-rows">${j.total_rows} satır</span>
    </div>`).join('');
}

/* ─── Jobs Page ────────────────────────────────────────────── */
async function loadJobs() {
  const url = currentJobFilter ? `/upload/jobs?status=${currentJobFilter}` : '/upload/jobs?limit=50';
  try {
    const jobs = await apiFetch(url);
    const el = document.getElementById('jobsList');
    if (!jobs.length) {
      el.innerHTML = `
        <div class="empty-state">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="21" x2="9" y2="9"/></svg>
          <p>Bu filtrede iş bulunamadı</p>
          <button class="btn btn-primary btn-sm" onclick="showPage('upload')">Dosya Yükle</button>
        </div>`;
      return;
    }
    el.innerHTML = jobs.map(j => jobCard(j)).join('');
  } catch (e) {
    toast('İşler yüklenemedi: ' + e.message, 'error');
  }
}

function jobCard(j) {
  const qualityPct = j.data_quality_score ? Math.round(j.data_quality_score * 100) : 0;
  return `
    <div class="job-card" onclick="openJobModal('${j.id}')">
      <div style="flex:1">
        <div class="job-name">${j.original_filename}</div>
        <div class="job-meta">${timeAgo(j.created_at)}</div>
      </div>
      <div class="job-stats">
        <div class="job-stat">
          <div class="job-stat-val">${j.total_rows}</div>
          <div class="job-stat-lbl">Satır</div>
        </div>
        <div class="job-stat">
          <div class="job-stat-val" style="color:var(--success)">${j.processed_rows}</div>
          <div class="job-stat-lbl">Geçerli</div>
        </div>
        <div class="job-stat">
          <div class="job-stat-val" style="color:var(--error)">${j.error_rows}</div>
          <div class="job-stat-lbl">Hata</div>
        </div>
        ${qualityPct > 0 ? `<div class="job-stat"><div class="job-stat-val" style="color:var(--warning)">${qualityPct}%</div><div class="job-stat-lbl">Kalite</div></div>` : ''}
      </div>
      <div style="display:flex;flex-direction:column;align-items:flex-end;gap:8px">
        ${statusBadge(j.status)}
        ${j.status === 'processing' ? `<div class="mini-progress"><div class="mini-progress-bar" style="width:${j.progress}%"></div></div>` : ''}
      </div>
    </div>`;
}

function filterJobs(status) {
  currentJobFilter = status;
  document.querySelectorAll('.filter-tab').forEach(t => {
    t.classList.toggle('active', t.dataset.status === status);
  });
  loadJobs();
}

/* ─── Job Detail Modal ─────────────────────────────────────── */
async function openJobModal(jobId) {
  document.getElementById('jobModal').style.display = 'flex';
  document.getElementById('modalBody').innerHTML = '<div class="empty-state"><p>Yükleniyor...</p></div>';

  try {
    const [job, recData] = await Promise.all([
      apiFetch(`/upload/jobs/${jobId}`),
      apiFetch(`/upload/jobs/${jobId}/records?page=1&page_size=20`),
    ]);

    document.getElementById('modalTitle').textContent = job.original_filename;
    document.getElementById('modalSubtitle').textContent =
      `${job.total_rows} satır · ${timeAgo(job.created_at)} · ${statusBadge(job.status)}`;

    const mappings = job.column_mappings?.mappings || [];
    const issues   = job.column_mappings?.data_quality_issues || [];
    const missing  = job.column_mappings?.missing_fields || [];
    const recs     = job.column_mappings?.recommendations || [];
    const qualPct  = job.data_quality_score ? Math.round(job.data_quality_score * 100) : 0;
    const qualColor = qualPct >= 80 ? 'var(--success)' : qualPct >= 50 ? 'var(--warning)' : 'var(--error)';

    document.getElementById('modalBody').innerHTML = `
      <!-- AI Summary -->
      <div class="modal-section">
        <div class="modal-section-title">🤖 AI Özeti</div>
        <div class="ai-summary-box">${job.ai_summary || 'Henüz analiz tamamlanmadı.'}</div>
      </div>

      <!-- Quality Score -->
      ${qualPct > 0 ? `
      <div class="modal-section">
        <div class="modal-section-title">📊 Veri Kalitesi</div>
        <div class="quality-ring-wrap">
          <div class="quality-ring" style="background:rgba(${qualPct>=80?'16,185,129':qualPct>=50?'245,158,11':'239,68,68'},0.15);border:3px solid ${qualColor}">
            <span style="color:${qualColor}">${qualPct}%</span>
          </div>
          <div class="quality-info">
            <strong>${qualPct >= 80 ? 'Yüksek' : qualPct >= 50 ? 'Orta' : 'Düşük'} Kalite</strong>
            <p>${job.processed_rows} geçerli · ${job.error_rows} hatalı satır</p>
          </div>
        </div>
      </div>` : ''}

      <!-- Column Mappings -->
      ${mappings.length > 0 ? `
      <div class="modal-section">
        <div class="modal-section-title">🗂️ Kolon Eşleştirmeleri (${mappings.length})</div>
        <table class="mapping-table">
          <thead><tr>
            <th>Kaynak Kolon</th><th>Hedef Alan</th><th>Güven</th><th>Notlar</th>
          </tr></thead>
          <tbody>${mappings.map(m => `
            <tr>
              <td><strong>${m.source_column}</strong></td>
              <td><code style="background:var(--bg-hover);padding:2px 6px;border-radius:4px;font-size:11px">${m.target_field}</code></td>
              <td><span class="conf-badge ${m.confidence>=0.8?'conf-high':m.confidence>=0.5?'conf-mid':'conf-low'}">${Math.round(m.confidence*100)}%</span></td>
              <td style="color:var(--text-secondary);font-size:12px">${m.notes || '–'}</td>
            </tr>`).join('')}
          </tbody>
        </table>
      </div>` : ''}

      <!-- Issues & Recommendations -->
      ${(issues.length || missing.length || recs.length) ? `
      <div class="modal-section">
        <div class="modal-section-title">⚠️ Sorunlar & Öneriler</div>
        ${issues.map(i => `<div class="issue-item"><span class="issue-icon">⚠️</span>${i}</div>`).join('')}
        ${missing.map(f => `<div class="issue-item"><span class="issue-icon">❓</span>Eksik alan: <strong>${f}</strong></div>`).join('')}
        ${recs.map(r => `<div class="issue-item"><span class="issue-icon">💡</span>${r}</div>`).join('')}
      </div>` : ''}

      <!-- Records Preview -->
      ${recData.items.length > 0 ? `
      <div class="modal-section">
        <div class="modal-section-title">📋 Veri Önizleme (İlk ${recData.items.length} / ${recData.total})</div>
        <div style="overflow-x:auto">
          <table class="records-table">
            <thead><tr>
              <th>#</th><th>Kategori</th><th>Yakıt</th>
              <th>Miktar</th><th>Birim</th><th>Tarih</th>
              <th>Araç</th><th>Durum</th>
            </tr></thead>
            <tbody>${recData.items.map(r => `
              <tr>
                <td class="mono" style="color:var(--text-muted)">${r.row_number}</td>
                <td>${categoryLabel(r.emission_category)}</td>
                <td>${r.fuel_type || '–'}</td>
                <td class="mono">${r.amount != null ? r.amount.toLocaleString() : '–'}</td>
                <td>${r.unit || '–'}</td>
                <td class="mono">${r.date ? r.date.split('T')[0] : '–'}</td>
                <td>${r.vehicle_id || '–'}</td>
                <td>${r.is_valid
                  ? '<span class="badge badge-completed">✓</span>'
                  : `<span class="badge badge-failed" title="${(r.validation_errors||[]).join(', ')}">✗</span>`}
                </td>
              </tr>`).join('')}
            </tbody>
          </table>
        </div>
      </div>` : ''}

      <!-- Export Actions -->
      <div class="modal-export-bar">
        <a class="btn btn-ghost" href="/api/analytics/jobs/${jobId}/export/csv" download>
          📥 CSV İndir
        </a>
        <a class="btn btn-ghost" href="/api/analytics/jobs/${jobId}/export/json" download>
          📥 JSON İndir
        </a>
        <button class="btn btn-ghost" style="color:var(--error)" onclick="deleteJob('${jobId}')">
          🗑️ Sil
        </button>
      </div>
    `;
  } catch (e) {
    document.getElementById('modalBody').innerHTML =
      `<div class="empty-state"><p>Hata: ${e.message}</p></div>`;
  }
}

function closeModal() {
  document.getElementById('jobModal').style.display = 'none';
}

async function deleteJob(jobId) {
  if (!confirm('Bu işi silmek istediğinizden emin misiniz?')) return;
  try {
    await apiFetch(`/upload/jobs/${jobId}`, { method: 'DELETE' });
    closeModal();
    toast('İş silindi', 'success');
    loadJobs();
    loadDashboard();
  } catch (e) {
    toast('Silme hatası: ' + e.message, 'error');
  }
}

/* ─── File Upload ──────────────────────────────────────────── */
const dropZone  = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');

dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('drag-over'); });
dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
dropZone.addEventListener('drop', e => {
  e.preventDefault();
  dropZone.classList.remove('drag-over');
  const f = e.dataTransfer.files[0];
  if (f) setFile(f);
});
dropZone.addEventListener('click', e => {
  if (e.target.closest('button')) return;
  fileInput.click();
});
fileInput.addEventListener('change', () => {
  if (fileInput.files[0]) setFile(fileInput.files[0]);
});
document.getElementById('clearFileBtn').addEventListener('click', e => {
  e.stopPropagation();
  clearFile();
});

function setFile(file) {
  const ext = file.name.split('.').pop().toLowerCase();
  if (!['xlsx','xls','csv'].includes(ext)) {
    toast('Desteklenmeyen dosya türü: .' + ext, 'error');
    return;
  }
  if (file.size > 50 * 1024 * 1024) {
    toast('Dosya çok büyük (maks 50MB)', 'error');
    return;
  }
  selectedFile = file;
  document.getElementById('previewFileName').textContent = file.name;
  document.getElementById('previewFileSize').textContent = formatBytes(file.size);
  document.getElementById('filePreview').style.display = 'flex';
  document.getElementById('dropZone').classList.add('has-file');
  document.getElementById('uploadActions').style.display = 'block';
}

function clearFile() {
  selectedFile = null;
  fileInput.value = '';
  document.getElementById('filePreview').style.display = 'none';
  document.getElementById('dropZone').classList.remove('has-file');
  document.getElementById('uploadActions').style.display = 'none';
  document.getElementById('uploadProgressCard').style.display = 'none';
}

async function startUpload() {
  if (!selectedFile) { toast('Önce dosya seçin', 'error'); return; }

  const btn = document.getElementById('uploadBtn');
  btn.disabled = true;
  btn.textContent = 'Yükleniyor...';

  document.getElementById('uploadProgressCard').style.display = 'block';
  setProgressStep(1);
  updateProgress(5, 'Dosya yükleniyor...');

  const fd = new FormData();
  fd.append('file', selectedFile);

  try {
    const res = await fetch(API + '/upload', { method: 'POST', body: fd });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Yükleme başarısız');
    }
    const data = await res.json();
    toast('✅ Dosya yüklendi! AI analiz başladı.', 'success');
    updateProgress(15, 'AI analiz ediliyor...');
    setProgressStep(2);
    pollJobProgress(data.job_id, btn);
  } catch (e) {
    toast('Yükleme hatası: ' + e.message, 'error');
    btn.disabled = false;
    btn.innerHTML = '⬆ AI ile Analiz Et';
  }
}

function pollJobProgress(jobId, btn) {
  clearInterval(pollTimer);
  pollTimer = setInterval(async () => {
    try {
      const job = await apiFetch(`/upload/jobs/${jobId}`);
      const pct = job.progress;

      updateProgress(pct, progressLabel(pct));
      if (pct > 15 && pct <= 40) setProgressStep(2);
      else if (pct > 40 && pct <= 70) setProgressStep(3);
      else if (pct > 70) setProgressStep(4);

      if (job.status === 'completed') {
        clearInterval(pollTimer);
        updateProgress(100, '✅ Tamamlandı!');
        setProgressStep(4, true);
        toast(`✅ ${job.processed_rows} kayıt işlendi! Kalite: ${Math.round((job.data_quality_score||0)*100)}%`, 'success');
        btn.disabled = false;
        btn.innerHTML = '⬆ AI ile Analiz Et';
        setTimeout(() => { clearFile(); showPage('jobs'); }, 2000);
      } else if (job.status === 'failed') {
        clearInterval(pollTimer);
        toast('❌ İşlem başarısız: ' + (job.error_message || ''), 'error');
        updateProgress(0, '❌ Hata oluştu');
        btn.disabled = false;
        btn.innerHTML = '⬆ AI ile Analiz Et';
      }
    } catch (e) { console.error('Poll error:', e); }
  }, 2000);
}

function updateProgress(pct, label) {
  document.getElementById('progressBar').style.width = pct + '%';
  document.getElementById('progressPct').textContent = pct + '%';
  document.getElementById('progressTitle').textContent = label;
}

function setProgressStep(activeStep, allDone = false) {
  for (let i = 1; i <= 4; i++) {
    const el = document.getElementById(`step${i}`);
    if (allDone) { el.className = 'step done'; continue; }
    if (i < activeStep)       el.className = 'step done';
    else if (i === activeStep) el.className = 'step active';
    else                       el.className = 'step';
  }
}

function progressLabel(pct) {
  if (pct < 15) return 'Dosya okunuyor...';
  if (pct < 40) return 'AI analiz yapıyor...';
  if (pct < 70) return 'Kolonlar eşleştiriliyor...';
  if (pct < 100) return 'Veritabanına kaydediliyor...';
  return 'Tamamlandı!';
}

/* ─── Helpers ──────────────────────────────────────────────── */
function statusBadge(status) {
  const map = {
    pending:    ['badge-pending',    '⏳ Bekliyor'],
    processing: ['badge-processing', '⚙️ İşleniyor'],
    completed:  ['badge-completed',  '✅ Tamamlandı'],
    failed:     ['badge-failed',     '❌ Hatalı'],
    cancelled:  ['badge-pending',    '🚫 İptal'],
  };
  const [cls, label] = map[status] || ['badge-pending', status];
  return `<span class="badge ${cls}">${label}</span>`;
}

function categoryLabel(cat) {
  const map = {
    mobile_combustion:    '🚗 Mobil Yanma',
    stationary_combustion:'🏭 Sabit Yanma',
    electricity:          '⚡ Elektrik',
    refrigerants:         '❄️ Soğutucu',
    waste:                '🗑️ Atık',
    water:                '💧 Su',
    business_travel:      '✈️ İş Seyahati',
    employee_commuting:   '🚌 Çalışan Ulaşım',
    purchased_goods:      '📦 Satın Alınan Mal',
    other:                '📋 Diğer',
  };
  return map[cat] || cat || '–';
}

function formatBytes(b) {
  if (b < 1024) return b + ' B';
  if (b < 1024 * 1024) return (b / 1024).toFixed(1) + ' KB';
  return (b / 1024 / 1024).toFixed(1) + ' MB';
}

function timeAgo(iso) {
  const d = new Date(iso);
  const diff = Date.now() - d.getTime();
  const mins  = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days  = Math.floor(diff / 86400000);
  if (mins < 1)    return 'Az önce';
  if (mins < 60)   return `${mins} dk önce`;
  if (hours < 24)  return `${hours} sa önce`;
  return `${days} gün önce`;
}

function toast(msg, type = 'info') {
  const tc = document.getElementById('toastContainer');
  const el = document.createElement('div');
  el.className = `toast ${type}`;
  const icons = { success:'✅', error:'❌', info:'ℹ️' };
  el.innerHTML = `<span>${icons[type]||''}</span><span>${msg}</span>`;
  tc.appendChild(el);
  setTimeout(() => el.remove(), 4000);
}

/* ─── Modal close on overlay click ──────────────────────────── */
document.getElementById('jobModal').addEventListener('click', e => {
  if (e.target === document.getElementById('jobModal')) closeModal();
});

/* ─── Init ─────────────────────────────────────────────────── */
checkHealth();
setInterval(checkHealth, 30000);
loadDashboard();
