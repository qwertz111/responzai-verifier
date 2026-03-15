"""
Tests fuer die LangGraph-Pipeline (orchestrator + config).

Prueft, ob die Pipeline korrekt aufgebaut wird, ob PipelineState
alle erforderlichen Felder hat und ob die Konfigurationswerte stimmen.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Fixtures laden
FIXTURES_PATH = Path(__file__).parent / "fixtures.json"
with open(FIXTURES_PATH, encoding="utf-8") as f:
    FIXTURES = json.load(f)


def test_build_pipeline_creates_graph():
    """build_pipeline() soll einen kompilierten LangGraph-Graphen zurueckgeben."""
    from pipeline.orchestrator import build_pipeline

    graph = build_pipeline()

    # Ein kompilierter LangGraph-Graph hat ein invoke- oder astream-Attribut
    assert graph is not None, "build_pipeline() darf nicht None zurueckgeben"
    assert hasattr(graph, "invoke") or hasattr(graph, "astream") or hasattr(graph, "ainvoke"), (
        "Der Graph muss ein aufrufbares LangGraph-Objekt sein (invoke/ainvoke/astream)"
    )


def test_pipeline_state_has_all_fields():
    """PipelineState muss alle fuer die Pipeline erforderlichen Felder definieren."""
    from pipeline.orchestrator import PipelineState

    required_fields = {
        # Eingabe
        "source_url",
        "source_text",
        # Simon
        "claims",
        # Vera
        "verified_claims",
        "unverified_claims",
        # Conrad
        "survived_claims",
        "weakened_claims",
        "refuted_claims",
        # Sven
        "contradictions",
        "consistency_score",
        # Pia
        "freshness_results",
        # Lena
        "legal_updates",
        # Davina
        "text_improvements",
        # Uma
        "ux_issues",
        # Berichte
        "verification_report",
        "improvement_report",
    }

    # TypedDict speichert seine Felder in __annotations__
    defined_fields = set(PipelineState.__annotations__.keys())

    missing = required_fields - defined_fields
    assert not missing, f"PipelineState fehlen folgende Felder: {missing}"


def test_pipeline_config_values():
    """Konfigurationswerte muessen die spezifizierten Schwellenwerte haben."""
    from pipeline.config import (
        VERIFICATION_THRESHOLD,
        ADVERSARIAL_PASS,
        CONSISTENCY_THRESHOLD,
        FRESHNESS_MAX_DAYS,
        LEGAL_COVERAGE_MIN,
        LLM_TEMPERATURE,
        LLM_MODEL,
        EMBEDDING_MODEL,
    )

    # Schwellenwerte gemaess Spezifikation pruefen
    assert VERIFICATION_THRESHOLD == 0.8, (
        f"VERIFICATION_THRESHOLD muss 0.8 sein, war: {VERIFICATION_THRESHOLD}"
    )
    assert LLM_TEMPERATURE == 0, (
        f"LLM_TEMPERATURE muss 0 sein (keine Kreativitaet), war: {LLM_TEMPERATURE}"
    )
    assert LEGAL_COVERAGE_MIN == 0.95, (
        f"LEGAL_COVERAGE_MIN muss 0.95 sein, war: {LEGAL_COVERAGE_MIN}"
    )
    assert CONSISTENCY_THRESHOLD == 0.7, (
        f"CONSISTENCY_THRESHOLD muss 0.7 sein, war: {CONSISTENCY_THRESHOLD}"
    )
    assert FRESHNESS_MAX_DAYS == 90, (
        f"FRESHNESS_MAX_DAYS muss 90 sein, war: {FRESHNESS_MAX_DAYS}"
    )

    # Adversariale Ergebnisse, die die Pipeline passieren duerfen
    assert "survived" in ADVERSARIAL_PASS, "'survived' muss in ADVERSARIAL_PASS sein"
    assert "weakened" in ADVERSARIAL_PASS, "'weakened' muss in ADVERSARIAL_PASS sein"
    assert "refuted" not in ADVERSARIAL_PASS, "'refuted' darf NICHT in ADVERSARIAL_PASS sein"

    # Modell-Konfiguration
    assert isinstance(LLM_MODEL, str) and len(LLM_MODEL) > 0, "LLM_MODEL muss ein nichtleerer String sein"
    assert "voyage" in EMBEDDING_MODEL.lower(), "EMBEDDING_MODEL sollte Voyage sein"
