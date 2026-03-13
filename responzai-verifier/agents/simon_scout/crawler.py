# agents/simon_scout/crawler.py

import requests
from bs4 import BeautifulSoup
from datetime import datetime

def crawl_page(url: str) -> dict:
    """
    Liest eine Webseite und extrahiert den Text.

    Warum BeautifulSoup?
    Webseiten enthalten viel mehr als nur Text: Navigation,
    Footer, Werbung, Skripte. BeautifulSoup hilft uns, nur
    den eigentlichen Inhalt zu finden.
    """
    response = requests.get(url, headers={
        "User-Agent": "responzai-verifier/1.0"
    })
    soup = BeautifulSoup(response.text, "html.parser")

    # Navigation, Footer und Skripte entfernen
    for element in soup.find_all(["nav", "footer", "script", "style"]):
        element.decompose()

    # Hauptinhalt finden
    # (Die genauen Selektoren hängen von der Website ab)
    main_content = soup.find("main") or soup.find("article") or soup.body

    return {
        "url": url,
        "title": soup.title.string if soup.title else "",
        "text": main_content.get_text(separator="\n", strip=True),
        "crawled_at": datetime.now().isoformat()
    }
