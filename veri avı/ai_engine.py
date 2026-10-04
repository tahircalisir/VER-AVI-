"""
ai_engine.py - Yerel Yapay Zeka (Ollama) Entegrasyon Modülü
Toplanan web verilerini Qwen 2.5 veya seçilen yerel modele gönderir,
kaynak atıflı sentez üretir ve JSON çıktısını hazırlar.
"""

from datetime import datetime
import json
import ollama

def list_local_models() -> list[str]:
    """
    Bilgisayarda kurulu olan Ollama modellerini listeler.
    """
    try:
        response = ollama.list()
        # ollama python kütüphanesinde modeller 'models' anahtarı altında döner
        models = [m.model for m in response.models] if hasattr(response, 'models') else []
        if not models and isinstance(response, dict) and "models" in response:
            models = [m["name"] for m in response["models"]]
        return models if models else ["qwen2.5:7b"]
    except Exception:
        return ["qwen2.5:7b", "llama3.1:8b"]


def synthesize_with_ai(query: str, sources: list[dict], model_name: str = "qwen2.5:7b") -> str:
    """
    Taranan web sayfalarını modele iletir ve kaynak atıflı ([1], [2] vb.)
    kapsamlı bir yanıt üretmesini ister.
    """
    # Kaynakları modelin okuyabileceği formata dönüştür
    context_blocks = []
    for s in sources:
        # Metni modele verirken çok uzunsa hafif kırp
        content_preview = s['content'][:2500]
        context_blocks.append(
            f"--- [KAYNAK {s['id']}] ---\n"
            f"Başlık: {s['title']}\n"
            f"URL: {s['url']}\n"
            f"İçerik:\n{content_preview}\n"
        )
    
    full_context = "\n".join(context_blocks)

    system_prompt = (
        "Sen yerel çalışan, son derece yetkin bir araştırma ve veri analiz asistanısın.\n"
        "Görevin: Kullanıcının sorusuna veya konusuna, sana sağlanan web kaynaklarındaki bilgileri "
        "kullanarak kapsamlı, tarafsız ve detaylı bir yanıt vermektir.\n\n"
        "KURALLAR:\n"
        "1. Bilgileri aktarırken mutlaka ilgili cümlenin veya bilginin sonuna [1], [2] gibi kaynak numaralarıyla atıf yap.\n"
        "2. Kaynaklarda açıkça yer almayan veya çelişkili olan durumlarda bunu dürüstçe belirt.\n"
        "3. Türkçe dilbilgisine uygun, akıcı ve profesyonel bir üslup kullan.\n"
        "4. Yanıtı gereksiz süslemeler yerine net başlıklar veya maddelerle zenginleştir."
    )

    user_prompt = (
        f"Kullanıcı Araştırma Konusu / Sorusu:\n\"{query}\"\n\n"
        f"İnternetten Taranan İlgili Kaynaklar:\n{full_context}\n\n"
        "Lütfen yukarıdaki kaynakları titizlikle inceleyerek konuyu/soruyu detaylıca yanıtla ve "
        "kullandığın yerlerde [1], [2] şeklinde kaynak numaralarını belirt."
    )

    try:
        response = ollama.chat(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            options={
                "temperature": 0.3, # Daha tutarlı ve kaynaklara bağlı kalması için
            }
        )
        return response["message"]["content"]
    except Exception as e:
        return f"Yapay zeka yanıt üretirken bir hata oluştu: {str(e)}\n\nLütfen Ollama'nın arka planda çalıştığından emin olun."


def generate_export_json(query: str, model_name: str, ai_answer: str, sources: list[dict]) -> dict:
    """
    Toplanan tüm verileri, kaynakları ve yapay zeka cevabını
    standart bir JSON şemasına dönüştürür.
    """
    formatted_sources = []
    for s in sources:
        formatted_sources.append({
            "id": s["id"],
            "baslik": s["title"],
            "url": s["url"],
            "ham_metin_boyutu": f"{len(s['content'])} karakter",
            "kazinan_metin": s["content"]
        })

    data_package = {
      "arama_sorgusu": query,
      "tarih": datetime.now().isoformat(),
      "kullanilan_model": model_name,
      "taranan_site_adedi": len(sources),
      "yapay_zeka_cevabi": ai_answer,
      "kaynaklar": formatted_sources
    }
    return data_package
