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

# ── Blender 4.x standalone (Debian-Paket ist 3.4 → kann keine 4.x .blend öffnen) ──
# Extra-Libs die Blender headless braucht
RUN apt-get update && apt-get install -y --no-install-recommends \
    libxrender1 libxi6 libxxf86vm1 libxfixes3 xz-utils \
    && rm -rf /var/lib/apt/lists/*
RUN wget -q "https://download.blender.org/release/Blender4.3/blender-4.3.2-linux-x64.tar.xz" \
    -O /tmp/blender.tar.xz \
    && tar -xf /tmp/blender.tar.xz -C /opt/ \
    && ln -s /opt/blender-4.3.2-linux-x64/blender /usr/local/bin/blender \
    && rm /tmp/blender.tar.xz

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
