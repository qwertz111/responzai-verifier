# document_ingestion/parsers/image_parser.py

import pytesseract
from PIL import Image

async def parse_image(file_path: str) -> dict:
    """
    Erkennt Text in Bildern mit Tesseract OCR.

    Wann kommt das vor?
    Manchmal werden Screenshots von Texten geschickt.
    Oder eingescannte Briefe und Formulare als einzelne Bilder.

    Einschränkung: OCR ist nicht perfekt. Bei schlechter
    Bildqualität sinkt die Erkennungsrate. Das System markiert
    OCR-extrahierten Text als "ocr_extracted", damit die
    Agenten wissen, dass der Text Fehler enthalten könnte.
    """
    img = Image.open(file_path)

    # OCR durchführen (Deutsch + Englisch)
    text = pytesseract.image_to_string(img, lang="deu+eng")

    # OCR-Konfidenz berechnen
    data = pytesseract.image_to_data(
        img, lang="deu+eng", output_type=pytesseract.Output.DICT
    )
    confidences = [int(c) for c in data["conf"] if int(c) > 0]
    avg_confidence = sum(confidences) / max(len(confidences), 1)

    return {
        "text": text,
        "pages": 1,
        "sections": [{"heading": "OCR-Text", "text": text}],
        "ocr_used": True,
        "ocr_confidence": round(avg_confidence, 1)
    }
