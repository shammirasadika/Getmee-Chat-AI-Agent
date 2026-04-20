FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV INGESTION_PORT=8001
EXPOSE ${INGESTION_PORT}

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${INGESTION_PORT}"]
