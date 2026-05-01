import streamlit as st
from streamlit import button
from core.llm import process_input
from datetime import datetime

st.title("AI Personal Assistant")

user_input = st.text_area("What did you do today?")

if st.button("submit"):

    result =  process_input(user_input)
    st.write("diary_entry")
    st.write(datetime.now().strftime("%B %d, %Y -- %H:%M"))
    st.write(result)