"""Calculate market indicators for the Trader AI Dashboard.

v1 focused on recent returns and volatility. v1.5 keeps those metrics and
adds trend and percentile context so today's readings are easier to judge.
"""

from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd


RANKED_ASSETS = (
    "China A50 / Proxy",
    "Nasdaq 100",
    "Gold",
    "Crude Oil",
    "US Dollar Index",
)


def _period_change(series: pd.Series, trading_days: int) -> float:
    """Return percentage price change over a trading-day lookback."""

    series = series.dropna()
    if len(series) <= trading_days:
        return np.nan
    return (series.iloc[-1] / series.iloc[-(trading_days + 1)] - 1) * 100


def _percentile_rank(history: pd.Series) -> float:
    """Return where the most recent observation ranks within its history."""

    history = history.dropna()
    if len(history) < 20:
        return np.nan
    return float((history <= history.iloc[-1]).mean() * 100)


def _rolling_volatility(series: pd.Series, window: int = 20) -> pd.Series:
    """Calculate rolling annualised volatility from daily returns."""

    daily_returns = series.pct_change()
    return daily_returns.rolling(window).std() * np.sqrt(252) * 100


def calculate_market_metrics(prices: pd.DataFrame) -> pd.DataFrame:
    """Build the v1.5 metric table from daily close price series.

    Percentage ranks compare the current reading with the trailing 252 trading
    days (about one year). A high VIX level percentile, for example, signals
    an unusually elevated fear gauge even when its latest daily move is small.
    """

    rows = []
    for asset in prices.columns:
        series = prices[asset].dropna()
        if series.empty:
            continue

        volatility_history = _rolling_volatility(series).dropna()
        current_volatility = (
            float(volatility_history.iloc[-1])
            if not volatility_history.empty
            else np.nan
        )
        trend_average = series.tail(50).mean() if len(series) >= 20 else np.nan
        trend = (
            (series.iloc[-1] / trend_average - 1) * 100
            if not pd.isna(trend_average)
            else np.nan
        )

        rows.append(
            {
                "Asset": asset,
                "Latest Price": series.iloc[-1],
                "1D Change (%)": _period_change(series, 1),
                "5D Change (%)": _period_change(series, 5),
                "20D Change (%)": _period_change(series, 20),
                "50D Trend (%)": trend,
                "20D Volatility (%)": current_volatility,
                "1Y Level Percentile": _percentile_rank(series.tail(252)),
                "1Y Volatility Percentile": _percentile_rank(
                    volatility_history.tail(252)
                ),
                "Last Date": series.index[-1].date(),
            }
        )

    if not rows:
        raise ValueError("The price table contains no usable price series.")

    return pd.DataFrame(rows).set_index("Asset")


def normalized_prices(prices: pd.DataFrame, lookback: int | None = None) -> pd.DataFrame:
    """Rebase each price series to 100 so trends can be compared visually."""

    selected = prices.tail(lookback) if lookback else prices
    normalized = {}
    for asset in selected.columns:
        series = selected[asset].dropna()
        if not series.empty:
            normalized[asset] = series / series.iloc[0] * 100
    return pd.DataFrame(normalized)


def build_momentum_ranking(
    metrics: pd.DataFrame,
    assets: Iterable[str] = RANKED_ASSETS,
) -> pd.DataFrame:
    """Rank tradable market proxies by their 20-day momentum.

    VIX and US 10Y Yield stay outside this ranking because a rising value there
    is usually risk information rather than a direct risk-asset leadership cue.
    """

    available = [asset for asset in assets if asset in metrics.index]
    columns = ["20D Change (%)", "50D Trend (%)", "1Y Level Percentile"]
    ranking = metrics.loc[available, columns].dropna(subset=["20D Change (%)"])
    ranking = ranking.sort_values("20D Change (%)", ascending=False).copy()
    ranking.insert(0, "Rank", range(1, len(ranking) + 1))
    return ranking


def build_return_heatmap_data(metrics: pd.DataFrame) -> pd.DataFrame:
    """Return recent performance columns for the dashboard heatmap."""

    columns = ["1D Change (%)", "5D Change (%)", "20D Change (%)"]
    return metrics[columns].rename(
        columns={
            "1D Change (%)": "1D",
            "5D Change (%)": "5D",
            "20D Change (%)": "20D",
        }
    )
