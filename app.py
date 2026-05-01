import streamlit as st
from streamlit import button
from core.llm import process_input

st.title("AI Personal Assistant")

user_input = st.text_area("What did you do today?")

if st.button("submit"):

    result =  process_input(user_input)
    st.write("diary_entry")
    st.write(result)