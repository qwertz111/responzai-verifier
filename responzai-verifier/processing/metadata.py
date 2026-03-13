# processing/metadata.py

import hashlib
import re
from collections import Counter
from typing import Optional


# Deutsche Stoppwörter für Sprach- und Keyword-Erkennung
GERMAN_STOPWORDS = {
    "der", "die", "das", "und", "in", "ist", "von", "mit", "ein", "eine",
    "einen", "dem", "den", "des", "zu", "auf", "für", "als", "an", "bei",
    "nach", "oder", "auch", "aber", "wenn", "so", "ich", "nicht", "es",
    "sie", "er", "wir", "durch", "im", "wird", "sind", "haben", "werden",
    "kann", "noch", "alle", "mehr", "über", "aus", "um", "hat", "war",
    "nur", "wie", "dass", "sich", "dieser", "diese", "dieses", "ihrer",
}

ENGLISH_STOPWORDS = {
    "the", "and", "is", "in", "of", "to", "a", "an", "that", "it",
    "for", "on", "with", "as", "at", "by", "from", "or", "but", "are",
    "was", "be", "has", "have", "had", "not", "this", "which", "they",
    "their", "we", "you", "he", "she", "all", "been", "more", "about",
    "so", "if", "can", "will", "do", "what", "how", "when", "there",
}

# Inhaltstyp-Muster für die Klassifikation von Chunks
CONTENT_TYPE_PATTERNS = {
    "recital": [r"\bErwägungsgrund\b", r"\bRecital\b", r"\bWhereas\b"],
    "article": [r"\bArtikel\s+\d+", r"\bArt\.\s+\d+", r"\bArticle\s+\d+"],
    "annex": [r"\bAnhang\b", r"\bAnnex\b", r"\bAnlage\b"],
    "definition": [r"\bbedeutet\b.*:\s*\"", r"\bdefiniert\s+als\b", r"\bim\s+Sinne\s+dieser\b"],
}


def enrich_chunk_metadata(chunk_content: str, source_metadata: dict) -> dict:
    """
    Reichert die Metadaten eines Chunks mit automatisch erkannten Informationen an.

    Warum diese Funktion?
    Beim Speichern von Chunks in die Vektordatenbank brauchen wir mehr als nur
    den Text. Die angereicherten Metadaten helfen Vera (VERIFY) beim Filtern
    und beim Ranking von Suchergebnissen. Ein Artikel-Chunk ist zum Beispiel
    wichtiger als ein allgemeiner Absatz.

    Die Anreicherung passiert zur Ingest-Zeit, nicht zur Suchzeit.
    Das spart Rechenzeit bei jeder Suchanfrage.
    """
    enriched = dict(source_metadata)

    # Wortanzahl ermitteln
    words = chunk_content.split()
    enriched["word_count"] = len(words)

    # Sprache erkennen
    enriched["language"] = _detect_language(chunk_content)

    # Inhaltstyp klassifizieren
    enriched["content_type"] = _classify_content_type(chunk_content)

    # Schlüsselbegriffe extrahieren
    enriched["key_terms"] = _extract_key_terms(chunk_content, enriched["language"])

    return enriched


def create_chunk_id(content: str, metadata: dict) -> str:
    """
    Erzeugt eine deterministische ID für einen Chunk auf Basis seines Inhalts.

    Warum deterministisch?
    Wenn dasselbe Dokument erneut eingespielt wird, soll der Chunk dieselbe ID
    bekommen. So können wir erkennen, ob sich ein Chunk verändert hat, ohne
    alle Chunks in der Datenbank neu zu vergleichen.

    Die ID basiert auf dem Inhalt und der Quell-URL, damit zwei Chunks mit
    identischem Text aus unterschiedlichen Quellen trotzdem verschiedene IDs haben.
    """
    source = metadata.get("source_url", "") or metadata.get("original_filename", "")
    raw = f"{source}::{content}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]


def _detect_language(text: str) -> str:
    """
    Erkennt die Sprache anhand von Stoppwörtern.

    Einfache Heuristik: Wir zählen, wie viele deutsche und englische
    Stoppwörter im Text vorkommen. Die Sprache mit mehr Treffern gewinnt.
    Für EU-Rechtstexte ist das ausreichend genau.
    """
    text_lower = text.lower()
    word_tokens = set(re.findall(r"\b[a-zA-ZäöüÄÖÜß]+\b", text_lower))

    german_hits = len(word_tokens & GERMAN_STOPWORDS)
    english_hits = len(word_tokens & ENGLISH_STOPWORDS)

    if german_hits > english_hits:
        return "de"
    elif english_hits > german_hits:
        return "en"
    else:
        return "unknown"


def _classify_content_type(text: str) -> str:
    """
    Klassifiziert den Inhaltstyp eines Chunks anhand von Textmustern.

    Rechtstexte haben klare Strukturen: Artikel, Erwägungsgründe, Anhänge
    und Definitionen. Diese Klassifikation hilft den Agenten, den richtigen
    Kontext zu verstehen. Ein Erwägungsgrund ist zum Beispiel weniger bindend
    als ein Artikel.
    """
    for content_type, patterns in CONTENT_TYPE_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return content_type
    return "general"


def _extract_key_terms(text: str, language: str = "de", top_n: int = 10) -> list:
    """
    Extrahiert die wichtigsten Begriffe aus einem Chunk.

    Vorgehen: Wir tokenisieren den Text, filtern Stoppwörter und kurze Wörter
    heraus und zählen die Häufigkeit. Die Top-N Begriffe sind die Schlüsselbegriffe.

    Warum keine komplexere NLP-Methode?
    Für Rechtstexte genügt Häufigkeit. Spezialbegriffe wie "Hochrisiko-KI-System"
    kommen selten vor, aber wenn, dann sind sie relevant. Eine TF-IDF-Berechnung
    über alle Chunks wäre aufwändiger und bringt hier kaum Mehrwert.
    """
    stopwords = GERMAN_STOPWORDS if language == "de" else ENGLISH_STOPWORDS
    words = re.findall(r"\b[a-zA-ZäöüÄÖÜß]{4,}\b", text.lower())
    filtered = [w for w in words if w not in stopwords]
    counter = Counter(filtered)
    return [term for term, _ in counter.most_common(top_n)]
