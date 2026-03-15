# pipeline/config.py

import os

# Schwellenwerte für die Pipeline
VERIFICATION_THRESHOLD = 0.8   # Mindest-Score für Vera
ADVERSARIAL_PASS = ["survived", "weakened"]  # Conrad: welche Ergebnisse ok sind
CONSISTENCY_THRESHOLD = 0.7    # Mindest-Score für Sven
FRESHNESS_MAX_DAYS = 90        # Pia: ab wann eine Quelle "stale" ist
LEGAL_COVERAGE_MIN = 0.95      # Lena: Mindest-Quellenabdeckung

# Modell-Konfiguration (steuerbar per Umgebungsvariable)
# Produktion: claude-sonnet-4-20250514 (Standard)
# Test:       claude-haiku-4-5-20251001 (~60x guenstiger)
# .env: LLM_MODEL=claude-haiku-4-5-20251001
LLM_MODEL = os.environ.get("LLM_MODEL", "claude-sonnet-4-20250514")
LLM_MODEL_STRONG = os.environ.get("LLM_MODEL_STRONG", "claude-opus-4-5")
LLM_TEMPERATURE = 0            # Keine Kreativität bei Prüfungen
EMBEDDING_MODEL = "voyage-3"
