/* ============================================================
   AI ERP – Frontend Application Logic
   ============================================================ */

const API = '/api';
let currentJobFilter = '';
let pollTimer = null;
let selectedFile = null;
let currentLang = localStorage.getItem('lang') || 'tr';

const i18n = {
  tr: {
    dashboard_title: "Dashboard", dashboard_subtitle: "Genel bakış ve istatistikler",
    checking: "Sistem Sağlıklı", upload_btn: "Dosya Yükle",
    nav_dashboard: "Dashboard", nav_upload: "Dosya Yükle", nav_templates: "Şablonlar", nav_jobs: "İşler",
    ai_active: "Gemini AI Aktif",
    stat_jobs: "Toplam İş", stat_records: "Toplam Kayıt", stat_valid: "Geçerli Kayıt", stat_quality: "Ort. Kalite",
    templates_title: "Kayıtlı Şablonlar", new_template_btn: "+ Yeni Şablon",
    loading: "Yükleniyor...", empty_templates: "Henüz şablon oluşturulmamış.",
    upload_subtitle: "Excel veya CSV yükleyin, AI analiz etsin",
    jobs_subtitle: "Tüm yükleme ve işleme işleri",
    templates_subtitle: "AI verilerinizi bu şablonlara dönüştürür",
    no_jobs_yet: "Henüz iş yok.", upload_file_link: "Dosya yükleyin", upload_first_file: "İlk Dosyayı Yükle",
    select_template_label: "1. Hedef Şablonu Seçin", select_template_desc: "Yapay zeka, yüklediğiniz dosyayı bu şablondaki kolonlara uyarlayacaktır.",
    upload_drop_title: "Excel / CSV Dosyası Yükleyin", upload_drop_subtitle: "Sürükleyip bırakın veya tıklayarak seçin", upload_drop_hint: "Desteklenen formatlar: .xlsx, .xls, .csv — Maks 50MB", upload_btn_select: "Dosya Seç",
    feat_ai_title: "Akıllı Kolon Tanıma", feat_ai_desc: "Türkçe ve İngilizce başlıkları otomatik algılar",
    feat_cat_title: "Otomatik Kategorizasyon", feat_cat_desc: "Veri türünü otomatik olarak tespit eder",
    feat_qa_title: "Veri Kalite Kontrolü", feat_qa_desc: "Eksik ve hatalı satırları raporlar",
    feat_exp_title: "CSV / JSON Export", feat_exp_desc: "Temizlenmiş veriyi dilediğiniz formatta indirin",
    upload_submit_btn: "AI ile Analiz Et",
    filter_all: "Tümü", filter_pending: "Bekliyor", filter_processing: "İşleniyor", filter_completed: "Tamamlandı", filter_failed: "Hatalı", btn_refresh: "Yenile",
    default_tpl: "Varsayılan ERP Şablonu (Tarih, Miktar, Açıklama, Tutar)",
    empty_recent_jobs: "Henüz iş yok.",
    filter_no_jobs: "Bu filtrede iş bulunamadı",
    job_rows: "Satır", job_valid: "Geçerli", job_error: "Hata", job_quality: "Kalite",
    job_detail_title: "İş Detayı", create_tpl_title: "Yeni Şablon Yarat",
    tpl_name_lbl: "Şablon Adı", tpl_name_ph: "Örn: Trendyol E-Ticaret",
    tpl_desc_lbl: "Açıklama", tpl_desc_ph: "Ürün aktarım şablonu",
    tpl_cols_lbl: "Hedef Kolonlar (AI bunlara çevirecek)", tpl_add_col: "+ Kolon Ekle", tpl_save: "Şablonu Kaydet",
    col_name_ph: "Kolon Adı (Örn: fiyat)", col_desc_ph: "Açıklama",
    type_string: "Metin", type_number: "Sayı", type_date: "Tarih",
    prog_read: "Dosya okunuyor...", prog_ai: "AI analiz yapıyor...", prog_map: "Kolonlar eşleştiriliyor...", prog_save: "Veritabanına kaydediliyor...", prog_done: "Tamamlandı!",
    health_ok: "Sistem Sağlıklı", health_warn: "Kısmi Sorun", health_err: "Bağlanamadı",
    dash_categories: "Analiz Kategorileri", dash_no_categories: "Henüz kategori verisi yok", dash_recent_jobs: "Son İşler", dash_see_all: "Tümünü Gör →",
    err_load_jobs: "İşler yüklenemedi: ", err_unsupported: "Desteklenmeyen dosya türü: ", err_too_large: "Dosya çok büyük (maks 50MB)", err_no_file: "Önce dosya seçin",
    btn_loading: "Yükleniyor...", upload_success: "✅ Dosya yüklendi! AI analiz başladı.", err_upload: "Yükleme hatası: ",
    err_tpl_name: "Şablon adı zorunlu", err_tpl_cols: "En az bir kolon eklemelisiniz", err_tpl_save: "Şablon kaydedilemedi", tpl_success: "Şablon başarıyla oluşturuldu!",
    err_general: "Hata: ", msg_job_deleted: "İş silindi", err_delete: "Silme hatası: ", confirm_delete: "Bu işi silmek istediğinizden emin misiniz?",
    status_pending: "⏳ Bekliyor", status_processing: "⚙️ İşleniyor", status_completed: "✅ Tamamlandı", status_failed: "❌ Hatalı", status_cancelled: "🚫 İptal",
    time_just_now: "Az önce", time_mins: " dk önce", time_hrs: " sa önce", time_days: " gün önce",
    cat_mobile: "🚗 Mobil Yanma", cat_stat: "🏭 Sabit Yanma", cat_elec: "⚡ Elektrik", cat_ref: "❄️ Soğutucu", cat_waste: "🗑️ Atık",
    cat_water: "💧 Su", cat_biz_travel: "✈️ İş Seyahati", cat_commute: "🚌 Çalışan Ulaşım", cat_goods: "📦 Satın Alınan Mal", cat_other: "📋 Diğer",
    dash_stats_title: "📊 Veri Kalitesi", dash_stats_high: "Yüksek", dash_stats_mid: "Orta", dash_stats_low: "Düşük", dash_stats_valid: "geçerli", dash_stats_err: "hatalı satır",
    dash_col_maps: "🗂️ Kolon Eşleştirmeleri", map_src: "Kaynak Kolon", map_tgt: "Hedef Alan", map_conf: "Güven", map_notes: "Notlar",
    dash_ai_summary: "🤖 AI Özeti", dash_no_ai: "Henüz analiz tamamlanmadı.", dash_issues: "⚠️ Sorunlar & Öneriler", dash_preview: "📋 Veri Önizleme", dash_preview_first: "İlk",
    dash_status: "Durum"
  },
  en: {
    dashboard_title: "Dashboard", dashboard_subtitle: "Overview and statistics",
    checking: "System Healthy", upload_btn: "Upload File",
    nav_dashboard: "Dashboard", nav_upload: "Upload File", nav_templates: "Templates", nav_jobs: "Jobs",
    ai_active: "Gemini AI Active",
    stat_jobs: "Total Jobs", stat_records: "Total Records", stat_valid: "Valid Records", stat_quality: "Avg. Quality",
    templates_title: "Saved Templates", new_template_btn: "+ New Template",
    loading: "Loading...", empty_templates: "No templates created yet.",
    upload_subtitle: "Upload Excel or CSV, AI will analyze",
    jobs_subtitle: "All upload and processing jobs",
    templates_subtitle: "AI maps your data to these templates",
    no_jobs_yet: "No jobs yet.", upload_file_link: "Upload a file", upload_first_file: "Upload First File",
    select_template_label: "1. Select Target Template", select_template_desc: "AI will adapt your uploaded file to the columns in this template.",
    upload_drop_title: "Upload Excel / CSV File", upload_drop_subtitle: "Drag and drop or click to select", upload_drop_hint: "Supported formats: .xlsx, .xls, .csv — Max 50MB", upload_btn_select: "Select File",
    feat_ai_title: "Smart Column Recognition", feat_ai_desc: "Automatically detects Turkish and English headers",
    feat_cat_title: "Auto Categorization", feat_cat_desc: "Automatically detects data type",
    feat_qa_title: "Data Quality Control", feat_qa_desc: "Reports missing and invalid rows",
    feat_exp_title: "CSV / JSON Export", feat_exp_desc: "Download cleaned data in any format",
    upload_submit_btn: "Analyze with AI",
    filter_all: "All", filter_pending: "Pending", filter_processing: "Processing", filter_completed: "Completed", filter_failed: "Failed", btn_refresh: "Refresh",
    default_tpl: "Default ERP Template (Date, Amount, Description, Cost)",
    empty_recent_jobs: "No jobs yet.",
    filter_no_jobs: "No jobs found for this filter",
    job_rows: "Rows", job_valid: "Valid", job_error: "Error", job_quality: "Quality",
    job_detail_title: "Job Detail", create_tpl_title: "Create New Template",
    tpl_name_lbl: "Template Name", tpl_name_ph: "E.g. E-Commerce",
    tpl_desc_lbl: "Description", tpl_desc_ph: "Product import template",
    tpl_cols_lbl: "Target Columns (AI will map to these)", tpl_add_col: "+ Add Column", tpl_save: "Save Template",
    col_name_ph: "Column Name (E.g. price)", col_desc_ph: "Description",
    type_string: "Text", type_number: "Number", type_date: "Date",
    prog_read: "Reading file...", prog_ai: "AI analyzing...", prog_map: "Mapping columns...", prog_save: "Saving to database...", prog_done: "Completed!",
    health_ok: "System Healthy", health_warn: "Partial Issue", health_err: "Cannot Connect",
    dash_categories: "Analysis Categories", dash_no_categories: "No category data yet", dash_recent_jobs: "Recent Jobs", dash_see_all: "See All →",
    err_load_jobs: "Failed to load jobs: ", err_unsupported: "Unsupported file type: ", err_too_large: "File is too large (max 50MB)", err_no_file: "Please select a file first",
    btn_loading: "Loading...", upload_success: "✅ File uploaded! AI analysis started.", err_upload: "Upload error: ",
    err_tpl_name: "Template name is required", err_tpl_cols: "You must add at least one column", err_tpl_save: "Template could not be saved", tpl_success: "Template created successfully!",
    err_general: "Error: ", msg_job_deleted: "Job deleted", err_delete: "Delete error: ", confirm_delete: "Are you sure you want to delete this job?",
    status_pending: "⏳ Pending", status_processing: "⚙️ Processing", status_completed: "✅ Completed", status_failed: "❌ Failed", status_cancelled: "🚫 Cancelled",
    time_just_now: "Just now", time_mins: " mins ago", time_hrs: " hrs ago", time_days: " days ago",
    cat_mobile: "🚗 Mobile Comb.", cat_stat: "🏭 Stat. Comb.", cat_elec: "⚡ Electricity", cat_ref: "❄️ Refrigerants", cat_waste: "🗑️ Waste",
    cat_water: "💧 Water", cat_biz_travel: "✈️ Business Travel", cat_commute: "🚌 Commuting", cat_goods: "📦 Purchased Goods", cat_other: "📋 Other",
    dash_stats_title: "📊 Data Quality", dash_stats_high: "High", dash_stats_mid: "Medium", dash_stats_low: "Low", dash_stats_valid: "valid", dash_stats_err: "error rows",
    dash_col_maps: "🗂️ Column Mappings", map_src: "Source Column", map_tgt: "Target Field", map_conf: "Confidence", map_notes: "Notes",
    dash_ai_summary: "🤖 AI Summary", dash_no_ai: "Analysis not completed yet.", dash_issues: "⚠️ Issues & Recommendations", dash_preview: "📋 Data Preview", dash_preview_first: "First",
    dash_status: "Status"
  }
};

function changeLanguage(lang) {
  currentLang = lang;
  localStorage.setItem('lang', lang);
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (i18n[lang] && i18n[lang][key]) {
      // If the element has children (like the SVG in the button), preserve them
      if(el.children.length > 0) {
        const textNode = Array.from(el.childNodes).find(n => n.nodeType === 3 && n.textContent.trim().length > 0);
        if(textNode) textNode.textContent = ' ' + i18n[lang][key];
      } else {
        el.textContent = i18n[lang][key];
      }
    }
  });

  document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
    const key = el.getAttribute('data-i18n-placeholder');
    if (i18n[lang] && i18n[lang][key]) {
      el.placeholder = i18n[lang][key];
    }
  });

  // Re-run showPage if titleEl has dataset pageName to refresh subtitles
  const titleEl = document.getElementById('pageTitle');
  if (titleEl && titleEl.dataset.pageName) {
    showPage(titleEl.dataset.pageName);
  }
}

// Initial language setup
document.addEventListener('DOMContentLoaded', () => {
  const select = document.getElementById('langSelect');
  if(select) select.value = currentLang;
  changeLanguage(currentLang);
});

/* ─── Page Navigation ──────────────────────────────────────── */
function showPage(name) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));

  document.getElementById(`page-${name}`).classList.add('active');
  const navEl = document.getElementById(`nav-${name}`);
  if (navEl) navEl.classList.add('active');

  const titles = {
    dashboard: [i18n[currentLang].dashboard_title, i18n[currentLang].dashboard_subtitle],
    upload: [i18n[currentLang].nav_upload, i18n[currentLang].upload_subtitle],
    jobs: [i18n[currentLang].nav_jobs, i18n[currentLang].jobs_subtitle],
    templates: [i18n[currentLang].nav_templates, i18n[currentLang].templates_subtitle],
  };
  const [title, sub] = titles[name] || [name, ''];
  const titleEl = document.getElementById('pageTitle');
  titleEl.textContent = title;
  titleEl.dataset.pageName = name;
  document.getElementById('pageSubtitle').textContent = sub;

  if (name === 'dashboard') loadDashboard();
  if (name === 'jobs') loadJobs();
  if (name === 'templates' || name === 'upload') loadTemplates();
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
    const data = await fetch('/api/health').then(r => r.json());
    const dot = document.getElementById('healthDot');
    const txt = document.getElementById('healthText');
    if (data.status === 'healthy') {
      dot.className = 'health-dot ok';
      txt.textContent = i18n[currentLang].health_ok;
    } else {
      dot.className = 'health-dot warn';
      txt.textContent = i18n[currentLang].health_warn;
    }
  } catch {
    document.getElementById('healthDot').className = 'health-dot err';
    document.getElementById('healthText').textContent = i18n[currentLang].health_err;
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
    el.innerHTML = `<div class="empty-state"><p>${i18n[currentLang].empty_recent_jobs} <a href="#" onclick="showPage('upload')">${i18n[currentLang].upload_file_link}</a></p></div>`;
    return;
  }
  el.innerHTML = jobs.map(j => `
    <div class="recent-job-item" onclick="openJobModal('${j.id}')">
      ${statusBadge(j.status)}
      <span class="rj-name">${j.original_filename}</span>
      <span class="rj-rows">${j.total_rows} ${i18n[currentLang].job_rows.toLowerCase()}</span>
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
          <p>${i18n[currentLang].filter_no_jobs}</p>
          <button class="btn btn-primary btn-sm" onclick="showPage('upload')">${i18n[currentLang].upload_btn}</button>
        </div>`;
      return;
    }
    el.innerHTML = jobs.map(j => jobCard(j)).join('');
  } catch (e) {
    toast(i18n[currentLang].err_load_jobs + e.message, 'error');
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
          <div class="job-stat-lbl">${i18n[currentLang].job_rows}</div>
        </div>
        <div class="job-stat">
          <div class="job-stat-val" style="color:var(--success)">${j.processed_rows}</div>
          <div class="job-stat-lbl">${i18n[currentLang].job_valid}</div>
        </div>
        <div class="job-stat">
          <div class="job-stat-val" style="color:var(--error)">${j.error_rows}</div>
          <div class="job-stat-lbl">${i18n[currentLang].job_error}</div>
        </div>
        ${qualityPct > 0 ? `<div class="job-stat"><div class="job-stat-val" style="color:var(--warning)">${qualityPct}%</div><div class="job-stat-lbl">${i18n[currentLang].job_quality}</div></div>` : ''}
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
  document.getElementById('modalBody').innerHTML = `<div class="empty-state"><p>${i18n[currentLang].loading}</p></div>`;

  try {
    const [job, recData] = await Promise.all([
      apiFetch(`/upload/jobs/${jobId}`),
      apiFetch(`/upload/jobs/${jobId}/records?page=1&page_size=20`),
    ]);

    document.getElementById('modalTitle').textContent = job.original_filename;
    document.getElementById('modalSubtitle').innerHTML =
      `${job.total_rows} satır &middot; ${timeAgo(job.created_at)} &middot; ${statusBadge(job.status)}`;

    const mappings = job.column_mappings?.mappings || [];
    const issues   = job.column_mappings?.data_quality_issues || [];
    const missing  = job.column_mappings?.missing_fields || [];
    const recs     = job.column_mappings?.recommendations || [];
    const qualPct  = job.data_quality_score ? Math.round(job.data_quality_score * 100) : 0;
    const qualColor = qualPct >= 80 ? 'var(--success)' : qualPct >= 50 ? 'var(--warning)' : 'var(--error)';

    document.getElementById('modalBody').innerHTML = `
      <!-- AI Summary -->
      <div class="modal-section">
        <div class="modal-section-title">${i18n[currentLang].dash_ai_summary}</div>
        <div class="ai-summary-box">${job.ai_summary || i18n[currentLang].dash_no_ai}</div>
      </div>

      <!-- Quality Score -->
      ${qualPct > 0 ? `
      <div class="modal-section">
        <div class="modal-section-title">${i18n[currentLang].dash_stats_title}</div>
        <div class="quality-ring-wrap">
          <div class="quality-ring" style="background:rgba(${qualPct>=80?'16,185,129':qualPct>=50?'245,158,11':'239,68,68'},0.15);border:3px solid ${qualColor}">
            <span style="color:${qualColor}">${qualPct}%</span>
          </div>
          <div class="quality-info">
            <strong>${qualPct >= 80 ? i18n[currentLang].dash_stats_high : qualPct >= 50 ? i18n[currentLang].dash_stats_mid : i18n[currentLang].dash_stats_low} ${i18n[currentLang].job_quality}</strong>
            <p>${job.processed_rows} ${i18n[currentLang].dash_stats_valid} · ${job.error_rows} ${i18n[currentLang].dash_stats_err}</p>
          </div>
        </div>
      </div>` : ''}

      <!-- Column Mappings -->
      ${mappings.length > 0 ? `
      <div class="modal-section">
        <div class="modal-section-title">${i18n[currentLang].dash_col_maps} (${mappings.length})</div>
        <table class="mapping-table">
          <thead><tr>
            <th>${i18n[currentLang].map_src}</th><th>${i18n[currentLang].map_tgt}</th><th>${i18n[currentLang].map_conf}</th><th>${i18n[currentLang].map_notes}</th>
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
        <div class="modal-section-title">${i18n[currentLang].dash_issues}</div>
        ${issues.map(i => `<div class="issue-item"><span class="issue-icon">⚠️</span>${i}</div>`).join('')}
        ${missing.map(f => `<div class="issue-item"><span class="issue-icon">❓</span>${f}</div>`).join('')}
        ${recs.map(r => `<div class="issue-item"><span class="issue-icon">💡</span>${r}</div>`).join('')}
      </div>` : ''}

      <!-- Records Preview -->
      ${recData.items.length > 0 ? (() => {
        const allKeys = new Set();
        recData.items.forEach(r => {
            if (r.extracted_data) Object.keys(r.extracted_data).forEach(k => allKeys.add(k));
        });
        const dynamicColumns = Array.from(allKeys);
        const translateCol = (c) => {
          const map = {
            tr: { date: "Tarih", description: "Açıklama", amount: "Miktar", cost: "Tutar" },
            en: { tarih: "Date", miktar: "Amount", aciklama: "Description", tutar: "Cost", islem_tarihi: "Date", islem_turu: "Type" }
          };
          if (map[currentLang] && map[currentLang][c.toLowerCase()]) return map[currentLang][c.toLowerCase()];
          return c.charAt(0).toUpperCase() + c.slice(1);
        };
        
        return `
      <div class="modal-section">
        <div class="modal-section-title">${i18n[currentLang].dash_preview} (${i18n[currentLang].dash_preview_first} ${recData.items.length} / ${recData.total})</div>
        <div style="overflow-x:auto">
          <table class="records-table">
            <thead><tr>
              <th>#</th>
              ${dynamicColumns.map(col => `<th>${translateCol(col)}</th>`).join('')}
              <th>${i18n[currentLang].dash_status}</th>
            </tr></thead>
            <tbody>${recData.items.map(r => `
              <tr>
                <td class="mono" style="color:var(--text-muted)">${r.row_number}</td>
                ${dynamicColumns.map(col => {
                    let val = (r.extracted_data || {})[col];
                    if (val == null) return '<td>–</td>';
                    if (typeof val === 'number') return `<td class="mono">${val.toLocaleString()}</td>`;
                    if (typeof val === 'string' && val.length > 15 && val.includes('T')) return `<td class="mono">${val.split('T')[0]}</td>`;
                    return `<td>${val}</td>`;
                }).join('')}
                <td>${r.is_valid
                  ? '<span class="badge badge-completed">✓</span>'
                  : `<span class="badge badge-failed" title="${(r.validation_errors||[]).join(', ')}">✗</span>`}
                </td>
              </tr>`).join('')}
            </tbody>
          </table>
        </div>
      </div>`;
      })() : ''}

      <!-- Export Actions -->
      <div class="modal-export-bar">
        <a class="btn btn-ghost" href="/api/analytics/jobs/${jobId}/export/csv" download>
          📥 CSV
        </a>
        <a class="btn btn-ghost" href="/api/analytics/jobs/${jobId}/export/json" download>
          📥 JSON
        </a>
        <button class="btn btn-ghost" style="color:var(--error)" onclick="deleteJob('${jobId}')">
          🗑️
        </button>
      </div>
    `;
  } catch (e) {
    document.getElementById('modalBody').innerHTML =
      `<div class="empty-state"><p>${i18n[currentLang].err_general}${e.message}</p></div>`;
  }
}

function closeModal() {
  document.getElementById('jobModal').style.display = 'none';
}

async function deleteJob(jobId) {
  if (!confirm(i18n[currentLang].confirm_delete)) return;
  try {
    await apiFetch(`/upload/jobs/${jobId}`, { method: 'DELETE' });
    closeModal();
    toast(i18n[currentLang].msg_job_deleted, 'success');
    loadJobs();
    loadDashboard();
  } catch (e) {
    toast(i18n[currentLang].err_delete + e.message, 'error');
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
    toast(i18n[currentLang].err_unsupported + '.' + ext, 'error');
    return;
  }
  if (file.size > 50 * 1024 * 1024) {
    toast(i18n[currentLang].err_too_large, 'error');
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
  if (!selectedFile) { toast(i18n[currentLang].err_no_file, 'error'); return; }

  const btn = document.getElementById('uploadBtn');
  btn.disabled = true;
  btn.textContent = i18n[currentLang].btn_loading;

  document.getElementById('uploadProgressCard').style.display = 'block';
  setProgressStep(1);
  updateProgress(5, i18n[currentLang].prog_read);

  const fd = new FormData();
  fd.append('file', selectedFile);

  const tplId = document.getElementById('templateSelect')?.value || '';
  let url = API + '/upload';
  const params = new URLSearchParams();
  if (tplId) params.append('template_id', tplId);
  params.append('language', currentLang);
  
  url += '?' + params.toString();

  try {
    const res = await fetch(url, { method: 'POST', body: fd });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || i18n[currentLang].err_upload);
    }
    const data = await res.json();
    toast(i18n[currentLang].upload_success, 'success');
    updateProgress(15, i18n[currentLang].prog_ai);
    setProgressStep(2);
    pollJobProgress(data.job_id, btn);
  } catch (e) {
    toast(i18n[currentLang].err_upload + e.message, 'error');
    btn.disabled = false;
    btn.innerHTML = i18n[currentLang].upload_submit_btn;
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
        updateProgress(100, '✅ ' + i18n[currentLang].prog_done);
        setProgressStep(4, true);
        
        const qScore = Math.round((job.data_quality_score||0)*100);
        const msg = currentLang === 'en' 
          ? `✅ ${job.processed_rows} records processed! Quality: ${qScore}%`
          : `✅ ${job.processed_rows} kayıt işlendi! Kalite: ${qScore}%`;
        toast(msg, 'success');
        
        btn.disabled = false;
        btn.innerHTML = i18n[currentLang].upload_submit_btn;
        setTimeout(() => { clearFile(); showPage('jobs'); }, 2000);
      } else if (job.status === 'failed') {
        clearInterval(pollTimer);
        const errMsg = currentLang === 'en' ? '❌ Process failed: ' : '❌ İşlem başarısız: ';
        toast(errMsg + (job.error_message || ''), 'error');
        updateProgress(0, currentLang === 'en' ? '❌ Error occurred' : '❌ Hata oluştu');
        btn.disabled = false;
        btn.innerHTML = i18n[currentLang].upload_submit_btn;
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
  if (pct < 15) return i18n[currentLang].prog_read;
  if (pct < 40) return i18n[currentLang].prog_ai;
  if (pct < 70) return i18n[currentLang].prog_map;
  if (pct < 100) return i18n[currentLang].prog_save;
  return i18n[currentLang].prog_done;
}

function formatBytes(bytes) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/* ─── Templates Logic ────────────────────────────────────────── */
async function loadTemplates() {
  try {
    const templates = await apiFetch('/templates');
    const list = document.getElementById('templatesList');
    const select = document.getElementById('templateSelect');

    let selectOptions = `<option value="" style="color:black">${i18n[currentLang].default_tpl}</option>`;
    let listHTML = '';

    if (templates.length === 0) {
      listHTML = `<div class="empty-state"><p>${i18n[currentLang].empty_templates}</p></div>`;
    } else {
      const defaultTplsEN = {
        "E-Ticaret Ürün Kataloğu": { name: "E-Commerce Product Catalog", desc: "Standard e-commerce import template including product, stock and pricing." },
        "İnsan Kaynakları - Personel ve Maaş": { name: "HR - Personnel and Salary", desc: "Used for mapping employee salary and department data." },
        "Banka Ekstresi": { name: "Bank Statement", desc: "Converts bank account transactions to a standard format." },
        "Araç Yakıt Tüketimi (Klasik ERP)": { name: "Vehicle Fuel Consumption (Classic ERP)", desc: "Analyzes vehicle, plate and fuel costs like legacy systems." }
      };

      templates.forEach(t => {
        let tName = t.name;
        let tDesc = t.description;
        if (currentLang === 'en' && defaultTplsEN[t.name]) {
          tName = defaultTplsEN[t.name].name;
          tDesc = defaultTplsEN[t.name].desc;
        }

        selectOptions += `<option value="${t.id}" style="color:black">${tName}</option>`;
        listHTML += `
          <div style="border:1px solid var(--border);border-radius:8px;padding:16px;margin-bottom:12px;background:var(--bg-body)">
            <h3 style="margin-bottom:4px;font-size:16px;color:var(--text-primary)">${tName}</h3>
            <p style="color:var(--text-secondary);font-size:13px;margin-bottom:12px;">${tDesc || ''}</p>
            <div style="display:flex;gap:8px;flex-wrap:wrap;">
              ${t.target_schema.map(f => `<span style="background:var(--bg-card);border:1px solid var(--border);color:var(--text-primary);padding:4px 8px;border-radius:4px;font-size:12px;">${f.name} <span style="opacity:0.5">(${f.type})</span></span>`).join('')}
            </div>
          </div>
        `;
      });
    }

    if(list) list.innerHTML = listHTML;
    if(select) select.innerHTML = selectOptions;
  } catch(e) {
    console.error("Templates error:", e);
  }
}

function showCreateTemplateModal() {
  document.getElementById('templateModal').style.display = 'flex';
  document.getElementById('tplName').value = '';
  document.getElementById('tplDesc').value = '';
  document.getElementById('tplFields').innerHTML = '';
  addTemplateField(); // add first field
}

function closeTemplateModal() {
  document.getElementById('templateModal').style.display = 'none';
}

function addTemplateField() {
  const div = document.createElement('div');
  div.style.display = 'flex';
  div.style.gap = '8px';
  div.innerHTML = `
    <input type="text" class="tpl-f-name" placeholder="${i18n[currentLang].col_name_ph}" style="flex:2;padding:8px;border-radius:6px;border:1px solid var(--border);background:var(--bg-body);color:white">
    <select class="tpl-f-type" style="flex:1;padding:8px;border-radius:6px;border:1px solid var(--border);background:var(--bg-body);color:white">
      <option value="string" style="color:black">${i18n[currentLang].type_string}</option>
      <option value="number" style="color:black">${i18n[currentLang].type_number}</option>
      <option value="date" style="color:black">${i18n[currentLang].type_date}</option>
    </select>
    <input type="text" class="tpl-f-desc" placeholder="${i18n[currentLang].col_desc_ph}" style="flex:3;padding:8px;border-radius:6px;border:1px solid var(--border);background:var(--bg-body);color:white">
    <button class="btn btn-ghost btn-sm" style="color:var(--error)" onclick="this.parentElement.remove()">✕</button>
  `;
  document.getElementById('tplFields').appendChild(div);
}

async function saveTemplate() {
  const name = document.getElementById('tplName').value.trim();
  const desc = document.getElementById('tplDesc').value.trim();
  if (!name) return toast(i18n[currentLang].err_tpl_name, 'error');

  const schema = [];
  document.querySelectorAll('#tplFields > div').forEach(row => {
    const fName = row.querySelector('.tpl-f-name').value.trim();
    const fType = row.querySelector('.tpl-f-type').value;
    const fDesc = row.querySelector('.tpl-f-desc').value.trim();
    if (fName) {
      schema.push({ name: fName, type: fType, description: fDesc });
    }
  });

  if (schema.length === 0) return toast(i18n[currentLang].err_tpl_cols, 'error');

  try {
    const res = await fetch(API + '/templates', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, description: desc, target_schema: schema })
    });
    if(!res.ok) throw new Error(i18n[currentLang].err_tpl_save);
    
    toast(i18n[currentLang].tpl_success, 'success');
    closeTemplateModal();
    loadTemplates();
  } catch (e) {
    toast(i18n[currentLang].err_general + e.message, 'error');
  }
}

/* ─── Helpers ──────────────────────────────────────────────── */
function statusBadge(status) {
  const map = {
    pending:    ['badge-pending',    i18n[currentLang].status_pending],
    processing: ['badge-processing', i18n[currentLang].status_processing],
    completed:  ['badge-completed',  i18n[currentLang].status_completed],
    failed:     ['badge-failed',     i18n[currentLang].status_failed],
    cancelled:  ['badge-pending',    i18n[currentLang].status_cancelled],
  };
  const [cls, label] = map[status] || ['badge-pending', status];
  return `<span class="badge ${cls}">${label}</span>`;
}

function categoryLabel(cat) {
  const map = {
    mobile_combustion:    i18n[currentLang].cat_mobile,
    stationary_combustion:i18n[currentLang].cat_stat,
    electricity:          i18n[currentLang].cat_elec,
    refrigerants:         i18n[currentLang].cat_ref,
    waste:                i18n[currentLang].cat_waste,
    water:                i18n[currentLang].cat_water,
    business_travel:      i18n[currentLang].cat_biz_travel,
    employee_commuting:   i18n[currentLang].cat_commute,
    purchased_goods:      i18n[currentLang].cat_goods,
    other:                i18n[currentLang].cat_other,
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
  if (mins < 1)    return i18n[currentLang].time_just_now;
  if (mins < 60)   return `${mins}${i18n[currentLang].time_mins}`;
  if (hours < 24)  return `${hours}${i18n[currentLang].time_hrs}`;
  return `${days}${i18n[currentLang].time_days}`;
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
