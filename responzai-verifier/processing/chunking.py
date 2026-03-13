# processing/chunking.py

def chunk_legal_text(text: str, metadata: dict, max_words: int = 500):
    """
    Zerlegt einen Rechtstext in Chunks.

    Warum max. 500 Wörter?
    Zu kleine Chunks verlieren den Kontext.
    Zu große Chunks verwässern die Suche.
    500 Wörter sind ein guter Mittelwert für Rechtstexte.
    """
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:
        if len((current_chunk + paragraph).split()) > max_words:
            if current_chunk:
                chunks.append({
                    "content": current_chunk.strip(),
                    "metadata": metadata
                })
            current_chunk = paragraph
        else:
            current_chunk += "\n\n" + paragraph

    if current_chunk:
        chunks.append({
            "content": current_chunk.strip(),
            "metadata": metadata
        })

    return chunks
