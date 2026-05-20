"""Compact Streamlit UI for local Ollama execution."""

from __future__ import annotations

from datetime import datetime, timedelta
from html import escape
from zoneinfo import ZoneInfo

import streamlit as st

from core.config import get_ollama_model
from core.diary_service import generate_or_update_diary
from core.llm import process_input
from core.notion import add_entry_to_notion
from core.validation import (
    check_ollama_available,
    format_config_issues,
    validate_config,
)
from core.voice import record_audio, transcribe_audio
from rag.fetch_data import fetch_diary_by_date

APP_TITLE = "AI Diary Assistant"
RECENT_DAYS = 5
RECORD_SECONDS = 30


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
                max-width: 1180px;
                padding: 1.25rem 1.5rem 2rem;
            }

            .app-header h1 {
                margin: 0 0 .2rem 0;
                font-size: 1.8rem;
                line-height: 1.15;
                font-weight: 720;
                color: var(--text-main);
            }

            .subtitle {
                margin: 0 0 1rem 0;
                color: var(--text-muted);
                font-size: .95rem;
                line-height: 1.4;
            }

            .section-title {
                color: var(--text-main);
                display: block;
                font-size: .98rem;
                font-weight: 700;
                margin: 0 0 .45rem 0;
            }

            .transcription-box,
            .entry-preview,
            .diary-reader {
                background: var(--surface-soft);
                border: 1px solid var(--border);
                border-radius: 8px;
                line-height: 1.55;
            }

            .transcription-box {
                margin-top: .45rem;
                max-height: 145px;
                overflow-y: auto;
                padding: .7rem .8rem;
            }

            .entry-preview {
                margin-top: .75rem;
                max-height: 180px;
                overflow-y: auto;
                padding: .8rem .9rem;
            }

            .diary-reader {
                font-size: .95rem;
                max-height: 520px;
                overflow-y: auto;
                padding: .9rem 1rem;
            }

            .entry-meta {
                align-items: center;
                display: flex;
                flex-wrap: wrap;
                gap: .55rem;
                justify-content: space-between;
                margin-bottom: .75rem;
            }

            .entry-meta span {
                color: var(--text-muted);
                font-size: .8rem;
            }

            .model-badge {
                background: var(--accent-soft);
                border: 1px solid #c8e1df;
                border-radius: 999px;
                color: #24585b;
                display: inline-flex;
                font-size: .76rem;
                font-weight: 650;
                padding: .25rem .55rem;
                white-space: nowrap;
            }

            div[data-testid="stVerticalBlockBorderWrapper"] {
                border-radius: 8px;
            }

            div[data-testid="stVerticalBlockBorderWrapper"] > div {
                padding: .8rem .9rem;
            }

            .stTextArea textarea {
                border-radius: 8px;
                min-height: 155px;
            }

            .stButton button, .stFormSubmitButton button {
                border-radius: 8px;
                font-weight: 650;
            }

            div[data-testid="stMarkdownContainer"] p {
                margin-bottom: .45rem;
            }

            @media (max-width: 760px) {
                .block-container { padding: 1rem .9rem 1.5rem; }
                .app-header h1 { font-size: 1.55rem; }
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
        st.info("Copy `.env.example` to `.env`, fill in Notion credentials, then restart.")
        st.stop()

    ollama_issue = check_ollama_available()
    if ollama_issue:
        st.warning(f"Ollama: {ollama_issue}")


def render_header() -> None:
    st.markdown(
        f"""
        <div class="app-header">
            <h1>{APP_TITLE}</h1>
            <p class="subtitle">Record, edit, save, and review daily diary entries.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_voice_input() -> None:
    st.markdown('<span class="section-title">Voice input</span>', unsafe_allow_html=True)

    if st.button(f"Start {RECORD_SECONDS}s Recording", type="secondary", use_container_width=True):
        with st.spinner(f"Recording for {RECORD_SECONDS} seconds..."):
            try:
                record_audio(duration=RECORD_SECONDS)
            except Exception as exc:
                st.error(f"Recording failed: {exc}")
                return

        with st.spinner("Transcribing with local Whisper..."):
            try:
                transcription = transcribe_audio()
            except Exception as exc:
                st.error(f"Transcription failed: {exc}")
                return

        st.session_state.voice_text = transcription.strip()
        st.success("Transcription ready.")

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
        with st.spinner("Cleaning entry with Ollama..."):
            result = process_input(user_input)

        clean_content = result["text"]
        model_used = result.get("model_used", get_ollama_model())
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
    st.markdown('<span class="section-title">Journal entry</span>', unsafe_allow_html=True)

    with st.form("entry_form", clear_on_submit=False):
        user_input = st.text_area(
            label="Entry",
            value=st.session_state.voice_text,
            height=170,
            placeholder="What did you work on, learn, or reflect on today?",
            label_visibility="collapsed",
        )

        col_save, col_generate = st.columns(2)
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

    model_name = escape(st.session_state.model_used or get_ollama_model())
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
    st.markdown('<span class="section-title">Recent diaries</span>', unsafe_allow_html=True)

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
        horizontal=True,
    )

    chosen_date = dates[labels.index(chosen_label)]
    if chosen_date != st.session_state.selected_date:
        st.session_state.selected_date = chosen_date
        st.rerun()


def render_diary_reader(selected_date) -> None:
    st.markdown(
        f'<span class="section-title">{selected_date.strftime("%A, %B %d, %Y")}</span>',
        unsafe_allow_html=True,
    )

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
    with st.container(border=True):
        render_date_picker(now)
    with st.container(border=True):
        render_diary_reader(st.session_state.selected_date)


def main() -> None:
    inject_styles()
    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    initialise_session_state(now)
    render_config_gate()
    render_header()

    left_col, right_col = st.columns([1.05, .95], gap="medium")
    with left_col:
        render_today_tab(now)
    with right_col:
        render_past_tab(now)


if __name__ == "__main__":
    main()
