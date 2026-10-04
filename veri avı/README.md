# 🌐 Yerel Veri Avcısı ve Araştırma Asistanı

Tamamen yerel bilgisayarınızda (veya üniversite kulübündeki güçlü iş istasyonlarında) çalışan; internetten arama yapıp temiz saf veri toplayan, kaynak atıflı (`[1]`, `[2]`) cevaplar üreten ve toplanan tüm ham verileri **AI eğitimi / arşivleme için `.json` formatında kaydeden** akıllı araştırma sistemi.

---

## 📁 Proje Dosya Yapısı

- `app.py`: Streamlit tabanlı modern ve kullanımı çok kolay web arayüzü.
- `searcher.py`: DuckDuckGo araması ve Trafilatura ile reklam/HTML temizliği yapan akıllı web kazıyıcı.
- `ai_engine.py`: Yerel Ollama modellerine (`qwen2.5:7b` vb.) bağlanan, prompt üreten ve verileri JSON paketine dönüştüren modül.
- `requirements.txt`: Gerekli Python kütüphaneleri.
- `baslat.bat`: Tek tıkla uygulamayı başlatan Windows çalıştırıcı dosyası.

---

## 🚀 Nasıl Çalıştırılır?

### Yöntem 1 (En Kolayı):
Klasördeki **`baslat.bat`** dosyasına **çift tıklayın**. 
Gerekli kütüphaneleri otomatik kontrol edip tarayıcınızda arayüzü açacaktır (`http://localhost:8501`).

### Yöntem 2 (Terminalden):
PowerShell veya Komut Satırı üzerinden şu komutları çalıştırabilirsiniz:
```powershell
pip install -r requirements.txt
streamlit run app.py
```

---

## ⚡ Kulüp Bilgisayarlarına Taşıma (Ölçekleme)
Bu klasörü kulüpteki daha güçlü bir bilgisayara (örn: RTX 3090 / 4090) kopyaladığınızda:
1. O bilgisayarda `ollama run qwen2.5:32b` veya `qwen2.5:14b` çalıştırın.
2. `baslat.bat` dosyasına tıklayın.
3. Sol menüden yeni modeli seçin ve taranacak kaynak sayısını 20-30 seviyelerine çıkarın!
