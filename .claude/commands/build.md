# Build-Befehl mit automatischem Modell-Routing

Wenn der Nutzer eine Aufgabe gibt, route wie folgt:

## Schritt 1: Aufgabe klassifizieren

Prüfe die Aufgabe gegen diese Kategorien:

**OPUS-Aufgaben** (Qualität entscheidend):
- Enthält: "Prompt", "System-Prompt", "Agenten-Prompt"
- Enthält: "Conrad", "adversarial", "Gegenprüfung"
- Enthält: "Lena", "Anti-Halluzination", "Quellenbindung", "verification_loop"
- Enthält: "Pipeline", "Orchestrierung", "orchestrator"
- Enthält: "Sicherheit", "Validierung", "Auth", "Security"
- Enthält: "Architektur", "Refactoring" (mit Strukturänderung)
- Enthält: "Debug" (bei komplexen Fehlern)

**HAIKU-Aufgaben** (reine Boilerplate):
- Enthält: "__init__", "init.py"
- Enthält: "Dockerfile", "docker-compose", "docker"
- Enthält: "requirements.txt", ".env", ".gitignore"
- Enthält: "Ordnerstruktur", "Verzeichnisse anlegen"
- Enthält: "README"
- Enthält: "config.py" (nur Konstanten)
- Die Aufgabe ist offensichtlich Kopierarbeit

**SONNET-Aufgaben** (alles andere):
- Parser, API-Routes, React-Komponenten
- Datenbank-Code, Tests, Bug-Fixes
- Standard-Implementierung

## Schritt 2: Subagent starten

Starte einen Agent mit dem passenden `model`-Parameter.
Gib dem Agenten eine PRÄZISE Aufgabenbeschreibung.
Füge NICHT die gesamte Arbeitsanweisung bei.
Gib nur den relevanten Kontext (Dateipfade, Schnittstellenbeschreibung, Beispiele).

## Schritt 3: Ergebnis prüfen

Nach Rückkehr des Subagenten:
- Prüfe das Ergebnis auf Vollständigkeit
- Bei Opus-Aufgaben: Kein weiterer Review nötig
- Bei Sonnet-Aufgaben: Kurzer Plausibilitätscheck
- Bei Haiku-Aufgaben: Nur prüfen ob Dateien erstellt wurden

## Schritt 4: Status aktualisieren

Aktualisiere die "Aktuelle Phase" in CLAUDE.md.
