from datetime import datetime, timedelta
from html import escape

import streamlit as st

from core.diary_service import generate_or_update_diary
from core.llm import process_input
from core.notion import add_entry_to_notion
from core.voice import (
    RECORDING_SECONDS,
    TRANSCRIPTION_FAILED_MESSAGE,
    record_audio,
    transcribe_audio,
)
from rag.fetch_data import fetch_diary_by_date


APP_TITLE = "AI Diary Assistant"
RECENT_DAYS = 5


st.set_page_config(
    page_title=APP_TITLE,
    page_icon=":memo:",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def inject_styles():
    st.markdown(
        """
        <style>
            :root {
                --app-bg: #f6f7f9;
                --surface: #ffffff;
                --surface-soft: #f9fafb;
                --text-main: #17202a;
                --text-muted: #667085;
                --border: #d9dee7;
                --accent: #2f6f73;
                --accent-soft: #e7f2f1;
                --warm: #9a6b2f;
            }

            [data-testid="stAppViewContainer"] {
                background: var(--app-bg);
            }

            .block-container {
                max-width: 1080px;
                padding-top: 3.25rem;
                padding-bottom: 3rem;
            }

            h1, h2, h3, h4 {
                color: var(--text-main);
                letter-spacing: 0;
            }

            p, li, label, [data-testid="stMarkdownContainer"] {
                color: var(--text-main);
            }

            div[data-testid="stCaptionContainer"] {
                color: var(--text-muted);
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
                font-size: 2.55rem;
                line-height: 1.05;
                font-weight: 760;
            }

            .subtitle {
                max-width: 720px;
                margin: .75rem 0 0 0;
                color: var(--text-muted);
                font-size: 1.05rem;
                line-height: 1.55;
            }

            .date-pill,
            .model-badge {
                border: 1px solid var(--border);
                background: var(--surface);
                border-radius: 999px;
                color: var(--text-muted);
                display: inline-flex;
                font-size: .84rem;
                font-weight: 650;
                padding: .45rem .75rem;
                white-space: nowrap;
            }

            .model-badge {
                background: var(--accent-soft);
                border-color: #c8e1df;
                color: #24585b;
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
                border-radius: 8px;
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
                border-radius: 8px;
                line-height: 1.72;
            }

            .transcription-box {
                margin-top: .9rem;
                padding: .85rem 1rem;
            }

            .entry-preview {
                margin-top: 1rem;
                padding: 1rem 1.1rem;
            }

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

            .diary-reader {
                font-size: 1rem;
                padding: 1.1rem 1.2rem;
            }

            div[data-testid="stTabs"] [role="tablist"] {
                border-bottom: 1px solid var(--border);
                gap: .35rem;
            }

            div[data-testid="stTabs"] [role="tab"] {
                color: var(--text-muted);
                font-weight: 650;
                padding: .75rem 1rem;
            }

            div[data-testid="stTabs"] [aria-selected="true"] {
                color: var(--accent);
            }

            .stTextArea textarea {
                border-radius: 8px;
                min-height: 170px;
            }

            .stButton button,
            .stFormSubmitButton button {
                border-radius: 8px;
                font-weight: 650;
            }

            @media (max-width: 760px) {
                .block-container {
                    padding-top: 1.25rem;
                }

                .app-header {
                    display: block;
                }

                .app-header h1 {
                    font-size: 2rem;
                }

                .date-pill {
                    margin-top: .9rem;
                }

                .system-summary {
                    grid-template-columns: 1fr;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def initialise_session_state(now):
    defaults = {
        "voice_text": "",
        "clean_content": "",
        "entry_ts": "",
        "model_used": "",
        "selected_date": now.date() - timedelta(days=1),
    }

    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def html_text(text):
    return "<br>".join(escape(str(text)).splitlines())


def render_header(now):
    st.markdown(
        f"""
        <div class="app-header">
            <div>
                <h1>{APP_TITLE}</h1>
                <p class="subtitle">
                    A voice-to-diary workflow that records daily notes, cleans them with
                    Gemini fallback routing, stores them in Notion, and generates readable
                    daily summaries.
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
            <div><strong>Voice input</strong><span>Groq Whisper speech-to-text</span></div>
            <div><strong>AI router</strong><span>Gemini multi-model fallback</span></div>
            <div><strong>Memory layer</strong><span>Notion log and diary databases</span></div>
            <div><strong>Workflow</strong><span>Capture, clean, save, generate</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.warning(
        "Demo environment: API keys, Notion database IDs, network access, and local "
        "microphone permissions must be configured for the full workflow."
    )


def render_voice_input():
    st.markdown("#### Voice note")
    st.caption(
        f"Record a {RECORDING_SECONDS}-second local audio note and transcribe it with Groq Whisper."
    )

    if st.button(
        f"Start {RECORDING_SECONDS}-second recording",
        key="record",
        use_container_width=True,
    ):
        try:
            with st.spinner(f"Recording for {RECORDING_SECONDS} seconds. Speak naturally."):
                record_audio(duration=RECORDING_SECONDS)

            with st.spinner("Transcribing audio with Groq Whisper..."):
                transcription = transcribe_audio()

        except Exception as exc:
            st.error(f"Recording is unavailable in this environment: {exc}")
            return

        if not transcription or transcription == TRANSCRIPTION_FAILED_MESSAGE:
            st.error(
                "Transcription failed. Check the Groq key, audio device, and network connection."
            )
            return

        st.session_state.voice_text = transcription.strip()
        st.success("Transcription ready. Review or edit it before saving.")

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


def save_entry(user_input, now):
    if not user_input.strip():
        st.warning("Write or record something first.")
        return

    try:
        with st.spinner("Cleaning your journal entry with Gemini..."):
            result = process_input(user_input)

        clean_content = result["text"]
        model_used = result.get("model_used", "Unknown model")
        today_str = now.strftime("%Y-%m-%d")
        time_now = now.strftime("%H:%M:%S")
        display_ts = now.strftime("%B %d, %Y at %H:%M")

        with st.spinner("Saving the cleaned entry to Notion..."):
            add_entry_to_notion(clean_content, today_str, time_now)

    except Exception as exc:
        st.error(f"Could not save the entry: {exc}")
        return

    st.session_state.clean_content = clean_content
    st.session_state.entry_ts = display_ts
    st.session_state.model_used = model_used
    st.session_state.voice_text = ""
    st.success("Entry saved to Notion.")


def generate_diary():
    try:
        with st.spinner("Collecting today's logs and drafting the diary..."):
            message = generate_or_update_diary()
    except Exception as exc:
        st.error(f"Could not generate the diary: {exc}")
        return

    if message.lower().startswith("no logs"):
        st.info(message)
    else:
        st.success(message)


def render_entry_form(now):
    st.markdown("#### Journal entry")
    st.caption("Write directly, or start from the voice transcription above.")

    with st.form("entry_form", clear_on_submit=False):
        user_input = st.text_area(
            label="Entry",
            value=st.session_state.voice_text,
            height=170,
            placeholder="Capture what happened today in plain language...",
            label_visibility="collapsed",
        )

        col_save, col_generate, col_space = st.columns([1, 1.15, 2.4])
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
        with col_space:
            st.caption("Saved entries feed the daily diary generator.")

    if submit_clicked:
        save_entry(user_input, now)

    if generate_clicked:
        generate_diary()


def render_saved_entry():
    if not st.session_state.clean_content:
        return

    model_name = escape(st.session_state.model_used or "Unknown model")
    st.markdown(
        f"""
        <div class="entry-preview">
            <div class="entry-meta">
                <span>{escape(st.session_state.entry_ts)}</span>
                <span class="model-badge">Model used: {model_name}</span>
            </div>
            <div>{html_text(st.session_state.clean_content)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_today_tab(now):
    st.markdown(
        '<p class="tab-intro">Capture a note, let Gemini clean it, and save the result to Notion.</p>',
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        render_voice_input()

    with st.container(border=True):
        render_entry_form(now)

    render_saved_entry()


def recent_dates(now):
    dates = [now.date() - timedelta(days=days_ago) for days_ago in range(1, RECENT_DAYS + 1)]
    selected = st.session_state.selected_date

    if selected not in dates:
        return [selected, *dates]

    return dates


def render_date_picker(now):
    st.markdown("#### Browse diaries")
    st.caption("Pick any date or jump through recent diary shortcuts.")

    manual_date = st.date_input(
        "Select diary date",
        value=st.session_state.selected_date,
    )

    if manual_date != st.session_state.selected_date:
        st.session_state.selected_date = manual_date
        st.rerun()

    dates = recent_dates(now)
    labels = [date.strftime("%b %d, %Y") for date in dates]
    default_idx = dates.index(st.session_state.selected_date)

    chosen_label = st.radio(
        "Recent entries",
        options=labels,
        index=default_idx,
    )

    chosen_date = dates[labels.index(chosen_label)]
    if chosen_date != st.session_state.selected_date:
        st.session_state.selected_date = chosen_date
        st.rerun()


def render_diary_reader(selected_date):
    display_date = selected_date.strftime("%A, %B %d, %Y")

    st.markdown(f"### {display_date}")

    try:
        diary_content = fetch_diary_by_date(selected_date)
    except Exception as exc:
        st.error(f"Could not load this diary from Notion: {exc}")
        return

    if not diary_content:
        st.info("No diary entry found for this date. Generate a diary first or choose another day.")
        return

    word_count = len(str(diary_content).split())
    st.caption(f"{word_count} words")
    st.markdown(
        f'<div class="diary-reader">{html_text(diary_content)}</div>',
        unsafe_allow_html=True,
    )


def render_past_tab(now):
    st.markdown(
        '<p class="tab-intro">Review generated diary entries stored in the Notion diary database.</p>',
        unsafe_allow_html=True,
    )

    col_left, col_right = st.columns([1, 2.2], gap="large")

    with col_left:
        with st.container(border=True):
            render_date_picker(now)

    with col_right:
        with st.container(border=True):
            render_diary_reader(st.session_state.selected_date)


def main():
    inject_styles()
    now = datetime.now()
    initialise_session_state(now)
    render_header(now)

    tab_today, tab_past = st.tabs(["Today's Entry", "Past Diaries"])

    with tab_today:
        render_today_tab(now)

    with tab_past:
        render_past_tab(now)


if __name__ == "__main__":
    main()
