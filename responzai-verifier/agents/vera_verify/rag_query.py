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

    results = []
    for row in rows:
        sim = float(row["similarity"])
        if sim < min_similarity:
            continue
        raw_meta = row["metadata"]
        if isinstance(raw_meta, dict):
            meta = raw_meta
        elif isinstance(raw_meta, str):
            import json
            try:
                meta = json.loads(raw_meta)
            except (json.JSONDecodeError, TypeError):
                meta = {}
        else:
            meta = {}
        # Quellenangabe mit Artikelreferenz anreichern
        source_label = row["title"]
        if meta.get("article"):
            source_label = f"{row['title']}, {meta['article']}"
            if meta.get("article_title"):
                source_label += f" ({meta['article_title']})"
        results.append({
            "chunk_id": row["id"],
            "text": row["content"][:800],
            "source": source_label,
            "metadata": meta,
            "similarity": sim,
        })
    return results
