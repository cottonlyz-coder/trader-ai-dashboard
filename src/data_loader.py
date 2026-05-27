"""Download the market data used by Trader AI Dashboard v1.

The functions in this file intentionally stay simple: yfinance is convenient
for a personal research dashboard, but a symbol can occasionally disappear or
return empty data. Markets with a sensible proxy therefore have fallback symbols.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

import pandas as pd
import yfinance as yf


@dataclass(frozen=True)
class MarketAsset:
    """Definition of one dashboard market and its Yahoo Finance symbols."""

    name: str
    tickers: Tuple[str, ...]
    note: str = ""


# Yahoo Finance does not always provide a perfect cash-index ticker for every
# market. For China A50 in particular, CSI 300 and SSE 50 ETF are usable broad
# China large-cap proxies if the A50 futures series is unavailable.
MARKET_ASSETS: Tuple[MarketAsset, ...] = (
    MarketAsset(
        "China A50 / Proxy",
        ("XIN9.FGI", "000300.SS", "510050.SS"),
        "若 A50 序列无法获取，则使用沪深 300 或上证 50 ETF 作为大盘代理观察。",
    ),
    MarketAsset("Nasdaq 100", ("^NDX", "QQQ")),
    MarketAsset("VIX", ("^VIX",)),
    MarketAsset("Gold", ("GC=F", "GLD")),
    MarketAsset("Crude Oil", ("CL=F", "USO")),
    MarketAsset("US Dollar Index", ("DX-Y.NYB", "UUP")),
    MarketAsset("US 10Y Yield", ("^TNX",)),
)


def _download_close(ticker: str, period: str) -> pd.Series:
    """Download one adjusted-close price series and return it by date."""

    history = yf.download(
        ticker,
        period=period,
        interval="1d",
        auto_adjust=True,
        progress=False,
        threads=False,
    )
    if history.empty:
        return pd.Series(dtype="float64")

    # yfinance may return either normal columns or MultiIndex columns,
    # depending on version and the number of requested symbols.
    close = history["Close"]
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]

    close = close.dropna().astype(float)
    close.name = ticker
    return close


def load_market_data(
    period: str = "6mo",
) -> Tuple[pd.DataFrame, pd.DataFrame, List[str]]:
    """Download close prices, trying fallback tickers when necessary.

    Returns:
        prices: Date-indexed table of close prices, one column per market.
        symbol_info: Which actual ticker was selected for each market.
        messages: Human-readable warning and fallback notes.

    Raises:
        RuntimeError: If no market data can be downloaded at all.
    """

    price_series: Dict[str, pd.Series] = {}
    selected_rows = []
    messages: List[str] = []

    for asset in MARKET_ASSETS:
        selected_ticker = None

        for ticker in asset.tickers:
            try:
                close = _download_close(ticker, period)
            except Exception as exc:  # Network/provider errors should not stop all assets.
                messages.append(
                    f"{asset.name}: ticker {ticker} 下载失败 "
                    f"({type(exc).__name__})。"
                )
                continue

            if not close.empty:
                selected_ticker = ticker
                price_series[asset.name] = close
                break

        if selected_ticker is None:
            messages.append(
                f"{asset.name}: 未找到可用数据；已尝试 {', '.join(asset.tickers)}。"
            )
            continue

        is_fallback = selected_ticker != asset.tickers[0]
        selected_rows.append(
            {
                "Asset": asset.name,
                "Ticker Used": selected_ticker,
                "Fallback Used": "Yes" if is_fallback else "No",
            }
        )
        if is_fallback:
            messages.append(
                f"{asset.name}: 优先 ticker {asset.tickers[0]} 不可用，"
                f"改用 fallback {selected_ticker}。"
            )
        if asset.note and is_fallback:
            messages.append(f"{asset.name}: {asset.note}")

    if not price_series:
        raise RuntimeError("未能下载任何市场数据，请检查网络连接或稍后重试。")

    prices = pd.concat(price_series, axis=1).sort_index().ffill()
    symbol_info = pd.DataFrame(selected_rows).set_index("Asset")
    return prices, symbol_info, messages
