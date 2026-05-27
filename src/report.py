"""Produce a concise trader-style market interpretation in Chinese."""

from __future__ import annotations

import pandas as pd

from src.regime import RegimeResult


def _format_move(metrics: pd.DataFrame, asset: str, column: str) -> str:
    """Format a move for reporting while handling missing instruments."""

    if asset not in metrics.index or pd.isna(metrics.loc[asset, column]):
        return "数据不足"
    return f"{float(metrics.loc[asset, column]):+.2f}%"


def generate_trader_commentary(
    metrics: pd.DataFrame,
    regime: RegimeResult,
) -> str:
    """Return a rules-based first draft of a trader's daily market note."""

    opening = {
        "Risk-On": "风险偏好目前偏积极，交易上更适合关注顺势机会，但不宜忽略止损。",
        "Risk-Off": "市场处于偏防守状态，首要任务是控制风险敞口并避免追逐反弹。",
        "Neutral / Mixed": "市场信号互有冲突，当前更适合等待确认并保持仓位弹性。",
    }[regime.label]

    snapshot = (
        f"Nasdaq 100 20日表现为 {_format_move(metrics, 'Nasdaq 100', '20D Change (%)')}，"
        f"VIX 5日变化为 {_format_move(metrics, 'VIX', '5D Change (%)')}；"
        f"黄金20日变化为 {_format_move(metrics, 'Gold', '20D Change (%)')}，"
        f"美元指数20日变化为 {_format_move(metrics, 'US Dollar Index', '20D Change (%)')}。"
    )
    drivers = "核心观察：" + " ".join(regime.reasons)
    reminder = "这是市场温度计式的观察，不构成具体买卖建议。"
    return "\n\n".join((opening, snapshot, drivers, reminder))

