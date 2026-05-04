import streamlit as st
from streamlit import button
from core.llm import process_input
from core.notion import add_entry_to_notion
from datetime import datetime
from core.voice import record_audio, transcribe_audio
from rag.fetch_data import fetch_todays_entries
from rag.combine_logs import combine_logs
from rag.diary_generator import generate_diary
from core.notion import add_daily_diary

st.title("AI Personal Assistant")

if "voice_text" not in st.session_state:
    st.session_state.voice_text = ""

if st.button("🎤 Record audio for 30 seconds"):
    st.write("recording... speak now...")
    record_audio(duration=30)
    st.write("Transcribing...")
    st.session_state.voice_text = transcribe_audio()
    st.success("Voice captured")

if st.session_state.voice_text:
    st.write("You said...")
    st.write(st.session_state.voice_text)

user_input = st.text_area(
    "What did you do today?",
     value=st.session_state.voice_text
)

if st.button("submit"):

    if not user_input.strip():
        st.warning("Please record or type something.")
    else:
        clean_content = process_input(user_input)

    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    time_now = now.strftime("%H:%M:%S")

    st.write("Diary_entry")
    st.write(datetime.now().strftime("%B %d, %Y -- %H:%M"))
    st.write(clean_content)

    add_entry_to_notion(clean_content, today, time_now)
    st.success("Content stored in Notion")


    st.session_state.voice_text = ""

if st.button("Generate Diary"):
    st.write("Generating Diary...")

    logs = fetch_todays_entries()

    if not logs:
        st.warning("No entries found.")
    else:
        combined = combine_logs(logs)
        diary = generate_diary(combined)
        st.write(diary)
        from datetime import datetime

        today = datetime.now().strftime("%Y-%m-%d")

        response = add_daily_diary(diary, today)

        #st.write("Notion response:", response)

        if response.get("object") == "error":
            st.error("Failed to save diary")
        else:
            st.success("Diary saved successfully")