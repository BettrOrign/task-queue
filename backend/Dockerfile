FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY backend/pyproject.toml backend/pyproject.toml
COPY README.md backend/README.md
RUN pip install --no-cache-dir -e ./backend

COPY backend/ ./backend/

ENV PYTHONPATH=/app/backend

EXPOSE 8000
CMD ["python", "-m", "app.main"]