# document_ingestion/parsers/pdf_parser.py

import fitz  # PyMuPDF
import subprocess
import os

async def parse_pdf(file_path: str) -> dict:
    """
    Extrahiert Text aus PDF-Dateien.

    Zwei Fälle:
    1. Text-PDF: Der Text ist direkt im PDF gespeichert.
       Das ist der einfache Fall. PyMuPDF liest ihn direkt.
    2. Gescanntes PDF: Das PDF ist eigentlich ein Bild.
       Hier brauchen wir OCR (Texterkennung).

    Wie unterscheiden wir die beiden?
    Wir versuchen zuerst, Text direkt zu lesen.
    Wenn kaum Text gefunden wird (weniger als 50 Zeichen
    pro Seite im Durchschnitt), ist es wahrscheinlich ein Scan.
    """
    doc = fitz.open(file_path)
    pages = []
    total_text = ""

    for page_num, page in enumerate(doc):
        text = page.get_text()
        pages.append({
            "page": page_num + 1,
            "text": text
        })
        total_text += text + "\n\n"

    # Prüfen, ob OCR nötig ist
    avg_chars_per_page = len(total_text) / max(len(pages), 1)

    if avg_chars_per_page < 50:
        # Wahrscheinlich ein gescanntes PDF. OCR verwenden.
        total_text = await _ocr_pdf(file_path)
        # Seiten neu aufteilen (OCR gibt den gesamten Text zurück)
        pages = [{"page": 1, "text": total_text}]

    doc.close()

    return {
        "text": total_text,
        "pages": len(pages),
        "sections": pages,
        "ocr_used": avg_chars_per_page < 50
    }


async def _ocr_pdf(file_path: str) -> str:
    """
    OCR für gescannte PDFs mit Tesseract.

    Ablauf:
    1. PDF in einzelne Bilder umwandeln (mit PyMuPDF)
    2. Jedes Bild durch Tesseract schicken
    3. Erkannten Text zusammenfügen

    Warum Tesseract?
    Tesseract ist die beste Open-Source-OCR-Engine.
    Sie unterstützt Deutsch und viele andere Sprachen.
    Sie läuft lokal, es werden keine Daten an externe
    Dienste geschickt.
    """
    import pytesseract
    from PIL import Image
    import io

    doc = fitz.open(file_path)
    full_text = ""

    for page in doc:
        # Seite als Bild rendern (300 DPI für gute Erkennung)
        pix = page.get_pixmap(dpi=300)
        img = Image.open(io.BytesIO(pix.tobytes("png")))

        # OCR durchführen (Deutsch + Englisch)
        text = pytesseract.image_to_string(img, lang="deu+eng")
        full_text += text + "\n\n"

    doc.close()
    return full_text
