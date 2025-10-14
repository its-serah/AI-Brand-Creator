FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive \
    HF_HOME=/models/hf \
    HUGGINGFACE_HUB_CACHE=/models/hf/hub \
    PYTHONUNBUFFERED=1

# + OpenCV runtime libs to avoid libGL errors
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg git libgl1 libglib2.0-0 \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python deps (no-cache to keep layers small)
COPY requirements.docker.txt /app/
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.docker.txt

# (Optional) bake models into the image. Remove if you want smaller images.
COPY _hf_warmup.py /app/
RUN python _hf_warmup.py || true

# App code
COPY . /app

# Runtime
ENV PYTHONPATH=/app/01-mvp-monolith \
    PORT=8080
EXPOSE 8080
WORKDIR /app/01-mvp-monolith
CMD ["sh","-c","python -m uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8080} --no-server-header"]
