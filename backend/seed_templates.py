import asyncio
import os
import sys

# Add parent directory to path to allow importing backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import AsyncSessionLocal
from backend.models import MappingTemplate

async def seed_templates():
    print("Veritabanına varsayılan şablonlar ekleniyor...")
    
    templates = [
        MappingTemplate(
            name="E-Ticaret Ürün Kataloğu",
            description="Ürün, stok ve fiyat bilgilerini içeren standart e-ticaret aktarım şablonu.",
            target_schema=[
                {"name": "urun_kodu", "type": "string", "description": "Benzersiz ürün SKU kodu"},
                {"name": "urun_adi", "type": "string", "description": "Ürünün tam adı"},
                {"name": "kategori", "type": "string", "description": "Ürün kategorisi veya grubu"},
                {"name": "fiyat", "type": "number", "description": "Satış fiyatı"},
                {"name": "stok_miktari", "type": "number", "description": "Eldeki mevcut stok adedi"}
            ]
        ),
        MappingTemplate(
            name="İnsan Kaynakları - Personel ve Maaş",
            description="Çalışanların maaş ve departman verilerini eşleştirmek için kullanılır.",
            target_schema=[
                {"name": "sicil_no", "type": "string", "description": "Personel sicil veya kimlik numarası"},
                {"name": "ad_soyad", "type": "string", "description": "Personelin tam adı ve soyadı"},
                {"name": "departman", "type": "string", "description": "Çalıştığı bölüm"},
                {"name": "maas", "type": "number", "description": "Net veya brüt maaş tutarı"},
                {"name": "ise_giris_tarihi", "type": "date", "description": "İşe başlama tarihi"}
            ]
        ),
        MappingTemplate(
            name="Banka Ekstresi",
            description="Banka hesap hareketlerini standart bir formata dönüştürür.",
            target_schema=[
                {"name": "islem_tarihi", "type": "date", "description": "Hareketin gerçekleştiği tarih"},
                {"name": "aciklama", "type": "string", "description": "İşlem açıklaması, gönderen/alan bilgisi"},
                {"name": "islem_turu", "type": "string", "description": "Gelen Havale, Giden EFT, Kart İşlemi vb."},
                {"name": "tutar", "type": "number", "description": "İşlem tutarı (Giren/Çıkan)"},
                {"name": "bakiye", "type": "number", "description": "İşlem sonrası güncel bakiye"}
            ]
        ),
        MappingTemplate(
            name="Araç Yakıt Tüketimi (Klasik ERP)",
            description="Eski sistemdeki gibi araç, plaka ve yakıt masraflarını analiz eder.",
            target_schema=[
                {"name": "tarih", "type": "date", "description": "Yakıt alım tarihi"},
                {"name": "plaka", "type": "string", "description": "Aracın plakası"},
                {"name": "yakit_tipi", "type": "string", "description": "Benzin, Motorin, LPG vb."},
                {"name": "miktar_litre", "type": "number", "description": "Alınan yakıtın litre bazında miktarı"},
                {"name": "toplam_tutar", "type": "number", "description": "Fatura tutarı"}
            ]
        )
    ]

    async with AsyncSessionLocal() as db:
        for tpl in templates:
            db.add(tpl)
        await db.commit()
    
    print("✅ Varsayılan şablonlar başarıyla eklendi!")

if __name__ == "__main__":
    asyncio.run(seed_templates())
