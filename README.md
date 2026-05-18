<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=6366f1&height=200&section=header&text=AI%20ERP&fontSize=72&fontColor=ffffff&animation=fadeIn&fontAlignY=38&desc=AI-Powered%20SaaS%20Data%20Mapping%20%26%20Integration%20Platform&descAlignY=55&descAlign=50" width="100%"/>

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

**AI ERP**, şirketlerin karmaşık Excel, CSV ve ERP çıktı dosyalarını yapay zeka gücüyle **otomatik olarak analiz eden**, yapılandırılmamış verileri okuyup belirlediğiniz **şablonlara (JSON/DB)** dinamik olarak dönüştüren tam kapsamlı bir **SaaS (Hizmet Olarak Yazılım)** platformudur.

> İnsan eli değmeden, "Tutar", "Price", "Miktar (Litre)" gibi karmaşık başlıkları sistemin tek bir standardına dönüştürür. Ayrıca **Banka Ekstreleri** gibi başında 10-15 satır çöp veri bulunan dosyaların başlık satırını yapay zeka ile dinamik olarak tespit eder!

### 🔄 Nasıl Çalışır?

Kullanıcı bir dosya yükler ve hedeflediği "Şablonu" seçer (Örn: Banka Ekstresi, İK Maaş Tablosu). AI dosyayı okur, başlıkları tahmin eder, dönüşümleri yapar ve veritabanına standart formatta kaydeder.

```
📄 KARMAŞIK KAYNAK DOSYA             →   🗂️ SEÇİLEN STANDART ŞABLON (Örn: Banka Ekstresi)
────────────────────────────────────────────────────────────────────────────
Garanti BBVA Ekstresi                →   (Atlanır - Çöp Veri)
TR3300... Numaralı Hesap             →   (Atlanır - Çöp Veri)
Dekont No                            →   id            = <string>
İşlem Zamanı                         →   islem_tarihi  = ISO Format (Date)
Kime / Açıklama                      →   aciklama      = <string>
Giren / Çıkan Tutar                  →   tutar         = <sayı>
────────────────────────────────────────────────────────────────────────────
```

---

## ✨ Öne Çıkan SaaS Özellikleri

| Özellik | Açıklama |
|---|---|
| 🌍 **Tam i18n Desteği** | Kullanıcı arayüzü ve AI raporları tek tıkla **Türkçe / İngilizce** değişir |
| 🗂️ **Dinamik Şablonlar** | E-Ticaret, İK, Bankacılık ve Yakıt tüketimi için dinamik Mapping yeteneği |
| 🧠 **Akıllı Başlık Tespiti** | Dosya başındaki gereksiz logoları ve bilgileri atlayıp asıl veriyi bulur |
| ✅ **Veri Kalite Kontrolü** | AI her satırı kontrol eder, hatalı ve eksik verileri size raporlar |
| 💬 **AI Durum Özeti** | Yapılan işlemi insancıl bir dille özetler ("Bu dosya lojistik firmasına aittir...") |

---

## 🏗️ Mimari

```
┌────────────────────────────────────────────────┐
│           Frontend – Dark Mode SPA              │
│       Drag & Drop · Real-time Translation       │
│              http://localhost:3000              │
└───────────────────┬────────────────────────────┘
                    │ REST API
┌───────────────────▼────────────────────────────┐
│              FastAPI Backend                    │
│    /api/upload  /api/templates  /api/analytics  │
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

---

---

# 🇬🇧 English

## 🎯 What is AI ERP?

**AI ERP** is a comprehensive **SaaS (Software as a Service)** platform that leverages artificial intelligence to **automatically analyze** complex Excel, CSV, and ERP export files, mapping unstructured data dynamically into your defined **templates (JSON/DB)**.

> Completely hands-free, it converts messy column headers like "Price", "Amount (Liter)", or "Tutar" into a single, standardized schema. It even features **Dynamic Header Detection** to intelligently skip metadata, logos, and garbage rows found at the top of files like **Bank Statements**!

### 🔄 How it Works

The user uploads a file and selects a target "Template" (e.g., Bank Statement, HR Salary Table). The AI reads the file, guesses the real table headers, performs the transformations, and saves the records to the database in a standard format.

```
📄 MESSY SOURCE FILE                 →   🗂️ TARGET TEMPLATE (e.g., Bank Statement)
────────────────────────────────────────────────────────────────────────────
Global Bank Statement                →   (Skipped - Garbage data)
Account No: TR3300...                →   (Skipped - Garbage data)
Transaction ID                       →   id            = <string>
Time of Tx                           →   transaction_date = ISO Format (Date)
Recipient / Note                     →   description   = <string>
Incoming / Outgoing                  →   amount        = <number>
────────────────────────────────────────────────────────────────────────────
```

---

## ✨ Key SaaS Features

| Feature | Description |
|---|---|
| 🌍 **Full i18n Support** | The UI, Data Tables, and even the AI-generated summaries switch between **Turkish & English** instantly |
| 🗂️ **Dynamic Templates** | Out-of-the-box mappings for E-Commerce, HR, Banking, and Fuel Consumption domains |
| 🧠 **Smart Header Detection** | Skips preliminary garbage rows and accurately locates where the actual data table begins |
| ✅ **Data Quality Control** | The AI parses every row, reporting errors, invalid values, and missing fields dynamically |
| 💬 **AI Insights** | Provides a human-readable summary of the file ("This file belongs to a logistics firm...") |

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
| 🌸 **Flower** | http://localhost:5555 | Celery task monitoring |

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
