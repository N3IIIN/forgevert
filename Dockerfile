FROM python:3.11-slim

# ── System-Abhängigkeiten ─────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Multimedia
    ffmpeg \
    fluidsynth \
    fluid-soundfont-gm \
    # Grafik
    libgl1-mesa-glx \
    libglib2.0-0 \
    libgomp1 \
    libcairo2-dev \
    inkscape \
    ghostscript \
    # LibreOffice (Office → PDF/DOCX/ODP)
    libreoffice-writer \
    libreoffice-calc \
    libreoffice-impress \
    python3-uno \
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

# ── Blender (FBX / BLEND → GLB — auskommentieren spart ~500MB) ───────────────
# RUN apt-get update && apt-get install -y --no-install-recommends blender \
#     && rm -rf /var/lib/apt/lists/*

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
