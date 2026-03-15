-- pgvector-Erweiterung aktivieren
CREATE EXTENSION IF NOT EXISTS vector;

-- Tabelle 1: Quellen
-- Speichert Informationen über jede Quelle
CREATE TABLE sources (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,                    -- z.B. "EU AI Act"
    source_type TEXT NOT NULL,              -- primary / secondary / own
    url TEXT,                               -- Wo die Quelle herkommt
    fetched_at TIMESTAMP DEFAULT NOW(),     -- Wann sie abgerufen wurde
    last_checked TIMESTAMP,                 -- Wann zuletzt geprüft
    hash TEXT,                              -- Digitaler Fingerabdruck
    metadata JSONB                          -- Zusätzliche Informationen
);

-- Tabelle 2: Chunks
-- Speichert die zerlegten Textstücke mit ihren Embeddings
CREATE TABLE chunks (
    id SERIAL PRIMARY KEY,
    source_id INTEGER REFERENCES sources(id),
    content TEXT NOT NULL,                  -- Der Textinhalt
    embedding vector(1024),                 -- Mathematische Darstellung
    chunk_index INTEGER,                    -- Position im Dokument
    metadata JSONB                          -- Kapitel, Artikel, etc.
);

-- Index für schnelle Ähnlichkeitssuche
CREATE INDEX ON chunks USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- Tabelle 3: Claims
-- Speichert die extrahierten Behauptungen
CREATE TABLE claims (
    id SERIAL PRIMARY KEY,
    source_url TEXT NOT NULL,               -- Wo die Behauptung steht
    claim_text TEXT NOT NULL,               -- Der Text der Behauptung
    category TEXT NOT NULL,                 -- LEGAL_CLAIM, etc.
    extracted_at TIMESTAMP DEFAULT NOW(),
    extracted_by TEXT DEFAULT 'simon',      -- Wer hat sie extrahiert

    -- Ergebnisse der Prüfung
    fact_check_score FLOAT,                -- Veras Score (0 bis 1)
    adversarial_result TEXT,               -- Conrads Ergebnis
    consistency_score FLOAT,               -- Svens Score
    freshness_status TEXT,                 -- Pias Status
    overall_confidence FLOAT,              -- Gesamtwert

    -- Verbesserungsvorschläge
    legal_suggestion TEXT,                 -- Lenas Vorschlag
    draft_suggestion TEXT,                 -- Davinas Vorschlag
    ux_suggestion TEXT,                    -- Umas Vorschlag

    action_required BOOLEAN DEFAULT FALSE,
    metadata JSONB
);

-- Tabelle 4: Prüfberichte
-- Speichert die fertigen Berichte
CREATE TABLE reports (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT NOW(),
    report_type TEXT NOT NULL,             -- verification / improvement
    source_url TEXT,
    total_claims INTEGER,
    verified_claims INTEGER,
    issues_found INTEGER,
    report_data JSONB,                     -- Der vollständige Bericht als JSON
    status TEXT DEFAULT 'completed'
);
