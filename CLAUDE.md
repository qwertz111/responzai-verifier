# responzai Multi-Agent Verification System

## Projekt-Überblick (Kurzfassung)

8 KI-Agenten prüfen und verbessern Texte zu EU AI Act, KI-Governance, KI-Kompetenz.
3 Repos: `responzai-verifier` (Agenten + API), `responzai-knowledge` (Wissensbasis), `responzai-web` (Website).
Stack: Python/FastAPI, LangGraph, PostgreSQL + pgvector, Claude API, Voyage-3, Docker, n8n.

### Agenten

| Agent | Kürzel | Aufgabe |
|-------|--------|---------|
| Simon | SCOUT | Text in prüfbare Claims zerlegen |
| Vera | VERIFY | Claims gegen Wissensbasis prüfen (RAG) |
| Conrad | CONTRA | Adversariale Gegenprüfung |
| Sven | SYNC | Konsistenzprüfung über alle Kanäle |
| Pia | PULSE | Aktualitätsprüfung (EUR-Lex, RSS) |
| Lena | LEGAL | Rechtliche Textaktualisierung (Anti-Halluzination!) |
| David | DRAFT | Sprachliche Optimierung (Stilguide) |
| Uma | UX | Bedienungsfreundlichkeit |

### Pipeline

```
Eingabe (URL / Text / Datei-Upload) → Simon → Vera → Conrad → Sven → Pia → Lena → David → Uma → Bericht
```

### Schwellenwerte

- Vera: Score >= 0.8 → weiter an Conrad
- Conrad: survived/weakened → weiter, refuted → raus
- Lena: Coverage >= 0.95, temperature=0, Rückprüfung durch Vera+Conrad
- Alle Agenten: temperature=0

## Vollständige Arbeitsanweisung

Detaillierte Spezifikation mit allen Prompts, Code-Beispielen und Infrastruktur-Anleitungen:
→ `responzai_arbeitsanweisung_claude_code_2.md`

Lies diese Datei NUR abschnittsweise, wenn du Details zu einem bestimmten Kapitel brauchst.
Lade NIEMALS die gesamte Datei in den Kontext.

## Konventionen

- Sprache im Code: Englisch (Variablen, Funktionen, Kommentare)
- Sprache der Agenten-Prompts: Deutsch
- Sprache der UI: Deutsch
- Keine Gedankenstriche in Texten
- Alle Agenten werden mit menschlichem Namen + Kürzel referenziert: "Simon (SCOUT)"
- Claims-Kategorien: LEGAL_CLAIM, PRODUCT_CLAIM, MARKET_CLAIM, TARGET_GROUP

---

## Token-Spar-Strategie (WICHTIG, IMMER BEFOLGEN)

### Priorität 1: Extrahieren statt Generieren

~35 Dateien existieren bereits als Code-Blöcke in der Arbeitsanweisung.
→ Siehe `CODE_MAP.md` für das vollständige Mapping.

**Ablauf für Dateien die in der Arbeitsanweisung stehen:**
1. Lies den Zeilenbereich aus `responzai_arbeitsanweisung_claude_code_2.md` (mit offset/limit)
2. Extrahiere den Code-Block (alles zwischen ``` und ```)
3. Schreibe ihn mit dem Write-Tool direkt in die Zieldatei
4. KEIN Subagent nötig. KEINE Neugeneration. Direkte Kopie.

**Das spart ~70% der Gesamtkosten.** Nur ~15 Dateien müssen tatsächlich generiert werden.

### Priorität 2: Batch-Erstellung

Wenn mehrere Dateien generiert werden müssen (nicht extrahiert), fasse ähnliche zusammen:
- NICHT: 8 Subagenten für 8 ähnliche Dateien
- STATTDESSEN: 1 Subagent erstellt alle ähnlichen Dateien in einem Durchlauf
- Beispiel: Ein Sonnet-Subagent erstellt alle fehlenden Agent-Module (style_guide.py, rewriter.py, structure_analyzer.py, usability_rules.py) zusammen

### Priorität 3: Modell-Routing (nur für Dateien die generiert werden müssen)

#### → Opus: Nur wenn ein Fehler teuer wäre
- Agenten-Prompts ÜBERARBEITEN (nicht extrahieren, die extrahierten sind schon gut)
- Conrads adversariale Strategien erweitern
- Lenas Anti-Halluzinations-Logik erweitern
- Security-Audit am Ende
- Debugging komplexer Fehler

#### → Sonnet: Standard-Generierung
- Die ~15 Dateien aus CODE_MAP.md Abschnitt "Was NICHT extrahiert werden kann"
- Tests schreiben
- Code-Reviews
- Bug-Fixes

#### → Haiku: Reine Struktur
- Ordnerstruktur anlegen
- Leere __init__.py Dateien
- .gitignore

### Priorität 4: Shared Schemas als Vertrag

- `shared/schemas.py` definiert ALLE Datentypen (Claim, VeraOutput, ConradOutput etc.)
- Jeder Subagent bekommt die für ihn relevanten Schemas als Kontext
- Das verhindert Inkompatibilitäten zwischen Modulen (unterschiedliche Feldnamen etc.)
- Spezifikation: `shared_schemas_spec.py` (wird in Phase 0 nach shared/schemas.py kopiert)

### Priorität 5: Zentrale Testdaten

- `tests/fixtures.json` enthält Beispiel-Claims, Vera-Ergebnisse, Conrad-Ergebnisse etc.
- Jeder Test importiert von dort. Kein Subagent erfindet eigene Testdaten.
- Spezifikation: `test_fixtures_spec.json`

### Priorität 6: Kontext minimieren

- Arbeitsanweisung NIEMALS komplett laden. Immer offset/limit mit max. 200 Zeilen.
- Subagenten bekommen NUR den für sie relevanten Kontext, nie die ganze Datei.
- CLAUDE.md bleibt unter 200 Zeilen (wird automatisch gecacht).

### Zusammenfassung der Methoden pro Datei

| Methode | Anzahl Dateien | Tokens-Kosten | Modell |
|---|---|---|---|
| Extraktion aus Arbeitsanweisung | ~35 | Minimal (nur Read+Write) | Keins (direkt) |
| Batch-Generierung (ähnliche Dateien) | ~12 | Niedrig (2-3 Sonnet-Aufrufe) | Sonnet |
| Einzelgenerierung (komplex) | ~3 | Mittel | Opus |
| Boilerplate | ~15 | Minimal | Haiku |

---

## Session-Startverhalten (WICHTIG)

**Bei JEDEM Gesprächsbeginn diese Schritte ausführen:**

1. Lies `PROGRESS.md` (den Build-Fortschritt)
2. Finde die erste nicht abgehakte Aufgabe (`- [ ]`)
3. Melde dich beim Nutzer mit GENAU diesem Format:

```
Phase X: [Phasenname]
Erledigt: Y von Z Aufgaben
Nächste Aufgaben: [Liste der nächsten 2-3 offenen Aufgaben]
Modelle: [welche Modelle für diese Aufgaben verwendet werden]

Soll ich weitermachen?
```

4. Wenn der Nutzer "ja", "weiter", "los", "mach" oder ähnliches sagt: Sofort starten.
5. Nach jeder erledigten Aufgabe: `PROGRESS.md` aktualisieren (`- [ ]` → `- [x]`)
6. Nach jeder Phase: Kurze Zusammenfassung, dann nächste Phase vorschlagen.

**Der Nutzer muss NICHTS über Phasen wissen. Er sagt nur "weiter" oder "stopp".**

## Fortschrittsdatei

→ `PROGRESS.md` (alle Aufgaben als Checkliste, wird automatisch aktualisiert)
