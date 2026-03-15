# agents/lena_legal/source_mapper.py

import hashlib
from agents.vera_verify.rag_query import find_relevant_chunks


async def map_sources_to_claim(claim: dict) -> list:
    """
    Findet die relevanten Quellstellen für einen Claim und
    versieht jede Stelle mit einem eindeutigen Hash.

    Warum ein Hash?
    Lena muss sich in ihrem Output auf konkrete Quellen beziehen.
    Der Hash ist ein kurzer, eindeutiger Fingerabdruck eines
    Textstücks. verification_loop.py prüft später, ob alle
    von Lena genannten Hashes tatsächlich aus dieser Liste stammen.

    Ablauf:
    1. Claim-Text an Vera's RAG-Suche übergeben.
    2. Für jeden Treffer einen SHA-256-Hash der ersten 12 Zeichen berechnen.
    3. Ergebnis als strukturierte Liste zurückgeben.
    """
    claim_text = claim.get("claim_text", "")
    chunks = await find_relevant_chunks(claim_text, top_k=3)

    result = []
    for chunk in chunks:
        raw_hash = hashlib.sha256(chunk["text"].encode()).hexdigest()[:12]
        result.append({
            "hash": raw_hash,
            "text": chunk["text"],
            "source": chunk["source"],
            "relevance": chunk["similarity"]
        })

    return result
