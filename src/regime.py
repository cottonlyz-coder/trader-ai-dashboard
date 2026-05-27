"""Transparent rule-based market regime classification for dashboard v1."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

import pandas as pd


@dataclass
class RegimeResult:
    """The market label, score and plain-language reasons behind it."""

    label: str
    score: int
    reasons: List[str]


def _change(metrics: pd.DataFrame, asset: str, column: str) -> float | None:
    """Safely read a metric, returning None if the asset is unavailable."""

    if asset not in metrics.index or pd.isna(metrics.loc[asset, column]):
        return None
    return float(metrics.loc[asset, column])


def classify_market_regime(metrics: pd.DataFrame) -> RegimeResult:
    """Classify the environment using a small, easy-to-audit rule set.

    The score focuses on growth appetite (Nasdaq), fear (VIX), defensive gold,
    and potential pressure from a rising dollar or US 10-year yield. This is a
    dashboard signal, not a standalone trading instruction.
    """

    score = 0
    reasons: List[str] = []

    nasdaq_20d = _change(metrics, "Nasdaq 100", "20D Change (%)")
    if nasdaq_20d is not None:
        if nasdaq_20d > 2:
            score += 2
            reasons.append(f"Nasdaq 100 近20日偏强（{nasdaq_20d:+.1f}%）。")
        elif nasdaq_20d < -2:
            score -= 2
            reasons.append(f"Nasdaq 100 近20日偏弱（{nasdaq_20d:+.1f}%）。")

    vix_5d = _change(metrics, "VIX", "5D Change (%)")
    if vix_5d is not None:
        if vix_5d < -5:
            score += 1
            reasons.append(f"VIX 近5日降温（{vix_5d:+.1f}%）。")
        elif vix_5d > 5:
            score -= 2
            reasons.append(f"VIX 近5日上升（{vix_5d:+.1f}%）。")

    dollar_20d = _change(metrics, "US Dollar Index", "20D Change (%)")
    if dollar_20d is not None:
        if dollar_20d > 2:
            score -= 1
            reasons.append(f"美元指数近20日偏强（{dollar_20d:+.1f}%）。")
        elif dollar_20d < -2:
            score += 1
            reasons.append(f"美元指数近20日偏弱（{dollar_20d:+.1f}%）。")

    yield_20d = _change(metrics, "US 10Y Yield", "20D Change (%)")
    if yield_20d is not None and yield_20d > 8:
        score -= 1
        reasons.append(f"美国10年期收益率近20日上升较快（{yield_20d:+.1f}%）。")

    if score >= 2:
        label = "Risk-On"
    elif score <= -2:
        label = "Risk-Off"
    else:
        label = "Neutral / Mixed"

    if not reasons:
        reasons.append("现有指标未显示强烈的一致方向。")
    return RegimeResult(label=label, score=score, reasons=reasons)
