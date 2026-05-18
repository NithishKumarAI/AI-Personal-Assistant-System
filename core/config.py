"""Configuration for the deployment showcase (Streamlit secrets only)."""

from __future__ import annotations

import streamlit as st

CONFIG_SOURCE = "streamlit_secrets"


def get_secret(key: str, default: str | None = None) -> str | None:
    try:
        value = st.secrets[key]
        if value is None or value == "":
            return default
        return str(value).strip()
    except (KeyError, FileNotFoundError, AttributeError, TypeError):
        return default


def get_required_secret(key: str) -> str:
    value = get_secret(key)
    if not value:
        raise RuntimeError(
            f"Missing required setting '{key}'. Add it in Streamlit Cloud "
            "Secrets or .streamlit/secrets.toml for local demos."
        )
    return value
