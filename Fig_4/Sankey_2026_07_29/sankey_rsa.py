#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Draw a publication-ready Sankey diagram for normalized RSA data."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.path import Path as MplPath
from matplotlib.patches import PathPatch, Rectangle


# ---------- Main appearance controls ----------
# Figure dimensions in inches: (width, height)
FIGURE_SIZE = (26, 11)
# Shared font size for period labels, node labels, and legend text
FONT_SIZE = 40


CLASSES = ("A", "B", "C", "D", "E")
CLASS_RANGES = {
    "A": "[0.0, 0.2)",
    "B": "[0.2, 0.4)",
    "C": "[0.4, 0.6)",
    "D": "[0.6, 0.8)",
    "E": "[0.8, 1.0]",
}
COLORS = {
    "A": "#B23A48",
    "B": "#EA7661",
    "C": "#F2C84B",
    "D": "#82AED3",
    "E": "#496FA8",
}


def classify(values: pd.Series) -> pd.Categorical:
    """Assign A–E using left-closed bins; the final bin includes 1.0."""
    numeric = pd.to_numeric(values, errors="raise")
    if numeric.isna().any() or ((numeric < 0) | (numeric > 1)).any():
        raise ValueError("RSA values must be non-missing and within [0, 1].")
    return pd.cut(
        numeric,
        bins=[0, 0.2, 0.4, 0.6, 0.8, 1.0],
        labels=CLASSES,
        include_lowest=True,
        right=False,
    ).where(numeric < 1, "E")


def load_categories(excel_path: Path, sheet_name: str) -> tuple[pd.DataFrame, list[str]]:
    data = pd.read_excel(excel_path, sheet_name=sheet_name)
    periods = [column for column in data.columns if str(column).startswith("Year")]
    if len(periods) < 2:
        raise ValueError("At least two columns named Year... are required.")
    categories = pd.DataFrame(
        {period: classify(data[period]) for period in periods},
        index=data.index,
    )
    return categories, periods


def transition_tables(categories: pd.DataFrame, periods: list[str]) -> list[pd.DataFrame]:
    tables: list[pd.DataFrame] = []
    for left, right in zip(periods[:-1], periods[1:]):
        table = pd.crosstab(categories[left], categories[right], dropna=False)
        tables.append(table.reindex(index=CLASSES, columns=CLASSES, fill_value=0))
    return tables


def _ribbon(
    ax: plt.Axes,
    x0: float,
    x1: float,
    source_bottom: float,
    source_top: float,
    target_bottom: float,
    target_top: float,
    color: str,
) -> None:
    bend = (x1 - x0) * 0.46
    vertices = [
        (x0, source_bottom),
        (x0 + bend, source_bottom),
        (x1 - bend, target_bottom),
        (x1, target_bottom),
        (x1, target_top),
        (x1 - bend, target_top),
        (x0 + bend, source_top),
        (x0, source_top),
        (x0, source_bottom),
    ]
    codes = [
        MplPath.MOVETO,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.LINETO,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CLOSEPOLY,
    ]
    ax.add_patch(
        PathPatch(
            MplPath(vertices, codes),
            facecolor=color,
            edgecolor="none",
            alpha=0.48,
            zorder=1,
        )
    )


def draw_sankey(
    categories: pd.DataFrame,
    periods: list[str],
    tables: list[pd.DataFrame],
    output_stem: Path,
    dpi: int,
) -> None:
    n = len(categories)
    node_width = 0.075
    gap = max(1.7, n * 0.023)
    x_positions = np.arange(len(periods), dtype=float)

    counts = {
        period: categories[period].value_counts().reindex(CLASSES, fill_value=0).astype(int)
        for period in periods
    }
    positions: dict[tuple[str, str], tuple[float, float]] = {}
    for period in periods:
        cursor = 0.0
        for category in CLASSES:
            height = float(counts[period][category])
            positions[(period, category)] = (cursor, cursor + height)
            cursor += height + gap

    source_offsets: dict[tuple[str, str], float] = {}
    target_offsets: dict[tuple[str, str], float] = {}
    for period in periods:
        for category in CLASSES:
            bottom, _ = positions[(period, category)]
            source_offsets[(period, category)] = bottom
            target_offsets[(period, category)] = bottom

    fig, ax = plt.subplots(figsize=FIGURE_SIZE, constrained_layout=True)
    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor("#FFFFFF")

    for step, table in enumerate(tables):
        left, right = periods[step], periods[step + 1]
        for source in CLASSES:
            for target in CLASSES:
                value = int(table.loc[source, target])
                if value == 0:
                    continue
                sb = source_offsets[(left, source)]
                tb = target_offsets[(right, target)]
                _ribbon(
                    ax,
                    x_positions[step] + node_width / 2,
                    x_positions[step + 1] - node_width / 2,
                    sb,
                    sb + value,
                    tb,
                    tb + value,
                    COLORS[source],
                )
                source_offsets[(left, source)] += value
                target_offsets[(right, target)] += value

    for step, period in enumerate(periods):
        for category in CLASSES:
            bottom, top = positions[(period, category)]
            count = int(counts[period][category])
            ax.add_patch(
                Rectangle(
                    (x_positions[step] - node_width / 2, bottom),
                    node_width,
                    top - bottom,
                    facecolor=COLORS[category],
                    edgecolor="none",
                    linewidth=0,
                    zorder=3,
                )
            )
            if count:
                side = -1 if step == 0 else 1
                x_text = x_positions[step] + side * (node_width / 2 + 0.025)
                alignment = "right" if side < 0 else "left"
                ax.text(
                    x_text,
                    (bottom + top) / 2,
                    f"{category}({count})",
                    ha=alignment,
                    va="center",
                    fontsize=FONT_SIZE,
                    color="#263238",
                    fontweight="normal",
                    zorder=4,
                )

    top_limit = max(top for _, top in positions.values())
    for x, period in zip(x_positions, periods):
        label = f"{str(period).replace('Year', '')}s"
        ax.text(
            x,
            top_limit + gap * 1.7,
            label,
            ha="center",
            va="bottom",
            fontsize=FONT_SIZE,
            color="#17212B",
            fontweight="bold",
        )

    legend_handles = [
        Rectangle((0, 0), 1, 1, facecolor=COLORS[c], edgecolor="none", label=f"{c}  {CLASS_RANGES[c]}")
        for c in reversed(CLASSES)
    ]
    legend = ax.legend(
        handles=legend_handles,
        title="Normalized RSA",
        title_fontsize=FONT_SIZE,
        ncol=1,
        loc="center left",
        bbox_to_anchor=(0.985, 0.5),
        borderaxespad=0,
        frameon=False,
        fontsize=FONT_SIZE,
        handlelength=1.35,
        handletextpad=0.55,
        labelspacing=0.9,
    )
    legend.get_title().set_fontweight("normal")
    ax.set_xlim(-0.42, len(periods) - 0.58)
    ax.set_ylim(-gap * 0.6, top_limit + gap * 2.8)
    ax.axis("off")

    output_stem.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_stem.with_suffix(".png"), dpi=dpi, facecolor=fig.get_facecolor())
    fig.savefig(output_stem.with_suffix(".svg"), facecolor=fig.get_facecolor())
    fig.savefig(output_stem.with_suffix(".pdf"), facecolor=fig.get_facecolor())
    plt.close(fig)


def save_transitions(
    tables: list[pd.DataFrame],
    periods: list[str],
    output_path: Path,
) -> None:
    rows = []
    for step, table in enumerate(tables):
        for source in CLASSES:
            for target in CLASSES:
                value = int(table.loc[source, target])
                if value:
                    rows.append(
                        {
                            "source_period": periods[step].replace("Year", ""),
                            "source_class": source,
                            "target_period": periods[step + 1].replace("Year", ""),
                            "target_class": target,
                            "basin_count": value,
                        }
                    )
    pd.DataFrame(rows).to_csv(output_path, index=False, encoding="utf-8-sig")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("Data.xlsx"))
    parser.add_argument("--sheet", default="2For_alluvial")
    parser.add_argument("--output", type=Path, default=Path("rsa_sankey"))
    parser.add_argument("--dpi", type=int, default=400)
    args = parser.parse_args()

    categories, periods = load_categories(args.input, args.sheet)
    tables = transition_tables(categories, periods)
    draw_sankey(categories, periods, tables, args.output, args.dpi)
    save_transitions(tables, periods, args.output.with_name(f"{args.output.name}_transitions.csv"))

    for period, counts in categories.apply(lambda s: s.value_counts()).items():
        if int(counts.sum()) != len(categories):
            raise RuntimeError(f"Count reconciliation failed for {period}.")
    print(f"Created {args.output.with_suffix('.png')}, .svg, .pdf")


if __name__ == "__main__":
    main()
