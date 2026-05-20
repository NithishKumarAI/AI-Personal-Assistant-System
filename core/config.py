"""Configuration helpers supporting both environment variables and Streamlit secrets."""

from __future__ import annotations

import os
import streamlit as st

CONFIG_SOURCE = "environment_or_streamlit_secrets"


def get_secret(key: str, default: str | None = None) -> str | None:
    # First priority: environment variables
    env_value = os.getenv(key)
    if env_value:
        return env_value.strip()

    # Second priority: Streamlit secrets
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
            f"Missing required setting '{key}'. "
            "Add it as an environment variable or Streamlit secret."
        )
    return value