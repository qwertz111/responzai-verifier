# agents/lena_legal/verification_loop.py

import hashlib

def verify_source_binding(lena_output: dict, provided_sources: list) -> dict:
    """
    Prüft, ob Lena sich wirklich nur auf die mitgelieferten Quellen bezieht.

    Warum ist das wichtig?
    Lena könnte "halluzinieren", also Informationen erfinden, die
    plausibel klingen, aber nicht in den Quellen stehen. Diese Prüfung
    stellt sicher, dass jede Quellenreferenz in Lenas Output tatsächlich
    auf eine echte Quelle zurückgeht.

    Wie funktioniert das?
    Jede Quelle bekommt einen digitalen Fingerabdruck (Hash).
    Wir prüfen, ob alle Fingerabdrücke, die Lena nennt, auch
    in den bereitgestellten Quellen vorkommen.
    """
    # Hashes der bereitgestellten Quellen berechnen
    source_hashes = set()
    for source in provided_sources:
        hash_value = hashlib.sha256(source["text"].encode()).hexdigest()[:12]
        source_hashes.add(hash_value)

    # Hashes in Lenas Output prüfen
    used_hashes = set()
    for ref in lena_output.get("sources_used", []):
        used_hashes.add(ref["hash"])

    # Gibt es Quellen, die Lena nennt, die wir nicht kennen?
    unknown_sources = used_hashes - source_hashes

    if unknown_sources:
        return {
            "status": "REJECTED",
            "reason": f"Lena referenziert unbekannte Quellen: {unknown_sources}",
            "action": "Lenas Vorschlag wird verworfen. Bitte manuell prüfen."
        }

    # Quellenabdeckung prüfen
    if lena_output.get("coverage", 0) < 0.95:
        return {
            "status": "REVIEW",
            "reason": f"Quellenabdeckung nur {lena_output.get('coverage', 0)*100:.0f}%",
            "action": "Lenas Vorschlag braucht menschliche Prüfung."
        }

    return {
        "status": "ACCEPTED",
        "reason": "Alle Quellen verifiziert, Abdeckung ausreichend."
    }


async def run_verification_loop(lena_output: dict, claim: dict):
    """
    Die Rückprüfungsschleife: Lenas Vorschlag geht nochmal durch
    Vera und Conrad.

    Ablauf:
    1. Lena generiert einen Textvorschlag.
    2. Quellen-Binding wird geprüft (Funktion oben).
    3. Vera prüft den neuen Text gegen die Wissensbasis.
    4. Conrad versucht, den neuen Text zu widerlegen.
    5. Nur wenn alles besteht, wird der Vorschlag akzeptiert.
    """
    from agents.vera_verify.scoring import verify_claim
    from agents.conrad_contra.evaluation import challenge_claim

    # Schritt 1: Quellen-Binding prüfen
    binding_check = verify_source_binding(lena_output, claim.get("source_passages", []))
    if binding_check["status"] == "REJECTED":
        return binding_check

    # Schritt 2: Neuen Claim aus Lenas Vorschlag erstellen
    new_claim = {
        "claim_text": lena_output.get("suggested_text", ""),
        "category": claim.get("category", "LEGAL_CLAIM"),
        "source_url": claim.get("source_url", "")
    }

    # Schritt 3: Vera prüft den neuen Text
    vera_result = await verify_claim(new_claim)
    if vera_result["score"] < 0.9:
        return {
            "status": "REJECTED",
            "reason": f"Vera gibt dem neuen Text nur Score {vera_result['score']}",
            "vera_feedback": vera_result
        }

    # Schritt 4: Conrad prüft den neuen Text
    conrad_result = await challenge_claim(new_claim, vera_result)
    if conrad_result["result"] == "refuted":
        return {
            "status": "REJECTED",
            "reason": "Conrad hat den neuen Text widerlegt",
            "conrad_feedback": conrad_result
        }

    return {
        "status": "ACCEPTED",
        "lena_output": lena_output,
        "vera_score": vera_result["score"],
        "conrad_result": conrad_result["result"]
    }
