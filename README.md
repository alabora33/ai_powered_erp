<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=6366f1&height=200&section=header&text=AI%20ERP&fontSize=72&fontColor=ffffff&animation=fadeIn&fontAlignY=38&desc=AI-Powered%20Excel%20%2F%20ERP%20Data%20Mapping%20System&descAlignY=55&descAlign=50" width="100%"/>

[![CI](https://github.com/alabora33/ai_powered_erp/actions/workflows/ci.yml/badge.svg)](https://github.com/alabora33/ai_powered_erp/actions/workflows/ci.yml)
[![CD](https://github.com/alabora33/ai_powered_erp/actions/workflows/cd.yml/badge.svg)](https://github.com/alabora33/ai_powered_erp/actions/workflows/cd.yml)
[![Python](https://img.shields.io/badge/Python-3.12-3776ab?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://docker.com)
[![Gemini](https://img.shields.io/badge/Gemini-AI-4285F4?logo=google&logoColor=white)](https://ai.google.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**[🇹🇷 Türkçe](#-türkçe) · [🇬🇧 English](#-english)**

</div>

---

# 🇹🇷 Türkçe

## 🎯 Proje Nedir?

**AI ERP**, şirketlerin farklı formatlarda tuttuğu Excel, CSV ve ERP çıktı dosyalarını yapay zeka ile **otomatik olarak analiz eden** ve **standart bir veri modeline dönüştüren** bir sistemdir.

> Gerçek bir iş problemini çözüyor: "Mazot Litre", "Fuel Consumption (L)", "yakıt_lt" gibi farklı başlıkları AI tek bir standarda indirgüyor.

### 🔄 Örnek Dönüşüm

```
📄 KAYNAK DOSYA                    →   🗂️ STANDART MODEL
─────────────────────────────────────────────────────────
Yakıt Tüketimi: Mazot              →   fuel_type     = "diesel"
Litre                              →   amount        = <sayı>
Tarih                              →   date          = ISO format
Araç Plaka                         →   vehicle_id    = "34ABC123"
Tedarikçi Firma                    →   supplier      = <metin>
Fatura Tutarı                      →   cost          = <sayı>
─────────────────────────────────────────────────────────
  emission_category = "mobile_combustion"  ← AI otomatik tespit etti
```

---

## 🤖 AI Özellikleri

| Özellik | Açıklama |
|---|---|
| 🧠 **Kolon Anlamlandırma** | Türkçe/İngilizce başlıkları otomatik tanır |
| 🗂️ **Kategori Tahmini** | Emisyon türünü tespit eder (araç, elektrik, atık...) |
| ❓ **Eksik Alan Tespiti** | Hangi zorunlu alanların eksik olduğunu raporlar |
| ✅ **Veri Kalite Skoru** | Her dosya için 0–100 arası güven skoru |
| ⚠️ **Hatalı Satır Raporu** | Hangi satırlarda sorun olduğunu açıklar |
| 📝 **Otomatik Açıklama** | Her kayıt için insan okunabilir açıklama üretir |
| 🔄 **Fallback Heuristic** | AI erişilemezse kural tabanlı eşleştirme yapar |

---

## 🏗️ Mimari

```
┌────────────────────────────────────────────────┐
│           Frontend – Dark Mode SPA              │
│         Drag & Drop · Real-time Progress        │
│              http://localhost:3000              │
└───────────────────┬────────────────────────────┘
                    │ REST API
┌───────────────────▼────────────────────────────┐
│              FastAPI Backend                    │
│    /api/upload  /api/analytics  /health         │
│           http://localhost:8000                 │
└──────┬────────────────┬───────────────┬─────────┘
       │                │               │
  ┌────▼────┐    ┌──────▼──────┐  ┌────▼──────────┐
  │PostgreSQL│   │ Redis Broker │  │  Gemini AI    │
  │  :5432  │   │    :6379     │  │   (Google)    │
  └─────────┘   └──────┬───────┘  └───────────────┘
                       │
               ┌───────▼───────┐
               │ Celery Worker │
               │  Background   │
               └───────┬───────┘
                       │
               ┌───────▼───────┐
               │    Flower     │
               │  Monitoring   │
               │    :5555      │
               └───────────────┘
```

---

## 🚀 Kurulum (5 Dakikada Çalıştır)

### Ön Gereksinimler

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) ✅
- Git ✅
- Gemini API Key ([buradan ücretsiz alın](https://aistudio.google.com/app/apikey)) ✅

### Adımlar

```bash
# 1. Repoyu klonla
git clone https://github.com/alabora33/ai_powered_erp.git
cd ai_powered_erp

# 2. Environment dosyasını hazırla
cp .env.example .env
```

`.env` dosyasını açıp şu satırı düzenle:
```env
GEMINI_API_KEY=senin_gemini_api_keyin_buraya
```

```bash
# 3. Tüm servisleri başlat
docker compose up -d

# 4. Logları izle (isteğe bağlı)
docker compose logs -f api
```

### Erişim Noktaları

| Servis | URL | Açıklama |
|---|---|---|
| 🌐 **Frontend** | http://localhost:3000 | Ana uygulama |
| 📚 **API Docs** | http://localhost:8000/api/docs | Swagger UI |
| 📖 **Redoc** | http://localhost:8000/api/redoc | Alternatif API dokümantasyon |
| 🌸 **Flower** | http://localhost:5555 | Celery task monitoring |
| 💚 **Health** | http://localhost:8000/health | Sistem sağlık durumu |

---

## 📁 Proje Yapısı

```
ai_powered_erp/
│
├── 📂 backend/                    # FastAPI uygulaması
│   ├── main.py                   # Giriş noktası, middleware, routing
│   ├── config.py                 # Pydantic Settings (env vars)
│   ├── database.py               # Async SQLAlchemy engine + session
│   ├── models.py                 # ORM modelleri (UploadJob, MappedRecord)
│   ├── schemas.py                # Pydantic request/response şemaları
│   ├── ai_service.py             # ✨ Gemini AI entegrasyonu
│   ├── data_processor.py         # Excel/CSV okuma + dönüşüm motoru
│   ├── celery_app.py             # Celery yapılandırması
│   ├── tasks.py                  # Async işleme görevleri (5 adım)
│   └── routers/
│       ├── upload.py             # Upload, job yönetimi endpoint'leri
│       └── analytics.py          # Dashboard + CSV/JSON export
│
├── 📂 frontend/                   # Vanilla JS SPA (dark mode)
│   ├── index.html                # HTML yapısı
│   ├── styles.css                # Dark mode CSS + animasyonlar
│   └── app.js                    # Uygulama mantığı + API çağrıları
│
├── 📂 .github/
│   └── workflows/
│       ├── ci.yml                # 🧪 Test + Lint + Docker build
│       ├── cd.yml                # 🚀 Docker push + Release
│       └── label.yml             # 🏷️ PR otomatik etiketleme
│
├── 📂 tests/
│   ├── test_data_processor.py    # Data processor unit testleri
│   └── test_api.py               # FastAPI integration testleri
│
├── docker-compose.yml            # Tüm servislerin orchestration'ı
├── Dockerfile                    # Python uygulama container'ı
├── nginx.conf                    # Reverse proxy + static files
├── requirements.txt              # Python bağımlılıkları
├── init.sql                      # PostgreSQL başlangıç şeması
├── pyproject.toml                # Pytest + Ruff konfigürasyonu
├── .env.example                  # Örnek environment dosyası
└── README.md                     # Bu dosya
```

---

## 🔌 API Referansı

```bash
# ── Dosya Yükleme ────────────────────────────────────────────
POST   /api/upload                           # Dosya yükle → job_id al
GET    /api/upload/jobs                      # Tüm işleri listele
GET    /api/upload/jobs/{job_id}             # İş durumunu sorgula
GET    /api/upload/jobs/{job_id}/records     # İşlenen kayıtları getir
DELETE /api/upload/jobs/{job_id}             # İşi sil

# ── Analitik & Export ─────────────────────────────────────────
GET    /api/analytics/dashboard              # Dashboard istatistikleri
GET    /api/analytics/jobs/{job_id}/export/csv   # CSV export
GET    /api/analytics/jobs/{job_id}/export/json  # JSON export

# ── Sistem ────────────────────────────────────────────────────
GET    /health                               # Sağlık durumu
GET    /api/docs                             # Swagger UI
```

---

## 🧪 Testleri Çalıştırma

```bash
# Docker container içinde
docker compose exec api pytest tests/ -v

# Yerel (virtual env)
pytest tests/ --cov=backend --cov-report=term-missing -v
```

---

## 🛠️ Geliştirme

```bash
# Servisi yeniden başlat
docker compose restart api

# Logları izle
docker compose logs -f api worker

# Worker sayısını artır
docker compose scale worker=3

# Sıfırdan başlat (veriyi sil)
docker compose down -v && docker compose up -d
```

---

## 📊 Desteklenen Emisyon Kategorileri

| Kategori | Açıklama | Örnek Kaynak Verisi |
|---|---|---|
| `mobile_combustion` | Araç yakıt tüketimi | Mazot, Benzin, Litre |
| `stationary_combustion` | Sabit tesisler | Kazan, Jeneratör, Doğalgaz |
| `electricity` | Elektrik tüketimi | kWh, Elektrik faturası |
| `refrigerants` | Soğutucu gaz | Freon, R-22, R-134a |
| `waste` | Atık yönetimi | Ton, m³, Atık miktarı |
| `water` | Su tüketimi | m³, Su faturası |
| `business_travel` | İş seyahatleri | Uçuş, km, Bilet |
| `employee_commuting` | Çalışan ulaşım | Servis, km |

---

---

# 🇬🇧 English

## 🎯 What is AI ERP?

**AI ERP** is a system that automatically analyzes Excel, CSV, and ERP export files using AI and converts them into a **standardized data model**.

> It solves a real business problem: column headers like "Mazot Litre", "Fuel Consumption (L)", and "yakıt_lt" all get mapped to the same standard field — automatically.

### 🔄 Example Transformation

```
📄 SOURCE FILE                     →   🗂️ STANDARD MODEL
─────────────────────────────────────────────────────────
Fuel Type: Mazot (Diesel)          →   fuel_type     = "diesel"
Litre                              →   amount        = <number>
Tarih (Date)                       →   date          = ISO format
Araç Plaka (License Plate)         →   vehicle_id    = "34ABC123"
Tedarikçi (Supplier)               →   supplier      = <text>
Fatura Tutarı (Invoice Amount)     →   cost          = <number>
─────────────────────────────────────────────────────────
  emission_category = "mobile_combustion"  ← detected by AI
```

---

## 🤖 AI Features

| Feature | Description |
|---|---|
| 🧠 **Column Understanding** | Detects Turkish & English headers automatically |
| 🗂️ **Category Classification** | Identifies emission type (vehicle, electricity, waste...) |
| ❓ **Missing Field Detection** | Reports which required fields are absent |
| ✅ **Data Quality Scoring** | Assigns 0–100% confidence score per file |
| ⚠️ **Error Row Reporting** | Explains which rows have issues and why |
| 📝 **Auto Descriptions** | Generates human-readable descriptions for each record |
| 🔄 **Heuristic Fallback** | Rule-based mapping when AI is unavailable |

---

## 🚀 Quick Start (5 Minutes)

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) ✅
- Git ✅
- Gemini API Key ([get one free](https://aistudio.google.com/app/apikey)) ✅

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/alabora33/ai_powered_erp.git
cd ai_powered_erp

# 2. Set up environment
cp .env.example .env
```

Edit `.env` and add your API key:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

```bash
# 3. Start all services
docker compose up -d

# 4. Watch logs (optional)
docker compose logs -f api
```

### Access Points

| Service | URL | Description |
|---|---|---|
| 🌐 **Frontend** | http://localhost:3000 | Main application |
| 📚 **API Docs** | http://localhost:8000/api/docs | Swagger UI |
| 📖 **Redoc** | http://localhost:8000/api/redoc | Alternative API docs |
| 🌸 **Flower** | http://localhost:5555 | Celery task monitoring |
| 💚 **Health** | http://localhost:8000/health | System health status |

---

## ⚙️ Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Backend** | FastAPI + Python 3.12 | Async REST API |
| **AI** | Google Gemini 1.5 Flash | Column analysis + structured output |
| **Database** | PostgreSQL 16 | Persistent storage |
| **Cache/Queue** | Redis 7 | Celery message broker |
| **Task Queue** | Celery | Background file processing |
| **Data** | Pandas + OpenPyXL | Excel/CSV reading |
| **Validation** | Pydantic v2 | Schema enforcement |
| **Monitoring** | Flower | Celery task dashboard |
| **Frontend** | Vanilla HTML/CSS/JS | Dark mode SPA |
| **Proxy** | Nginx | Static files + API proxy |
| **Container** | Docker Compose | Full orchestration |
| **CI/CD** | GitHub Actions | Automated testing + deployment |

---

## 🔌 API Reference

```bash
# ── File Upload ──────────────────────────────────────────────
POST   /api/upload                           # Upload file → get job_id
GET    /api/upload/jobs                      # List all jobs
GET    /api/upload/jobs/{job_id}             # Poll job status & progress
GET    /api/upload/jobs/{job_id}/records     # Get mapped records (paginated)
DELETE /api/upload/jobs/{job_id}             # Delete job and records

# ── Analytics & Export ───────────────────────────────────────
GET    /api/analytics/dashboard              # Dashboard statistics
GET    /api/analytics/jobs/{job_id}/export/csv   # Download as CSV
GET    /api/analytics/jobs/{job_id}/export/json  # Download as JSON

# ── System ───────────────────────────────────────────────────
GET    /health                               # DB + Redis + AI health check
GET    /api/docs                             # Swagger UI (interactive)
GET    /api/redoc                            # ReDoc documentation
```

---

## 🧪 Running Tests

```bash
# Inside Docker
docker compose exec api pytest tests/ -v

# Locally
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate        # Linux/Mac
pip install -r requirements.txt
pytest tests/ --cov=backend -v
```

---

## 🔄 CI/CD Pipeline

```
Push to main branch
        │
        ▼
┌──────────────────────────────────┐
│  CI Workflow (ci.yml)            │
│  1. 🔍 Ruff Lint & Format check  │
│  2. 🧪 Tests (Python 3.11+3.12) │
│     └─ with PostgreSQL + Redis   │
│  3. 🐳 Docker build validation   │
│  4. 🔒 Security vulnerability    │
│     scan (pip-audit)             │
└──────────────┬───────────────────┘
               │ All pass
               ▼
┌──────────────────────────────────┐
│  CD Workflow (cd.yml)            │
│  5. 🐳 Build & push to GHCR     │
│  6. 📦 Create Release (on tag)  │
└──────────────────────────────────┘
```

### Adding Gemini API Key as GitHub Secret

1. Go to your repo → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Name: `GEMINI_API_KEY`
4. Value: `your_api_key_here`

---

## 🗂️ Supported Emission Categories

| Category | Description | Example Source Data |
|---|---|---|
| `mobile_combustion` | Vehicle fuel consumption | Diesel, Gasoline, Litre |
| `stationary_combustion` | Fixed facilities | Boiler, Generator, Natural Gas |
| `electricity` | Power consumption | kWh, Electricity bill |
| `refrigerants` | Refrigerant gases | Freon, R-22, R-134a |
| `waste` | Waste management | Ton, m³, Waste amount |
| `water` | Water consumption | m³, Water bill |
| `business_travel` | Business trips | Flights, km, Tickets |
| `employee_commuting` | Employee transport | Shuttle, km |

---

## 🔒 Security Notes

- The `.env` file is in `.gitignore` — your API key is **never committed**
- Use `.env.example` as a template (it has no real secrets)
- Change `SECRET_KEY` in production
- Restrict `ALLOWED_ORIGINS` in production (not `*`)

---

## 📄 License

MIT License © 2024 Ali Bora

---

<div align="center">

Made with ❤️ using **Gemini AI** · **FastAPI** · **PostgreSQL** · **Celery** · **Docker**

⭐ Star this repo if it helped you!

</div>
