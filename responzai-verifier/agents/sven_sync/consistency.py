# agents/sven_sync/consistency.py

import asyncpg
import numpy as np
from processing.embedding import create_embeddings

async def find_similar_claims(claims: list, threshold: float = 0.85) -> list:
    """
    Findet Behauptungen, die sich ähnlich sind.

    Warum?
    Ähnliche Behauptungen könnten sich widersprechen.
    Wenn auf der Website steht "ab Februar 2025" und im
    Newsletter "ab März 2025", dann ist das ein Problem.

    threshold=0.85 bedeutet: Wir suchen nach Behauptungen,
    die zu mindestens 85% ähnlich sind.
    """
    # Embeddings für alle Claims erzeugen
    claim_texts = [c["claim_text"] for c in claims]
    embeddings = create_embeddings(claim_texts)

    # Ähnlichkeiten berechnen
    pairs = []
    for i in range(len(claims)):
        for j in range(i + 1, len(claims)):
            # Kosinus-Ähnlichkeit berechnen
            similarity = np.dot(embeddings[i], embeddings[j]) / (
                np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[j])
            )

            if similarity >= threshold:
                pairs.append({
                    "claim_a": claims[i],
                    "claim_b": claims[j],
                    "similarity": float(similarity)
                })

    return pairs
