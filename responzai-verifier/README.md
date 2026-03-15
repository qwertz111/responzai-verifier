# responzai-verifier

Kern-Backend des responzai-Systems: 8 KI-Agenten zur automatisierten Prüfung und Verbesserung von Texten zu EU AI Act, KI-Governance und KI-Kompetenz.

**English:** Core backend for the responzai system: 8 AI agents for automated verification and improvement of texts on EU AI Act, AI governance, and AI literacy.

## Überblick (Overview)

Das Verifier-Backend orchestriert eine Pipeline aus 8 spezialisierten Agenten:

- **Simon (SCOUT)** - Zerlegung von Texten in prüfbare Claims
- **Vera (VERIFY)** - Fact-Checking gegen die Knowledge Base (RAG)
- **Conrad (CONTRA)** - Adversariale Gegenprüfung
- **Sven (SYNC)** - Konsistenzprüfung über alle Kanäle
- **Pia (PULSE)** - Aktualitätsprüfung (EUR-Lex, RSS)
- **Lena (LEGAL)** - Rechtliche Textaktualisierung mit Anti-Halluzination
- **Davina (DRAFT)** - Sprachliche Optimierung nach Stilguide
- **Uma (UX)** - Bedienungsfreundlichkeit und Nutzererfahrung

Stack: **Python 3.10+**, FastAPI, LangGraph, PostgreSQL+pgvector, Claude API, Voyage-3, Docker.

## Installation

### Anforderungen (Requirements)

- Python 3.10 oder höher
- PostgreSQL 14+ (mit pgvector Extension)
- Docker & Docker Compose (für Container-Setup)
- API Keys: Anthropic, Voyage, Cloudflare (optional)

### Lokal

```bash
# Repository klonen
git clone https://github.com/responzai-eu/responzai-verifier.git
cd responzai-verifier

# Virtuelle Umgebung erstellen
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Dependencies installieren
pip install -r requirements.txt

# Umgebungsvariablen konfigurieren
cp .env.example .env
# Bearbeite .env mit deinen API Keys (siehe docs/SECRETS.md)

# Datenbank initialisieren
python -m alembic upgrade head

# Development-Server starten
uvicorn responzai.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker

```bash
# Alle Services mit Docker Compose starten
docker-compose up -d

# Datenbank-Migrations ausführen
docker-compose exec api python -m alembic upgrade head

# API läuft unter http://localhost:8000
# Swagger-Docs: http://localhost:8000/docs
```

## Architektur

### Verzeichnisstruktur

```
responzai-verifier/
├── responzai/
│   ├── agents/              # 8 Agent-Module
│   │   ├── scout.py         # Simon (SCOUT)
│   │   ├── verify.py        # Vera (VERIFY)
│   │   ├── contra.py        # Conrad (CONTRA)
│   │   ├── sync.py          # Sven (SYNC)
│   │   ├── pulse.py         # Pia (PULSE)
│   │   ├── legal.py         # Lena (LEGAL)
│   │   ├── draft.py         # Davina (DRAFT)
│   │   └── ux.py            # Uma (UX)
│   ├── core/                # Kernfunktionalität
│   │   ├── pipeline.py      # 8-Agenten-Pipeline
│   │   ├── schemas.py       # Datenstrukturen
│   │   └── config.py        # Konfiguration
│   ├── api/
│   │   ├── routes/          # API-Endpunkte
│   │   └── main.py          # FastAPI App
│   ├── db/                  # Datenbank
│   │   ├── models.py        # SQLAlchemy Models
│   │   └── alembic/         # Migrations
│   └── main.py              # Entry Point
├── tests/
│   ├── test_agents.py
│   ├── test_api.py
│   ├── test_pipeline.py
│   └── fixtures.json        # Test-Daten
├── docs/
│   ├── SECRETS.md           # Secrets-Dokumentation
│   └── API.md               # API-Spezifikation
├── .env.example
├── requirements.txt
├── docker-compose.yml
└── README.md
```

### Pipeline-Fluss

```
Eingabe (URL/Text/Datei)
    ↓
Simon (SCOUT)   → Claims extrahieren
    ↓
Vera (VERIFY)   → RAG-Fact-Checking (Score >= 0.8 → weiter)
    ↓
Conrad (CONTRA) → Adversariale Prüfung (survived/weakened → weiter)
    ↓
Sven (SYNC)     → Konsistenz über Kanäle
    ↓
Pia (PULSE)     → Aktualität prüfen (EUR-Lex, RSS)
    ↓
Lena (LEGAL)    → Rechtliche Updates (temp=0, Rückprüfung)
    ↓
Davina (DRAFT)   → Stil & Lesbarkeit
    ↓
Uma (UX)        → Bedienungsfreundlichkeit
    ↓
Pruefbericht (mit Empfehlung: approved/approved_with_changes/rejected)
```

### Schwellenwerte (Thresholds)

- Vera: Score >= 0.8 weiterleiten, sonst warnen
- Conrad: Survived/Weakened Claims weitergeben, Refuted ausschließen
- Lena: Coverage >= 0.95, temperature=0, Rückprüfung durch Vera+Conrad
- Alle Agenten: temperature=0 (deterministisch)

## API-Endpunkte (Endpoints)

### Prüfung starten

```
POST /verify
Content-Type: application/json

{
  "text": "string (erforderlich)",
  "source": "string (optional: newsletter/blog/article)",
  "metadata": {
    "title": "string",
    "author": "string",
    "cms": "string (wordpress/ghost/strapi)"
  }
}

Response 202 (Accepted):
{
  "task_id": "uuid",
  "status": "pending",
  "created_at": "2025-03-13T10:30:00Z"
}
```

### Entwurf prüfen (Publish-Ready Check)

```
POST /verify/draft
Content-Type: application/json

{
  "text": "string (erforderlich)",
  "source": "string (optional)",
  "metadata": {...}
}

Response 202 (Accepted):
{
  "task_id": "uuid",
  "status": "pending",
  "recommendation": "pending"  # approved / approved_with_changes / rejected
}
```

### Ergebnis abrufen

```
GET /verify/{task_id}

Response 200 (Ok):
{
  "task_id": "uuid",
  "status": "completed",
  "scout_output": {...},
  "verify_output": {...},
  "contra_output": {...},
  "sync_output": {...},
  "pulse_output": {...},
  "legal_output": {...},
  "draft_output": {...},
  "ux_output": {...},
  "overall_score": 0.85,
  "recommendation": "approved_with_changes",
  "completed_at": "2025-03-13T10:35:00Z"
}
```

### Health Check

```
GET /health

Response 200:
{
  "status": "healthy",
  "version": "0.1.0",
  "db_connected": true
}
```

## Testing

### Tests ausführen

```bash
# Alle Tests
pytest tests/ -v

# Nur Agenten-Tests
pytest tests/test_agents.py -v

# Mit Coverage-Report
pytest tests/ --cov=responzai --cov-report=html
```

### Test-Struktur

- `test_agents.py` - Unit-Tests für jeden Agenten
- `test_api.py` - Integration Tests für API-Endpunkte
- `test_pipeline.py` - End-to-End Pipeline-Tests
- `fixtures.json` - Beispiel-Claims und Test-Daten

## Deployment

### Production-Build

```bash
# Docker Image bauen
docker build -t responzai-verifier:latest .

# Zu Container Registry pushen
docker tag responzai-verifier:latest gcr.io/your-project/responzai-verifier:latest
docker push gcr.io/your-project/responzai-verifier:latest
```

### Kubernetes / Cloud Run

```bash
# Zu Cloud Run deployen (GCP)
gcloud run deploy responzai-verifier \
  --image gcr.io/your-project/responzai-verifier:latest \
  --platform managed \
  --region europe-west1 \
  --set-env-vars ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY
```

### Environment (Production)

- Database: Cloud SQL (PostgreSQL 14+)
- Cache: Redis (optional, für Task-Queue)
- Storage: Cloud Storage (für Document Upload)
- Monitoring: Cloud Logging + Sentry
- Secrets: Cloud Secret Manager

## Links zu anderen Repos

- [responzai-knowledge](https://github.com/responzai-eu/responzai-knowledge) - Knowledge Base & Document Ingestion
- [responzai-web](https://github.com/responzai-eu/responzai-web) - Frontend (React/TypeScript)

## Lizenz

MIT License. Siehe LICENSE für Details.

## Support

- Issues: https://github.com/responzai-eu/responzai-verifier/issues
- Docs: /api/docs (Swagger UI)
- Email: support@responzai.eu
