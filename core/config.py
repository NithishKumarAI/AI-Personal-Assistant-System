import os

from dotenv import load_dotenv
try:
    import streamlit as st
except Exception:
    st = None

load_dotenv()

def get_secret(key, default=None):
    if st:
        try:
            return st.secrets[key]
        except Exception:
            pass
    return os.getenv(key, default)