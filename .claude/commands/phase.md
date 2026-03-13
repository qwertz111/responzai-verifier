# Phase ausführen

Der Nutzer gibt eine Phase an (z.B. "Stunde 1", "Phase 2", oder "S3").
Führe die entsprechende Phase aus dem 5-Stunden-Plan aus.

## Phase 1 / Stunde 1: Fundament

Ziel: Repos, Ordnerstruktur, Boilerplate, DB-Schema, FastAPI-Grundgerüst.

Parallel starten:
- [Haiku] Ordnerstruktur responzai-verifier (alle Ordner laut CLAUDE.md)
- [Haiku] Ordnerstruktur responzai-knowledge
- [Haiku] Alle __init__.py, Dockerfile, docker-compose.yml, .env.example, requirements.txt, .gitignore
- [Sonnet] database/schema.sql (sources, chunks, claims, reports + pgvector)
- [Sonnet] database/connection.py + database/models.py
- [Sonnet] api/main.py + leere Route-Dateien (verify.py, upload.py, improve.py, reports.py)

## Phase 2 / Stunde 2: Wissensbasis + Document Ingestion

Ziel: Dokumente einlesen, chunken, embedden, speichern.

Parallel starten:
- [Sonnet] processing/chunking.py (chunk_legal_text, max 500 Wörter, Absatzgrenzen)
- [Sonnet] processing/embedding.py (Voyage-3, create_embeddings, create_query_embedding)
- [Sonnet] processing/metadata.py (Metadaten aus Chunks extrahieren)
- [Sonnet] document_ingestion/router.py (Format-Erkennung, MIME-Type + Extension)
- [Sonnet] document_ingestion/parsers/ (pdf, docx, xlsx, pptx, image, txt, html, markdown, email)
- [Sonnet] document_ingestion/preprocessor.py + storage.py + metadata_extractor.py
- [Sonnet] api/routes/upload.py (POST /verify/document)

## Phase 3 / Stunde 3: Simon + Vera

Ziel: Erste zwei Agenten funktionieren Ende-zu-Ende.

Sequentiell (Prompts zuerst, dann Code der sie importiert):
1. Parallel:
   - [Opus] agents/simon_scout/prompt.py
   - [Opus] agents/vera_verify/prompt.py
2. Dann parallel:
   - [Sonnet] agents/simon_scout/crawler.py + parser.py
   - [Sonnet] agents/vera_verify/rag_query.py + scoring.py

## Phase 4 / Stunde 4: Conrad + Sven + Pia + Pipeline

Ziel: Komplette Prüfpipeline.

Sequentiell:
1. [Opus] agents/conrad_contra/prompt.py (adversarialer Prompt, kritisch!)
2. Parallel:
   - [Sonnet] agents/conrad_contra/strategies.py + evaluation.py
   - [Sonnet] agents/sven_sync/prompt.py + consistency.py + contradiction_map.py
   - [Sonnet] agents/pia_pulse/prompt.py + monitors.py + freshness.py
3. [Sonnet] pipeline/orchestrator.py (LangGraph StateGraph, alle 8 Knoten)
4. [Sonnet] pipeline/config.py + pipeline/reporting.py

## Phase 5 / Stunde 5: Verbesserungsteam + Frontend

Ziel: MVP ist nutzbar.

Sequentiell:
1. [Opus] agents/lena_legal/prompt.py (Anti-Halluzinations-Regeln, kritisch!)
2. Parallel:
   - [Sonnet] agents/lena_legal/source_mapper.py + text_generator.py + verification_loop.py
   - [Sonnet] agents/david_draft/prompt.py + style_guide.py + rewriter.py
   - [Sonnet] agents/uma_ux/prompt.py + structure_analyzer.py + usability_rules.py
3. Parallel:
   - [Sonnet] src/components/DocumentUpload.jsx
   - [Sonnet] src/components/VerificationDashboard.jsx + ReportViewer.jsx
   - [Sonnet] src/pages/verify.jsx
