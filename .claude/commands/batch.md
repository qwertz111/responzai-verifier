# Batch-Build: Mehrere Aufgaben parallel auf verschiedene Modelle verteilen

Der Nutzer gibt eine Phase oder eine Liste von Aufgaben.
Du zerlegst sie in unabhängige Teilaufgaben und startest Subagenten PARALLEL.

## Ablauf

1. Zerlege die Aufgabe in unabhängige Teilaufgaben
2. Klassifiziere jede Teilaufgabe (Opus / Sonnet / Haiku)
3. Starte alle unabhängigen Subagenten GLEICHZEITIG in einem einzigen Tool-Call-Block
4. Warte auf alle Ergebnisse
5. Prüfe und integriere

## Beispiel: "Baue Stunde 1"

Wird zerlegt in diese parallelen Subagenten:

- Haiku: "Erstelle die komplette Ordnerstruktur für responzai-verifier mit allen Unterordnern"
- Haiku: "Erstelle alle __init__.py Dateien in responzai-verifier"
- Haiku: "Erstelle Dockerfile, docker-compose.yml, .env.example, .gitignore, requirements.txt"
- Sonnet: "Erstelle database/schema.sql mit den 4 Tabellen: sources, chunks, claims, reports (pgvector)"
- Sonnet: "Erstelle database/connection.py (asyncpg) und database/models.py (Pydantic)"
- Sonnet: "Erstelle api/main.py (FastAPI mit CORS) und leere Route-Dateien"

Alle 6 Subagenten starten parallel. Haiku-Aufgaben sind in Sekunden fertig.
Sonnet-Aufgaben brauchen etwas länger. Opus wird hier nicht gebraucht.

## Beispiel: "Baue Stunde 3"

Wird zerlegt in:

- Opus: "Schreibe den System-Prompt für Simon (SCOUT) in agents/simon_scout/prompt.py"
- Opus: "Schreibe den System-Prompt für Vera (VERIFY) in agents/vera_verify/prompt.py"
- Sonnet: "Erstelle agents/simon_scout/crawler.py (BeautifulSoup, requests)"
- Sonnet: "Erstelle agents/simon_scout/parser.py (Claude API Aufruf, JSON-Parsing)"
- Sonnet: "Erstelle agents/vera_verify/rag_query.py (pgvector Similarity-Search)"
- Sonnet: "Erstelle agents/vera_verify/scoring.py (Claude API Aufruf)"

Die Opus-Prompts und Sonnet-Implementierungen starten parallel.

## Wichtige Regeln

- Gib jedem Subagenten den VOLLSTÄNDIGEN Dateipfad
- Gib jedem Subagenten die Schnittstellenbeschreibung (Eingabe/Ausgabe)
- Referenziere NICHT die Arbeitsanweisung, sondern extrahiere den relevanten Kontext
- Starte maximal 6 Subagenten gleichzeitig (mehr bringt keinen Vorteil)
- Wenn Aufgaben voneinander abhängen (z.B. Prompt muss fertig sein bevor der Code den Prompt importiert), starte sie SEQUENTIELL
