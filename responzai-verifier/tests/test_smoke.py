"""
End-to-End Smoke-Tests fuer das responzai-Agentensystem.

Diese Tests prüfen, ob alle Module importierbar sind und die
Grundstrukturen (Pydantic-Modelle, Fixtures, Pipeline) korrekt
instanziiert werden koennen. Kein echter API-Aufruf noetig.
"""

import json
import pytest
import importlib
from pathlib import Path
from datetime import datetime

# Fixtures laden
FIXTURES_PATH = Path(__file__).parent / "fixtures.json"
with open(FIXTURES_PATH, encoding="utf-8") as f:
    FIXTURES = json.load(f)


# ─── Import-Tests ─────────────────────────────────────────────────────────────

def test_all_agent_modules_importable():
    """Alle Agenten-Module muessen ohne Fehler importierbar sein."""
    agent_modules = [
        "agents.simon_scout.prompt",
        "agents.simon_scout.crawler",
        "agents.simon_scout.parser",
        "agents.vera_verify.prompt",
        "agents.vera_verify.rag_query",
        "agents.vera_verify.scoring",
        "agents.conrad_contra.prompt",
        "agents.conrad_contra.strategies",
        "agents.conrad_contra.evaluation",
        "agents.sven_sync.prompt",
        "agents.sven_sync.consistency",
        "agents.pia_pulse.prompt",
        "agents.pia_pulse.monitors",
        "agents.lena_legal.prompt",
        "agents.lena_legal.verification_loop",
        "agents.david_draft.prompt",
        "agents.uma_ux.prompt",
    ]

    failed_imports = []
    for module_name in agent_modules:
        try:
            importlib.import_module(module_name)
        except ImportError as e:
            failed_imports.append(f"{module_name}: {e}")
        except Exception as e:
            # Andere Fehler (z.B. fehlende Env-Vars beim Modulstart) tolerieren wir nicht
            failed_imports.append(f"{module_name}: {type(e).__name__}: {e}")

    assert not failed_imports, (
        "Folgende Module konnten nicht importiert werden:\n" +
        "\n".join(f"  - {m}" for m in failed_imports)
    )


def test_pipeline_importable():
    """pipeline.orchestrator und pipeline.config muessen importierbar sein."""
    import pipeline.orchestrator
    import pipeline.config

    # Grundlegende Attribute prüfen
    assert hasattr(pipeline.orchestrator, "build_pipeline"), \
        "pipeline.orchestrator muss 'build_pipeline' exportieren"
    assert hasattr(pipeline.orchestrator, "PipelineState"), \
        "pipeline.orchestrator muss 'PipelineState' exportieren"
    assert hasattr(pipeline.config, "VERIFICATION_THRESHOLD"), \
        "pipeline.config muss 'VERIFICATION_THRESHOLD' exportieren"


def test_shared_schemas_valid():
    """Pydantic-Modelle aus shared/schemas.py muessen mit Beispieldaten instanziiert werden koennen."""
    from shared.schemas import (
        Claim, ClaimCategory, Verifiability,
        VeraOutput, VerificationStatus, SupportingPassage,
        ConradOutput, AdversarialResult, StrategyFinding, Severity,
        FreshnessStatus,
        PipelineInput,
    )

    # Claim instanziieren
    sample = FIXTURES["sample_claims"][0]
    claim = Claim(
        id=sample["id"],
        claim_text=sample["claim_text"],
        category=ClaimCategory(sample["category"]),
        verifiability=Verifiability(sample["verifiability"]),
        original_text=sample["original_text"],
        source_url=sample["source_url"],
        implicit_assumptions=sample.get("implicit_assumptions", []),
    )
    assert claim.id == "claim_001"

    # VeraOutput instanziieren
    vera = FIXTURES["sample_vera_result"]
    vera_output = VeraOutput(
        claim_id=vera["claim_id"],
        score=vera["score"],
        status=VerificationStatus(vera["status"]),
        reasoning=vera["reasoning"],
        supporting_passages=[
            SupportingPassage(
                chunk_id=p["chunk_id"],
                text=p["text"],
                source=p["source"],
                relevance=p["relevance"],
            )
            for p in vera["supporting_passages"]
        ],
        gaps=vera.get("gaps", []),
    )
    assert 0.0 <= vera_output.score <= 1.0

    # ConradOutput instanziieren
    conrad = FIXTURES["sample_conrad_result"]
    conrad_output = ConradOutput(
        claim_id=conrad["claim_id"],
        result=AdversarialResult(conrad["result"]),
        strategies_applied=[
            StrategyFinding(
                strategy=s["strategy"],
                finding=s["finding"],
                evidence=s["evidence"],
                severity=Severity(s["severity"]),
            )
            for s in conrad["strategies_applied"]
        ],
        overall_assessment=conrad["overall_assessment"],
        suggested_refinement=conrad.get("suggested_refinement"),
    )
    assert conrad_output.result in AdversarialResult

    # PipelineInput instanziieren
    pipeline_input = PipelineInput(
        source_url=FIXTURES["sample_url"],
        source_text=FIXTURES["sample_text"],
    )
    assert pipeline_input.source_url == FIXTURES["sample_url"]


def test_fixtures_loadable():
    """fixtures.json muss korrekt laden und alle erwarteten Schluessel enthalten."""
    required_keys = {
        "sample_text",
        "sample_url",
        "sample_claims",
        "sample_vera_result",
        "sample_conrad_result",
        "sample_chunk",
    }

    missing = required_keys - set(FIXTURES.keys())
    assert not missing, f"fixtures.json fehlen folgende Schluessel: {missing}"

    # Mindestens 3 Beispiel-Claims
    assert len(FIXTURES["sample_claims"]) >= 3, "Mindestens 3 sample_claims erwartet"

    # Score-Werte muessen im gueltigen Bereich liegen
    assert 0.0 <= FIXTURES["sample_vera_result"]["score"] <= 1.0, \
        "vera_result.score muss zwischen 0 und 1 liegen"

    # Conrad-Ergebnis muss gueltigen Wert haben
    assert FIXTURES["sample_conrad_result"]["result"] in {"survived", "weakened", "refuted"}, \
        "sample_conrad_result.result muss survived/weakened/refuted sein"

    # Jeder Sample-Claim muss einen gueltigen Kategorie-Wert haben
    valid_categories = {"LEGAL_CLAIM", "PRODUCT_CLAIM", "MARKET_CLAIM", "TARGET_GROUP"}
    for claim in FIXTURES["sample_claims"]:
        assert claim["category"] in valid_categories, \
            f"Ungueltiger Kategorie-Wert: {claim['category']}"


def test_document_ingestion_modules_importable():
    """Alle document_ingestion-Module muessen importierbar sein."""
    ingestion_modules = [
        "document_ingestion.router",
        "document_ingestion.preprocessor",
        "document_ingestion.storage",
        "document_ingestion.metadata_extractor",
    ]

    failed = []
    for module_name in ingestion_modules:
        try:
            importlib.import_module(module_name)
        except ImportError as e:
            failed.append(f"{module_name}: {e}")
        except Exception as e:
            failed.append(f"{module_name}: {type(e).__name__}: {e}")

    assert not failed, (
        "Folgende document_ingestion-Module konnten nicht importiert werden:\n" +
        "\n".join(f"  - {m}" for m in failed)
    )
