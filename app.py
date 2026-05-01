import streamlit as st
from streamlit import button
from core.llm import process_input
from core.notion import add_entry_to_notion
from datetime import datetime

st.title("AI Personal Assistant")

user_input = st.text_area("What did you do today?")

if st.button("submit"):

    clean_content =  process_input(user_input)

    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    time_now = now.strftime("%H:%M:%S")

    st.write("Diary_entry")
    st.write(datetime.now().strftime("%B %d, %Y -- %H:%M"))
    st.write(clean_content)
    add_entry_to_notion(clean_content,today,time_now)