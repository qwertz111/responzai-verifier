# database/seed.py

import asyncpg
from processing.embedding import create_embeddings
from processing.chunking import chunk_legal_text

async def seed_database():
    """
    Befüllt die Datenbank zum ersten Mal.

    Dieser Prozess läuft einmal am Anfang und dann
    bei jeder Aktualisierung der Quellen.
    """
    conn = await asyncpg.connect("postgresql://responzai:PASSWORT@localhost/verifier")

    # 1. Quelle registrieren
    source_id = await conn.fetchval("""
        INSERT INTO sources (title, source_type, url)
        VALUES ($1, $2, $3)
        RETURNING id
    """, "EU AI Act", "primary", "https://eur-lex.europa.eu/...")

    # 2. Text in Chunks zerlegen
    chunks = chunk_legal_text(ai_act_text, {"source": "EU AI Act"})

    # 3. Embeddings erzeugen (in Batches von 50)
    for i in range(0, len(chunks), 50):
        batch = chunks[i:i+50]
        texts = [c["content"] for c in batch]
        embeddings = create_embeddings(texts)

        # 4. In Datenbank speichern
        for chunk, embedding in zip(batch, embeddings):
            await conn.execute("""
                INSERT INTO chunks (source_id, content, embedding, metadata)
                VALUES ($1, $2, $3, $4)
            """, source_id, chunk["content"], embedding, chunk["metadata"])

    await conn.close()
    print(f"Wissensbasis befüllt: {len(chunks)} Chunks gespeichert.")
