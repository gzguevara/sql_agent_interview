# Deloitte Mini Project

This project is a small full-stack data assistant that lets a user ask questions in a web UI, runs a LangChain SQL agent against a local database, and streams intermediate tool activity plus final answers back to the user.

## What The App Does

- Accepts natural-language questions from the frontend chat interface.
- Sends the full conversation to a backend API endpoint.
- Uses a LangChain agent to inspect schema, generate SQL queries, execute tools, and compose a response.
- Streams runtime events (`tool_call`, `tool_result`, `final`) back to the frontend as NDJSON.
- Supports Google-based login and backend-side authorization for protected chat access.

## Main Components

## Frontend (`frontend/`)

- Streamlit-based chat application.
- Handles user login/logout (Google OIDC).
- Maintains session conversation state in `st.session_state`.
- Calls the backend streaming endpoint and renders:
  - intermediate tool events
  - final assistant answer

See: `frontend/README.md`

## Backend (`backend/`)

- FastAPI service exposing:
  - `GET /health`
  - `POST /chat/stream`
- Streams newline-delimited JSON (`application/x-ndjson`) to the frontend.
- Hosts the LangChain agent integration and SQL toolkit wiring.
- Verifies bearer tokens and enforces allowlisted user emails for chat access.

See: `backend/README.md`

## LangChain Layer (`langchain/` and backend agent code)

- Contains notebook/prototyping assets for experimentation and local iteration.
- Production-style runtime agent logic is implemented in backend service code (notably `backend/app/agent.py`).
- Focuses on SQL-agent behavior:
  - tool selection
  - query generation and execution
  - streaming event emission

## High-Level Flow

1. User logs in on Streamlit frontend.
2. User sends a chat prompt.
3. Frontend sends conversation + auth token to backend.
4. Backend authorizes request and starts LangChain agent stream.
5. Backend emits NDJSON events.
6. Frontend displays tool activity and final response.

## Repository Structure

```text
deloitte/
  frontend/   # Streamlit UI
  backend/    # FastAPI API + LangChain agent runtime
  langchain/  # notebooks / experimentation assets
  data/       # local data assets
```

## Notes

- Local secrets are intentionally excluded from git (`.env`, `.streamlit/secrets.toml`).
- This project is structured as an interview-ready demo emphasizing practical architecture, streaming UX, and basic authentication/authorization principles.
