# Code-Extraktion aus der Arbeitsanweisung

Diese Datei mappt Code-Blöcke aus `responzai_arbeitsanweisung_claude_code_2.md`
auf ihre Zieldateien. Statt Code neu zu generieren, wird er direkt extrahiert.

## Extraktion statt Generation

Lies den angegebenen Zeilenbereich aus der Arbeitsanweisung und schreibe
den Inhalt des Code-Blocks in die Zieldatei. Das spart ~90% der Tokens
gegenüber Neugeneration.

## Mapping (Zeilen sind Richtwerte, Code-Block-Grenzen suchen)

### Phase 1: Fundament
| Zieldatei | Quelle (ca. Zeile) | Modell | Anmerkung |
|---|---|---|---|
| database/schema.sql | ~838-909 | Extraktion | 4 Tabellen + pgvector |
| docker-compose.yml | ~545-614 | Extraktion | 3 Services |
| Dockerfile | ~3104-3123 | Extraktion | Basis-Image, aber ERSETZEN durch erweiterte Version mit Tesseract (~Zeile 1878) |
| requirements.txt | ~3070-3100 | Extraktion | Basis-Pakete, ERGÄNZEN um Document-Ingestion-Pakete (~Zeile 1912) |
| .env.example | ~3037-3066 | Extraktion | |

### Phase 2: Wissensbasis + Document Ingestion
| Zieldatei | Quelle (ca. Zeile) | Modell | Anmerkung |
|---|---|---|---|
| processing/embedding.py | ~955-1000 | Extraktion | |
| processing/chunking.py | ~1034-1068 | Extraktion | |
| database/seed.py | ~1072-1113 | Extraktion | |
| document_ingestion/router.py | ~1165-1308 | Extraktion | |
| document_ingestion/parsers/pdf_parser.py | ~1312-1432 | Extraktion | |
| document_ingestion/parsers/docx_parser.py | ~1436-1505 | Extraktion | |
| document_ingestion/parsers/xlsx_parser.py | ~1509-1560 | Extraktion | |
| document_ingestion/parsers/pptx_parser.py | ~1564-1597 | Extraktion | |
| document_ingestion/parsers/image_parser.py | ~1600-1638 | Extraktion | |
| document_ingestion/preprocessor.py | ~1601-1639 | Extraktion | |
| document_ingestion/metadata_extractor.py | ~1643-1700 | Extraktion | |
| document_ingestion/storage.py | ~1704-1772 | Extraktion | |
| api/routes/upload.py | ~1776-1862 | Extraktion | |

### Phase 3: Simon + Vera
| Zieldatei | Quelle (ca. Zeile) | Modell | Anmerkung |
|---|---|---|---|
| agents/simon_scout/prompt.py | ~1953-1999 | Extraktion | |
| agents/simon_scout/crawler.py | ~2005-2040 | Extraktion | |
| agents/simon_scout/parser.py | ~2044-2092 | Extraktion | |
| agents/vera_verify/prompt.py | ~2100-2138 | Extraktion | |
| agents/vera_verify/rag_query.py | ~2143-2187 | Extraktion | |
| agents/vera_verify/scoring.py | ~2191-2248 | Extraktion | |

### Phase 4: Conrad + Sven + Pia + Pipeline
| Zieldatei | Quelle (ca. Zeile) | Modell | Anmerkung |
|---|---|---|---|
| agents/conrad_contra/prompt.py | ~2257-2304 | Extraktion | |
| agents/conrad_contra/strategies.py | ~2308-2351 | Extraktion | |
| agents/conrad_contra/evaluation.py | ~2355-2416 | Extraktion | |
| agents/sven_sync/prompt.py | ~2424-2472 | Extraktion | |
| agents/sven_sync/consistency.py | ~2477-2516 | Extraktion | |
| agents/pia_pulse/prompt.py | ~2525-2558 | Extraktion | |
| agents/pia_pulse/monitors.py | ~2562-2612 | Extraktion | |
| pipeline/orchestrator.py | ~2900-3145 | Extraktion | |
| pipeline/config.py | ~3150-3163 | Extraktion | |

### Phase 5: Verbesserungsteam + Frontend
| Zieldatei | Quelle (ca. Zeile) | Modell | Anmerkung |
|---|---|---|---|
| agents/lena_legal/prompt.py | ~2625-2668 | Extraktion | |
| agents/lena_legal/verification_loop.py | ~2672-2778 | Extraktion | |
| agents/david_draft/prompt.py | ~2785-2830 | Extraktion | |
| agents/uma_ux/prompt.py | ~2838-2888 | Extraktion | |
| src/components/VerificationBadge.jsx | ~3632-3682 | Extraktion | |
| src/components/DocumentUpload.jsx | ~3700-3900 | Extraktion | |
| src/components/VerificationDashboard.jsx | ~3905-4020 | Extraktion | |
| src/components/ReportViewer.jsx | ~4025-4110 | Extraktion | |
| src/pages/verify.jsx | ~3690-3760 | Extraktion | |

## Was NICHT extrahiert werden kann (muss generiert werden)

Diese Dateien existieren nicht in der Arbeitsanweisung und müssen generiert werden:

| Zieldatei | Modell | Warum |
|---|---|---|
| agents/sven_sync/contradiction_map.py | Sonnet | Nur erwähnt, nicht ausgeschrieben |
| agents/pia_pulse/freshness.py | Sonnet | Nur erwähnt, nicht ausgeschrieben |
| agents/lena_legal/source_mapper.py | Sonnet | Nur erwähnt, nicht ausgeschrieben |
| agents/lena_legal/text_generator.py | Sonnet | Nur erwähnt, nicht ausgeschrieben |
| agents/david_draft/style_guide.py | Sonnet | Nur erwähnt, nicht ausgeschrieben |
| agents/david_draft/rewriter.py | Sonnet | Nur erwähnt, nicht ausgeschrieben |
| agents/uma_ux/structure_analyzer.py | Sonnet | Nur erwähnt, nicht ausgeschrieben |
| agents/uma_ux/usability_rules.py | Sonnet | Nur erwähnt, nicht ausgeschrieben |
| database/connection.py | Sonnet | Nur erwähnt, nicht ausgeschrieben |
| database/models.py | Sonnet | Nur erwähnt, nicht ausgeschrieben |
| pipeline/reporting.py | Sonnet | Nur erwähnt, nicht ausgeschrieben |
| api/main.py (vollständig) | Sonnet | Teilweise vorhanden, muss ergänzt werden |
| document_ingestion/parsers/odt_parser.py | Sonnet | Nicht ausgeschrieben |
| document_ingestion/parsers/email_parser.py | Sonnet | Nicht ausgeschrieben |
| Alle Tests | Sonnet | Nicht in der Arbeitsanweisung |
