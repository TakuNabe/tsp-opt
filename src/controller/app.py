"""Streamlit application entry point for tsp-opt."""

import sys
from pathlib import Path

# Ensure the project root is in sys.path so `src.*` imports work
# when invoked via `streamlit run src/controller/app.py`.
_PROJECT_ROOT = str(Path(__file__).resolve().parents[2])
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import streamlit as st

from src.controller.location_page import render_page


def main() -> None:
    """Run the Streamlit application."""
    st.set_page_config(page_title="TSP Optimizer - Location Manager", layout="wide")
    st.title("TSP Optimizer - Location Manager")
    render_page()


if __name__ == "__main__":
    main()
