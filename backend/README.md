# Backend Agent Service

Small FastAPI backend for streaming LangChain SQL-agent events as NDJSON.

## What this service does

- Exposes `GET /health` for readiness checks.
- Exposes `POST /chat/stream` for a stateless chat run (requires Google bearer token).
- Accepts a full conversation thread from the client.
- Streams raw agent runtime events as newline-delimited JSON (`application/x-ndjson`).

## Folder layout

```text
backend/
  app/
    __init__.py
    main.py
    api.py
    agent.py
    config.py
    schemas.py
    streaming.py
  .env.example
  requirements.txt
```

## Setup

1. Create and activate an environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create `.env` in `backend/` from `.env.example` and fill values.

Auth-related values:

- `GOOGLE_OAUTH_CLIENT_ID`: Google OAuth web client ID used to verify incoming ID tokens.
- `ALLOWED_EMAILS`: comma-separated user emails allowed to call `/chat/stream`.

## Run locally

From inside `backend/`:

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

## API

### Health

```bash
curl -s http://127.0.0.1:8000/health
```

### Stream chat (NDJSON)

```bash
export ID_TOKEN="your_google_id_token"

curl -N -X POST "http://127.0.0.1:8000/chat/stream" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${ID_TOKEN}" \
  -d '{
    "messages": [
      {"role": "system", "content": "You are a data assistant."},
      {"role": "user", "content": "Which sectors have the highest number of companies with set targets?"}
    ]
  }'
```

Each line in the response stream is one JSON event.
