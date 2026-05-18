"""Streamlit UI — local Gemini execution (gemini-local branch)."""

from __future__ import annotations

from datetime import datetime, timedelta
from html import escape

import streamlit as st

from core.diary_service import generate_or_update_diary
from core.llm import process_input
from core.notion import add_entry_to_notion
from core.validation import format_config_issues, validate_config
from core.voice import TRANSCRIPTION_FAILED_MESSAGE, transcribe_audio
from rag.fetch_data import fetch_diary_by_date

APP_TITLE = "AI Diary Assistant"
RECENT_DAYS = 5


st.set_page_config(
    page_title=APP_TITLE,
    page_icon=":memo:",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def inject_styles() -> None:
    st.markdown(
        """
        <style>
            :root {
                --app-bg: #f4f6f8;
                --surface: #ffffff;
                --surface-soft: #f9fafb;
                --text-main: #17202a;
                --text-muted: #667085;
                --border: #d9dee7;
                --accent: #2f6f73;
                --accent-soft: #e7f2f1;
                --success: #1f7a4d;
                --warning: #9a6b2f;
            }

            [data-testid="stAppViewContainer"] {
                background: var(--app-bg);
            }

            .block-container {
                max-width: 1080px;
                padding-top: 2.5rem;
                padding-bottom: 3rem;
            }

            .app-header {
                display: flex;
                justify-content: space-between;
                gap: 1.5rem;
                align-items: flex-start;
                margin-bottom: 1rem;
            }

            .app-header h1 {
                margin: 0;
                font-size: 2.45rem;
                line-height: 1.08;
                font-weight: 760;
                color: var(--text-main);
            }

            .subtitle {
                max-width: 720px;
                margin: .7rem 0 0 0;
                color: var(--text-muted);
                font-size: 1.02rem;
                line-height: 1.55;
            }

            .date-pill,
            .model-badge,
            .status-pill {
                border: 1px solid var(--border);
                background: var(--surface);
                border-radius: 999px;
                color: var(--text-muted);
                display: inline-flex;
                font-size: .82rem;
                font-weight: 650;
                padding: .4rem .72rem;
                white-space: nowrap;
            }

            .model-badge {
                background: var(--accent-soft);
                border-color: #c8e1df;
                color: #24585b;
            }

            .status-pill.ok {
                border-color: #b7e2cb;
                background: #edf9f1;
                color: var(--success);
            }

            .system-summary {
                display: grid;
                grid-template-columns: repeat(4, minmax(0, 1fr));
                gap: .75rem;
                margin: 1rem 0 1.15rem 0;
            }

            .system-summary div {
                background: var(--surface);
                border: 1px solid var(--border);
                border-radius: 10px;
                padding: .85rem .9rem;
            }

            .system-summary strong {
                color: var(--text-main);
                display: block;
                font-size: .88rem;
                margin-bottom: .2rem;
            }

            .system-summary span {
                color: var(--text-muted);
                display: block;
                font-size: .82rem;
                line-height: 1.35;
            }

            .tab-intro {
                color: var(--text-muted);
                font-size: .95rem;
                margin: .25rem 0 1rem 0;
            }

            .transcription-box,
            .entry-preview,
            .diary-reader {
                background: var(--surface-soft);
                border: 1px solid var(--border);
                border-radius: 10px;
                line-height: 1.72;
            }

            .transcription-box { margin-top: .9rem; padding: .85rem 1rem; }
            .entry-preview { margin-top: 1rem; padding: 1rem 1.1rem; }
            .diary-reader { font-size: 1rem; padding: 1.1rem 1.2rem; }

            .entry-meta {
                align-items: center;
                display: flex;
                flex-wrap: wrap;
                gap: .55rem;
                justify-content: space-between;
                margin-bottom: .75rem;
            }

            .entry-meta span:first-child {
                color: var(--text-muted);
                font-size: .86rem;
            }

            div[data-testid="stTabs"] [role="tablist"] {
                border-bottom: 1px solid var(--border);
                gap: .35rem;
            }

            div[data-testid="stTabs"] [aria-selected="true"] {
                color: var(--accent);
            }

            .stTextArea textarea { border-radius: 10px; min-height: 170px; }
            .stButton button, .stFormSubmitButton button {
                border-radius: 10px;
                font-weight: 650;
            }

            @media (max-width: 760px) {
                .block-container { padding-top: 1.25rem; }
                .app-header { display: block; }
                .app-header h1 { font-size: 2rem; }
                .system-summary { grid-template-columns: 1fr; }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def initialise_session_state(now: datetime) -> None:
    defaults = {
        "voice_text": "",
        "clean_content": "",
        "entry_ts": "",
        "model_used": "",
        "selected_date": now.date() - timedelta(days=1),
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def html_text(text: str) -> str:
    return "<br>".join(escape(str(text)).splitlines())


def render_config_gate() -> None:
    issues = validate_config()
    if issues:
        st.error(format_config_issues(issues))
        st.info(
            "Copy `.env.example` to `.env`, fill in your API keys and Notion database IDs, "
            "then restart: `streamlit run app.py`"
        )
        st.stop()

    st.markdown(
        '<span class="status-pill ok">`.env` configuration loaded</span>',
        unsafe_allow_html=True,
    )


def render_header(now: datetime) -> None:
    st.markdown(
        f"""
        <div class="app-header">
            <div>
                <h1>{APP_TITLE}</h1>
                <p class="subtitle">
                    Local development build: voice or text capture, Gemini cleanup with
                    multi-model fallback, and Notion-backed daily diary generation.
                </p>
            </div>
            <div class="date-pill">{now.strftime("%A, %B %d, %Y")}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="system-summary">
            <div><strong>Voice</strong><span>Groq Whisper (browser mic)</span></div>
            <div><strong>LLM</strong><span>Gemini fallback router</span></div>
            <div><strong>Storage</strong><span>Notion log and diary databases</span></div>
            <div><strong>Flow</strong><span>Capture → clean → save → summarize</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption(
        "Runs locally with `.env` — use your own Notion integration and API keys."
    )


def render_voice_input() -> None:
    st.markdown("#### Voice note")
    st.caption("Record in your browser; audio is sent to Groq for transcription.")

    audio_value = st.audio_input("Record your journal entry")

    if audio_value:
        with open("temp_audio.wav", "wb") as audio_file:
            audio_file.write(audio_value.read())

        with st.spinner("Transcribing with Groq Whisper..."):
            transcription = transcribe_audio("temp_audio.wav")

        if not transcription or transcription == TRANSCRIPTION_FAILED_MESSAGE:
            st.error("Transcription failed. Check GROQ_API_KEY in your .env file.")
            return

        st.session_state.voice_text = transcription.strip()
        st.success("Transcription ready — review or edit below.")

    if st.session_state.voice_text:
        st.markdown(
            f"""
            <div class="transcription-box">
                <strong>Transcription</strong><br>
                {html_text(st.session_state.voice_text)}
            </div>
            """,
            unsafe_allow_html=True,
        )


def save_entry(user_input: str, now: datetime) -> None:
    if not user_input.strip():
        st.warning("Write or record something first.")
        return

    try:
        with st.spinner("Cleaning entry with Gemini..."):
            result = process_input(user_input)

        clean_content = result["text"]
        model_used = result.get("model_used", "Unknown model")
        today_str = now.strftime("%Y-%m-%d")
        time_now = now.strftime("%H:%M:%S")
        display_ts = now.strftime("%B %d, %Y at %H:%M")

        with st.spinner("Saving to Notion..."):
            add_entry_to_notion(clean_content, today_str, time_now)

    except Exception as exc:
        st.error(f"Could not save the entry: {exc}")
        return

    st.session_state.clean_content = clean_content
    st.session_state.entry_ts = display_ts
    st.session_state.model_used = model_used
    st.session_state.voice_text = ""
    st.success("Entry saved to Notion.")


def generate_diary() -> None:
    try:
        with st.spinner("Generating today's diary from saved logs..."):
            message = generate_or_update_diary()
    except Exception as exc:
        st.error(f"Could not generate the diary: {exc}")
        return

    if message.lower().startswith("no logs"):
        st.info(message)
    else:
        st.success(message)


def render_entry_form(now: datetime) -> None:
    st.markdown("#### Journal entry")
    st.caption("Type freely or start from the transcription above.")

    with st.form("entry_form", clear_on_submit=False):
        user_input = st.text_area(
            label="Entry",
            value=st.session_state.voice_text,
            height=170,
            placeholder="What did you work on, learn, or reflect on today?",
            label_visibility="collapsed",
        )

        col_save, col_generate, _ = st.columns([1, 1.15, 2.4])
        with col_save:
            submit_clicked = st.form_submit_button(
                "Save Entry",
                type="primary",
                use_container_width=True,
            )
        with col_generate:
            generate_clicked = st.form_submit_button(
                "Generate Diary",
                use_container_width=True,
            )

    if submit_clicked:
        save_entry(user_input, now)
    if generate_clicked:
        generate_diary()


def render_saved_entry() -> None:
    if not st.session_state.clean_content:
        return

    model_name = escape(st.session_state.model_used or "Unknown model")
    st.markdown(
        f"""
        <div class="entry-preview">
            <div class="entry-meta">
                <span>{escape(st.session_state.entry_ts)}</span>
                <span class="model-badge">Model: {model_name}</span>
            </div>
            <div>{html_text(st.session_state.clean_content)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_today_tab(now: datetime) -> None:
    st.markdown(
        '<p class="tab-intro">Capture a note, clean it with Gemini, and save it to your Daily Logs database.</p>',
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        render_voice_input()
    with st.container(border=True):
        render_entry_form(now)
    render_saved_entry()


def recent_dates(now: datetime) -> list:
    dates = [now.date() - timedelta(days=offset) for offset in range(1, RECENT_DAYS + 1)]
    selected = st.session_state.selected_date
    if selected not in dates:
        return [selected, *dates]
    return dates


def render_date_picker(now: datetime) -> None:
    st.markdown("#### Browse diaries")
    st.caption("Select a date or use a recent shortcut.")

    manual_date = st.date_input("Select diary date", value=st.session_state.selected_date)
    if manual_date != st.session_state.selected_date:
        st.session_state.selected_date = manual_date
        st.rerun()

    dates = recent_dates(now)
    labels = [date.strftime("%b %d, %Y") for date in dates]
    chosen_label = st.radio(
        "Recent entries",
        options=labels,
        index=dates.index(st.session_state.selected_date),
    )

    chosen_date = dates[labels.index(chosen_label)]
    if chosen_date != st.session_state.selected_date:
        st.session_state.selected_date = chosen_date
        st.rerun()


def render_diary_reader(selected_date) -> None:
    st.markdown(f"### {selected_date.strftime('%A, %B %d, %Y')}")

    try:
        diary_content = fetch_diary_by_date(selected_date)
    except Exception as exc:
        st.error(f"Could not load diary: {exc}")
        return

    if not diary_content:
        st.info("No diary for this date. Save logs and run **Generate Diary** first.")
        return

    st.caption(f"{len(str(diary_content).split())} words")
    st.markdown(
        f'<div class="diary-reader">{html_text(diary_content)}</div>',
        unsafe_allow_html=True,
    )


def render_past_tab(now: datetime) -> None:
    st.markdown(
        '<p class="tab-intro">Read generated diaries from your Daily Diary database.</p>',
        unsafe_allow_html=True,
    )

    col_left, col_right = st.columns([1, 2.2], gap="large")
    with col_left:
        with st.container(border=True):
            render_date_picker(now)
    with col_right:
        with st.container(border=True):
            render_diary_reader(st.session_state.selected_date)


def main() -> None:
    inject_styles()
    now = datetime.now()
    initialise_session_state(now)
    render_config_gate()
    render_header(now)

    tab_today, tab_past = st.tabs(["Today's Entry", "Past Diaries"])
    with tab_today:
        render_today_tab(now)
    with tab_past:
        render_past_tab(now)


if __name__ == "__main__":
    main()
