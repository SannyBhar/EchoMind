"""Streamlit dashboard shell for EchoMind."""

import streamlit as st

from echomind.memory.service import load_demo_memory


def dashboard_title() -> str:
    """Return dashboard title for smoke tests and page rendering."""

    return "EchoMind Dashboard"


def render_page() -> None:
    """Render a minimal non-clinical landing page."""

    record = load_demo_memory()

    st.set_page_config(page_title=dashboard_title(), layout="wide")
    st.title(dashboard_title())
    st.caption(
        "Research-only interface for simulation-based cue ranking. "
        "This dashboard is non-clinical and does not provide diagnosis or treatment guidance."
    )

    st.subheader("MVP Demo Memory")
    st.write(
        {
            "memory_id": record.memory_id,
            "title": record.title,
            "narrative": record.narrative,
        }
    )


if __name__ == "__main__":
    render_page()
