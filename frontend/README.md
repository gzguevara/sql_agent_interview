# Streamlit Frontend (Google Auth Demo)

Minimal Streamlit chat frontend for the FastAPI backend in `../backend`.

## What it does

- Uses a stateful in-session conversation (`st.session_state`).
- Uses Google login via Streamlit OIDC (`st.login`, `st.user`, `st.logout`).
- Sends the Google ID token as `Authorization: Bearer <token>` to `POST /chat/stream`.
- Reads NDJSON stream events from the backend.
- Displays tool calls and tool results for each assistant answer.

## Requirements

- Python 3.10+
- Backend running locally (default: `http://127.0.0.1:8000`)
- Google OAuth client credentials in local Streamlit secrets

## Install

From `frontend/`:

```bash
pip install -r requirements.txt
```

## Configure Streamlit auth

Create `frontend/.streamlit/secrets.toml`:

```toml
[auth]
redirect_uri = "http://localhost:8501/oauth2callback"
cookie_secret = "your_random_cookie_secret"
client_id = "your_google_client_id"
client_secret = "your_google_client_secret"
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"
expose_tokens = "id"
```

Important:

- Keep this file local and out of git.
- `redirect_uri` must exactly match your Google OAuth client redirect URI.

## Run

```bash
streamlit run app.py
```

## Backend URL

The app uses:

- `BACKEND_BASE_URL` environment variable, or
- sidebar `Backend URL` input

Default value:

```text
http://127.0.0.1:8000
```

## Typical local workflow

1. Start backend from `backend/` with auth env values configured.
2. Start frontend:

```bash
streamlit run app.py
```

3. Log in with Google and ask a question in chat.
4. Inspect tool activity in:

- live `Agent is working...` status section during the run
- `Tool activity` expander under the assistant response after completion

## Interview auth notes

- Authentication: user proves identity with Google OIDC.
- Authorization: backend allowlist restricts access by user email.
- Backend verification is mandatory; frontend login alone is not trusted.

## Notes

- Chat memory is session-only and resets on browser refresh.
