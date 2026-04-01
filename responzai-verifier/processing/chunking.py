# processing/chunking.py

import re


def chunk_legal_text(text: str, metadata: dict, max_words: int = 500):
    """
    Zerlegt einen Rechtstext in Chunks.
    Erkennt Artikelgrenzen (Artikel X, ANHANG X, KAPITEL X) und speichert
    die Strukturinfo als Metadaten. Zu lange Artikel werden bei max_words
    gesplittet, behalten aber die Artikelzuordnung.
    """
    lines = text.split("\n")
    sections = _split_into_sections(lines)

    chunks = []
    for section in sections:
        section_meta = {**metadata}
        if section["article"]:
            section_meta["article"] = section["article"]
        if section["title"]:
            section_meta["article_title"] = section["title"]
        if section["section_type"]:
            section_meta["section_type"] = section["section_type"]

        content = section["content"].strip()
        if not content:
            continue

        # Zu lange Abschnitte bei Absatzgrenzen splitten
        if len(content.split()) > max_words:
            sub_chunks = _split_long_section(content, max_words)
            for i, sub in enumerate(sub_chunks):
                chunk_meta = {**section_meta}
                if len(sub_chunks) > 1:
                    chunk_meta["part"] = f"{i + 1}/{len(sub_chunks)}"
                chunks.append({"content": sub.strip(), "metadata": chunk_meta})
        else:
            chunks.append({"content": content, "metadata": section_meta})

    return chunks


# Muster fuer Strukturelemente in EUR-Lex Texten
_ARTICLE_RE = re.compile(r"^Artikel\s+(\d+[a-z]?)\s*$")
_ANNEX_RE = re.compile(r"^ANHANG\s+([IVXLCDM]+(?:\s+[A-Z])?)\s*$")
_CHAPTER_RE = re.compile(r"^KAPITEL\s+([IVXLCDM]+)\s*$")
_SECTION_RE = re.compile(r"^ABSCHNITT\s+(\d+)\s*$")


def _split_into_sections(lines: list[str]) -> list[dict]:
    """Splittet den Text an Artikel-/Anhang-/Kapitelgrenzen."""
    sections = []
    current = {"article": None, "title": None, "section_type": "preamble", "lines": []}
    chapter = None

    for line in lines:
        stripped = line.strip()

        # Kapitel-Ueberschrift merken (wird nicht als eigener Chunk gespeichert)
        m = _CHAPTER_RE.match(stripped)
        if m:
            # Vorherigen Abschnitt abschliessen
            if current["lines"]:
                current["content"] = "\n".join(current["lines"])
                sections.append(current)
            chapter = f"Kapitel {m.group(1)}"
            current = {"article": None, "title": chapter, "section_type": "chapter", "lines": [stripped]}
            continue

        # Artikel-Ueberschrift
        m = _ARTICLE_RE.match(stripped)
        if m:
            if current["lines"]:
                current["content"] = "\n".join(current["lines"])
                sections.append(current)
            article_num = m.group(1)
            current = {
                "article": f"Artikel {article_num}",
                "title": None,
                "section_type": "article",
                "lines": [stripped],
            }
            continue

        # Anhang-Ueberschrift
        m = _ANNEX_RE.match(stripped)
        if m:
            if current["lines"]:
                current["content"] = "\n".join(current["lines"])
                sections.append(current)
            current = {
                "article": f"Anhang {m.group(1)}",
                "title": None,
                "section_type": "annex",
                "lines": [stripped],
            }
            continue

        # Titel nach Artikel/Anhang-Ueberschrift erkennen
        # (kann durch Leerzeilen getrennt sein)
        if (current["section_type"] in ("article", "annex")
                and current["title"] is None
                and stripped
                and not stripped[0].isdigit()
                and not stripped.startswith("(")
                and all(l.strip() == "" or l.strip() == current["lines"][0].strip()
                        for l in current["lines"])):
            current["title"] = stripped

        current["lines"].append(line)

    # Letzten Abschnitt abschliessen
    if current["lines"]:
        current["content"] = "\n".join(current["lines"])
        sections.append(current)

    return sections


def _split_long_section(text: str, max_words: int) -> list[str]:
    """Splittet einen zu langen Abschnitt an Absatzgrenzen."""
    paragraphs = text.split("\n\n")
    chunks = []
    current = ""

    for paragraph in paragraphs:
        if len((current + paragraph).split()) > max_words and current:
            chunks.append(current.strip())
            current = paragraph
        else:
            current += "\n\n" + paragraph

    if current.strip():
        chunks.append(current.strip())

    return chunks
