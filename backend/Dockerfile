










FROM python:3.11-slim AS base

RUN apt-get update \
	&& apt-get install -y --no-install-recommends gcc libpq-dev \
	&& rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
	PYTHONDONTWRITEBYTECODE=1 \
	PYTHON_ENV=production

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN useradd -m appuser

COPY --chown=appuser:appuser . .

USER appuser

EXPOSE 8080

CMD gunicorn app.main:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --workers 1 --timeout 120
