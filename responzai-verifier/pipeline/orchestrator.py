# pipeline/orchestrator.py

from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Optional
import json


class PipelineState(TypedDict):
    source_url: str
    source_text: str
    claims: List[dict]
    verified_claims: List[dict]
    unverified_claims: List[dict]
    survived_claims: List[dict]
    weakened_claims: List[dict]
    refuted_claims: List[dict]
    contradictions: List[dict]
    consistency_score: float
    freshness_results: List[dict]
    legal_updates: List[dict]
    text_improvements: List[dict]
    ux_issues: List[dict]
    verification_report: Optional[dict]
    improvement_report: Optional[dict]
    _event_bus: Optional[object]


async def _emit(state, event_type, data):
    bus = state.get("_event_bus")
    if bus:
        await bus.emit(event_type, data)


async def simon_step(state: PipelineState) -> PipelineState:
    """Simon extrahiert Claims aus dem Text."""
    from agents.simon_scout.parser import extract_claims
    from agents.simon_scout.crawler import crawl_page

    await _emit(state, "agent_start", {
        "agent": "simon", "name": "Simon", "role": "SCOUT",
        "description": "Extrahiert pruefbare Behauptungen aus dem Text",
    })

    if state["source_url"] and not state["source_text"]:
        await _emit(state, "agent_progress", {
            "agent": "simon", "message": "Lade Webseite...", "progress": 0.1,
        })
        page = crawl_page(state["source_url"])
        state["source_text"] = page["text"]

    try:
        await _emit(state, "agent_progress", {
            "agent": "simon", "message": "Analysiere Text und extrahiere Claims...", "progress": 0.3,
        })
        result = await extract_claims(state["source_text"], state["source_url"])
        state["claims"] = result["claims"]
    except Exception as e:
        print(f"Simon: Fehler - {e}")
        state["claims"] = []

    await _emit(state, "agent_complete", {
        "agent": "simon",
        "summary": f"{len(state['claims'])} Claims gefunden",
        "stats": {"claims": len(state["claims"])},
    })
    print(f"Simon: {len(state['claims'])} Claims gefunden.")
    return state


async def vera_step(state: PipelineState) -> PipelineState:
    """Vera prüft jeden Claim gegen die Wissensbasis (sequentiell, Rate Limit)."""
    from agents.vera_verify.scoring import verify_claim

    total = len(state["claims"])
    await _emit(state, "agent_start", {
        "agent": "vera", "name": "Vera", "role": "VERIFY",
        "description": f"Prueft {total} Claims gegen die Wissensbasis",
    })

    verified = []
    unverified = []

    for i, claim in enumerate(state["claims"]):
        await _emit(state, "agent_progress", {
            "agent": "vera",
            "message": f"Pruefe Claim {i+1}/{total}: {claim.get('claim_text', '')[:60]}...",
            "progress": (i + 1) / max(total, 1),
            "claim_id": claim.get("id", ""),
        })
        try:
            result = await verify_claim(claim)
            claim["vera_result"] = result

            if result.get("score", 0) >= 0.8:
                verified.append(claim)
            else:
                unverified.append(claim)
        except Exception as e:
            print(f"Vera: Fehler bei Claim {claim.get('id', '?')} - {e}")
            claim["vera_result"] = {"score": 0.0, "reasoning": f"Fehler: {e}"}
            unverified.append(claim)

    state["verified_claims"] = verified
    state["unverified_claims"] = unverified

    await _emit(state, "agent_complete", {
        "agent": "vera",
        "summary": f"{len(verified)} verifiziert, {len(unverified)} unsicher",
        "stats": {"verified": len(verified), "unverified": len(unverified)},
    })
    print(f"Vera: {len(verified)} verifiziert, {len(unverified)} unsicher.")
    return state


async def conrad_step(state: PipelineState) -> PipelineState:
    """Conrad versucht, die verifizierten Claims zu widerlegen (sequentiell)."""
    from agents.conrad_contra.evaluation import challenge_claim

    total = len(state["verified_claims"])
    await _emit(state, "agent_start", {
        "agent": "conrad", "name": "Conrad", "role": "CONTRA",
        "description": f"Prueft {total} verifizierte Claims adversarial",
    })

    survived = []
    weakened = []
    refuted = []

    for i, claim in enumerate(state["verified_claims"]):
        await _emit(state, "agent_progress", {
            "agent": "conrad",
            "message": f"Fordere Claim {i+1}/{total} heraus: {claim.get('claim_text', '')[:60]}...",
            "progress": (i + 1) / max(total, 1),
            "claim_id": claim.get("id", ""),
        })
        try:
            result = await challenge_claim(claim, claim["vera_result"])
            claim["conrad_result"] = result

            verdict = result.get("result", "survived")
            if verdict == "survived":
                survived.append(claim)
            elif verdict == "weakened":
                weakened.append(claim)
            else:
                refuted.append(claim)
        except Exception as e:
            print(f"Conrad: Fehler bei Claim {claim.get('id', '?')} - {e}")
            claim["conrad_result"] = {"result": "survived", "reasoning": f"Fehler: {e}"}
            survived.append(claim)

    state["survived_claims"] = survived
    state["weakened_claims"] = weakened
    state["refuted_claims"] = refuted

    await _emit(state, "agent_complete", {
        "agent": "conrad",
        "summary": f"{len(survived)} ueberlebt, {len(weakened)} geschwaecht, {len(refuted)} widerlegt",
        "stats": {"survived": len(survived), "weakened": len(weakened), "refuted": len(refuted)},
    })
    print(f"Conrad: {len(survived)} überlebt, {len(weakened)} geschwächt, {len(refuted)} widerlegt.")
    return state


async def sven_step(state: PipelineState) -> PipelineState:
    """Sven prüft die Konsistenz aller Claims auf Widersprüche."""
    from agents.sven_sync.consistency import find_similar_claims
    from agents.sven_sync.contradiction_map import check_contradictions

    all_active = state["survived_claims"] + state["weakened_claims"]

    await _emit(state, "agent_start", {
        "agent": "sven", "name": "Sven", "role": "SYNC",
        "description": f"Prueft {len(all_active)} Claims auf Widersprueche",
    })

    if len(all_active) < 2:
        state["contradictions"] = []
        state["consistency_score"] = 1.0
        await _emit(state, "agent_complete", {
            "agent": "sven",
            "summary": "Zu wenig Claims fuer Konsistenzpruefung",
            "stats": {"contradictions": 0, "consistency_score": 1.0},
        })
        print("Sven: Zu wenig Claims fuer Konsistenzpruefung.")
        return state

    try:
        await _emit(state, "agent_progress", {
            "agent": "sven", "message": "Suche aehnliche Claim-Paare...", "progress": 0.3,
        })
        similar_pairs = await find_similar_claims(all_active)

        if not similar_pairs:
            state["contradictions"] = []
            state["consistency_score"] = 1.0
            await _emit(state, "agent_complete", {
                "agent": "sven",
                "summary": "Keine Widersprueche gefunden",
                "stats": {"contradictions": 0, "consistency_score": 1.0},
            })
            print("Sven: Keine aehnlichen Paare gefunden.")
            return state

        await _emit(state, "agent_progress", {
            "agent": "sven",
            "message": f"Pruefe {len(similar_pairs)} Paare auf Widersprueche...",
            "progress": 0.7,
        })
        result = await check_contradictions(similar_pairs)
        state["contradictions"] = result["contradictions"]
        state["consistency_score"] = result["consistency_score"]

        await _emit(state, "agent_complete", {
            "agent": "sven",
            "summary": f"{len(result['contradictions'])} Widersprueche, Score={result['consistency_score']}",
            "stats": {"contradictions": len(result["contradictions"]), "consistency_score": result["consistency_score"]},
        })
        print(f"Sven: {len(result['contradictions'])} Widersprueche, Score={result['consistency_score']}.")

    except Exception as e:
        state["contradictions"] = []
        state["consistency_score"] = 1.0
        await _emit(state, "agent_complete", {
            "agent": "sven",
            "summary": f"Fehler: {e}. Score auf 1.0 gesetzt",
            "stats": {"contradictions": 0, "consistency_score": 1.0},
        })
        print(f"Sven: Fehler - {e}. Score auf 1.0 gesetzt.")

    return state


async def pia_step(state: PipelineState) -> PipelineState:
    """Pia prüft die Aktualität aller Claims."""
    claims_to_check = state["survived_claims"] + state["weakened_claims"]

    await _emit(state, "agent_start", {
        "agent": "pia", "name": "Pia", "role": "PULSE",
        "description": f"Prueft {len(claims_to_check)} Claims auf Aktualitaet",
    })

    freshness_results = []
    for claim in claims_to_check:
        result = {
            "claim_id": claim.get("id", "unbekannt"),
            "freshness": "fresh",
        }
        freshness_results.append(result)

    state["freshness_results"] = freshness_results

    await _emit(state, "agent_complete", {
        "agent": "pia",
        "summary": f"{len(freshness_results)} Claims geprueft",
        "stats": {"checked": len(freshness_results)},
    })
    print(f"Pia: {len(freshness_results)} Claims auf Aktualität geprüft.")
    return state


async def lena_step(state: PipelineState) -> PipelineState:
    """Lena generiert rechtliche Aktualisierungen mit Rueckpruefung."""
    from agents.lena_legal.source_mapper import map_sources_to_claim
    from agents.lena_legal.text_generator import generate_legal_update
    from agents.lena_legal.verification_loop import run_verification_loop

    legal_updates = []
    problematic = state["weakened_claims"] + state["refuted_claims"]
    problematic += [c for c in state["freshness_results"]
                    if c.get("freshness") in ["stale", "outdated"]]

    await _emit(state, "agent_start", {
        "agent": "lena", "name": "Lena", "role": "LEGAL",
        "description": f"Erstellt rechtliche Updates fuer {len(problematic)} problematische Claims",
    })

    for i, claim in enumerate(problematic):
        claim_text = claim.get("claim_text", "")
        if not claim_text:
            continue

        await _emit(state, "agent_progress", {
            "agent": "lena",
            "message": f"Bearbeite Claim {i+1}/{len(problematic)}: {claim_text[:60]}...",
            "progress": (i + 1) / max(len(problematic), 1),
        })

        try:
            sources = await map_sources_to_claim(claim)
            if not sources:
                legal_updates.append({
                    "status": "REVIEW",
                    "reason": "Keine relevanten Quellen gefunden.",
                    "claim": claim_text,
                })
                continue

            lena_output = await generate_legal_update(claim, sources)
            claim["lena_output"] = lena_output
            claim["source_passages"] = sources

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

    await _emit(state, "agent_complete", {
        "agent": "lena",
        "summary": f"{len(legal_updates)} rechtliche Updates",
        "stats": {"updates": len(legal_updates)},
    })
    print(f"Lena: {len(legal_updates)} rechtliche Updates vorgeschlagen.")
    return state


async def david_step(state: PipelineState) -> PipelineState:
    """Davina optimiert den Quelltext sprachlich nach responzai-Stilguide."""
    from agents.david_draft.style_guide import check_style
    from agents.david_draft.rewriter import rewrite_text

    await _emit(state, "agent_start", {
        "agent": "david", "name": "Davina", "role": "DRAFT",
        "description": "Optimiert den Text sprachlich",
    })

    source_text = state.get("source_text", "")
    if not source_text:
        state["text_improvements"] = []
        await _emit(state, "agent_complete", {
            "agent": "david", "summary": "Kein Quelltext vorhanden",
            "stats": {"improvements": 0},
        })
        print("Davina: Kein Quelltext vorhanden, uebersprungen.")
        return state

    try:
        await _emit(state, "agent_progress", {
            "agent": "david", "message": "Pruefe Stilguide-Regeln...", "progress": 0.3,
        })
        style_issues = check_style(source_text)

        await _emit(state, "agent_progress", {
            "agent": "david",
            "message": f"{len(style_issues)} Stilprobleme gefunden, erstelle Verbesserungen...",
            "progress": 0.6,
        })
        result = await rewrite_text(source_text, style_issues)
        state["text_improvements"] = result.get("changes", [])

        await _emit(state, "agent_complete", {
            "agent": "david",
            "summary": f"{len(state['text_improvements'])} Textverbesserungen",
            "stats": {"improvements": len(state["text_improvements"])},
        })
        print(f"Davina: {len(state['text_improvements'])} Textverbesserungen vorgeschlagen.")
    except Exception as e:
        state["text_improvements"] = [{
            "error": str(e),
            "reason": "Davina konnte den Text nicht optimieren."
        }]
        await _emit(state, "agent_complete", {
            "agent": "david", "summary": f"Fehler: {e}",
            "stats": {"improvements": 0},
        })
        print(f"Davina: Fehler - {e}")

    return state


async def uma_step(state: PipelineState) -> PipelineState:
    """Uma prueft die Bedienungsfreundlichkeit des Quelltexts."""
    from agents.uma_ux.structure_analyzer import analyze_structure
    from agents.uma_ux.usability_rules import review_usability

    await _emit(state, "agent_start", {
        "agent": "uma", "name": "Uma", "role": "UX",
        "description": "Analysiert Struktur und Bedienungsfreundlichkeit",
    })

    source_text = state.get("source_text", "")
    if not source_text:
        state["ux_issues"] = []
        await _emit(state, "agent_complete", {
            "agent": "uma", "summary": "Kein Quelltext vorhanden",
            "stats": {"issues": 0},
        })
        print("Uma: Kein Quelltext vorhanden, uebersprungen.")
        return state

    try:
        await _emit(state, "agent_progress", {
            "agent": "uma", "message": "Analysiere Dokumentstruktur...", "progress": 0.3,
        })
        paragraphs = [p.strip() for p in source_text.split("\n\n") if p.strip()]
        sections = [{"content": p, "title": "", "level": None} for p in paragraphs]
        structure_info = analyze_structure(sections)

        await _emit(state, "agent_progress", {
            "agent": "uma", "message": "Pruefe Usability-Regeln...", "progress": 0.6,
        })
        result = await review_usability(source_text, sections, structure_info)
        state["ux_issues"] = result.get("issues", [])

        await _emit(state, "agent_complete", {
            "agent": "uma",
            "summary": f"{len(state['ux_issues'])} UX-Probleme",
            "stats": {"issues": len(state["ux_issues"])},
        })
        print(f"Uma: {len(state['ux_issues'])} UX-Probleme gefunden.")
    except Exception as e:
        state["ux_issues"] = [{
            "error": str(e),
            "reason": "Uma konnte die UX-Pruefung nicht durchfuehren."
        }]
        await _emit(state, "agent_complete", {
            "agent": "uma", "summary": f"Fehler: {e}",
            "stats": {"issues": 0},
        })
        print(f"Uma: Fehler - {e}")

    return state


async def generate_reports(state: PipelineState) -> PipelineState:
    """Erstellt die finalen Berichte."""
    from pipeline.reporting import create_verification_report, create_improvement_report

    await _emit(state, "agent_start", {
        "agent": "reports", "name": "Report", "role": "REPORT",
        "description": "Erstellt Verifikations- und Verbesserungsbericht",
    })

    state["verification_report"] = create_verification_report(state)
    state["improvement_report"] = create_improvement_report(state)

    await _emit(state, "agent_complete", {
        "agent": "reports", "summary": "Berichte erstellt",
        "stats": {},
    })
    print("Berichte erstellt.")
    return state


def build_pipeline():
    """Baut die LangGraph-Pipeline zusammen."""
    workflow = StateGraph(PipelineState)

    workflow.add_node("simon", simon_step)
    workflow.add_node("vera", vera_step)
    workflow.add_node("conrad", conrad_step)
    workflow.add_node("sven", sven_step)
    workflow.add_node("pia", pia_step)
    workflow.add_node("lena", lena_step)
    workflow.add_node("david", david_step)
    workflow.add_node("uma", uma_step)
    workflow.add_node("reports", generate_reports)

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


def build_improvement_pipeline():
    """Verkürzte Pipeline: nur Davina und Uma."""
    workflow = StateGraph(PipelineState)

    workflow.add_node("david", david_step)
    workflow.add_node("uma", uma_step)
    workflow.add_node("reports", generate_reports)

    workflow.set_entry_point("david")
    workflow.add_edge("david", "uma")
    workflow.add_edge("uma", "reports")
    workflow.add_edge("reports", END)

    return workflow.compile()
