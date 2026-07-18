FROM python:3.11-slim

# ── System-Abhängigkeiten ─────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Multimedia
    ffmpeg \
    fluidsynth \
    # Grafik
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    libcairo2-dev \
    ghostscript \
    # Pandoc (Markup-Konvertierungen)
    pandoc \
    # Archive
    unrar-free \
    p7zip-full \
    # OCR
    tesseract-ocr \
    tesseract-ocr-deu \
    tesseract-ocr-eng \
    # Allgemein
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ── Blender: neueste stabile Version (immer aktuell, damit .blend-Dateien gelesen werden) ──
# Extra-Libs die Blender headless braucht
RUN apt-get update && apt-get install -y --no-install-recommends \
    libxrender1 libxi6 libxxf86vm1 libxfixes3 xz-utils \
    && rm -rf /var/lib/apt/lists/*
COPY fetch_blender.sh /tmp/fetch_blender.sh
RUN sh /tmp/fetch_blender.sh && rm /tmp/fetch_blender.sh

WORKDIR /app

# ── Python-Abhängigkeiten ─────────────────────────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Anwendungscode ────────────────────────────────────────────────────────────
COPY . .

EXPOSE 8000

# Max. Dateigröße in MB
ENV MAX_FILE_MB=500

# PORT wird von Render/Railway automatisch gesetzt; Fallback 8000 für lokal
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers ${WEB_CONCURRENCY:-1}"]
