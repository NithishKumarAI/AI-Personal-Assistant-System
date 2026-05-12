import streamlit as st
from core.llm import process_input            # Cleans/formats raw user input using the LLM
from core.notion import add_entry_to_notion  # Saves data to Notion database
from datetime import datetime, timedelta      # For working with dates and time
from core.voice import record_audio, transcribe_audio         # Records mic and converts speech to text via Whisper
from rag.fetch_data import fetch_diary_by_date  # Pulls entries from Notion

st.set_page_config(
    page_title="AI Personal Journal",
    page_icon="📔",
    layout="centered",           # Keeps content in a readable centre column
    initial_sidebar_state="collapsed",
)

# ── Session state initialisation ──────────────────────────────────────────────
# st.session_state persists values across reruns (Streamlit reruns the whole
# script on every user interaction, so without this, values would reset each time).
#
# We initialise only if the key doesn't exist yet — this prevents resetting
# values that the user has already set in the current session.
for k, v in [
    ("voice_text",    ""),    # Holds the Whisper transcription after recording
    ("clean_content", ""),    # Holds the LLM-processed entry after Submit
    ("entry_ts",      ""),    # Holds the timestamp string shown with the saved entry
    ("model_used", ""),
    ("selected_date", None),  # Holds the date selected in the Past Diaries tab
]:
    if k not in st.session_state:
        st.session_state[k] = v

# Grab the current date and time once — used throughout the file
now = datetime.now()

# Default the selected date to yesterday if it hasn't been set yet
if st.session_state.selected_date is None:
    st.session_state.selected_date = now.date() - timedelta(days=1)


# ── Header ────────────────────────────────────────────────────────────────────
# Two columns: title on the left, today's date on the right
col_title, col_date = st.columns([3, 1])
with col_title:
    st.title("📔 AI Personal Journal")
with col_date:
    # st.caption renders small grey text — used here for the date
    st.caption(now.strftime("%A, %B %d, %Y"))

st.divider()  # Horizontal rule between header and tabs


# ── Tabs ──────────────────────────────────────────────────────────────────────
# Two tabs: one for writing today's entry, one for reading past diaries.
# Streamlit returns a tab object for each — content goes inside a `with` block.
tab_today, tab_past = st.tabs(["✍️ Today's Entry", "📖 Past Diaries"])


# ═════════════════════════════════════════════════════════════════════════════
# TAB 1 — TODAY'S ENTRY
# Lets the user record audio OR type text, then save it to Notion.
# Also has a "Generate Diary" button that compiles all of today's logs
# into a single diary entry using the LLM.
# ═════════════════════════════════════════════════════════════════════════════
with tab_today:

    # ── Section: Voice recording ──────────────────────────────────────────────
    st.subheader("🎙️ Voice Input")

    # Info box explains to the user what the record button does
    st.info("**Record a voice note** — 30 seconds · transcribed by Whisper AI")

    # Record button — triggers audio capture then Whisper transcription.
    # The result is stored in session_state so it survives the next rerun.
    if st.button("🎙️ Start Recording", key="record"):
        with st.spinner("Recording… speak now"):
            record_audio(duration=30)          # Captures 30 seconds of mic audio
        with st.spinner("Transcribing…"):
            st.session_state.voice_text = transcribe_audio()  # Whisper converts audio → text
        st.success("Voice captured ✓")

    # If there is a transcription, show it so the user can review before submitting
    if st.session_state.voice_text:
        st.caption("You said:")
        st.write(f"*{st.session_state.voice_text}*")  # Italic via markdown asterisks

    st.divider()

    # ── Section: Text entry ───────────────────────────────────────────────────
    st.subheader("📝 What did you do today?")
    # Text area pre-filled with the voice transcription (if any).
    # The user can edit it before saving.
    user_input = st.text_area(
        label="Entry",
        value=st.session_state.voice_text,
        height=160,
        placeholder="Write freely or speak — this is your space…",
        label_visibility="collapsed",
    )
    # ── Action buttons ────────────────────────────────────────────────────────
    # Two buttons side by side using columns.
    # col3 is an empty spacer column so buttons don't stretch full width.
    with st.form("entry_form"):

        col1, col2, col3 = st.columns([1, 1.4, 3])

        with col1:
            submit_clicked = st.form_submit_button(
                "💾 Save Entry",
                type="primary"
            )

        with col2:
            generate_clicked = st.form_submit_button(
                "✦ Generate Diary"
            )

    # ── Save Entry logic ──────────────────────────────────────────────────────
    if submit_clicked:
        if not user_input.strip():
            # .strip() removes whitespace — warns if the text box is empty
            st.warning("Write or record something first.")
        else:
            with st.spinner("Processing…"):

                result = process_input(user_input)

                clean_content = result["text"]

                model_used = result["model_used"]

            # Format date and time strings for Notion and the display timestamp
            today_str = now.strftime("%Y-%m-%d")       # e.g. "2026-05-10"
            time_now  = now.strftime("%H:%M:%S")       # e.g. "14:32:01"
            disp_ts   = now.strftime("%B %d, %Y — %H:%M")  # e.g. "May 10, 2026 — 14:32"

            # Store the processed content and timestamp in session state
            # so they persist after Streamlit reruns on the next interaction
            st.session_state.clean_content = clean_content
            st.session_state.entry_ts      = disp_ts
            st.session_state.model_used = model_used
            # Save the entry to Notion — this calls the Notion API
            add_entry_to_notion(clean_content, today_str, time_now)

            # Clear voice text so the textarea doesn't re-populate on next rerun
            st.session_state.voice_text = ""
            st.success("Entry saved to Notion ✓")

    # Show the saved entry below the buttons if one exists in session state
    if st.session_state.clean_content:
        st.divider()
        st.caption(f"✦ {st.session_state.entry_ts}")   # Small timestamp above the entry
        st.caption(f"⚡ Model Used: {st.session_state.model_used}")
        st.write(st.session_state.clean_content)        # The LLM-processed entry text

    # ── Generate Diary logic ──────────────────────────────────────────────────
    # Fetches ALL of today's saved log entries from Notion,
    # combines them into one block, then asks the LLM to write a diary from them.
    from core.diary_service import generate_or_update_diary

    if generate_clicked:

        with st.spinner("Generating diary..."):

            message = generate_or_update_diary()

        st.success(message)


# ═════════════════════════════════════════════════════════════════════════════
# TAB 2 — PAST DIARIES
# Lets the user pick a date and read the diary saved for that day.
# Two columns: left = date selector, right = diary reader.
# ═════════════════════════════════════════════════════════════════════════════
with tab_past:

    col_left, col_right = st.columns([1, 2.5])

    # ── Left column: Date selection ───────────────────────────────────────────
    with col_left:
        st.subheader("📅 Pick a date")

        # Calendar date picker — user can pick any date
        manual_date = st.date_input(
            "Date",
            value=st.session_state.selected_date,
            label_visibility="collapsed",
            key="date_picker",
        )

        # If the user changed the calendar date, update session state and rerun
        # so the right column immediately shows the new date's diary
        if manual_date != st.session_state.selected_date:
            st.session_state.selected_date = manual_date
            st.rerun()

        st.caption("Recent entries")

        # Build a list of the last 5 days for the quick-select radio buttons
        recent_dates  = [now.date() - timedelta(days=i) for i in range(1, 6)]
        recent_labels = [d.strftime("%b %d, %Y") for d in recent_dates]

        # Find which recent date is currently selected so the radio
        # starts on the right option. If the selected date is older than
        # 5 days (i.e. not in recent_dates), default to the first option.
        try:
            default_idx = recent_dates.index(st.session_state.selected_date)
        except ValueError:
            default_idx = 0

        # Radio widget styled as a compact list of recent dates.
        # No custom CSS needed — Streamlit's native radio is clean enough.
        chosen_label = st.radio(
            "recent",
            options=recent_labels,
            index=default_idx,
            label_visibility="collapsed",  # Label hidden; st.caption above explains it
            key="recent_radio",
        )

        # Convert the chosen label back to a date object and sync to session state
        chosen_date = recent_dates[recent_labels.index(chosen_label)]
        if chosen_date != st.session_state.selected_date:
            st.session_state.selected_date = chosen_date
            st.rerun()  # Force a rerun so the right column updates immediately

    # ── Right column: Diary reader ────────────────────────────────────────────
    with col_right:
        selected = st.session_state.selected_date

        # Fetch the diary for the selected date from Notion
        diary_content = fetch_diary_by_date(selected)

        # Display the date as the section header
        disp_date = selected.strftime("%A, %B %d, %Y")
        st.subheader(f"📖 {disp_date}")
        st.divider()

        if diary_content:
            # Show word count as a small caption above the diary text
            wc = len(str(diary_content).split())
            st.caption(f"{wc} words")

            # Render the diary — st.write handles plain text and markdown
            st.write(diary_content)
        else:
            # Friendly message if no diary was saved for this date
            st.info("No diary entry found for this date. Try a different day or generate today's diary first.")