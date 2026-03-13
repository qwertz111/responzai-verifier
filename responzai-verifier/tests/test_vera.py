"""
Tests fuer Vera (VERIFY) - den Verifikations-Agenten.

Vera prueft Claims gegen die Wissensbasis (RAG) und gibt Scores
zwischen 0 und 1 zurueck. Diese Tests mocken Claude-API und Datenbank.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock, call

# Fixtures laden
FIXTURES_PATH = Path(__file__).parent / "fixtures.json"
with open(FIXTURES_PATH, encoding="utf-8") as f:
    FIXTURES = json.load(f)


def _make_claude_response(result_data: dict) -> MagicMock:
    """Hilfsfunktion: Erstellt ein gefaketes Claude-Antwortobjekt."""
    mock_message = MagicMock()
    mock_message.content = [MagicMock()]
    mock_message.content[0].text = json.dumps(result_data)
    return mock_message


def _make_sample_chunks() -> list:
    """Gibt Beispiel-Chunks fuer RAG-Suche zurueck."""
    chunk = FIXTURES["sample_chunk"]
    return [
        {
            "chunk_id": 42,
            "text": chunk["content"],
            "source": chunk["metadata"]["source"],
            "metadata": chunk["metadata"],
            "similarity": 0.95
        }
    ]


@pytest.mark.asyncio
async def test_verify_claim_returns_score():
    """Mockt Claude-API und Datenbank, prüft, ob verify_claim einen Score zwischen 0 und 1 liefert."""
    vera_result = FIXTURES["sample_vera_result"]

    with patch("agents.vera_verify.scoring.find_relevant_chunks", new_callable=AsyncMock) as mock_rag, \
         patch("anthropic.Anthropic") as MockAnthropic:

        mock_rag.return_value = _make_sample_chunks()

        mock_client = MagicMock()
        mock_client.messages.create.return_value = _make_claude_response(vera_result)
        MockAnthropic.return_value = mock_client

        import agents.vera_verify.scoring as scoring_module
        scoring_module.client = mock_client

        claim = FIXTURES["sample_claims"][0]
        result = await scoring_module.verify_claim(claim)

    assert "score" in result, "Ergebnis muss 'score' enthalten"
    assert 0.0 <= result["score"] <= 1.0, f"Score muss zwischen 0 und 1 liegen, war: {result['score']}"


@pytest.mark.asyncio
async def test_find_relevant_chunks():
    """Mockt asyncpg und Voyage-Embedding-API, prüft, ob find_relevant_chunks eine Liste liefert."""
    sample_embedding = [0.1] * 1024  # Voyage-3 hat 1024 Dimensionen

    # Gefakte Datenbankzeilen
    mock_rows = [
        {
            "id": 42,
            "content": FIXTURES["sample_chunk"]["content"],
            "metadata": json.dumps(FIXTURES["sample_chunk"]["metadata"]),
            "title": "Verordnung (EU) 2024/1689",
            "similarity": 0.95
        }
    ]

    with patch("agents.vera_verify.rag_query.create_query_embedding", return_value=sample_embedding), \
         patch("asyncpg.connect", new_callable=AsyncMock) as mock_connect:

        mock_conn = AsyncMock()
        mock_conn.fetch.return_value = mock_rows
        mock_conn.close = AsyncMock()
        mock_connect.return_value = mock_conn

        from agents.vera_verify.rag_query import find_relevant_chunks
        result = await find_relevant_chunks("KI-Kompetenz Pflicht EU AI Act")

    assert isinstance(result, list), "find_relevant_chunks muss eine Liste zurueckgeben"


@pytest.mark.asyncio
async def test_high_score_means_verified():
    """Ein Score >= 0.8 sollte den Status 'verified' ergeben."""
    high_score_result = {
        "claim_id": "claim_001",
        "score": 0.92,
        "status": "verified",
        "reasoning": "Klar belegbar durch Art. 4.",
        "supporting_passages": [],
        "gaps": []
    }

    with patch("agents.vera_verify.scoring.find_relevant_chunks", new_callable=AsyncMock) as mock_rag, \
         patch("anthropic.Anthropic") as MockAnthropic:

        mock_rag.return_value = _make_sample_chunks()

        mock_client = MagicMock()
        mock_client.messages.create.return_value = _make_claude_response(high_score_result)
        MockAnthropic.return_value = mock_client

        import agents.vera_verify.scoring as scoring_module
        scoring_module.client = mock_client

        claim = FIXTURES["sample_claims"][0]
        result = await scoring_module.verify_claim(claim)

    assert result["score"] >= 0.8, "Score sollte >= 0.8 sein"
    assert result["status"] == "verified", "Status sollte 'verified' sein"


@pytest.mark.asyncio
async def test_low_score_means_uncertain():
    """Ein Score < 0.5 sollte einen anderen Status als 'verified' ergeben."""
    low_score_result = {
        "claim_id": "claim_003",
        "score": 0.35,
        "status": "uncertain",
        "reasoning": "Keine ausreichenden Belege gefunden.",
        "supporting_passages": [],
        "gaps": ["Keine Primärquelle gefunden"]
    }

    with patch("agents.vera_verify.scoring.find_relevant_chunks", new_callable=AsyncMock) as mock_rag, \
         patch("anthropic.Anthropic") as MockAnthropic:

        mock_rag.return_value = []

        mock_client = MagicMock()
        mock_client.messages.create.return_value = _make_claude_response(low_score_result)
        MockAnthropic.return_value = mock_client

        import agents.vera_verify.scoring as scoring_module
        scoring_module.client = mock_client

        claim = FIXTURES["sample_claims"][2]
        result = await scoring_module.verify_claim(claim)

    assert result["score"] < 0.5, "Score sollte < 0.5 sein"
    assert result["status"] != "verified", "Status sollte NICHT 'verified' sein"
