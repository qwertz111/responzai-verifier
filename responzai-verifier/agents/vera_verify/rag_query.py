# agents/vera_verify/rag_query.py

import asyncpg
from processing.embedding import create_query_embedding

async def find_relevant_chunks(claim_text: str, top_k: int = 5) -> list:
    """
    Sucht die relevantesten Stellen in der Wissensbasis.

    Wie funktioniert das?
    1. Wir wandeln die Behauptung in einen Vektor um.
    2. Wir suchen in der Datenbank nach den ähnlichsten Vektoren.
    3. Die ähnlichsten Stellen sind am wahrscheinlichsten relevant.

    top_k=5 bedeutet: Wir holen die 5 besten Treffer.
    Warum 5? Genug für Kontext, aber nicht so viel, dass
    irrelevante Stellen die Bewertung verwässern.
    """
    query_embedding = create_query_embedding(claim_text)

    conn = await asyncpg.connect("postgresql://responzai:PASSWORT@localhost/verifier")

    rows = await conn.fetch("""
        SELECT c.id, c.content, c.metadata, s.title,
               1 - (c.embedding <=> $1::vector) AS similarity
        FROM chunks c
        JOIN sources s ON c.source_id = s.id
        ORDER BY c.embedding <=> $1::vector
        LIMIT $2
    """, query_embedding, top_k)

    await conn.close()

    return [
        {
            "chunk_id": row["id"],
            "text": row["content"],
            "source": row["title"],
            "metadata": row["metadata"],
            "similarity": float(row["similarity"])
        }
        for row in rows
    ]
