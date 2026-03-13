"""
Tests fuer Simon (SCOUT) - den Claims-Extraktor.

Simon zerlegt Texte in prüfbare Behauptungen und kategorisiert sie.
Diese Tests prüfen, ob Simon die erwartete Struktur liefert,
ohne echte Claude-API-Aufrufe zu machen.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock

# Fixtures laden
FIXTURES_PATH = Path(__file__).parent / "fixtures.json"
with open(FIXTURES_PATH, encoding="utf-8") as f:
    FIXTURES = json.load(f)

VALID_CATEGORIES = {"LEGAL_CLAIM", "PRODUCT_CLAIM", "MARKET_CLAIM", "TARGET_GROUP"}
VALID_VERIFIABILITIES = {"high", "medium", "low"}


def _make_claude_response(claims_data: dict) -> MagicMock:
    """Hilfsfunktion: Erstellt ein gefaketes Claude-Antwortobjekt."""
    mock_message = MagicMock()
    mock_message.content = [MagicMock()]
    mock_message.content[0].text = json.dumps(claims_data)
    return mock_message


@pytest.mark.asyncio
async def test_extract_claims_returns_valid_structure():
    """Mockt den Claude-API-Aufruf und prüft, ob extract_claims ein dict mit 'claims'-Key liefert."""
    mock_response_data = {
        "claims": FIXTURES["sample_claims"],
        "summary": {"total": 3, "categories": {"LEGAL_CLAIM": 2, "PRODUCT_CLAIM": 1}}
    }

    with patch("anthropic.Anthropic") as MockAnthropic:
        mock_client = MagicMock()
        mock_client.messages.create.return_value = _make_claude_response(mock_response_data)
        MockAnthropic.return_value = mock_client

        # Modul neu laden, damit der gemockte Client genutzt wird
        import importlib
        import agents.simon_scout.parser as parser_module
        parser_module.client = mock_client

        result = await parser_module.extract_claims(
            FIXTURES["sample_text"],
            FIXTURES["sample_url"]
        )

    assert isinstance(result, dict), "Ergebnis muss ein dict sein"
    assert "claims" in result, "Ergebnis muss den Key 'claims' enthalten"
    assert isinstance(result["claims"], list), "'claims' muss eine Liste sein"


@pytest.mark.asyncio
async def test_claim_has_required_fields():
    """Jeder extrahierte Claim muss alle Pflichtfelder enthalten."""
    required_fields = {"id", "claim_text", "category", "verifiability", "original_text", "source_url"}

    mock_response_data = {
        "claims": FIXTURES["sample_claims"],
        "summary": {}
    }

    with patch("anthropic.Anthropic") as MockAnthropic:
        mock_client = MagicMock()
        mock_client.messages.create.return_value = _make_claude_response(mock_response_data)
        MockAnthropic.return_value = mock_client

        import agents.simon_scout.parser as parser_module
        parser_module.client = mock_client

        result = await parser_module.extract_claims(
            FIXTURES["sample_text"],
            FIXTURES["sample_url"]
        )

    for claim in result["claims"]:
        missing = required_fields - set(claim.keys())
        assert not missing, f"Claim fehlt Felder: {missing}"


def test_crawl_page():
    """Mockt requests.get und prüft, ob crawl_page url, title und text zurückgibt."""
    html_content = """
    <html>
        <head><title>responzai - EU AI Act Compliance</title></head>
        <body>
            <main>
                <h1>Produkte</h1>
                <p>Der EU AI Act verpflichtet Unternehmen zur KI-Kompetenz.</p>
            </main>
        </body>
    </html>
    """

    mock_response = MagicMock()
    mock_response.text = html_content

    with patch("requests.get", return_value=mock_response):
        from agents.simon_scout.crawler import crawl_page
        result = crawl_page(FIXTURES["sample_url"])

    assert "url" in result, "Ergebnis muss 'url' enthalten"
    assert "title" in result, "Ergebnis muss 'title' enthalten"
    assert "text" in result, "Ergebnis muss 'text' enthalten"
    assert result["url"] == FIXTURES["sample_url"]
    assert isinstance(result["text"], str)
    assert len(result["text"]) > 0


@pytest.mark.asyncio
async def test_claim_categories_are_valid():
    """Alle Kategorien in den extrahierten Claims müssen gültige Werte haben."""
    mock_response_data = {
        "claims": FIXTURES["sample_claims"],
        "summary": {}
    }

    with patch("anthropic.Anthropic") as MockAnthropic:
        mock_client = MagicMock()
        mock_client.messages.create.return_value = _make_claude_response(mock_response_data)
        MockAnthropic.return_value = mock_client

        import agents.simon_scout.parser as parser_module
        parser_module.client = mock_client

        result = await parser_module.extract_claims(
            FIXTURES["sample_text"],
            FIXTURES["sample_url"]
        )

    for claim in result["claims"]:
        assert claim["category"] in VALID_CATEGORIES, (
            f"Ungültige Kategorie '{claim['category']}'. "
            f"Erlaubt: {VALID_CATEGORIES}"
        )
