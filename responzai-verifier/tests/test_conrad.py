"""
Tests fuer Conrad (CONTRA) - den adversarialen Gegenpruef-Agenten.

Conrad versucht, verifizierte Claims zu widerlegen. Er nutzt
inverse RAG-Suchen und vier adversariale Strategien.
Diese Tests mocken Claude-API und RAG-Suche.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock

# Fixtures laden
FIXTURES_PATH = Path(__file__).parent / "fixtures.json"
with open(FIXTURES_PATH, encoding="utf-8") as f:
    FIXTURES = json.load(f)

VALID_ADVERSARIAL_RESULTS = {"survived", "weakened", "refuted"}


def _make_claude_response(result_data: dict) -> MagicMock:
    """Hilfsfunktion: Erstellt ein gefaketes Claude-Antwortobjekt."""
    mock_message = MagicMock()
    mock_message.content = [MagicMock()]
    mock_message.content[0].text = json.dumps(result_data)
    return mock_message


def _make_sample_chunks() -> list:
    """Gibt Beispiel-Gegenbeweis-Chunks zurueck."""
    return [
        {
            "chunk_id": 99,
            "text": "Die Pflichten nach Art. 4 gelten nur für Anbieter und Betreiber, nicht für alle Unternehmen.",
            "source": "EU AI Act Erwägungsgrunde",
            "metadata": {},
            "similarity": 0.72
        }
    ]


@pytest.mark.asyncio
async def test_challenge_claim_returns_result():
    """Mockt Claude-API und RAG, prüft, ob challenge_claim ein dict mit 'result'-Key liefert."""
    conrad_result = FIXTURES["sample_conrad_result"]

    with patch("agents.conrad_contra.evaluation.inverse_rag_search", new_callable=AsyncMock) as mock_rag, \
         patch("anthropic.Anthropic") as MockAnthropic:

        mock_rag.return_value = _make_sample_chunks()

        mock_client = MagicMock()
        mock_client.messages.create.return_value = _make_claude_response(conrad_result)
        MockAnthropic.return_value = mock_client

        import agents.conrad_contra.evaluation as evaluation_module
        evaluation_module.client = mock_client

        claim = FIXTURES["sample_claims"][0]
        vera_result = FIXTURES["sample_vera_result"]
        result = await evaluation_module.challenge_claim(claim, vera_result)

    assert isinstance(result, dict), "Ergebnis muss ein dict sein"
    assert "result" in result, "Ergebnis muss den Key 'result' enthalten"


@pytest.mark.asyncio
async def test_adversarial_result_values():
    """Das 'result'-Feld muss einen der drei gueltigen Werte haben: survived/weakened/refuted."""
    for adversarial_result in ["survived", "weakened", "refuted"]:
        mock_result = {
            "claim_id": "claim_001",
            "result": adversarial_result,
            "strategies_applied": [
                {
                    "strategy": "AUSNAHMENSUCHE",
                    "finding": "Kein relevanter Einwand gefunden.",
                    "evidence": "",
                    "severity": "none"
                }
            ],
            "overall_assessment": f"Claim hat Test '{adversarial_result}' bestanden.",
            "suggested_refinement": None
        }

        with patch("agents.conrad_contra.evaluation.inverse_rag_search", new_callable=AsyncMock) as mock_rag, \
             patch("anthropic.Anthropic") as MockAnthropic:

            mock_rag.return_value = _make_sample_chunks()

            mock_client = MagicMock()
            mock_client.messages.create.return_value = _make_claude_response(mock_result)
            MockAnthropic.return_value = mock_client

            import agents.conrad_contra.evaluation as evaluation_module
            evaluation_module.client = mock_client

            claim = FIXTURES["sample_claims"][0]
            vera_result = FIXTURES["sample_vera_result"]
            result = await evaluation_module.challenge_claim(claim, vera_result)

        assert result["result"] in VALID_ADVERSARIAL_RESULTS, (
            f"Ungültiges Ergebnis: '{result['result']}'. "
            f"Erlaubt: {VALID_ADVERSARIAL_RESULTS}"
        )


@pytest.mark.asyncio
async def test_inverse_rag_search():
    """Mockt find_relevant_chunks und prüft, ob inverse_rag_search Gegensuchen erzeugt."""
    sample_chunks = _make_sample_chunks()

    # inverse_rag_search ruft find_relevant_chunks mehrfach auf (4 Gegensuchen)
    with patch("agents.vera_verify.rag_query.find_relevant_chunks", new_callable=AsyncMock) as mock_find:
        mock_find.return_value = sample_chunks

        from agents.conrad_contra.strategies import inverse_rag_search
        result = await inverse_rag_search("Der EU AI Act gilt für alle Unternehmen.")

    assert isinstance(result, list), "inverse_rag_search muss eine Liste zurueckgeben"
    # find_relevant_chunks sollte mehrfach aufgerufen worden sein (4 Gegensuchen)
    assert mock_find.call_count >= 1, "find_relevant_chunks sollte mindestens einmal aufgerufen worden sein"


@pytest.mark.asyncio
async def test_strategies_are_applied():
    """strategies_applied im Conrad-Ergebnis muss eine nicht-leere Liste sein."""
    conrad_result = FIXTURES["sample_conrad_result"]
    # Sicherstellen, dass das Fixture selbst Strategien hat
    assert len(conrad_result["strategies_applied"]) > 0

    with patch("agents.conrad_contra.evaluation.inverse_rag_search", new_callable=AsyncMock) as mock_rag, \
         patch("anthropic.Anthropic") as MockAnthropic:

        mock_rag.return_value = _make_sample_chunks()

        mock_client = MagicMock()
        mock_client.messages.create.return_value = _make_claude_response(conrad_result)
        MockAnthropic.return_value = mock_client

        import agents.conrad_contra.evaluation as evaluation_module
        evaluation_module.client = mock_client

        claim = FIXTURES["sample_claims"][0]
        vera_result = FIXTURES["sample_vera_result"]
        result = await evaluation_module.challenge_claim(claim, vera_result)

    assert "strategies_applied" in result, "Ergebnis muss 'strategies_applied' enthalten"
    assert isinstance(result["strategies_applied"], list), "'strategies_applied' muss eine Liste sein"
    assert len(result["strategies_applied"]) > 0, "'strategies_applied' darf nicht leer sein"
