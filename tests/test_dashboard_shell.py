from unittest.mock import patch

from apps.dashboard.app import dashboard_title, render_page


def test_dashboard_title_is_stable() -> None:
    assert dashboard_title() == "Remembra Dashboard"


def test_render_page_runs_without_streamlit_server() -> None:
    with (
        patch("apps.dashboard.app.st.set_page_config"),
        patch("apps.dashboard.app.st.title"),
        patch("apps.dashboard.app.st.caption"),
        patch("apps.dashboard.app.st.subheader"),
        patch("apps.dashboard.app.st.write"),
    ):
        render_page()
