# Das Verifier-Team — Architektur und Funktionsweise

## Was ist das Verifier-Team?

Das Verifier-Team ist eine Komponente von responzai: ein automatisches Prüf- und Verbesserungssystem für Texte rund um EU AI Act, KI-Governance und KI-Kompetenz. Es kombiniert 8 spezialisierte KI-Agenten, eine rechtliche Wissensbasis und eine Automatisierungspipeline zu einem vollständigen Qualitätssicherungssystem für Content-Teams.

**Kernaufgabe:** Sicherstellen, dass kein Artikel, kein Newsletter, kein Blog-Post online geht, der falsche oder veraltete Aussagen zum EU AI Act enthält.

---

## Von der Eingabe zum Bericht

```
Eingabe (Text / URL / Datei)
        │
        ▼
┌───────────────┐
│ Simon (SCOUT) │  → Zerlegt Text in prüfbare Claims
└───────┬───────┘
        ▼
┌───────────────┐
│ Vera (VERIFY) │  → Prüft Claims gegen Wissensbasis (RAG)
└───────┬───────┘    Score < 0.8 → ausgesiebt
        ▼
┌────────────────┐
│ Conrad (CONTRA)│  → Adversariale Gegenprüfung
└───────┬────────┘    "refuted" → ausgesiebt
        ▼
┌──────────────┐
│  Sven (SYNC) │  → Konsistenzprüfung (intern + kanalübergreifend)
└───────┬──────┘
        ▼
┌──────────────┐
│  Pia (PULSE) │  → Aktualitätsprüfung (EUR-Lex, RSS-Feeds)
└───────┬──────┘
        ▼
┌──────────────┐
│  Lena (LEGAL)│  → Rechtliche Textkorrektur (Anti-Halluzination)
└───────┬──────┘
        ▼
┌───────────────┐
│ Davina (DRAFT)│  → Sprachliche Optimierung (Stilguide)
└───────┬───────┘
        ▼
┌─────────────┐
│  Uma (UX)   │  → Struktur- und Lesbarkeitsprüfung
└───────┬─────┘
        ▼
   Bericht + Badge
```

---

## Die 8 Agenten im Detail

### 1. Simon (SCOUT) — Zerteiler

Simon liest den eingehenden Text und zerlegt ihn in einzelne, isoliert prüfbare Behauptungen — sogenannte **Claims**.

**Was er tut:**
- Identifiziert jede faktische Aussage im Text
- Klassifiziert sie in vier Kategorien:
  - `LEGAL_CLAIM` — Aussage über Gesetze, Paragraphen, Fristen
  - `PRODUCT_CLAIM` — Aussage über KI-Produkte oder -Systeme
  - `MARKET_CLAIM` — Aussage über den KI-Markt
  - `TARGET_GROUP_CLAIM` — Aussage über betroffene Zielgruppen
- Verknüpft jeden Claim mit seinem Originaltext (für spätere Korrekturen)

**Output:** Strukturierte Liste von Claims mit Kategorie, Originaltext und Position im Dokument.

---

### 2. Vera (VERIFY) — Prüferin

Vera ist das Herzstück des Teams. Sie prüft jeden Claim gegen die interne Wissensbasis per **RAG** (siehe technische Sektion).

**Was sie tut:**
- Sucht in der Wissensbasis nach den relevantesten Textstellen zum Claim
- Vergleicht die Aussage im Claim mit dem, was die Quellen sagen
- Vergibt einen Score von 0.0 bis 1.0 (Übereinstimmungsgrad)
- Gibt die verwendeten Quellen mit Fundstelle zurück

**Schwellenwert:** Score ≥ 0.8 → weiter zu Conrad. Darunter → Claim wird als "nicht verifiziert" markiert.

---

### 3. Conrad (CONTRA) — Advocatus Diaboli

Conrad denkt wie ein Gegenanwalt: Er sucht nicht nach Bestätigung, sondern gezielt nach Widerlegung.

**Was er tut:**
- Generiert für jeden Claim Gegenargumente, Ausnahmen und Einschränkungen
- Bewertet jeden Claim mit einem von drei Status:
  - `survived` — Claim hält der Gegenprüfung stand
  - `weakened` — Claim ist vereinfacht, aber nicht falsch (bekommt Einschränkungs-Hinweis)
  - `refuted` — Claim ist nachweislich falsch → wird aus dem Bericht entfernt
- Verhindert, dass halbrichtige Vereinfachungen als "verifiziert" durchkommen

---

### 4. Sven (SYNC) — Konsistenzwächter

Sven schaut nicht auf einzelne Claims, sondern auf das **Zusammenspiel**.

**Was er tut:**
- Prüft ob Claims im selben Text sich widersprechen
- Prüft ob aktuelle Aussagen im Widerspruch zu früheren Artikeln auf der Website stehen
- Erstellt eine "Contradiction Map" — eine Übersicht aller Widersprüche
- Besonders wichtig für Organisationen, die über längere Zeiträume zum Thema publizieren

---

### 5. Pia (PULSE) — Aktualitätswächter

Pia verbindet das Team mit der Außenwelt: Sie prüft ob Informationen noch aktuell sind.

**Was sie tut:**
- Ruft regelmäßig **EUR-Lex** ab (offizielles EU-Rechtsportal) — neue Verordnungen, Änderungen, Durchführungsakte
- Überwacht **RSS-Feeds** relevanter Quellen (Kommission, ENISA, nationale Behörden)
- Vergleicht Datum der Quelle mit dem Datum der Aussage im Text
- Markiert veraltete Claims mit einer "Freshness"-Warnung

---

### 6. Lena (LEGAL) — Textaktualisiererin

Lena schreibt. Aber mit einem strengen Anti-Halluzinations-Prinzip.

**Was sie tut:**
- Nimmt jeden fehlerhaften oder veralteten Claim
- Formuliert einen korrekten Ersatztext — **ausschließlich** auf Basis der Wissensbasis, nie aus dem Trainings-Gedächtnis des Modells
- Schickt jeden neu geschriebenen Satz zur Rückprüfung an Vera und Conrad
- Nur wenn Vera Score ≥ 0.95 vergibt UND Conrad nicht widerlegt, wird der Text übernommen
- Verwendet temperature=0 (kein Zufall, maximale Reproduzierbarkeit)

**Warum so streng?** Rechtliche Texte dulden keine Approximationen. Lena schreibt lieber gar nichts als etwas Falsches.

---

### 7. Davina (DRAFT) — Stiloptimiererin

Davina verbessert was sprachlich verbesserungswürdig ist — ohne den Inhalt zu verändern.

**Was sie tut:**
- Wendet einen definierten Stilguide an (verständlich, zielgruppengerecht, kein Juristendeutsch)
- Vereinfacht komplexe Satzkonstruktionen
- Sorgt für einheitliche Terminologie im Text
- Ändert **nie** den faktischen Inhalt — nur die Formulierung

---

### 8. Uma (UX) — Strukturanalystin

Uma hat den Leser im Blick, nicht die Fakten.

**Was sie tut:**
- Prüft logischen Aufbau und Lesefluss
- Bewertet ob Überschriften den Inhalt korrekt beschreiben
- Prüft ob der Text für die Zielgruppe verständlich ist
- Gibt konkrete Verbesserungsvorschläge für Struktur und Darstellung (keine Umschreibung, nur Empfehlungen)

---

## Wie die Agenten kommunizieren

Die Agenten sind **entkoppelt** — sie kennen sich nicht gegenseitig. Die Kommunikation läuft ausschließlich über strukturierte Datenobjekte (Python Pydantic-Modelle in `shared/schemas.py`).

```python
# Beispiel: Was Vera zurückgibt
VeraOutput(
    claim_id="c-001",
    score=0.92,
    verdict="verified",
    sources=["EU AI Act Art. 6 Abs. 1", "Erwägungsgrund 51"],
    supporting_text="Hochrisiko-KI-Systeme müssen..."
)
```

Der **Orchestrator** (`pipeline/orchestrator.py`) ist der einzige, der alle Agenten kennt. Er:
- Startet die Agenten in der richtigen Reihenfolge
- Wendet Schwellenwerte an (welche Claims weiterlaufen)
- Sammelt alle Outputs ein
- Fasst alles zum finalen Bericht zusammen

---

## Technische Komponenten

### RAG — Retrieval-Augmented Generation

RAG ist die Methode, mit der Vera und Lena auf die Wissensbasis zugreifen, anstatt das Trainings-Wissen des KI-Modells zu nutzen.

**Wie es funktioniert:**

```
1. Aufbau der Wissensbasis (einmalig):
   EU AI Act PDFs → Text-Chunks (je ~500 Wörter)
                  → Embedding (Voyage-3 Modell)
                  → Speicherung in PostgreSQL + pgvector

2. Zur Laufzeit (bei jeder Prüfung):
   Claim-Text → Embedding
              → Vektordatenbank-Suche (Cosine Similarity)
              → Top-5 relevanteste Textstellen zurück
              → Claude bekommt: Claim + Quellen → Bewertung
```

**Warum das besser ist als einfach Claude zu fragen:**
- Claude kennt den EU AI Act aus dem Training — aber nicht die aktuelle Version von gestern
- RAG gibt Claude die exakten, aktuellen Quellen direkt in den Prompt
- Lena kann so auf einzelne Paragraphen verweisen statt aus dem Gedächtnis zu schreiben

**Technischer Stack:**
- **Voyage-3** (Anthropic) als Embedding-Modell — erzeugt numerische Vektoren aus Text
- **PostgreSQL + pgvector** als Vektordatenbank — speichert Vektoren und macht Ähnlichkeitssuche
- **Claude API** (claude-opus-4-6 / claude-sonnet-4-6) für die eigentliche Analyse

---

### n8n — Automatisierungsplattform

n8n ist ein Open-Source Workflow-Automatisierungstool (ähnlich Zapier, aber selbst gehostet). Es läuft auf demselben Server wie das Verifier-Team und steuert alle automatischen Abläufe.

**Workflow 1 — Wöchentlicher Prüflauf:**
```
Zeitplan (jeden Montag 06:00)
  → Liste aller zu prüfenden URLs aus der Datenbank laden
  → Für jede URL: POST /verify an die API
  → Ergebnisse in Datenbank speichern
  → Bei Score < 0.8: E-Mail-Benachrichtigung an Redaktion
```

**Workflow 2 — EUR-Lex Monitoring (für Pia):**
```
Zeitplan (täglich)
  → EUR-Lex RSS-Feed abrufen
  → Neue Dokumente identifizieren
  → In Wissensbasis einpflegen (Embedding + Speicherung)
  → Pia informieren: "Neue Quelle verfügbar"
```

**Workflow 3 — Newsletter-Prüfung:**
```
Trigger: Eingehende E-Mail (Newsletter-Entwurf)
  → Text extrahieren
  → POST /verify an die API
  → Bericht als E-Mail zurückschicken
```

**Workflow 4 — Pre-Publication Check (CMS-Webhook):**
```
Trigger: Webhook vom CMS (wenn Artikel auf "Zur Prüfung" gesetzt wird)
  → POST /verify/draft an die API
  → Score ≥ 0.8: CMS-Status → "Freigegeben"
  → Score < 0.8: CMS-Status → "Überarbeitung nötig" + Bericht anhängen
```

**Warum n8n statt eigener Cronjobs?**
- Visuelle Workflows — keine Code-Kenntnisse nötig für Anpassungen
- Eingebautes Retry-Handling bei Fehlern
- Logging aller Workflow-Läufe
- Einfache Integration mit E-Mail, Webhooks, APIs

---

### FastAPI — Die API-Schicht

FastAPI ist das Python-Framework, das das Verifier-Team als HTTP-API nach außen verfügbar macht.

**Wichtige Endpunkte:**

| Endpunkt | Methode | Funktion |
|----------|---------|----------|
| `/verify` | POST | Vollständige Prüfung (Text/URL/Datei) |
| `/verify/draft` | POST | Pre-Publication Check (schneller, ohne Pia+Sven) |
| `/upload` | POST | Dokument hochladen und in Wissensbasis einpflegen |
| `/reports/{id}` | GET | Gespeicherten Bericht abrufen |
| `/improve` | POST | Verbesserungsvorschläge für einen Text |

---

### Docker — Deployment

Alle Komponenten laufen in Docker-Containern auf dem Hetzner-Server:

```
┌─────────────────────────────────────────┐
│           Hetzner CX33 Server           │
│                                         │
│  ┌─────────┐  ┌──────────┐  ┌───────┐  │
│  │ FastAPI  │  │PostgreSQL│  │  n8n  │  │
│  │ (Port   │  │+ pgvector│  │(Port  │  │
│  │  8000)  │  │(Port5432)│  │ 5678) │  │
│  └────┬────┘  └──────────┘  └───────┘  │
│       │                                 │
│  ┌────┴──────────────────────────────┐  │
│  │     Nginx (Port 80/443)           │  │
│  │     → api.responzai.eu            │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

---

## Das Ergebnis: Der Verifikationsbericht

```json
{
  "score": 87,
  "verdict": "partially_verified",
  "badge": "Teilweise verifiziert",
  "claims_total": 12,
  "claims_verified": 8,
  "claims_weakened": 3,
  "claims_refuted": 1,
  "suggestions": [
    {
      "type": "correction",
      "original": "Der EU AI Act gilt ab sofort",
      "corrected": "Der EU AI Act tritt stufenweise in Kraft...",
      "source": "EU AI Act Art. 113"
    }
  ]
}
```

Dieser Bericht wird im Verify-Interface auf responzai.eu als visuelles Dashboard dargestellt — mit Badge, Scores pro Claim und direkt kopierbaren Korrekturvorschlägen.
