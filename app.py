"""Streamlit UI — offline local LLM execution (local-llm branch)."""

from __future__ import annotations

from datetime import datetime, timedelta
from html import escape

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

APP_TITLE = "AI Personal Journal"
RECENT_DAYS = 5
RECORD_SECONDS = 30

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=":notebook:",
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
                --accent: #3d5a80;
                --accent-soft: #e8eef5;
                --success: #1f7a4d;
            }
            [data-testid="stAppViewContainer"] { background: var(--app-bg); }
            .block-container { max-width: 1080px; padding-top: 2.5rem; padding-bottom: 3rem; }
            .app-header { display: flex; justify-content: space-between; gap: 1.5rem; margin-bottom: 1rem; }
            .app-header h1 { margin: 0; font-size: 2.4rem; color: var(--text-main); font-weight: 760; }
            .subtitle { color: var(--text-muted); font-size: 1.02rem; line-height: 1.55; max-width: 720px; margin-top: .65rem; }
            .date-pill, .model-badge, .status-pill {
                border: 1px solid var(--border); border-radius: 999px;
                font-size: .82rem; font-weight: 650; padding: .4rem .72rem;
                display: inline-flex; background: var(--surface); color: var(--text-muted);
            }
            .model-badge { background: var(--accent-soft); border-color: #c5d4e8; color: #2c4768; }
            .status-pill.ok { border-color: #b7e2cb; background: #edf9f1; color: var(--success); }
            .status-pill.warn { border-color: #f0d7a5; background: #fff8eb; color: #8a6118; }
            .system-summary {
                display: grid; grid-template-columns: repeat(4, minmax(0, 1fr));
                gap: .75rem; margin: 1rem 0 1.15rem 0;
            }
            .system-summary div {
                background: var(--surface); border: 1px solid var(--border);
                border-radius: 10px; padding: .85rem .9rem;
            }
            .system-summary strong { display: block; font-size: .88rem; color: var(--text-main); margin-bottom: .2rem; }
            .system-summary span { font-size: .82rem; color: var(--text-muted); line-height: 1.35; display: block; }
            .tab-intro { color: var(--text-muted); font-size: .95rem; margin: .25rem 0 1rem 0; }
            .transcription-box, .entry-preview, .diary-reader {
                background: var(--surface-soft); border: 1px solid var(--border);
                border-radius: 10px; line-height: 1.72;
            }
            .transcription-box { margin-top: .9rem; padding: .85rem 1rem; }
            .entry-preview { margin-top: 1rem; padding: 1rem 1.1rem; }
            .diary-reader { padding: 1.1rem 1.2rem; }
            .entry-meta { display: flex; flex-wrap: wrap; gap: .55rem; justify-content: space-between; margin-bottom: .75rem; }
            .entry-meta span:first-child { color: var(--text-muted); font-size: .86rem; }
            div[data-testid="stTabs"] [aria-selected="true"] { color: var(--accent); }
            .stTextArea textarea { border-radius: 10px; min-height: 170px; }
            @media (max-width: 760px) {
                .system-summary { grid-template-columns: 1fr; }
                .app-header { display: block; }
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
        st.markdown(
            f'<span class="status-pill warn">Ollama: {escape(ollama_issue)}</span>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<span class="status-pill ok">Ollama ready · {escape(get_ollama_model())}</span>',
            unsafe_allow_html=True,
        )


def render_header(now: datetime) -> None:
    st.markdown(
        f"""
        <div class="app-header">
            <div>
                <h1>{APP_TITLE}</h1>
                <p class="subtitle">
                    Privacy-first journal: local Whisper transcription, Ollama text cleanup,
                    and optional Notion storage — no cloud LLM required.
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
            <div><strong>Voice</strong><span>Local Whisper (offline)</span></div>
            <div><strong>LLM</strong><span>Ollama + llama3</span></div>
            <div><strong>Storage</strong><span>Your Notion databases</span></div>
            <div><strong>Privacy</strong><span>Speech + text stay on your machine</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption("Requires Ollama, FFmpeg, and a working microphone. Notion stores entries in the cloud.")


def render_voice_input() -> None:
    st.markdown("#### Voice note")
    st.caption(f"Record up to {RECORD_SECONDS} seconds from your machine microphone.")

    if st.button("Start recording", type="secondary"):
        with st.spinner(f"Recording for {RECORD_SECONDS} seconds — speak now..."):
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

        st.session_state.voice_text = transcription
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
        model_used = result.get("model_used", "Ollama")
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
        with st.spinner("Generating diary from today's logs..."):
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
    st.caption("Type or edit the transcription, then save.")

    with st.form("entry_form", clear_on_submit=False):
        user_input = st.text_area(
            label="Entry",
            value=st.session_state.voice_text,
            height=170,
            placeholder="What did you do, learn, or reflect on today?",
            label_visibility="collapsed",
        )

        col_save, col_generate, _ = st.columns([1, 1.15, 2.4])
        with col_save:
            submit_clicked = st.form_submit_button("Save Entry", type="primary", use_container_width=True)
        with col_generate:
            generate_clicked = st.form_submit_button("Generate Diary", use_container_width=True)

    if submit_clicked:
        save_entry(user_input, now)
    if generate_clicked:
        generate_diary()


def render_saved_entry() -> None:
    if not st.session_state.clean_content:
        return

    model_name = escape(st.session_state.model_used or "Ollama")
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
        '<p class="tab-intro">Capture offline, clean with Ollama, and save to your Daily Logs database.</p>',
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
        st.info("No diary for this date. Save logs and run **Generate Diary**.")
        return

    st.caption(f"{len(str(diary_content).split())} words")
    st.markdown(
        f'<div class="diary-reader">{html_text(diary_content)}</div>',
        unsafe_allow_html=True,
    )


def render_past_tab(now: datetime) -> None:
    st.markdown(
        '<p class="tab-intro">Read diaries from your Daily Diary Notion database.</p>',
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
