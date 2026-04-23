# ChromaDB Self-Hosted Deployment

This folder contains the configuration for running ChromaDB as a self-hosted service using Docker Compose. Only ChromaDB runs here—no backend, frontend, or ingestion services are included.

## Usage

### Start ChromaDB
```sh
docker compose up -d
```

### Stop ChromaDB
```sh
docker compose down
```

## Connection Details
- ChromaDB will be available on port **8000** of your VM.
- Data is stored persistently in a Docker-managed volume (`chroma_data`).
- Other services (backend, ingestion, etc.) should connect using these environment variables:

```
CHROMA_MODE=http
CHROMA_HOST=<VM-IP or hostname>
CHROMA_PORT=8000
```

Replace `<VM-IP or hostname>` with your server's address.

---

For more details, see the [ChromaDB documentation](https://docs.trychroma.com/).
