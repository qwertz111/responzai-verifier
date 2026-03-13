# pipeline/config.py

# Schwellenwerte für die Pipeline
VERIFICATION_THRESHOLD = 0.8   # Mindest-Score für Vera
ADVERSARIAL_PASS = ["survived", "weakened"]  # Conrad: welche Ergebnisse ok sind
CONSISTENCY_THRESHOLD = 0.7    # Mindest-Score für Sven
FRESHNESS_MAX_DAYS = 90        # Pia: ab wann eine Quelle "stale" ist
LEGAL_COVERAGE_MIN = 0.95      # Lena: Mindest-Quellenabdeckung

# Modell-Konfiguration
LLM_MODEL = "claude-sonnet-4-20250514"
LLM_TEMPERATURE = 0            # Keine Kreativität bei Prüfungen
EMBEDDING_MODEL = "voyage-3"
