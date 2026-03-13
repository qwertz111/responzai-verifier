# document_ingestion/preprocessor.py

import re
import unicodedata

def clean_text(text: str) -> str:
    """
    Bereinigt den extrahierten Text.

    Warum ist das nötig?
    PDF-Parser liefern oft kaputten Text: doppelte Leerzeichen,
    Zeilenumbrüche mitten im Wort, seltsame Sonderzeichen.
    Word-Dokumente haben manchmal unsichtbare Steuerzeichen.

    Diese Funktion räumt auf, ohne den Inhalt zu verändern.
    """
    # Unicode normalisieren (verschiedene Darstellungen vereinheitlichen)
    text = unicodedata.normalize("NFKC", text)

    # Steuerzeichen entfernen (außer Zeilenumbruch und Tab)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

    # Mehrfache Leerzeichen zu einem
    text = re.sub(r"[ \t]+", " ", text)

    # Mehr als zwei aufeinanderfolgende Leerzeilen zu zwei
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Bindestrich-Trennungen am Zeilenende zusammenfügen
    # "Verant-\nwortung" → "Verantwortung"
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)

    # Leerzeichen am Anfang und Ende jeder Zeile entfernen
    lines = [line.strip() for line in text.split("\n")]
    text = "\n".join(lines)

    return text.strip()
