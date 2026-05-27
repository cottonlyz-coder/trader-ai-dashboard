"""Generate concise trader-facing interpretation for dashboard v1.5."""

from __future__ import annotations

import pandas as pd

from src.indicators import build_momentum_ranking
from src.regime import RegimeResult


def _format_move(metrics: pd.DataFrame, asset: str, column: str) -> str:
    """Format a move for reporting while handling missing instruments."""

    if asset not in metrics.index or pd.isna(metrics.loc[asset, column]):
        return "数据不足"
    return f"{float(metrics.loc[asset, column]):+.2f}%"


def build_dimension_table(regime: RegimeResult) -> pd.DataFrame:
    """Convert component signals into a readable notebook table."""

    return pd.DataFrame(
        [
            {
                "观察维度": item.name,
                "信号": item.label,
                "风险贡献分": item.score,
                "依据": item.evidence,
            }
            for item in regime.dimensions
        ]
    ).set_index("观察维度")


def generate_trader_commentary(
    metrics: pd.DataFrame,
    regime: RegimeResult,
    include_watch_items: bool = True,
) -> str:
    """Return a rules-based daily market note in Chinese."""

    opening = {
        "Risk-On": "风险偏好偏积极，可以寻找顺势机会，但需先定义失效条件。",
        "Risk-Off": "环境偏防守，控制风险敞口和交易频率比寻找反弹更重要。",
        "Neutral / Mixed": "市场信号分化，当前更适合小仓位观察并等待共振。",
    }[regime.label]

    ranking = build_momentum_ranking(metrics)
    leadership = "暂无完整的强弱排序数据。"
    if len(ranking) >= 2:
        leader = ranking.index[0]
        laggard = ranking.index[-1]
        leadership = (
            f"近20日相对最强的是 {leader}"
            f"（{ranking.iloc[0]['20D Change (%)']:+.2f}%），"
            f"最弱的是 {laggard}"
            f"（{ranking.iloc[-1]['20D Change (%)']:+.2f}%）。"
        )

    snapshot = (
        f"Nasdaq 100 近20日 {_format_move(metrics, 'Nasdaq 100', '20D Change (%)')}，"
        f"VIX 近5日 {_format_move(metrics, 'VIX', '5D Change (%)')}，"
        f"美元指数近20日 {_format_move(metrics, 'US Dollar Index', '20D Change (%)')}。"
    )
    drivers = "主要驱动：" + " ".join(regime.reasons)
    reminder = "本摘要用于研究与复盘，不构成具体买卖建议。"
    paragraphs = [opening, snapshot, leadership, drivers]
    if include_watch_items and regime.watch_items:
        paragraphs.append("下一步观察：" + " ".join(regime.watch_items))
    paragraphs.append(reminder)
    return "\n\n".join(paragraphs)


def generate_daily_brief_markdown(metrics: pd.DataFrame, regime: RegimeResult) -> str:
    """Build a notebook-friendly decision brief in Markdown."""

    watch_items = regime.watch_items or ["继续观察风险维度是否形成共振，并维持既定风险纪律。"]
    watch_lines = "\n".join(f"- {item}" for item in watch_items)
    return (
        f"## 今日决策摘要：**{regime.label}**  |  综合分数：**{regime.score:+d}**\n\n"
        f"{generate_trader_commentary(metrics, regime, include_watch_items=False)}\n\n"
        f"### 观察清单\n{watch_lines}"
    )
