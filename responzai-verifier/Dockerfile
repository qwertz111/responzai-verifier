# Basis-Image: Python 3.11 (schlank)
FROM python:3.11-slim

# Tesseract OCR und deutsche Sprachdaten installieren
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-deu \
    && rm -rf /var/lib/apt/lists/*

# Arbeitsverzeichnis im Container
WORKDIR /app

# Abhängigkeiten zuerst kopieren (für Cache-Optimierung)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Quellcode kopieren
COPY . .

# Upload-Verzeichnis erstellen
RUN mkdir -p /app/data/uploads

# Port freigeben
EXPOSE 8000

# Anwendung starten
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
