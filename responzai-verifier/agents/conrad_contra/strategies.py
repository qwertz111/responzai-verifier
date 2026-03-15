# agents/conrad_contra/strategies.py

from agents.vera_verify.rag_query import find_relevant_chunks

async def inverse_rag_search(claim_text: str) -> list:
    """
    Conrads eigene Suche in der Wissensbasis.

    Warum eine eigene Suche?
    Vera sucht nach Belegen FÜR die Behauptung.
    Conrad sucht nach Belegen GEGEN die Behauptung.
    Dafür formuliert er die Suchanfrage um.

    Beispiel:
    Behauptung: "Art. 4 gilt für alle Unternehmen"
    Conrads Suche: "Ausnahmen Art. 4" und "nicht anwendbar Art. 4"
    """
    # Gegensuche formulieren
    # 2 Queries statt 4 (spart 50% Voyage-Calls, gleiche Abdeckung)
    counter_queries = [
        f"Ausnahmen und Einschränkungen: {claim_text}",
        f"Änderung, Aufhebung, nicht anwendbar: {claim_text}",
    ]

    all_chunks = []
    for query in counter_queries:
        chunks = await find_relevant_chunks(query, top_k=2)
        all_chunks.extend(chunks)

    # Duplikate entfernen und nach Relevanz sortieren
    seen_ids = set()
    unique_chunks = []
    for chunk in sorted(all_chunks, key=lambda x: x["similarity"], reverse=True):
        if chunk["chunk_id"] not in seen_ids:
            seen_ids.add(chunk["chunk_id"])
            unique_chunks.append(chunk)

    return unique_chunks[:5]
