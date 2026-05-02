import streamlit as st
from streamlit import button
from core.llm import process_input
from core.notion import add_entry_to_notion
from datetime import datetime
from core.voice import record_audio, transcribe_audio

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

    add_entry_to_notion(clean_content,today,time_now)
    st.success("Content stored in Notion")

    st.session_state.voice_text = ""