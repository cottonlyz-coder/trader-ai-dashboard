"""Visual dashboard layout for Colab and a future Streamlit migration."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

from src.indicators import build_return_heatmap_data, normalized_prices
from src.regime import RegimeResult


REGIME_COLORS = {
    "Risk-On": "#087f5b",
    "Risk-Off": "#c92a2a",
    "Neutral / Mixed": "#e67700",
}

DIMENSION_LABELS = {
    "权益动能": "Equity Momentum",
    "波动压力": "Volatility",
    "美元/利率压力": "USD / Rates",
    "中国资产": "China Equity",
}


def _display_value(metrics: pd.DataFrame, asset: str, column: str, suffix: str) -> str:
    """Format a headline metric for a dashboard summary card."""

    if asset not in metrics.index or pd.isna(metrics.loc[asset, column]):
        return "N/A"
    return f"{metrics.loc[asset, column]:+.1f}{suffix}"


def plot_decision_dashboard(
    prices: pd.DataFrame,
    metrics: pd.DataFrame,
    regime: RegimeResult,
    lookback: int = 120,
) -> plt.Figure:
    """Create a single-page market overview figure for notebook display."""

    background = "#f6f8fc"
    text_color = "#172b4d"
    status_color = REGIME_COLORS.get(regime.label, "#e67700")
    figure = plt.figure(figsize=(16, 12), facecolor=background)
    grid = figure.add_gridspec(3, 2, height_ratios=[1.0, 2.6, 2.0], hspace=0.34, wspace=0.20)

    header = figure.add_subplot(grid[0, :])
    header.set_facecolor(background)
    header.axis("off")
    date_value = metrics["Last Date"].max() if "Last Date" in metrics else ""
    header.text(0.0, 0.92, "TRADER AI DECISION DASHBOARD  |  v1.5", fontsize=19, weight="bold", color=text_color)
    header.text(0.0, 0.58, f"Market Regime: {regime.label}", fontsize=25, weight="bold", color=status_color)
    header.text(0.0, 0.29, f"Composite score: {regime.score:+d}    Data through: {date_value}", fontsize=11, color="#526581")

    cards = [
        ("NASDAQ 20D", _display_value(metrics, "Nasdaq 100", "20D Change (%)", "%")),
        ("VIX LEVEL PCTL", _display_value(metrics, "VIX", "1Y Level Percentile", "th")),
        ("USD 20D", _display_value(metrics, "US Dollar Index", "20D Change (%)", "%")),
        ("10Y 20D", _display_value(metrics, "US 10Y Yield", "20D Change (%)", "%")),
    ]
    for number, (label, value) in enumerate(cards):
        x_position = 0.48 + number * 0.13
        header.text(
            x_position,
            0.62,
            value,
            fontsize=18,
            weight="bold",
            color=text_color,
            ha="center",
            bbox={"boxstyle": "round,pad=0.7", "facecolor": "white", "edgecolor": "#dce3ef"},
        )
        header.text(x_position, 0.18, label, fontsize=9, color="#526581", ha="center")

    trend_axis = figure.add_subplot(grid[1, 0])
    rebased = normalized_prices(prices, lookback=lookback)
    for asset in rebased.columns:
        trend_axis.plot(rebased.index, rebased[asset], label=asset, linewidth=1.6)
    trend_axis.axhline(100, color="#adb5bd", linewidth=1, linestyle="--")
    trend_axis.set_title(f"Relative Trend | last {lookback} sessions (start = 100)", loc="left", weight="bold")
    trend_axis.grid(alpha=0.18)
    trend_axis.legend(fontsize=8, frameon=False, ncol=2)
    trend_axis.set_facecolor("white")

    return_axis = figure.add_subplot(grid[1, 1])
    return_table = build_return_heatmap_data(metrics).dropna(how="all")
    heat_values = return_table.fillna(0).to_numpy()
    max_abs = max(float(np.abs(heat_values).max()), 1.0)
    cmap = LinearSegmentedColormap.from_list("risk_returns", ["#d9485f", "#ffffff", "#168f65"])
    return_axis.imshow(heat_values, cmap=cmap, vmin=-max_abs, vmax=max_abs, aspect="auto")
    return_axis.set_xticks(range(len(return_table.columns)), return_table.columns)
    return_axis.set_yticks(range(len(return_table.index)), return_table.index)
    return_axis.set_title("Cross-Asset Returns (%)", loc="left", weight="bold")
    for row in range(len(return_table.index)):
        for column in range(len(return_table.columns)):
            value = return_table.iloc[row, column]
            label = "-" if pd.isna(value) else f"{value:+.1f}"
            return_axis.text(column, row, label, ha="center", va="center", fontsize=9, color=text_color)
    return_axis.set_facecolor("white")

    percentile_axis = figure.add_subplot(grid[2, 0])
    risk_assets = ["VIX", "US Dollar Index", "US 10Y Yield", "Gold"]
    available = [asset for asset in risk_assets if asset in metrics.index]
    percentiles = metrics.loc[available, "1Y Level Percentile"].dropna()
    bars = percentile_axis.barh(percentiles.index, percentiles.values, color="#339af0", alpha=0.85)
    percentile_axis.axvline(75, color="#c92a2a", linestyle="--", linewidth=1, label="Elevated zone")
    percentile_axis.set_xlim(0, 100)
    percentile_axis.set_title("Current Level Percentile | trailing year", loc="left", weight="bold")
    percentile_axis.grid(axis="x", alpha=0.18)
    percentile_axis.legend(fontsize=8, frameon=False, loc="lower right")
    percentile_axis.set_facecolor("white")
    for bar, value in zip(bars, percentiles.values):
        percentile_axis.text(value + 2, bar.get_y() + bar.get_height() / 2, f"{value:.0f}", va="center", fontsize=9)

    score_axis = figure.add_subplot(grid[2, 1])
    scored_dimensions = [item for item in regime.dimensions if item.name != "商品背景"]
    values = [item.score for item in scored_dimensions]
    colors = ["#168f65" if value > 0 else "#d9485f" if value < 0 else "#adb5bd" for value in values]
    score_axis.barh(
        [DIMENSION_LABELS.get(item.name, item.name) for item in scored_dimensions],
        values,
        color=colors,
    )
    score_axis.axvline(0, color="#526581", linewidth=1)
    score_axis.set_xlim(-3, 3)
    score_axis.set_title("Risk Contribution by Dimension", loc="left", weight="bold")
    score_axis.grid(axis="x", alpha=0.18)
    score_axis.set_facecolor("white")

    figure.suptitle("", y=1.0)
    return figure
