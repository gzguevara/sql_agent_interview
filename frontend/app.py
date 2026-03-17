from __future__ import annotations

import os
from typing import Any

import streamlit as st

from api_client import BackendHTTPError, BackendStreamError, check_health, stream_chat_events

DEFAULT_BACKEND_URL = os.getenv("BACKEND_BASE_URL", "http://127.0.0.1:8000")


def _init_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "turns" not in st.session_state:
        st.session_state.turns = []
    if "is_streaming" not in st.session_state:
        st.session_state.is_streaming = False
    if "backend_url" not in st.session_state:
        st.session_state.backend_url = DEFAULT_BACKEND_URL
    if "user_email" not in st.session_state:
        st.session_state.user_email = ""


def _get_id_token() -> str | None:
    if not getattr(st.user, "is_logged_in", False):
        return None

    tokens = getattr(st.user, "tokens", None)
    if tokens is None:
        return None

    try:
        return tokens["id"]
    except Exception:
        return None


def _enforce_login() -> str:
    if not getattr(st.user, "is_logged_in", False):
        st.subheader("This app is private")
        st.caption("Please sign in with Google to use the chat backend.")
        st.button("Log in with Google", on_click=st.login)
        st.stop()

    user_email = str(getattr(st.user, "email", "") or "").strip()
    st.session_state.user_email = user_email

    id_token = _get_id_token()
    if not id_token:
        st.error(
            "Google login succeeded, but no ID token is exposed. "
            "Set `expose_tokens = \"id\"` in `.streamlit/secrets.toml`."
        )
        if st.button("Log out", on_click=st.logout):
            st.stop()
        st.stop()

    return id_token


def _format_tool_line(event: dict[str, Any]) -> str:
    event_name = event.get("event", "")
    data = event.get("data", {})
    step = data.get("step", "unknown-step")
    tool = data.get("tool", "unknown-tool")

    if event_name == "tool_call":
        args = data.get("args", {})
        return f"[{step}] tool_call `{tool}` args={args}"
    if event_name == "tool_result":
        content = str(data.get("content", ""))
        preview = content if len(content) < 280 else f"{content[:280]}..."
        return f"[{step}] tool_result `{tool}` content={preview}"
    if event_name == "error":
        message = data.get("message", "Unknown stream error")
        detail = data.get("detail", "")
        return f"error: {message} ({detail})"
    return f"[{step}] {event_name}: {data}"


def _render_turn(turn: dict[str, Any]) -> None:
    role = turn.get("role", "assistant")
    with st.chat_message(role):
        st.markdown(turn.get("content", ""))

        tool_events = turn.get("tool_events", [])
        if role == "assistant" and tool_events:
            with st.expander("Tool activity", expanded=False):
                for event in tool_events:
                    st.code(_format_tool_line(event), language="text")


def _render_history() -> None:
    for turn in st.session_state.turns:
        _render_turn(turn)


def _run_chat_turn(prompt: str, backend_url: str, id_token: str) -> None:
    user_turn = {"role": "user", "content": prompt}
    st.session_state.turns.append(user_turn)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        tool_events: list[dict[str, Any]] = []
        final_text = ""
        stream_had_error = False

        with st.status("Agent is working...", expanded=True) as status:
            try:
                for event in stream_chat_events(
                    backend_url,
                    st.session_state.messages,
                    id_token=id_token,
                ):
                    event_name = event.get("event", "")
                    data = event.get("data", {})

                    if event_name in {"tool_call", "tool_result"}:
                        tool_events.append(event)
                        status.write(_format_tool_line(event))
                    elif event_name == "final":
                        final_text = str(data.get("text", "")).strip()
                    elif event_name == "error":
                        stream_had_error = True
                        status.write(_format_tool_line(event))
                        status.update(label="Agent failed", state="error", expanded=True)
                    else:
                        status.write(_format_tool_line(event))

                if not stream_had_error:
                    status.update(label="Agent complete", state="complete", expanded=False)
            except BackendHTTPError as exc:
                stream_had_error = True
                status.write(str(exc))
                if exc.status_code == 401:
                    status.write("Authentication failed. Please log in again.")
                elif exc.status_code == 403:
                    status.write(
                        "Authenticated, but this email is not on the backend allowlist."
                    )
                status.update(label="Backend returned an error", state="error", expanded=True)
            except BackendStreamError as exc:
                stream_had_error = True
                status.write(str(exc))
                status.update(label="Stream connection failed", state="error", expanded=True)
            except Exception as exc:  # Defensive fallback for UI stability.
                stream_had_error = True
                status.write(f"Unexpected error: {exc}")
                status.update(label="Unexpected frontend error", state="error", expanded=True)

        if final_text:
            st.markdown(final_text)
            st.session_state.messages.append({"role": "assistant", "content": final_text})
            st.session_state.turns.append(
                {
                    "role": "assistant",
                    "content": final_text,
                    "tool_events": tool_events,
                }
            )
            return

        if stream_had_error:
            fallback = "I could not complete this request due to a stream error."
            st.error(fallback)
            st.session_state.turns.append(
                {
                    "role": "assistant",
                    "content": fallback,
                    "tool_events": tool_events,
                }
            )
            return

        # If stream closed without `final`, preserve trace and surface a clear message.
        fallback = "No final answer was returned before the stream ended."
        st.warning(fallback)
        st.session_state.turns.append(
            {
                "role": "assistant",
                "content": fallback,
                "tool_events": tool_events,
            }
        )


def _render_sidebar() -> str:
    st.sidebar.header("Connection")
    backend_url = st.sidebar.text_input("Backend URL", key="backend_url")

    user_email = st.session_state.get("user_email", "")
    if user_email:
        st.sidebar.caption(f"Signed in as `{user_email}`")
    st.sidebar.button("Log out", on_click=st.logout)

    col_a, col_b = st.sidebar.columns(2)
    if col_a.button("Check health"):
        ok, message = check_health(backend_url)
        if ok:
            st.sidebar.success(message)
        else:
            st.sidebar.error(message)

    if col_b.button("Clear chat"):
        st.session_state.messages = []
        st.session_state.turns = []
        st.rerun()

    st.sidebar.caption("Session-only chat memory. Refresh clears state.")
    return backend_url


def main() -> None:
    st.set_page_config(page_title="SQL Agent Chat", page_icon=":speech_balloon:", layout="centered")
    st.title("SQL Agent Chat")
    st.caption("Streamlit MVP frontend for the FastAPI NDJSON backend.")

    _init_state()
    id_token = _enforce_login()
    backend_url = _render_sidebar()
    _render_history()

    prompt = st.chat_input("Ask about the dataset...", disabled=st.session_state.is_streaming)
    if not prompt:
        return

    st.session_state.is_streaming = True
    try:
        _run_chat_turn(prompt, backend_url, id_token)
    finally:
        st.session_state.is_streaming = False


if __name__ == "__main__":
    main()
