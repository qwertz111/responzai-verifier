# processing/embedding.py

import os
import voyageai
from typing import List
from dotenv import load_dotenv

load_dotenv()

# Voyage-3 Client initialisieren
client = voyageai.Client(api_key=os.environ["VOYAGE_API_KEY"])

def create_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Erzeugt Embeddings für eine Liste von Texten.

    Was passiert hier?
    1. Wir schicken die Texte an die Voyage-3 API.
    2. Die API gibt für jeden Text einen Vektor zurück.
    3. Wir speichern diese Vektoren in der Datenbank.

    Warum Voyage-3?
    Voyage-3 ist speziell für die Suche in Dokumenten optimiert.
    Es versteht den Zusammenhang zwischen Frage und Antwort
    besser als allgemeine Embedding-Modelle.
    """
    result = client.embed(
        texts,
        model="voyage-3",
        input_type="document"  # Für Dokumente in der Wissensbasis
    )
    return result.embeddings


def create_query_embedding(query: str) -> List[float]:
    """
    Erzeugt ein Embedding für eine Suchanfrage.

    Warum ein separater Typ?
    Voyage-3 unterscheidet zwischen "document" (der gespeicherte Text)
    und "query" (die Suchanfrage). Das verbessert die Suchergebnisse.
    """
    result = client.embed(
        [query],
        model="voyage-3",
        input_type="query"  # Für Suchanfragen
    )
    return result.embeddings[0]
