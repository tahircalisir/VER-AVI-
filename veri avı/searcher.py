"""
searcher.py - Web Arama ve Akıllı Metin Kazıma Modülü
DuckDuckGo kullanarak web araması yapar ve sayfaların saf metinlerini çıkarır.
"""

import time
import requests
from bs4 import BeautifulSoup
import trafilatura
from duckduckgo_search import DDGS

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

def search_duckduckgo(query: str, max_results: int = 5) -> list[dict]:
    """
    DuckDuckGo üzerinden arama yapar ve bulunan linklerin listesini döndürür.
    """
    results = []
    try:
        with DDGS() as ddgs:
            # DuckDuckGo metin araması
            raw_results = list(ddgs.text(query, max_results=max_results, region="tr-tr", safesearch="moderate"))
            
            # Eğer tr-tr'de az sonuç çıkarsa genel arama yap
            if len(raw_results) < max_results:
                extra = list(ddgs.text(query, max_results=max_results - len(raw_results), region="wt-wt", safesearch="moderate"))
                raw_results.extend(extra)

            for item in raw_results:
                url = item.get("href") or item.get("link")
                title = item.get("title", "Başlıksız")
                snippet = item.get("body", "")
                if url and not any(r["url"] == url for r in results):
                    results.append({
                        "title": title,
                        "url": url,
                        "snippet": snippet
                    })
    except Exception as e:
        print(f"Arama hatası: {e}")
    
    return results[:max_results]


def scrape_page_content(url: str, max_chars: int = 4000) -> str:
    """
    Verilen URL'deki web sayfasını ziyaret eder, reklam ve gereksiz kodları
    temizleyerek saf metni (content) döndürür.
    """
    # 1. Öncelik: Trafilatura (reklam ve menüleri temizleyen en gelişmiş kütüphane)
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            extracted_text = trafilatura.extract(
                downloaded,
                include_comments=False,
                include_tables=True,
                no_fallback=False
            )
            if extracted_text and len(extracted_text.strip()) > 100:
                return extracted_text.strip()[:max_chars]
    except Exception:
        pass

    # 2. Alternatif: Requests + BeautifulSoup (Trafilatura başarısız olursa)
    try:
        response = requests.get(url, headers=HEADERS, timeout=7)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Script, style ve svg etiketlerini temizle
            for tag in soup(["script", "style", "noscript", "svg", "header", "footer", "nav", "aside"]):
                tag.decompose()
            
            text = " ".join(soup.stripped_strings)
            if len(text) > 100:
                return text[:max_chars]
    except Exception:
        pass

    return ""


def gather_data_pipeline(query: str, max_results: int = 5, status_callback=None) -> list[dict]:
    """
    Belirtilen arama sorgusu için linkleri bulur ve sayfaların metinlerini kazır.
    """
    if status_callback:
        status_callback(f"🔍 DuckDuckGo üzerinde '{query}' aranıyor...")

    search_hits = search_duckduckgo(query, max_results=max_results)
    
    if not search_hits:
        if status_callback:
            status_callback("⚠️ Uygun arama sonucu bulunamadı.")
        return []

    collected_sources = []
    
    for i, item in enumerate(search_hits, 1):
        url = item["url"]
        title = item["title"]
        if status_callback:
            status_callback(f"📥 Sayfa taranıyor ({i}/{len(search_hits)}): {title[:40]}...")

        content = scrape_page_content(url)
        
        # Eğer içerik çekilemediyse arama motorundaki özeti (snippet) kullan
        if not content:
            content = item.get("snippet", "Sayfa içeriği doğrudan okunamadı, arama özeti kullanılıyor.")

        collected_sources.append({
            "id": i,
            "title": title,
            "url": url,
            "snippet": item.get("snippet", ""),
            "content": content
        })
        time.sleep(0.3)  # Sunucuları boğmamak için ufak bekleme

    return collected_sources
