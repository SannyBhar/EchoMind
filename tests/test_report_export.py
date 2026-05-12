from pathlib import Path

from scripts.export_report_artifacts import export_report_artifacts


def test_export_report_artifacts_produces_final_figures_and_tables(tmp_path: Path) -> None:
    input_root = Path("artifacts/experiments/multi_memory")
    output_root = tmp_path / "report"

    export_report_artifacts(input_root=input_root, output_root=output_root)

    assert (output_root / "final_figures" / "figure_1_pipeline_overview.png").exists()
    assert (output_root / "final_figures" / "figure_2_grouped_composite_scores.png").exists()
    assert (output_root / "final_figures" / "figure_3_personalized_vs_generic.png").exists()
    assert (output_root / "final_figures" / "figure_4_warm_vs_neutral.png").exists()
    assert (output_root / "final_figures" / "figure_5_delivery_mode_limited.png").exists()

    assert (
        output_root / "final_figures" / "data" / "figure_2_grouped_composite_scores.csv"
    ).exists()
    assert (
        output_root / "final_figures" / "data" / "figure_3_personalized_vs_generic.csv"
    ).exists()
    assert (
        output_root / "final_figures" / "data" / "figure_4_warm_vs_neutral.csv"
    ).exists()
    assert (
        output_root / "final_figures" / "data" / "figure_5_delivery_mode_limited.csv"
    ).exists()

    assert (output_root / "final_tables" / "table_1_representative_ranked_cues.csv").exists()
    assert (output_root / "final_tables" / "table_1_representative_ranked_cues.md").exists()
    assert (output_root / "final_tables" / "table_2_summary_findings.csv").exists()
    assert (output_root / "final_tables" / "table_2_summary_findings.md").exists()

    assert (output_root / "plots" / "dimension_warm_vs_neutral.png").exists()
    assert (output_root / "plots" / "dimension_delivery_mode.png").exists()
    assert (output_root / "plots" / "dimension_personalized_vs_generic.png").exists()
