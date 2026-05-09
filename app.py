import streamlit as st
from core.llm import process_input
from core.notion import add_entry_to_notion, add_daily_diary
from datetime import datetime, timedelta
from core.voice import record_audio, transcribe_audio
from rag.fetch_data import fetch_todays_entries, fetch_diary_by_date
from rag.combine_logs import combine_logs
from rag.diary_generator import generate_diary

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Personal Journal",
    page_icon="📔",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;0,700;1,400&family=Lora:ital,wght@0,400;0,500;1,400&display=swap');

/* ── Reset & globals ───────────────────────────────────────── */
html, body, [class*="css"]            { font-family: 'Lora', Georgia, serif !important; }
#MainMenu, footer, header             { visibility: hidden !important; }
.block-container {
    max-width: 820px !important;
    padding-top: 2.8rem !important;
    padding-bottom: 3rem !important;
}

/* ── App header ────────────────────────────────────────────── */
.jnl-header {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    margin-bottom: 6px;
}
.jnl-title {
    font-family: 'Playfair Display', serif;
    font-size: 2rem;
    font-weight: 700;
    color: #1a1a1a;
    letter-spacing: -0.01em;
}
.jnl-date {
    font-family: 'Lora', serif;
    font-style: italic;
    font-size: 0.88rem;
    color: #aaa;
}
.jnl-rule {
    height: 1px;
    background: linear-gradient(90deg, #c8bfa8 0%, transparent 100%);
    margin-top: 6px;
    margin-bottom: 1.8rem;
}

/* ── TAB PILL SWITCHER ─────────────────────────────────────── */
/*  Streamlit renders tabs as <button data-baseweb="tab">       */
div[data-baseweb="tab-list"] {
    background-color: #f0ede6 !important;
    border-radius: 12px !important;
    padding: 5px !important;
    gap: 4px !important;
    border-bottom: none !important;
    width: -moz-fit-content !important;
    width: fit-content !important;
}
button[data-baseweb="tab"] {
    background-color: transparent !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Lora', serif !important;
    font-size: 0.88rem !important;
    font-weight: 400 !important;
    color: #999 !important;
    padding: 8px 22px !important;
    transition: all 0.18s ease !important;
    outline: none !important;
    box-shadow: none !important;
}
button[data-baseweb="tab"]:hover {
    color: #555 !important;
    background-color: rgba(255,255,255,0.5) !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    background-color: #ffffff !important;
    color: #1a1a1a !important;
    font-weight: 500 !important;
    box-shadow: 0 1px 6px rgba(0,0,0,0.10) !important;
}
/* Kill Streamlit's default underline indicator */
div[data-baseweb="tab-highlight"],
div[data-baseweb="tab-border"] {
    display: none !important;
    background: transparent !important;
    height: 0 !important;
}

/* ── Mic card ──────────────────────────────────────────────── */
.mic-card {
    display: flex;
    align-items: center;
    gap: 18px;
    background: #faf7f2;
    border: 1px solid #e8e1d0;
    border-radius: 14px;
    padding: 16px 20px;
    margin-top: 14px;
    margin-bottom: 10px;
}
.mic-circle {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    background: linear-gradient(135deg, #c98020 0%, #e8a825 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    font-size: 1.3rem;
    box-shadow: 0 3px 10px rgba(186, 117, 23, 0.28);
}
.mic-label-main { font-size: 0.93rem; font-weight: 500; color: #1a1a1a; margin-bottom: 3px; }
.mic-label-sub  { font-size: 0.78rem; color: #b0a898; font-style: italic; }

/* ── Transcript quote ──────────────────────────────────────── */
.transcript-box {
    background: #fffdf6;
    border-left: 3px solid #c98020;
    border-radius: 0 10px 10px 0;
    padding: 13px 18px;
    font-style: italic;
    font-size: 0.93rem;
    color: #555;
    line-height: 1.8;
    margin: 10px 0 14px;
}

/* ── Soft rule ─────────────────────────────────────────────── */
.soft-rule {
    height: 1px;
    background: linear-gradient(90deg, #e0d8c8 0%, transparent 80%);
    margin: 1.25rem 0;
}

/* ── Textarea ──────────────────────────────────────────────── */
textarea {
    font-family: 'Lora', serif !important;
    font-size: 0.95rem !important;
    line-height: 1.8 !important;
    border-radius: 10px !important;
    border: 1px solid #e3ddd1 !important;
    background: #fafaf7 !important;
    color: #2a2a2a !important;
    caret-color: #c98020 !important;
    padding: 14px 16px !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
textarea:focus {
    border-color: #c98020 !important;
    box-shadow: 0 0 0 3px rgba(201,128,32,0.10) !important;
    background: #ffffff !important;
    outline: none !important;
}
.stTextArea > label {
    font-family: 'Lora', serif !important;
    font-size: 0.73rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.10em !important;
    color: #c0b8a8 !important;
    font-weight: 500 !important;
    font-style: normal !important;
}

/* ── BUTTONS  (use simple descendant  .wrapper button) ─────── */

/* Base reset for all st buttons */
.stButton button,
div[data-testid="stButton"] button {
    font-family: 'Lora', serif !important;
    font-size: 0.88rem !important;
    transition: all 0.18s ease !important;
    cursor: pointer !important;
    letter-spacing: 0.01em !important;
}

/* — Record amber pill — */
.btn-record button {
    background: linear-gradient(135deg, #c98020 0%, #e8a825 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 50px !important;
    padding: 0.6rem 1.8rem !important;
    font-weight: 500 !important;
    box-shadow: 0 3px 12px rgba(186,117,23,0.32) !important;
}
.btn-record button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 5px 18px rgba(186,117,23,0.42) !important;
    background: linear-gradient(135deg, #b37018 0%, #d49820 100%) !important;
}

/* — Save dark pill — */
.btn-save button {
    background: #1c1c1c !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 9px !important;
    padding: 0.6rem 2rem !important;
    font-weight: 500 !important;
}
.btn-save button:hover {
    background: #383838 !important;
    transform: translateY(-1px) !important;
}

/* — Generate outline — */
.btn-gen button {
    background: transparent !important;
    color: #999 !important;
    border: 1px solid #ddd6c8 !important;
    border-radius: 9px !important;
    padding: 0.6rem 1.6rem !important;
}
.btn-gen button:hover {
    border-color: #c98020 !important;
    color: #c98020 !important;
    background: rgba(201,128,32,0.04) !important;
}

/* — Quick-date ghost buttons — */
.btn-date button {
    background: #ffffff !important;
    color: #666 !important;
    border: 1px solid #e8e1d5 !important;
    border-radius: 8px !important;
    padding: 7px 12px !important;
    font-size: 0.82rem !important;
    font-weight: 400 !important;
    width: 100% !important;
    text-align: left !important;
    justify-content: flex-start !important;
}
.btn-date button:hover {
    border-color: #c98020 !important;
    color: #c98020 !important;
    background: #fffdf6 !important;
}

/* ── Entry result card ─────────────────────────────────────── */
.entry-card {
    background: #fffdf6;
    border: 1px solid #e8e1d0;
    border-radius: 13px;
    padding: 22px 24px;
    margin-top: 1.2rem;
}
.entry-card-ts {
    font-size: 0.70rem;
    font-weight: 500;
    letter-spacing: 0.10em;
    text-transform: uppercase;
    color: #c98020;
    margin-bottom: 10px;
    padding-bottom: 10px;
    border-bottom: 1px solid #f0e8d8;
}
.entry-card-body {
    font-size: 0.96rem;
    line-height: 1.88;
    color: #2a2a2a;
}

/* ── Generated diary card ──────────────────────────────────── */
.gen-card {
    background: #fffdf6;
    border: 1px solid #e8e1d0;
    border-radius: 14px;
    padding: 28px 30px;
    margin-top: 1.2rem;
}
.gen-card-label {
    font-size: 0.70rem;
    font-weight: 500;
    letter-spacing: 0.10em;
    text-transform: uppercase;
    color: #c98020;
    margin-bottom: 16px;
    padding-bottom: 14px;
    border-bottom: 1px solid #f0e8d8;
}
.gen-card-body             { font-size: 1rem; line-height: 1.95; color: #2d2d2d; }
.gen-card-body p           { margin-bottom: 1.1rem; }
.gen-card-body p:last-child{ margin-bottom: 0; }

/* ── Past Diaries tab — left column labels ─────────────────── */
.col-label {
    font-size: 0.70rem;
    text-transform: uppercase;
    letter-spacing: 0.10em;
    color: #c0b8a8;
    font-weight: 500;
    margin-bottom: 8px;
}
.recent-label {
    font-size: 0.72rem;
    color: #d0c8b8;
    font-style: italic;
    margin-top: 16px;
    margin-bottom: 8px;
}

/* ── Diary reader card ─────────────────────────────────────── */
.reader-card {
    background: #ffffff;
    border: 1px solid #e3ddd1;
    border-radius: 16px;
    padding: 32px 36px;
    min-height: 300px;
}
.reader-dateline {
    font-family: 'Playfair Display', serif;
    font-size: 1.45rem;
    font-weight: 700;
    color: #1a1a1a;
    margin-bottom: 5px;
    line-height: 1.25;
}
.reader-meta {
    font-size: 0.77rem;
    color: #c0b8a8;
    font-style: italic;
    margin-bottom: 22px;
    padding-bottom: 18px;
    border-bottom: 1px solid #ede8de;
}
.reader-body               { font-size: 0.98rem; line-height: 2.0; color: #2d2d2d; }
.reader-body p             { margin-bottom: 1.15rem; }
.reader-body p:last-child  { margin-bottom: 0; }
.reader-empty {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 220px;
    color: #d0c8b8;
    font-style: italic;
    font-size: 0.92rem;
    text-align: center;
    line-height: 1.9;
}

/* ── Date input ────────────────────────────────────────────── */
.stDateInput > label {
    font-family: 'Lora', serif !important;
    font-size: 0.70rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.10em !important;
    color: #c0b8a8 !important;
    font-weight: 500 !important;
}
input[type="text"][aria-label],
input[data-baseweb="base-input"] {
    font-family: 'Lora', serif !important;
    border-radius: 9px !important;
    border: 1px solid #e3ddd1 !important;
    font-size: 0.88rem !important;
}

/* ── Streamlit alerts ──────────────────────────────────────── */
.stSuccess > div, .stWarning > div, .stError > div {
    border-radius: 10px !important;
    font-family: 'Lora', serif !important;
}

/* ── Spinner text ──────────────────────────────────────────── */
.stSpinner > div { font-family: 'Lora', serif !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
for k, v in [("voice_text", ""), ("clean_content", ""), ("entry_ts", "")]:
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────
now = datetime.now()
fmt_today = now.strftime("%A, %B %d, %Y")

st.markdown(f"""
<div class="jnl-header">
    <div class="jnl-title">📔 AI Personal Journal</div>
    <div class="jnl-date">{fmt_today}</div>
</div>
<div class="jnl-rule"></div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────────────────────
tab_today, tab_past = st.tabs(["✍️  Today's Entry", "📖  Past Diaries"])

# ═════════════════════════════════════════════════════════════════════════════
# TAB 1 — TODAY'S ENTRY
# ═════════════════════════════════════════════════════════════════════════════
with tab_today:

    # ── Mic info card
    st.markdown("""
    <div class="mic-card">
        <div class="mic-circle">🎙️</div>
        <div>
            <div class="mic-label-main">Record a voice note</div>
            <div class="mic-label-sub">30 seconds · transcribed automatically by Whisper AI</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Record button (amber pill)
    st.markdown('<div class="btn-record">', unsafe_allow_html=True)
    record_clicked = st.button("🎙️  Start Recording", key="record")
    st.markdown('</div>', unsafe_allow_html=True)

    if record_clicked:
        with st.spinner("Recording… speak now"):
            record_audio(duration=30)
        with st.spinner("Transcribing…"):
            st.session_state.voice_text = transcribe_audio()
        st.success("Voice captured ✓")

    # ── Transcript quote
    if st.session_state.voice_text:
        st.markdown(
            f'<div class="transcript-box">"{st.session_state.voice_text}"</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="soft-rule"></div>', unsafe_allow_html=True)

    # ── Text area
    user_input = st.text_area(
        "What did you do today?",
        value=st.session_state.voice_text,
        height=150,
        placeholder="Write freely — this is your space…",
        key="textarea_main",
    )

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    # ── Action buttons
    c1, c2, c3 = st.columns([2, 2.4, 4])
    with c1:
        st.markdown('<div class="btn-save">', unsafe_allow_html=True)
        submit_clicked = st.button("Save Entry", key="submit")
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="btn-gen">', unsafe_allow_html=True)
        generate_clicked = st.button("✦  Generate Diary", key="generate")
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Submit logic
    if submit_clicked:
        if not user_input.strip():
            st.warning("Write or record something first.")
        else:
            with st.spinner("Processing…"):
                clean_content = process_input(user_input)

            today_str = now.strftime("%Y-%m-%d")
            time_now  = now.strftime("%H:%M:%S")
            disp_ts   = now.strftime("%B %d, %Y — %H:%M")

            st.session_state.clean_content = clean_content
            st.session_state.entry_ts      = disp_ts

            add_entry_to_notion(clean_content, today_str, time_now)
            st.session_state.voice_text = ""
            st.success("Entry saved to Notion ✓")

    if st.session_state.clean_content:
        st.markdown(f"""
        <div class="entry-card">
            <div class="entry-card-ts">✦  {st.session_state.entry_ts}</div>
            <div class="entry-card-body">{st.session_state.clean_content}</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Generate diary logic
    if generate_clicked:
        with st.spinner("Fetching today's logs…"):
            logs = fetch_todays_entries()

        if not logs:
            st.warning("No entries found for today yet.")
        else:
            with st.spinner("Writing your diary…"):
                combined = combine_logs(logs)
                diary    = generate_diary(combined)

            today_str = now.strftime("%Y-%m-%d")
            response  = add_daily_diary(diary, today_str)

            if response.get("object") == "error":
                st.error("Couldn't save diary to Notion.")
            else:
                st.success("Diary saved to Notion ✓")

            paras      = [p.strip() for p in diary.split("\n") if p.strip()]
            diary_html = "".join(f"<p>{p}</p>" for p in paras)

            st.markdown(f"""
            <div class="gen-card">
                <div class="gen-card-label">✦  Today's Diary — {fmt_today}</div>
                <div class="gen-card-body">{diary_html}</div>
            </div>
            """, unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# TAB 2 — PAST DIARIES
# ═════════════════════════════════════════════════════════════════════════════
with tab_past:

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 2.5])

    with col_left:
        st.markdown('<div class="col-label">Pick a date</div>', unsafe_allow_html=True)
        selected_date = st.date_input(
            "Date",
            value=now.date() - timedelta(days=1),
            label_visibility="collapsed",
            key="date_picker",
        )

        st.markdown('<div class="recent-label">Recent entries</div>', unsafe_allow_html=True)

        for delta in range(1, 6):
            d = now.date() - timedelta(days=delta)
            st.markdown('<div class="btn-date">', unsafe_allow_html=True)
            if st.button(d.strftime("%b %d, %Y"), key=f"quick_{delta}", use_container_width=True):
                selected_date = d
            st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        diary_content = fetch_diary_by_date(selected_date)
        disp_date     = selected_date.strftime("%A, %B %d, %Y")

        if diary_content:
            paras      = [p.strip() for p in str(diary_content).split("\n") if p.strip()]
            diary_html = "".join(f"<p>{p}</p>" for p in paras)
            wc         = len(" ".join(paras).split())

            st.markdown(f"""
            <div class="reader-card">
                <div class="reader-dateline">{disp_date}</div>
                <div class="reader-meta">{wc} words</div>
                <div class="reader-body">{diary_html}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="reader-card">
                <div class="reader-dateline">{disp_date}</div>
                <div class="reader-empty">
                    No diary found for this date.<br>
                    <span style="font-size:0.82rem">Try a different day or generate today's diary first.</span>
                </div>
            </div>
            """, unsafe_allow_html=True)