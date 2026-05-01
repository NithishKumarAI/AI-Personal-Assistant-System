import streamlit as st
from streamlit import button

st.title("AI Personal Assistant")

user_input = st.text_area("What did you do today?")

if st.button("submit"):
    st.write(user_input)