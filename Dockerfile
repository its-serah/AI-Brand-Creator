FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg git && \
    rm -rf /var/lib/apt/lists/*

# HF cache inside the image (fast cold starts)
ENV HF_HOME=/models/hf \
    HUGGINGFACE_HUB_CACHE=/models/hf/hub \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Python deps
COPY requirements.docker.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.docker.txt

# --- Prewarm model weights (optional but recommended) ---
COPY _hf_warmup.py /app/
RUN python _hf_warmup.py || true
# --------------------------------------------------------

# App code
COPY . /app

# App module path
ENV PYTHONPATH=/app/01-mvp-monolith
ENV PORT=8080
EXPOSE 8080

# Run API (use Cloud Run $PORT)
WORKDIR /app/01-mvp-monolith
CMD ["sh","-c","python -m uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8080} --no-server-header"]
