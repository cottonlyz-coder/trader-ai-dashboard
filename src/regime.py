"""Transparent rule-based market regime classification for dashboard v1.5."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

import pandas as pd


@dataclass
class DimensionSignal:
    """One interpretable component of the overall market state."""

    name: str
    label: str
    score: int
    evidence: str


@dataclass
class RegimeResult:
    """The market label, score, component signals and action prompts."""

    label: str
    score: int
    reasons: List[str]
    dimensions: List[DimensionSignal] = field(default_factory=list)
    watch_items: List[str] = field(default_factory=list)


def _change(metrics: pd.DataFrame, asset: str, column: str) -> float | None:
    """Safely read a metric, returning None if the asset is unavailable."""

    if asset not in metrics.index or pd.isna(metrics.loc[asset, column]):
        return None
    return float(metrics.loc[asset, column])


def _direction_label(score: int, positive: str, negative: str) -> str:
    """Translate a signed score into a plain-language label."""

    if score > 0:
        return positive
    if score < 0:
        return negative
    return "中性"


def classify_market_regime(metrics: pd.DataFrame) -> RegimeResult:
    """Classify the environment using five explainable dimensions.

    Positive scores indicate conditions supportive of risk appetite. Negative
    scores indicate defensive pressure. Commodities are shown as context, but
    do not drive the headline label in this first decision-dashboard version.
    """

    dimensions: List[DimensionSignal] = []
    watch_items: List[str] = []

    nasdaq_20d = _change(metrics, "Nasdaq 100", "20D Change (%)")
    equity_score = 0
    if nasdaq_20d is not None:
        if nasdaq_20d > 2:
            equity_score = 2
        elif nasdaq_20d < -2:
            equity_score = -2
        equity_evidence = f"Nasdaq 100 近20日 {nasdaq_20d:+.1f}%"
    else:
        equity_evidence = "Nasdaq 100 数据不足"
    dimensions.append(
        DimensionSignal(
            "权益动能",
            _direction_label(equity_score, "偏强", "偏弱"),
            equity_score,
            equity_evidence,
        )
    )

    vix_5d = _change(metrics, "VIX", "5D Change (%)")
    vix_percentile = _change(metrics, "VIX", "1Y Level Percentile")
    volatility_score = 0
    volatility_notes = []
    if vix_percentile is not None:
        volatility_notes.append(f"VIX 水平位于一年 {vix_percentile:.0f}% 分位")
        if vix_percentile >= 75:
            volatility_score -= 2
            watch_items.append("VIX 已在一年高位区间，仓位与止损应优先于进攻。")
        elif vix_percentile <= 30:
            volatility_score += 1
    if vix_5d is not None:
        volatility_notes.append(f"近5日 {vix_5d:+.1f}%")
        if vix_5d > 5:
            volatility_score -= 1
        elif vix_5d < -5:
            volatility_score += 1
    dimensions.append(
        DimensionSignal(
            "波动压力",
            _direction_label(volatility_score, "缓和", "升温"),
            volatility_score,
            "；".join(volatility_notes) or "VIX 数据不足",
        )
    )

    dollar_20d = _change(metrics, "US Dollar Index", "20D Change (%)")
    yield_20d = _change(metrics, "US 10Y Yield", "20D Change (%)")
    liquidity_score = 0
    liquidity_notes = []
    if dollar_20d is not None:
        liquidity_notes.append(f"美元20日 {dollar_20d:+.1f}%")
        if dollar_20d > 2:
            liquidity_score -= 1
            watch_items.append("美元走强，关注其是否继续压制权益和商品风险偏好。")
        elif dollar_20d < -2:
            liquidity_score += 1
    if yield_20d is not None:
        liquidity_notes.append(f"10Y收益率20日 {yield_20d:+.1f}%")
        if yield_20d > 8:
            liquidity_score -= 1
            watch_items.append("长端收益率上行较快，成长股估值可能承压。")
        elif yield_20d < -8:
            liquidity_score += 1
    dimensions.append(
        DimensionSignal(
            "美元/利率压力",
            _direction_label(liquidity_score, "友好", "偏紧"),
            liquidity_score,
            "；".join(liquidity_notes) or "美元与利率数据不足",
        )
    )

    china_20d = _change(metrics, "China A50 / Proxy", "20D Change (%)")
    china_score = 0
    if china_20d is not None:
        if china_20d > 2:
            china_score = 1
        elif china_20d < -2:
            china_score = -1
        china_evidence = f"中国大盘代理近20日 {china_20d:+.1f}%"
    else:
        china_evidence = "中国大盘代理数据不足"
    dimensions.append(
        DimensionSignal(
            "中国资产",
            _direction_label(china_score, "改善", "偏弱"),
            china_score,
            china_evidence,
        )
    )

    gold_20d = _change(metrics, "Gold", "20D Change (%)")
    crude_20d = _change(metrics, "Crude Oil", "20D Change (%)")
    commodity_label = "中性"
    if gold_20d is not None and crude_20d is not None:
        if gold_20d > 3 and crude_20d > 3:
            commodity_label = "实物资产偏强"
        elif gold_20d > 3 and crude_20d < 0:
            commodity_label = "防守需求偏强"
        elif gold_20d < -3 and crude_20d < -3:
            commodity_label = "商品偏弱"
    commodity_evidence = (
        f"黄金20日 {gold_20d:+.1f}%；原油20日 {crude_20d:+.1f}%"
        if gold_20d is not None and crude_20d is not None
        else "商品数据不足"
    )
    dimensions.append(DimensionSignal("商品背景", commodity_label, 0, commodity_evidence))

    score = equity_score + volatility_score + liquidity_score + china_score
    if score >= 3:
        label = "Risk-On"
    elif score <= -3:
        label = "Risk-Off"
    else:
        label = "Neutral / Mixed"

    if label == "Neutral / Mixed":
        watch_items.append("多维信号尚未形成共振，等待 Nasdaq 与 VIX 给出一致确认。")
    elif label == "Risk-On" and volatility_score < 0:
        watch_items.append("权益偏强但波动压力仍在，避免把风险偏好改善等同于低风险。")

    reasons = [
        f"{signal.name}：{signal.label}（{signal.evidence}）。"
        for signal in dimensions
        if signal.score != 0
    ]
    if not reasons:
        reasons.append("现有指标未显示强烈的一致方向。")
    return RegimeResult(label, score, reasons, dimensions, watch_items)
