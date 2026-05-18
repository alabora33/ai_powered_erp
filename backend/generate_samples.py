import os
import random
from datetime import datetime, timedelta

import pandas as pd


def generate_samples():
    output_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # 1. E-Ticaret (Dağınık ve Türkçe/İngilizce Karışık)
    ecommerce_data = {
        "SKU Numarası": [f"TR-{random.randint(1000, 9999)}" for _ in range(5)],
        "Product Title": [
            "Mavi Pamuklu Tişört",
            "Kablosuz Kulaklık PRO",
            "Spor Ayakkabı",
            "Termos 1.5L",
            "Mekanik Klavye",
        ],
        "Group/Cat": ["Giyim", "Elektronik", "Ayakkabı", "Kamp", "Bilgisayar"],
        "Satış Bedeli (TL)": [150.50, 899.99, 1250.00, 345.00, 2100.00],
        "Mevcut Adet": [45, 12, 8, 105, 3],
    }
    pd.DataFrame(ecommerce_data).to_excel(
        os.path.join(output_dir, "ornek_eticaret_urunleri.xlsx"), index=False
    )

    # 2. İnsan Kaynakları (Kötü isimlendirmelerle)
    hr_data = {
        "Kimlik/Sicil": ["P001", "P002", "P003", "P004", "P005"],
        "İsim Soyisim": ["Ahmet Yılmaz", "Ayşe Demir", "Mehmet Çelik", "Fatma Şahin", "Can Yıldız"],
        "Bölümü": ["Satış", "IT", "Muhasebe", "Satış", "İnsan Kaynakları"],
        "Net Ödeme": [17002, 35000, 22000, 17500, 28000],
        "Giriş T.": ["01.01.2023", "15.06.2022", "10.09.2023", "01.11.2021", "20.02.2024"],
    }
    pd.DataFrame(hr_data).to_excel(
        os.path.join(output_dir, "ornek_ik_maas_tablosu.xlsx"), index=False
    )

    # 3. Banka Ekstresi
    bank_data = {
        "Tarih": [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(5)],
        "Açıklama Detayı": [
            "Ahmet Yılmaz Kira",
            "Elektrik Faturası",
            "Maaş Ödemesi",
            "Amazon TR Alışveriş",
            "ATM Para Çekme",
        ],
        "Tür": ["Gelen Havale", "Fatura Ödeme", "Kurum Ödemesi", "POS Harcaması", "Nakit"],
        "Tutar": [15000, -850.50, 35000, -1250, -5000],
        "Kalan": [25000, 24149.50, 59149.50, 57899.50, 52899.50],
    }
    pd.DataFrame(bank_data).to_excel(
        os.path.join(output_dir, "ornek_banka_ekstresi.xlsx"), index=False
    )

    # 4. Araç Yakıt (Eski sistem gibi karmaşık)
    fuel_data = {
        "Fiş Tarihi": ["2024-05-10", "2024-05-11", "2024-05-12", "2024-05-13", "2024-05-14"],
        "Araç Plakası": ["34ABC123", "06XYZ987", "35DEF456", "34ABC123", "06XYZ987"],
        "Ürün Adı": [
            "V-Max Kurşunsuz",
            "Motorin PRO",
            "LPG Otogaz",
            "V-Max Kurşunsuz",
            "Motorin PRO",
        ],
        "Litre / Adet": [45.5, 52.0, 30.0, 40.0, 55.2],
        "Toplam Fiyat": [1820.00, 2080.00, 600.00, 1600.00, 2208.00],
    }
    pd.DataFrame(fuel_data).to_excel(os.path.join(output_dir, "ornek_arac_yakit.xlsx"), index=False)

    print("Örnek Excel dosyaları başarıyla oluşturuldu!")


if __name__ == "__main__":
    generate_samples()
