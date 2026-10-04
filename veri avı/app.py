"""
app.py - Yerel Veri Avcısı ve Araştırma Asistanı Kullanıcı Arayüzü (Streamlit)
Çalıştırmak için: streamlit run app.py
"""

import json
from datetime import datetime
import streamlit as st

from searcher import gather_data_pipeline
from ai_engine import list_local_models, synthesize_with_ai, generate_export_json

# Sayfa Yapılandırması
st.set_page_config(
    page_title="Yerel Veri Avcısı & AI Asistanı",
    page_icon="🌐",
    layout="wide"
)

# Özel CSS ile Modern ve Şık Görünüm
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        color: #888;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }
    .source-card {
        padding: 12px;
        border-radius: 8px;
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Yan Panel (Ayarlar)
with st.sidebar:
    st.header("⚙️ Ayarlar & Donanım")
    
    # Mevcut Modelleri Algıla
    available_models = list_local_models()
    default_idx = 0
    for i, m in enumerate(available_models):
        if "qwen2.5:7b" in m or "qwen" in m:
            default_idx = i
            break

    selected_model = st.selectbox(
        "Kullanılacak Yerel Model:",
        options=available_models,
        index=default_idx,
        help="Laptopunuzda Qwen 2.5 7B, kulüpteki daha güçlü bilgisayarlarda 14B/32B/70B modelleri seçebilirsiniz."
    )

    # Taranacak Kaynak Sayısı (1 - 30 arası, güçlü PC'ler için geniş)
    max_sources = st.slider(
        "Taranacak Kaynak Sayısı:",
        min_value=1,
        max_value=30,
        value=5,
        step=1,
        help="Laptopunuzda 3-8 kaynak idealdir. Kulüpteki güçlü sistemlerde 20-30 kaynağa çıkarabilirsiniz."
    )

    st.markdown("---")
    st.markdown("### 💻 Sistem Durumu")
    st.success("🟢 Yerel Ollama Motoru Aktif")
    st.caption("Verileriniz tamamen yerel bilgisayarınızda işlenir, harici sunuculara veya ücretli API'lara gönderilmez.")


# Ana Sayfa İçeriği
st.markdown('<div class="main-title">🌐 Yerel Veri Avcısı & Araştırma Asistanı</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">İnternetten canlı veri toplar, kaynak göstererek analiz eder ve AI eğitimi için JSON üretir.</div>', unsafe_allow_html=True)

# Arama Formu
query = st.text_input(
    "Araştırmak istediğiniz kelime, konu veya soru:",
    placeholder="Örn: Kuantum bilgisayarların siber güvenliğe etkileri",
    key="search_query"
)

col1, col2 = st.columns([1, 4])
with col1:
    search_button = st.button("🚀 Araştır & Veri Topla", type="primary", use_container_width=True)

# Arama İşlemi Tetiklendiğinde
if search_button and query.strip():
    status_container = st.status("Veri avı başlatılıyor...", expanded=True)
    
    def update_status(msg):
        status_container.write(msg)

    # 1. Aşama: Web Taraması ve Metin Kazıma
    sources = gather_data_pipeline(
        query=query.strip(),
        max_results=max_sources,
        status_callback=update_status
    )

    if not sources:
        status_container.update(label="Arama tamamlandı ancak kaynak bulunamadı!", state="error")
        st.warning("Bu konuyla ilgili taranabilecek web sayfası bulunamadı. Lütfen sorguyu farklı kelimelerle deneyin.")
    else:
        # 2. Aşama: Yerel Model ile Sentezleme
        update_status(f"🧠 {selected_model} modeli kaynakları okuyor ve analiz ediyor...")
        ai_response = synthesize_with_ai(query=query.strip(), sources=sources, model_name=selected_model)
        
        status_container.update(label="✅ Araştırma ve veri toplama başarıyla tamamlandı!", state="complete", expanded=False)

        # 3. Aşama: Sonuçları Ekrana Yazdır
        st.markdown("### 📝 Yapay Zeka Özeti ve Analizi")
        st.markdown(ai_response)

        # JSON Paketini Hazırla
        json_data = generate_export_json(
            query=query.strip(),
            model_name=selected_model,
            ai_answer=ai_response,
            sources=sources
        )
        json_string = json.dumps(json_data, ensure_ascii=False, indent=2)

        # İndirme Butonu
        st.markdown("---")
        timestamp_slug = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"veri_avi_{timestamp_slug}.json"

        st.download_button(
            label="💾 Bu Araştırmayı JSON Olarak İndir (Eğitim & Arşiv İçin)",
            data=json_string.encode("utf-8"),
            file_name=filename,
            mime="application/json",
            type="secondary",
            use_container_width=True
        )

        # 4. Aşama: Bulunan Kaynakların Detayları (Genişletilebilir Akordeon)
        with st.expander(f"📚 Taranan Tüm Kaynaklar ve Ham Metinler ({len(sources)} Site)"):
            for s in sources:
                st.markdown(f"**[{s['id']}] [{s['title']}]({s['url']})**")
                st.caption(f"Bağlantı: {s['url']} | Boyut: {len(s['content'])} karakter")
                with st.container():
                    st.text_area(
                        label=f"Kaynak {s['id']} Çekilen Metin:",
                        value=s['content'][:1500] + ("..." if len(s['content']) > 1500 else ""),
                        height=120,
                        key=f"text_area_{s['id']}"
                    )
                st.markdown("---")

elif search_button and not query.strip():
    st.warning("Lütfen bir soru veya arama kelimesi girin.")
