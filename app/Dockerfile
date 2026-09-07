FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt \
    && useradd --create-home --uid 1000 uploader

COPY --chown=uploader:uploader uploader.py .

USER uploader

ENTRYPOINT ["python", "/app/uploader.py"]
