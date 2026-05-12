from unittest.mock import patch

from apps.dashboard.app import dashboard_title, render_page
from echomind.dashboard.service import run_demo_inspection


def test_dashboard_title_is_stable() -> None:
    assert dashboard_title() == "EchoMind Dashboard"


def test_run_demo_inspection_builds_dashboard_payload(tmp_path) -> None:
    result = run_demo_inspection(artifact_root=tmp_path / "dashboard")

    assert result.planned_variants
    assert result.rendered_stimulus_manifest.stimuli
    assert result.inference_result.summary.ranked_cue_ids
    assert result.scoring_report.scores
    assert result.experiment_report.grouped_comparisons


def test_render_page_runs_without_streamlit_server() -> None:
    with (
        patch("apps.dashboard.app.st.set_page_config"),
        patch("apps.dashboard.app.st.title"),
        patch("apps.dashboard.app.st.caption"),
        patch("apps.dashboard.app.st.warning"),
        patch("apps.dashboard.app.st.info"),
        patch("apps.dashboard.app.st.text_input", return_value="artifacts/test-dashboard"),
        patch("apps.dashboard.app.st.button", return_value=False),
        patch("apps.dashboard.app.st.spinner"),
        patch("apps.dashboard.app._load_inspection_result", return_value=None),
        patch("apps.dashboard.app.st.error"),
    ):
        render_page()
