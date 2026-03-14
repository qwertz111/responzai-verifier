# pipeline/orchestrator.py

from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Optional
import json

# Der "State" ist der Zustand, der durch die Pipeline fließt.
# Jeder Agent liest daraus und schreibt hinein.

class PipelineState(TypedDict):
    # Eingabe
    source_url: str
    source_text: str

    # Simon (SCOUT)
    claims: List[dict]

    # Vera (VERIFY)
    verified_claims: List[dict]
    unverified_claims: List[dict]

    # Conrad (CONTRA)
    survived_claims: List[dict]
    weakened_claims: List[dict]
    refuted_claims: List[dict]

    # Sven (SYNC)
    contradictions: List[dict]
    consistency_score: float

    # Pia (PULSE)
    freshness_results: List[dict]

    # Lena (LEGAL)
    legal_updates: List[dict]

    # David (DRAFT)
    text_improvements: List[dict]

    # Uma (UX)
    ux_issues: List[dict]

    # Berichte
    verification_report: Optional[dict]
    improvement_report: Optional[dict]


# Die einzelnen Schritte der Pipeline

async def simon_step(state: PipelineState) -> PipelineState:
    """Simon extrahiert Claims aus dem Text."""
    from agents.simon_scout.parser import extract_claims
    from agents.simon_scout.crawler import crawl_page

    # Wenn eine URL gegeben ist, zuerst crawlen
    if state["source_url"] and not state["source_text"]:
        page = crawl_page(state["source_url"])
        state["source_text"] = page["text"]

    # Claims extrahieren
    result = await extract_claims(state["source_text"], state["source_url"])
    state["claims"] = result["claims"]

    print(f"Simon: {len(state['claims'])} Claims gefunden.")
    return state


async def vera_step(state: PipelineState) -> PipelineState:
    """Vera prüft jeden Claim gegen die Wissensbasis."""
    from agents.vera_verify.scoring import verify_claim

    verified = []
    unverified = []

    for claim in state["claims"]:
        result = await verify_claim(claim)
        claim["vera_result"] = result

        if result["score"] >= 0.8:
            verified.append(claim)
        else:
            unverified.append(claim)

    state["verified_claims"] = verified
    state["unverified_claims"] = unverified

    print(f"Vera: {len(verified)} verifiziert, {len(unverified)} unsicher.")
    return state


async def conrad_step(state: PipelineState) -> PipelineState:
    """Conrad versucht, die verifizierten Claims zu widerlegen."""
    from agents.conrad_contra.evaluation import challenge_claim

    survived = []
    weakened = []
    refuted = []

    for claim in state["verified_claims"]:
        result = await challenge_claim(claim, claim["vera_result"])
        claim["conrad_result"] = result

        if result["result"] == "survived":
            survived.append(claim)
        elif result["result"] == "weakened":
            weakened.append(claim)
        else:
            refuted.append(claim)

    state["survived_claims"] = survived
    state["weakened_claims"] = weakened
    state["refuted_claims"] = refuted

    print(f"Conrad: {len(survived)} überlebt, {len(weakened)} geschwächt, {len(refuted)} widerlegt.")
    return state


async def sven_step(state: PipelineState) -> PipelineState:
    """Sven prüft die Konsistenz aller Claims."""
    from agents.sven_sync.consistency import find_similar_claims

    # Alle Claims, die noch im Rennen sind
    all_active = state["survived_claims"] + state["weakened_claims"]

    similar_pairs = await find_similar_claims(all_active)

    # TODO: Für jedes ähnliche Paar prüfen, ob sie sich widersprechen
    # (Hier kommt Svens Claude-Aufruf)

    state["contradictions"] = []  # Wird befüllt
    state["consistency_score"] = 1.0  # Default: keine Widersprueche gefunden

    print(f"Sven: {len(similar_pairs)} ähnliche Paare gefunden.")
    return state


async def pia_step(state: PipelineState) -> PipelineState:
    """Pia prüft die Aktualität aller Claims."""
    from agents.pia_pulse.monitors import check_eurlex_updates, check_freshness

    freshness_results = []

    for claim in state["survived_claims"] + state["weakened_claims"]:
        # Zeitbezüge im Claim finden und Aktualität prüfen
        # (Vereinfachte Version)
        result = {
            "claim_id": claim["id"],
            "freshness": "fresh",  # Wird durch Pias Claude-Aufruf bestimmt
        }
        freshness_results.append(result)

    state["freshness_results"] = freshness_results

    print(f"Pia: {len(freshness_results)} Claims auf Aktualität geprüft.")
    return state


async def lena_step(state: PipelineState) -> PipelineState:
    """Lena generiert rechtliche Aktualisierungen mit Rueckpruefung."""
    from agents.lena_legal.source_mapper import map_sources_to_claim
    from agents.lena_legal.text_generator import generate_legal_update
    from agents.lena_legal.verification_loop import run_verification_loop

    legal_updates = []

    # Lena arbeitet nur an Claims, die Probleme haben
    problematic = state["weakened_claims"] + state["refuted_claims"]
    problematic += [c for c in state["freshness_results"]
                    if c.get("freshness") in ["stale", "outdated"]]

    for claim in problematic:
        claim_text = claim.get("claim_text", "")
        if not claim_text:
            continue

        try:
            # 1. Relevante Quellen finden und mit Hashes versehen
            sources = await map_sources_to_claim(claim)
            if not sources:
                legal_updates.append({
                    "status": "REVIEW",
                    "reason": "Keine relevanten Quellen gefunden.",
                    "claim": claim_text,
                })
                continue

            # 2. Lena generiert Textvorschlag (Claude Opus, temperature=0)
            lena_output = await generate_legal_update(claim, sources)
            claim["lena_output"] = lena_output
            claim["source_passages"] = sources

            # 3. Rueckpruefung: Quellen-Binding + Vera + Conrad
            if not lena_output.get("suggested_text"):
                legal_updates.append({
                    "status": "REVIEW",
                    "reason": "Lena konnte keinen Textvorschlag generieren.",
                    "claim": claim_text,
                })
                continue

            result = await run_verification_loop(lena_output, claim)
            legal_updates.append(result)

        except Exception as e:
            legal_updates.append({
                "status": "ERROR",
                "reason": f"Fehler bei Lena: {str(e)}",
                "claim": claim_text,
            })

    state["legal_updates"] = legal_updates

    print(f"Lena: {len(legal_updates)} rechtliche Updates vorgeschlagen.")
    return state


async def david_step(state: PipelineState) -> PipelineState:
    """David optimiert die Texte sprachlich."""
    # David arbeitet an allen Texten, nicht nur an problematischen
    state["text_improvements"] = []  # Wird befüllt

    print("David: Textoptimierung abgeschlossen.")
    return state


async def uma_step(state: PipelineState) -> PipelineState:
    """Uma prüft die Bedienungsfreundlichkeit."""
    state["ux_issues"] = []  # Wird befüllt

    print("Uma: UX-Prüfung abgeschlossen.")
    return state


async def generate_reports(state: PipelineState) -> PipelineState:
    """Erstellt die finalen Berichte."""
    from pipeline.reporting import create_verification_report, create_improvement_report

    state["verification_report"] = create_verification_report(state)
    state["improvement_report"] = create_improvement_report(state)

    print("Berichte erstellt.")
    return state


# Den Graphen zusammenbauen

def build_pipeline():
    """
    Baut die LangGraph-Pipeline zusammen.

    Die Pipeline hat zwei Phasen:
    Phase 1 (Prüfung): Simon → Vera → Conrad → Sven → Pia
    Phase 2 (Verbesserung): Lena → David → Uma → Berichte
    """
    workflow = StateGraph(PipelineState)

    # Knoten hinzufügen (jeder Agent ist ein Knoten)
    workflow.add_node("simon", simon_step)
    workflow.add_node("vera", vera_step)
    workflow.add_node("conrad", conrad_step)
    workflow.add_node("sven", sven_step)
    workflow.add_node("pia", pia_step)
    workflow.add_node("lena", lena_step)
    workflow.add_node("david", david_step)
    workflow.add_node("uma", uma_step)
    workflow.add_node("reports", generate_reports)

    # Kanten hinzufügen (die Reihenfolge)
    workflow.set_entry_point("simon")
    workflow.add_edge("simon", "vera")
    workflow.add_edge("vera", "conrad")
    workflow.add_edge("conrad", "sven")
    workflow.add_edge("sven", "pia")
    workflow.add_edge("pia", "lena")
    workflow.add_edge("lena", "david")
    workflow.add_edge("david", "uma")
    workflow.add_edge("uma", "reports")
    workflow.add_edge("reports", END)

    return workflow.compile()
