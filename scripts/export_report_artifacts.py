"""Export publication-ready CS439 report artifacts from a multi-memory run.

Reads `multi_memory_report.json` produced by `run_multi_memory_experiments.py`
and emits:
  - summary.json / dimension_summary.csv / per_memory_scores.csv
  - representative_memory_ranked.csv / representative_memory_meta.json
  - artifacts/report/final_figures/*.png
  - artifacts/report/final_figures/data/*.csv
  - artifacts/report/final_tables/*.{csv,md}

All outputs are deterministic given the frozen `paper.v1.0` config and the
checked-in multi-memory run. Non-clinical research artifacts only.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
from dataclasses import asdict
from pathlib import Path
from statistics import mean, pstdev
from typing import Any

from echomind.experiments.paper_config import PAPER_CONFIG

os.environ.setdefault("MPLBACKEND", "Agg")

import matplotlib.pyplot as plt  # noqa: E402,I001
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402,I001


REPRESENTATIVE_MEMORY_ID = "demo-university-001"
FIGURE_DPI = 300

FINAL_FIGURE_FILENAMES = {
    "pipeline": "figure_1_pipeline_overview.png",
    "grouped": "figure_2_grouped_composite_scores.png",
    "personalized": "figure_3_personalized_vs_generic.png",
    "warm": "figure_4_warm_vs_neutral.png",
    "delivery": "figure_5_delivery_mode_limited.png",
}

FINAL_TABLE_FILENAMES = {
    "representative_csv": "table_1_representative_ranked_cues.csv",
    "representative_md": "table_1_representative_ranked_cues.md",
    "summary_csv": "table_2_summary_findings.csv",
    "summary_md": "table_2_summary_findings.md",
}


def _load_report(input_root: Path) -> dict[str, Any]:
    path = input_root / "aggregate" / "multi_memory_report.json"
    if not path.exists():
        raise FileNotFoundError(
            f"Expected multi-memory report at {path}. "
            "Run scripts/run_multi_memory_experiments.py first."
        )
    return json.loads(path.read_text(encoding="utf-8"))


def _dimension_lookup(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {dim["dimension"]: dim for dim in report["aggregated_comparisons"]}


def _paper_dimension_lookup() -> dict[str, Any]:
    return {dim.key: dim for dim in PAPER_CONFIG.dimensions}


def _group_rows_for_dimension(report: dict[str, Any], dimension: str) -> list[dict[str, Any]]:
    return _dimension_lookup(report)[dimension]["groups"]


def _group_series_by_memory(report: dict[str, Any], dimension: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for memory in report["per_memory_results"]:
        comparison = next(
            (item for item in memory["grouped_comparisons"] if item["dimension"] == dimension),
            None,
        )
        if comparison is None:
            continue

        group_map = {group["group_key"]: group for group in comparison["groups"]}
        row = {
            "memory_id": memory["memory_id"],
            "memory_title": memory["memory_title"],
        }
        for key, group in group_map.items():
            row[key] = group["avg_composite_score"]
        rows.append(row)
    return rows


def _representative_memory(report: dict[str, Any], memory_id: str) -> dict[str, Any]:
    return next(
        (memory for memory in report["per_memory_results"] if memory["memory_id"] == memory_id),
        report["per_memory_results"][0],
    )


def _summary_stat_rows(
    memory_rows: list[dict[str, Any]],
    group_keys: tuple[str, ...],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for key in group_keys:
        values = [float(row[key]) for row in memory_rows if key in row]
        rows.append(
            {
                "group_key": key,
                "mean_avg_composite_score": round(mean(values), 6),
                "std_dev": round(pstdev(values), 6),
                "min_avg_composite_score": round(min(values), 6),
                "max_avg_composite_score": round(max(values), 6),
                "memory_count": len(values),
            }
        )
    return rows


def _configure_matplotlib() -> None:
    plt.rcParams.update(
        {
            "font.size": 10,
            "axes.titlesize": 12,
            "axes.labelsize": 10,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "legend.fontsize": 9,
            "figure.titlesize": 12,
            "axes.edgecolor": "black",
            "axes.linewidth": 0.8,
            "grid.color": "#C7C7C7",
            "grid.linewidth": 0.6,
            "grid.alpha": 0.8,
        }
    )


def _save_figure(fig: plt.Figure, path: Path) -> None:
    fig.savefig(path, dpi=FIGURE_DPI, bbox_inches="tight")
    plt.close(fig)


def _write_summary_json(report: dict[str, Any], output_root: Path) -> None:
    config_blob = {
        "version": PAPER_CONFIG.version,
        "dataset": asdict(PAPER_CONFIG.dataset),
        "cue_families": asdict(PAPER_CONFIG.cue_families),
        "scoring_weights": PAPER_CONFIG.scoring_weights.model_dump(),
        "dimensions": [asdict(d) for d in PAPER_CONFIG.dimensions],
        "inference_engine": PAPER_CONFIG.inference_engine,
        "inference_path": PAPER_CONFIG.inference_path,
        "limitations": list(PAPER_CONFIG.limitations),
        "reproduce_command": PAPER_CONFIG.reproduce_command,
    }
    summary = {
        "paper_config": config_blob,
        "run_id": report["run_id"],
        "memory_count": report["memory_count"],
        "aggregated_comparisons": report["aggregated_comparisons"],
        "created_at": report["created_at"],
    }
    (output_root / "summary.json").write_text(
        json.dumps(summary, indent=2, default=str), encoding="utf-8"
    )


def _write_dimension_csv(report: dict[str, Any], output_root: Path) -> None:
    rows: list[dict[str, Any]] = []
    for dim in report["aggregated_comparisons"]:
        for group in dim["groups"]:
            rows.append(
                {
                    "dimension": dim["dimension"],
                    "group_key": group["group_key"],
                    "memory_count": group["memory_count"],
                    "total_cues": group["total_cues"],
                    "mean_avg_composite_score": group["mean_avg_composite_score"],
                    "max_avg_composite_score": group["max_avg_composite_score"],
                    "min_avg_composite_score": group["min_avg_composite_score"],
                }
            )
    _write_csv(output_root / "dimension_summary.csv", rows)


def _write_per_memory_csv(report: dict[str, Any], output_root: Path) -> None:
    rows: list[dict[str, Any]] = []
    for memory in report["per_memory_results"]:
        for cue in memory["ranked_cues"]:
            rows.append(
                {
                    "memory_id": memory["memory_id"],
                    "memory_title": memory["memory_title"],
                    "cue_id": cue["cue_id"],
                    "delivery_mode": cue["delivery_mode"],
                    "tone": cue["tone"],
                    "personalization_level": cue["personalization_level"],
                    "response_strength": cue["response_strength"],
                    "modality_factor": cue["modality_factor"],
                    "personalization_factor": cue["personalization_factor"],
                    "composite_score": cue["composite_score"],
                    "variant_family": cue["metadata"].get("variant_family"),
                }
            )
    _write_csv(output_root / "per_memory_scores.csv", rows)


def _write_representative_csv(report: dict[str, Any], output_root: Path, memory_id: str) -> None:
    target = _representative_memory(report, memory_id)
    rows = [
        {
            "rank": idx + 1,
            "cue_id": cue["cue_id"],
            "variant_family": cue["metadata"].get("variant_family"),
            "delivery_mode": cue["delivery_mode"],
            "tone": cue["tone"],
            "personalization_level": cue["personalization_level"],
            "response_strength": cue["response_strength"],
            "modality_factor": cue["modality_factor"],
            "personalization_factor": cue["personalization_factor"],
            "composite_score": cue["composite_score"],
        }
        for idx, cue in enumerate(target["ranked_cues"])
    ]
    _write_csv(output_root / "representative_memory_ranked.csv", rows)
    (output_root / "representative_memory_meta.json").write_text(
        json.dumps(
            {"memory_id": target["memory_id"], "memory_title": target["memory_title"]},
            indent=2,
        ),
        encoding="utf-8",
    )


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as file_handle:
        writer = csv.DictWriter(file_handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _write_markdown_table(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return

    headers = list(rows[0].keys())
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row[header]) for header in headers) + " |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _format_bar_label(value: float) -> str:
    return f"{value:.3f}"


def _figure_1_pipeline_overview(output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(11, 2.8))
    ax.axis("off")

    steps = [
        ("Planner", "Cue families\n(6 deterministic variants)"),
        ("Renderer", "Text/audio/video\nartifacts + manifest"),
        ("TRIBE Smoke", "Text-first preprocess\n+ stub inference"),
        ("Scoring", "response_strength\n+ heuristic factors"),
        ("Reporting", "Grouped comparisons\n+ tables/figures"),
    ]

    x_positions = [0.04, 0.24, 0.44, 0.64, 0.84]
    box_width = 0.13
    box_height = 0.42
    y = 0.34

    for idx, ((title, body), x) in enumerate(zip(steps, x_positions, strict=True)):
        box = FancyBboxPatch(
            (x, y),
            box_width,
            box_height,
            boxstyle="round,pad=0.015,rounding_size=0.02",
            linewidth=1.0,
            edgecolor="black",
            facecolor=("#F4F4F4" if idx % 2 == 0 else "#E2E2E2"),
            transform=ax.transAxes,
        )
        ax.add_patch(box)
        ax.text(
            x + box_width / 2,
            y + box_height * 0.67,
            title,
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=11,
            fontweight="bold",
        )
        ax.text(
            x + box_width / 2,
            y + box_height * 0.32,
            body,
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=9,
        )
        if idx < len(steps) - 1:
            arrow = FancyArrowPatch(
                (x + box_width + 0.015, y + box_height / 2),
                (x_positions[idx + 1] - 0.015, y + box_height / 2),
                arrowstyle="-|>",
                mutation_scale=12,
                linewidth=1.0,
                color="black",
                transform=ax.transAxes,
            )
            ax.add_patch(arrow)

    ax.set_title("EchoMind publication pipeline", pad=12)
    fig.text(
        0.5,
        0.07,
        "Non-clinical, simulation-only slice. Current inference path is text-first: "
        "only TEXT_ONLY cues traverse the TRIBE stub.",
        ha="center",
        fontsize=9,
    )
    _save_figure(fig, output_path)


def _figure_2_grouped_composite_scores(
    report: dict[str, Any],
    output_path: Path,
    csv_path: Path,
) -> None:
    paper_dims = _paper_dimension_lookup()
    dimension_order = [
        "personalized_vs_generic",
        "warm_vs_neutral",
        "delivery_mode",
    ]
    groups_by_dim = {
        key: _group_rows_for_dimension(report, key)
        for key in dimension_order
    }

    rows: list[dict[str, Any]] = []
    bar_positions: list[float] = []
    bar_values: list[float] = []
    bar_labels: list[str] = []
    bar_hatches: list[str] = []
    centers: list[float] = []
    x_cursor = 0.0

    hatch_map = {
        "generic": "",
        "personalized": "//",
        "neutral": "",
        "warm": "//",
        "text_only": "",
        "narration": "//",
        "slideshow_narration": "xx",
    }

    for dim_key in dimension_order:
        dim_groups = groups_by_dim[dim_key]
        current_positions: list[float] = []
        for idx, group in enumerate(dim_groups):
            pos = x_cursor + idx
            current_positions.append(pos)
            bar_positions.append(pos)
            bar_values.append(group["mean_avg_composite_score"])
            bar_labels.append(group["group_key"])
            bar_hatches.append(hatch_map.get(group["group_key"], ""))
            rows.append(
                {
                    "dimension": dim_key,
                    "group_key": group["group_key"],
                    "confidence": paper_dims[dim_key].confidence,
                    "mean_avg_composite_score": group["mean_avg_composite_score"],
                    "min_avg_composite_score": group["min_avg_composite_score"],
                    "max_avg_composite_score": group["max_avg_composite_score"],
                    "memory_count": group["memory_count"],
                    "total_cues": group["total_cues"],
                }
            )
        centers.append(sum(current_positions) / len(current_positions))
        x_cursor = current_positions[-1] + 1.8

    _write_csv(csv_path, rows)

    fig, ax = plt.subplots(figsize=(10.8, 4.8))
    bars = ax.bar(
        bar_positions,
        bar_values,
        width=0.75,
        color="#D9D9D9",
        edgecolor="black",
        linewidth=0.9,
    )
    for bar, hatch, value in zip(bars, bar_hatches, bar_values, strict=True):
        bar.set_hatch(hatch)
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + 0.01,
            _format_bar_label(value),
            ha="center",
            va="bottom",
            fontsize=8,
        )

    ax.set_ylabel("Mean per-memory composite score")
    ax.set_xticks(bar_positions)
    ax.set_xticklabels(bar_labels)
    ax.set_ylim(0, max(bar_values) * 1.25)
    ax.yaxis.grid(True)
    ax.set_axisbelow(True)
    ax.set_title("Grouped average composite score by comparison dimension")

    for center, dim_key in zip(centers, dimension_order, strict=True):
        label = dim_key.replace("_", " ") + f"\n[{paper_dims[dim_key].confidence}]"
        ax.text(center, -0.17, label, transform=ax.get_xaxis_transform(), ha="center", fontsize=9)

    for left, right in zip(centers, centers[1:], strict=True):
        separator = (left + right) / 2
        ax.axvline(separator, color="#B0B0B0", linewidth=0.8, ymin=0.02, ymax=0.95)

    fig.text(
        0.5,
        0.01,
        "Mean values come from the frozen synthetic 12-memory run. "
        "Delivery-mode bars should be interpreted with caution: only TEXT_ONLY "
        "reaches the TRIBE stub.",
        ha="center",
        fontsize=8.5,
    )
    _save_figure(fig, output_path)


def _figure_3_personalized_vs_generic(
    report: dict[str, Any],
    output_path: Path,
    csv_path: Path,
) -> None:
    rows = _group_series_by_memory(report, "personalized_vs_generic")
    rows = sorted(
        rows,
        key=lambda row: float(row["generic"]) - float(row["personalized"]),
        reverse=True,
    )
    export_rows = [
        {
            "memory_id": row["memory_id"],
            "memory_title": row["memory_title"],
            "generic_avg_composite_score": round(float(row["generic"]), 6),
            "personalized_avg_composite_score": round(float(row["personalized"]), 6),
            "difference_generic_minus_personalized": round(
                float(row["generic"]) - float(row["personalized"]), 6
            ),
        }
        for row in rows
    ]
    _write_csv(csv_path, export_rows)

    fig, ax = plt.subplots(figsize=(10.8, 5.6))
    y_positions = list(range(len(rows)))

    generic_vals = [float(row["generic"]) for row in rows]
    personalized_vals = [float(row["personalized"]) for row in rows]

    for y_pos, generic, personalized in zip(
        y_positions, generic_vals, personalized_vals, strict=True
    ):
        ax.plot([personalized, generic], [y_pos, y_pos], color="#8A8A8A", linewidth=1.0)

    ax.scatter(personalized_vals, y_positions, color="white", edgecolors="black", s=34, zorder=3)
    ax.scatter(generic_vals, y_positions, color="black", s=34, zorder=3)

    ax.set_yticks(y_positions)
    ax.set_yticklabels([row["memory_id"].replace("demo-", "") for row in rows])
    ax.set_xlabel("Average composite score")
    ax.set_title("Per-memory personalized vs generic comparison")
    ax.yaxis.grid(False)
    ax.xaxis.grid(True)
    ax.set_axisbelow(True)
    ax.invert_yaxis()

    legend_handles = [
        plt.Line2D(
            [0],
            [0],
            marker="o",
            color="black",
            linestyle="",
            markersize=6,
            label="generic",
        ),
        plt.Line2D(
            [0],
            [0],
            marker="o",
            markerfacecolor="white",
            markeredgecolor="black",
            linestyle="",
            markersize=6,
            label="personalized",
        ),
    ]
    ax.legend(handles=legend_handles, loc="lower right", frameon=False)

    fig.text(
        0.5,
        0.01,
        "Exploratory view. Higher generic scores in this stub-backed run reflect "
        "text-hash variance in the deterministic TRIBE placeholder, not evidence "
        "that generic cues support recall better.",
        ha="center",
        fontsize=8.5,
    )
    _save_figure(fig, output_path)


def _figure_4_warm_vs_neutral(
    report: dict[str, Any],
    output_path: Path,
    csv_path: Path,
) -> None:
    rows = _group_series_by_memory(report, "warm_vs_neutral")
    stat_rows = _summary_stat_rows(rows, ("neutral", "warm"))
    _write_csv(csv_path, stat_rows)

    means = [row["mean_avg_composite_score"] for row in stat_rows]
    stds = [row["std_dev"] for row in stat_rows]
    labels = [row["group_key"] for row in stat_rows]

    fig, ax = plt.subplots(figsize=(6.2, 4.4))
    bars = ax.bar(
        labels,
        means,
        yerr=stds,
        capsize=5,
        color=["#EFEFEF", "#C8C8C8"],
        edgecolor="black",
        linewidth=0.9,
    )
    bars[1].set_hatch("//")

    for bar, value in zip(bars, means, strict=True):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + max(stds) * 0.25 + 0.005,
            _format_bar_label(value),
            ha="center",
            va="bottom",
            fontsize=9,
        )

    ax.set_ylabel("Mean per-memory composite score")
    ax.set_title("Warm vs neutral framing")
    ax.yaxis.grid(True)
    ax.set_axisbelow(True)

    fig.text(
        0.5,
        0.03,
        "Error bars show ±1 SD across per-memory averages. "
        "This is the cleanest current contrast because both groups traverse the "
        "same text-first stub path.",
        ha="center",
        fontsize=8.5,
    )
    _save_figure(fig, output_path)


def _figure_5_delivery_mode(
    report: dict[str, Any],
    output_path: Path,
    csv_path: Path,
) -> None:
    rows = _group_series_by_memory(report, "delivery_mode")
    stat_rows = _summary_stat_rows(rows, ("text_only", "narration", "slideshow_narration"))
    _write_csv(csv_path, stat_rows)

    means = [row["mean_avg_composite_score"] for row in stat_rows]
    stds = [row["std_dev"] for row in stat_rows]
    labels = [row["group_key"] for row in stat_rows]

    fig, ax = plt.subplots(figsize=(7.0, 4.6))
    bars = ax.bar(
        labels,
        means,
        yerr=stds,
        capsize=5,
        color=["#BDBDBD", "#EFEFEF", "#FFFFFF"],
        edgecolor="black",
        linewidth=0.9,
    )
    bars[1].set_hatch("//")
    bars[2].set_hatch("xx")

    for bar, value in zip(bars, means, strict=True):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + 0.01,
            _format_bar_label(value),
            ha="center",
            va="bottom",
            fontsize=9,
        )

    ax.set_ylabel("Mean per-memory composite score")
    ax.set_title("Delivery mode comparison [limited]")
    ax.yaxis.grid(True)
    ax.set_axisbelow(True)

    fig.text(
        0.5,
        0.02,
        "Limited interpretation: only TEXT_ONLY cues traverse the current TRIBE stub. "
        "Narration and slideshow values are heuristic-only constants under the "
        "text-first smoke path.",
        ha="center",
        fontsize=8.5,
    )
    _save_figure(fig, output_path)


def _write_representative_table_artifacts(
    report: dict[str, Any],
    table_dir: Path,
) -> None:
    target = _representative_memory(report, REPRESENTATIVE_MEMORY_ID)
    rows = [
        {
            "rank": idx + 1,
            "cue_family": cue["metadata"].get("variant_family"),
            "response_strength": round(float(cue["response_strength"]), 6),
            "modality_factor": round(float(cue["modality_factor"]), 6),
            "personalization_factor": round(float(cue["personalization_factor"]), 6),
            "composite_score": round(float(cue["composite_score"]), 6),
        }
        for idx, cue in enumerate(target["ranked_cues"])
    ]

    _write_csv(table_dir / FINAL_TABLE_FILENAMES["representative_csv"], rows)
    _write_markdown_table(table_dir / FINAL_TABLE_FILENAMES["representative_md"], rows)


def _summary_finding_rows(report: dict[str, Any]) -> list[dict[str, Any]]:
    dim_lookup = _paper_dimension_lookup()
    agg_lookup = _dimension_lookup(report)

    warm = {row["group_key"]: row for row in agg_lookup["warm_vs_neutral"]["groups"]}
    personalized = {
        row["group_key"]: row for row in agg_lookup["personalized_vs_generic"]["groups"]
    }
    delivery = {row["group_key"]: row for row in agg_lookup["delivery_mode"]["groups"]}

    warm_gap = (
        warm["warm"]["mean_avg_composite_score"]
        - warm["neutral"]["mean_avg_composite_score"]
    )
    personalized_gap = (
        personalized["generic"]["mean_avg_composite_score"]
        - personalized["personalized"]["mean_avg_composite_score"]
    )

    return [
        {
            "comparison_dimension": "warm_vs_neutral",
            "interpretation_label": (
                f"Warm framing is slightly higher than neutral (+{warm_gap:.3f} mean composite)"
            ),
            "confidence": dim_lookup["warm_vs_neutral"].confidence,
            "limitation_note": dim_lookup["warm_vs_neutral"].caveat,
        },
        {
            "comparison_dimension": "personalized_vs_generic",
            "interpretation_label": (
                "Generic cues score higher in the frozen run; treat as a stub-text artifact "
                f"(generic - personalized = +{personalized_gap:.3f})"
            ),
            "confidence": dim_lookup["personalized_vs_generic"].confidence,
            "limitation_note": dim_lookup["personalized_vs_generic"].caveat,
        },
        {
            "comparison_dimension": "delivery_mode",
            "interpretation_label": (
                "TEXT_ONLY is highest because it is the only delivery mode that "
                "reaches the TRIBE stub "
                f"(text_only mean = {delivery['text_only']['mean_avg_composite_score']:.3f})"
            ),
            "confidence": dim_lookup["delivery_mode"].confidence,
            "limitation_note": dim_lookup["delivery_mode"].caveat,
        },
    ]


def _write_summary_table_artifacts(report: dict[str, Any], table_dir: Path) -> None:
    rows = _summary_finding_rows(report)
    _write_csv(table_dir / FINAL_TABLE_FILENAMES["summary_csv"], rows)
    _write_markdown_table(table_dir / FINAL_TABLE_FILENAMES["summary_md"], rows)


def _export_legacy_plots(report: dict[str, Any], output_root: Path) -> None:
    """Keep legacy paths populated for existing docs and downstream references."""

    plot_dir = output_root / "plots"
    plot_dir.mkdir(parents=True, exist_ok=True)
    data_dir = output_root / "legacy_plot_data"
    data_dir.mkdir(parents=True, exist_ok=True)

    _figure_4_warm_vs_neutral(
        report,
        plot_dir / "dimension_warm_vs_neutral.png",
        data_dir / "dimension_warm_vs_neutral.csv",
    )
    _figure_5_delivery_mode(
        report,
        plot_dir / "dimension_delivery_mode.png",
        data_dir / "dimension_delivery_mode.csv",
    )
    _figure_3_personalized_vs_generic(
        report,
        plot_dir / "per_memory_personalized_vs_generic.png",
        data_dir / "per_memory_personalized_vs_generic.csv",
    )

    personalized_rows = _group_rows_for_dimension(report, "personalized_vs_generic")
    fig, ax = plt.subplots(figsize=(5.8, 4.0))
    labels = [row["group_key"] for row in personalized_rows]
    values = [row["mean_avg_composite_score"] for row in personalized_rows]
    bars = ax.bar(labels, values, color=["#2F2F2F", "#D9D9D9"], edgecolor="black")
    bars[1].set_hatch("//")
    for bar, value in zip(bars, values, strict=True):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + 0.01,
            _format_bar_label(value),
            ha="center",
            va="bottom",
            fontsize=9,
        )
    ax.set_title("Personalized vs generic [exploratory]")
    ax.set_ylabel("Mean per-memory composite score")
    ax.yaxis.grid(True)
    ax.set_axisbelow(True)
    fig.text(
        0.5,
        0.02,
        "Exploratory: generic > personalized here reflects the deterministic stub text path.",
        ha="center",
        fontsize=8.5,
    )
    _save_figure(fig, plot_dir / "dimension_personalized_vs_generic.png")

    target = _representative_memory(report, REPRESENTATIVE_MEMORY_ID)
    families = [
        cue["metadata"].get("variant_family", cue["cue_id"]) for cue in target["ranked_cues"]
    ]
    scores = [float(cue["composite_score"]) for cue in target["ranked_cues"]]

    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    bars = ax.barh(families[::-1], scores[::-1], color="#D9D9D9", edgecolor="black")
    for bar, value in zip(bars, scores[::-1], strict=True):
        ax.text(
            bar.get_width() + 0.005,
            bar.get_y() + bar.get_height() / 2,
            f"{value:.3f}",
            va="center",
            fontsize=8,
        )
    ax.set_xlabel("Composite score")
    ax.set_title(f"Ranked cues for {target['memory_id']}")
    _save_figure(fig, plot_dir / "representative_memory_ranked.png")


def export_report_artifacts(input_root: Path, output_root: Path) -> None:
    _configure_matplotlib()
    output_root.mkdir(parents=True, exist_ok=True)

    report = _load_report(input_root)

    _write_summary_json(report, output_root)
    _write_dimension_csv(report, output_root)
    _write_per_memory_csv(report, output_root)
    _write_representative_csv(report, output_root, REPRESENTATIVE_MEMORY_ID)

    final_figure_dir = output_root / "final_figures"
    final_figure_data_dir = final_figure_dir / "data"
    final_table_dir = output_root / "final_tables"
    final_figure_dir.mkdir(parents=True, exist_ok=True)
    final_figure_data_dir.mkdir(parents=True, exist_ok=True)
    final_table_dir.mkdir(parents=True, exist_ok=True)

    _figure_1_pipeline_overview(final_figure_dir / FINAL_FIGURE_FILENAMES["pipeline"])
    _figure_2_grouped_composite_scores(
        report,
        final_figure_dir / FINAL_FIGURE_FILENAMES["grouped"],
        final_figure_data_dir / "figure_2_grouped_composite_scores.csv",
    )
    _figure_3_personalized_vs_generic(
        report,
        final_figure_dir / FINAL_FIGURE_FILENAMES["personalized"],
        final_figure_data_dir / "figure_3_personalized_vs_generic.csv",
    )
    _figure_4_warm_vs_neutral(
        report,
        final_figure_dir / FINAL_FIGURE_FILENAMES["warm"],
        final_figure_data_dir / "figure_4_warm_vs_neutral.csv",
    )
    _figure_5_delivery_mode(
        report,
        final_figure_dir / FINAL_FIGURE_FILENAMES["delivery"],
        final_figure_data_dir / "figure_5_delivery_mode_limited.csv",
    )

    _write_representative_table_artifacts(report, final_table_dir)
    _write_summary_table_artifacts(report, final_table_dir)
    _export_legacy_plots(report, output_root)


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Export CS439 report-ready artifacts from a multi-memory run."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("artifacts/experiments/multi_memory"),
        help="Root directory produced by run_multi_memory_experiments.py.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/report"),
        help="Directory where report artifacts will be written.",
    )
    return parser


def main() -> None:
    args = _build_arg_parser().parse_args()
    export_report_artifacts(args.input, args.output)
    print(f"Wrote report artifacts to {args.output}")


if __name__ == "__main__":
    main()
