# agents/vera_verify/rag_query.py

from database.connection import get_pool
from processing.embedding import create_query_embedding


async def find_relevant_chunks(claim_text: str, top_k: int = 8, min_similarity: float = 0.15) -> list:
    """
    Sucht die relevantesten Stellen in der Wissensbasis.
    top_k=8 holt genuegend Kandidaten, min_similarity=0.15 laesst auch
    schwaecher formulierte Treffer durch (Vera bewertet selbst).
    Chunk-Text wird auf 800 Zeichen gekuerzt (spart Tokens).
    """
    query_embedding = create_query_embedding(claim_text)
    embedding_str = str(query_embedding)

    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT c.id, c.content, c.metadata, s.title,
                   1 - (c.embedding <=> $1::vector) AS similarity
            FROM chunks c
            JOIN sources s ON c.source_id = s.id
            ORDER BY c.embedding <=> $1::vector
            LIMIT $2
        """, embedding_str, top_k)

    return [
        {
            "chunk_id": row["id"],
            "text": row["content"][:800],
            "source": row["title"],
            "metadata": row["metadata"],
            "similarity": float(row["similarity"])
        }
        for row in rows
        if float(row["similarity"]) >= min_similarity
    ]
