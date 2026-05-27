"""Calculate the simple market indicators shown in dashboard v1."""

from __future__ import annotations

import numpy as np
import pandas as pd


def _period_change(series: pd.Series, trading_days: int) -> float:
    """Return percentage price change over a trading-day lookback."""

    series = series.dropna()
    if len(series) <= trading_days:
        return np.nan
    return (series.iloc[-1] / series.iloc[-(trading_days + 1)] - 1) * 100


def calculate_market_metrics(prices: pd.DataFrame) -> pd.DataFrame:
    """Build the v1 metric table from daily close price series.

    Volatility is annualised using the common 252 trading-day convention.
    The result remains percentage based so it is easy to read in a notebook.
    """

    rows = []
    for asset in prices.columns:
        series = prices[asset].dropna()
        if series.empty:
            continue

        daily_returns = series.pct_change().dropna()
        volatility = (
            daily_returns.tail(20).std() * np.sqrt(252) * 100
            if len(daily_returns) >= 5
            else np.nan
        )
        rows.append(
            {
                "Asset": asset,
                "Latest Price": series.iloc[-1],
                "1D Change (%)": _period_change(series, 1),
                "5D Change (%)": _period_change(series, 5),
                "20D Change (%)": _period_change(series, 20),
                "20D Volatility (%)": volatility,
                "Last Date": series.index[-1].date(),
            }
        )

    if not rows:
        raise ValueError("The price table contains no usable price series.")

    return pd.DataFrame(rows).set_index("Asset")


def normalized_prices(prices: pd.DataFrame) -> pd.DataFrame:
    """Rebase each price series to 100 so trends can be compared visually."""

    normalized = {}
    for asset in prices.columns:
        series = prices[asset].dropna()
        if not series.empty:
            normalized[asset] = series / series.iloc[0] * 100
    return pd.DataFrame(normalized)

