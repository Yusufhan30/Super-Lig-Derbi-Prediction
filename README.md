# ⚽ Galatasaray vs Fenerbahçe — Derbi Skor Tahmin Sistemi

> Süper Lig 2025-26 sezonu istatistiklerine dayalı, Poisson dağılımı kullanan interaktif derbi analiz uygulaması.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red?style=flat-square&logo=streamlit)
![Plotly](https://img.shields.io/badge/Plotly-5.20+-purple?style=flat-square&logo=plotly)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## 📸 Ekran Görüntüleri

![Simülasyon ve Skor Tahmini](screenshoots/Screenshot%202026-04-25%20233505.png)

![Heatmap ve Radar](screenshoots/Screenshot%202026-04-25%20233516.png)

![İstatistik ve xG](screenshoots/Screenshot%202026-04-25%20233526.png)


## 🎯 Proje Hakkında

Bu proje, **veri bilimi yöntemleriyle futbol maç tahmini** yapmayı amaçlamaktadır.
SofaScore üzerinden elde edilen 30 maçlık Süper Lig verisi kullanılarak:

- Ağırlıklı feature skorlama ile her takımın güç puanı hesaplanır
- Poisson dağılımıyla olasılıksal skor matrisi üretilir
- Gol dakikası dağılımı analiz edilerek maçın kırılma anları tespit edilir

---

## 📊 Uygulama İçeriği

| Bölüm | Açıklama |
|-------|----------|
| 🎛️ İnteraktif Simülasyon | Ev sahibi/deplasman katsayılarını kaydırarak anlık skor tahmini |
| 🎲 Skor Olasılık Matrisi | Poisson ile her olası skora yüzdelik ihtimal |
| ⏱️ Gol Dakikası Heatmap | 15'er dakikalık periyotlarda atılan/yenilen gol yoğunluğu |
| 📡 Radar Chart | 9 metrikte GS vs FB performans karşılaştırması |
| 📊 Butterfly Bar | 14 istatistik karşılıklı görselleştirme |
| 🔬 xG Periyot Trendi | Poisson lambda + gol dağılımıyla periyot bazlı beklenen gol |

---

## 🧠 Model Nasıl Çalışır?

```
Veri (14 feature)
    ↓
Ağırlıklı Feature Skoru
    ↓
Poisson Lambda (xG) Hesabı
    ↓
Skor Olasılık Matrisi (7x7)
    ↓
En Olası Skor + Kazanma Olasılıkları
```

**Seçilen 14 Feature:**
- Maç başına gol & yenilen gol
- Büyük şans yaratma & kaçırma
- İsabetli / toplam şut
- Top kontrolü & pas kalitesi
- Pressing (top geri kazanma)
- Tehlike engelleme & temiz kale
- Penaltı dönüşüm oranı

> Overfitting'i önlemek için 48 ham istatistikten yalnızca skor üretimi ve engellemeyle doğrudan ilişkili 14 feature tutulmuştur.

---

## 🚀 Kurulum

```bash
# Repoyu klonla
git clone https://github.com/KULLANICIN/derbi-analiz.git
cd derbi-analiz

# Bağımlılıkları yükle
pip install -r requirements.txt

# Uygulamayı başlat
streamlit run app.py
```

---

## 📁 Dosya Yapısı

```
derbi-analiz/
├── app.py                      # Ana Streamlit uygulaması
├── requirements.txt            # Python bağımlılıkları
├── README.md                   # Bu dosya
└── Data/
    ├── derbi_model_data.csv    # 14 feature istatistik seti
    └── Derbi_dakikaları.csv    # Periyot bazlı gol dağılımı
```

---

## 📈 Model Çıktısı (Varsayılan Parametreler)

| | Galatasaray | Fenerbahçe |
|--|--|--|
| xG (Beklenen Gol) | 3.24 | 2.86 |
| Kazanma Olasılığı | %43.3 | %33.2 |
| Beraberlik | %16.3 | — |
| **Tahmin Edilen Skor** | **3** | **2** |

---

## ⚠️ Önemli Not

Bu uygulama **istatistiksel bir simülasyon** olup kesin sonuç garantisi vermez.
Futbolda her maç kendi dinamiklerini taşır. Proje, veri bilimi tekniklerinin
spor analitiğine uygulanmasını göstermeyi amaçlamaktadır.

---

## 🛠️ Teknolojiler

- **Python 3.10+**
- **Streamlit** — İnteraktif web arayüzü
- **Plotly** — Dinamik görselleştirmeler
- **Pandas / NumPy** — Veri işleme
- **Poisson Dağılımı** — Olasılıksal skor modeli

---

## 📬 İletişim

Projeyi beğendiysen ⭐ vermeyi unutma!
Sorular ve öneriler için [LinkedIn](https://linkedin.com/in/KULLANICIN) üzerinden ulaşabilirsin.
