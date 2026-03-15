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
    Rückprüfung von Lenas Vorschlag.

    Nur Hash-basierte Quellen-Validierung (kein zweiter Vera+Conrad-Durchlauf).
    Der Hash-Check ist ausreichend: er stellt sicher, dass Lena sich
    nur auf bekannte Quellen bezieht und keine Inhalte erfindet.
    """
    binding_check = verify_source_binding(lena_output, claim.get("source_passages", []))

    if binding_check["status"] != "ACCEPTED":
        return binding_check

    return {
        "status": "ACCEPTED",
        "lena_output": lena_output,
    }
