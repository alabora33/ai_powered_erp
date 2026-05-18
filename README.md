# AI ERP – Akıllı Excel / Veri Eşleştirme Sistemi

<div align="center">

![AI ERP Banner](https://img.shields.io/badge/AI%20ERP-v1.0.0-6366f1?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNMTIgMmwzLjA5IDYuMjZMMjIgOS4yN2wtNSA0Ljg3IDEuMTggNi44OEwxMiAxNy43N2wtNi4xOCAzLjI1TDcgMTQuMTQgMiA5LjI3bDYuOTEtMS4wMUwxMiAyeiIgZmlsbD0id2hpdGUiLz48L3N2Zz4=)
![Python](https://img.shields.io/badge/Python-3.12-3776ab?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini-AI-4285F4?style=for-the-badge&logo=google&logoColor=white)

**Excel, fatura, ERP çıktısı veya CSV yükleyin — AI otomatik olarak kolonları tanısın, kategorize etsin ve standart veri modeline dönüştürsün.**

</div>

---

## 🎯 Proje Nedir?

Firmalar farklı formatlarda veri tutar: kimisi "Mazot Litre", kimisi "Fuel Consumption (L)", kimisi "yakıt_lt". Bu sistem AI kullanarak bu farklılıkları otomatik algılar ve hepsini tek bir standart modele dönüştürür.

### Örnek Dönüşüm

| Kaynak Dosya | → | Standart Model |
|---|---|---|
| `Yakıt Tüketimi` | → | `fuel_type = diesel` |
| `Mazot Litre` | → | `amount = litre` |
| `Tarih` | → | `date = invoice_date` |
| `Araç Plaka` | → | `vehicle_id = plate` |
| `Tedarikçi` | → | `supplier` |

---

## 🏗️ Mimari

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (Nginx)                      │
│              Dark Mode SPA – Port 3000                    │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/WS
┌────────────────────▼────────────────────────────────────┐
│                  FastAPI Backend                          │
│              Async REST API – Port 8000                   │
│  /api/upload  /api/analytics  /health  /api/docs         │
└──────┬──────────────────┬──────────────────┬────────────┘
       │                  │                  │
┌──────▼──────┐  ┌────────▼───────┐  ┌──────▼──────────┐
│ PostgreSQL  │  │  Redis Broker  │  │  Gemini AI API  │
│  Port 5432  │  │   Port 6379    │  │   (Google)      │
└─────────────┘  └───────┬────────┘  └─────────────────┘
                         │
                ┌────────▼────────┐
                │  Celery Worker  │
                │ Background Jobs │
                └────────┬────────┘
                         │
                ┌────────▼────────┐
                │ Celery Flower   │
                │  Monitoring     │
                │   Port 5555     │
                └─────────────────┘
```

---

## 🤖 AI Özellikleri

| Özellik | Açıklama |
|---|---|
| **Kolon Anlamlandırma** | Türkçe/İngilizce başlıkları otomatik tanır |
| **Kategori Tahmini** | Emisyon türünü tespit eder (mobile_combustion, electricity...) |
| **Eksik Alan Tespiti** | Hangi zorunlu alanların eksik olduğunu raporlar |
| **Veri Kalite Kontrolü** | Her satır için güven skoru hesaplar |
| **Hatalı Satır Raporu** | Hangi satırlarda sorun olduğunu açıklar |
| **Fallback Heuristic** | AI erişilemezse kural tabanlı eşleştirme yapar |

---

## 🚀 Kurulum

### Ön Gereksinimler

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) kurulu olması
- Git

### 1. Repoyu Klonla

```bash
git clone https://github.com/YOUR_USERNAME/ai_erp.git
cd ai_erp
```

### 2. Environment Dosyasını Hazırla

```bash
cp .env.example .env
# .env dosyasını düzenle:
# GEMINI_API_KEY=your_key_here
```

### 3. Docker ile Başlat

```bash
docker compose up -d
```

### 4. Uygulamaya Eriş

| Servis | URL |
|---|---|
| 🌐 **Frontend** | http://localhost:3000 |
| 📚 **API Docs** | http://localhost:8000/api/docs |
| 🔍 **Redoc** | http://localhost:8000/api/redoc |
| 🌸 **Flower** | http://localhost:5555 |
| 💚 **Health** | http://localhost:8000/health |

---

## 📁 Proje Yapısı

```
ai_erp/
├── backend/
│   ├── main.py           # FastAPI uygulama giriş noktası
│   ├── config.py         # Pydantic Settings (env vars)
│   ├── database.py       # Async SQLAlchemy engine
│   ├── models.py         # ORM modelleri (UploadJob, MappedRecord)
│   ├── schemas.py        # Pydantic request/response şemaları
│   ├── ai_service.py     # Gemini AI entegrasyonu
│   ├── data_processor.py # Excel/CSV okuma ve veri dönüşümü
│   ├── celery_app.py     # Celery konfigürasyonu
│   ├── tasks.py          # Async işleme görevleri
│   └── routers/
│       ├── upload.py     # Upload ve iş yönetimi endpoint'leri
│       └── analytics.py  # Dashboard ve export endpoint'leri
├── frontend/
│   ├── index.html        # SPA HTML yapısı
│   ├── styles.css        # Dark mode CSS (vanilla)
│   └── app.js            # Uygulama mantığı
├── docker-compose.yml    # Tüm servislerin orchestration'ı
├── Dockerfile            # Python uygulama container'ı
├── nginx.conf            # Nginx reverse proxy
├── requirements.txt      # Python bağımlılıkları
├── init.sql              # PostgreSQL başlangıç SQL
├── .env                  # Environment değişkenleri (git'e eklenmez)
└── .env.example          # Örnek env dosyası
```

---

## 🔌 API Referansı

### Upload

```bash
# Dosya yükle
POST /api/upload
Content-Type: multipart/form-data
Body: file=<your-file>

# İş durumu sorgula
GET /api/upload/jobs/{job_id}

# Tüm işleri listele
GET /api/upload/jobs?limit=20&status=completed

# İşin kayıtlarını getir (sayfalı)
GET /api/upload/jobs/{job_id}/records?page=1&page_size=50

# İşi sil
DELETE /api/upload/jobs/{job_id}
```

### Analytics & Export

```bash
# Dashboard istatistikleri
GET /api/analytics/dashboard

# CSV export
GET /api/analytics/jobs/{job_id}/export/csv

# JSON export
GET /api/analytics/jobs/{job_id}/export/json
```

---

## 🛠️ Geliştirme

### Local Geliştirme (Docker olmadan)

```bash
# Python environment
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# PostgreSQL ve Redis'in çalıştığından emin ol
# .env dosyasını local değerlerle güncelle

# API'yi başlat
uvicorn backend.main:app --reload

# Celery worker'ı başlat (ayrı terminal)
celery -A backend.celery_app worker --loglevel=info
```

### Logları Görüntüle

```bash
docker compose logs -f api      # API logs
docker compose logs -f worker   # Celery worker logs
docker compose logs -f db       # PostgreSQL logs
```

### Servisi Yeniden Başlat

```bash
docker compose restart api
docker compose restart worker
```

---

## 📊 Desteklenen Veri Tipleri

| Emisyon Kategorisi | Açıklama |
|---|---|
| `mobile_combustion` | Araç yakıt tüketimi |
| `stationary_combustion` | Sabit tesisler (kazan, jeneratör) |
| `electricity` | Elektrik tüketimi |
| `refrigerants` | Soğutucu gaz kaçakları |
| `waste` | Atık yönetimi |
| `water` | Su tüketimi |
| `business_travel` | İş seyahatleri |
| `employee_commuting` | Çalışan ulaşım |
| `purchased_goods` | Satın alınan mal/hizmet |

---

## 🔒 Güvenlik

- API anahtarı `.env` dosyasında saklanır, Git'e **eklenmez**
- `.gitignore` ile hassas dosyalar korunur
- Production'da `SECRET_KEY` mutlaka değiştirilmeli
- CORS ayarları `ALLOWED_ORIGINS` ile kontrol edilir

---

## 📄 Lisans

MIT License © 2024 Ali Bora

---

<div align="center">
  <strong>Gemini AI</strong> · <strong>FastAPI</strong> · <strong>PostgreSQL</strong> · <strong>Celery</strong> · <strong>Docker</strong>
</div>
