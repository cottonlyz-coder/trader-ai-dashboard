"""AI-assisted trade review utilities.

The module is safe to import without an OpenAI API key. API calls only happen
inside review_trades_with_openai(), and the key is read from the environment.
"""

from __future__ import annotations

import os
from textwrap import dedent

import pandas as pd

from src.regime import RegimeResult
from src.report import build_dimension_table


REQUIRED_TRADE_COLUMNS = [
    "date",
    "symbol",
    "direction",
    "setup",
    "entry_price",
    "exit_price",
    "position_size",
    "risk_amount",
    "pnl",
    "market_regime_before_trade",
    "plan",
    "execution_notes",
    "emotion_tag",
    "lesson",
]


def validate_trade_journal(trades: pd.DataFrame) -> None:
    """Raise a clear error if the trade journal misses required columns."""

    missing = [column for column in REQUIRED_TRADE_COLUMNS if column not in trades.columns]
    if missing:
        raise ValueError(f"Trade journal is missing columns: {', '.join(missing)}")


def summarize_trade_journal(trades: pd.DataFrame) -> pd.DataFrame:
    """Build simple performance and behavior metrics for review context."""

    validate_trade_journal(trades)
    pnl = pd.to_numeric(trades["pnl"], errors="coerce").fillna(0)
    risk = pd.to_numeric(trades["risk_amount"], errors="coerce")
    risk = risk.where(risk != 0)
    return pd.DataFrame(
        [
            {
                "Trades": len(trades),
                "Total PnL": pnl.sum(),
                "Win Rate (%)": (pnl.gt(0).mean() * 100) if len(pnl) else 0,
                "Average PnL": pnl.mean() if len(pnl) else 0,
                "Average R Multiple": (pnl / risk).dropna().mean(),
                "Largest Loss": pnl.min() if len(pnl) else 0,
                "Largest Win": pnl.max() if len(pnl) else 0,
            }
        ]
    )


def build_trade_review_context(
    trades: pd.DataFrame,
    metrics: pd.DataFrame,
    regime: RegimeResult,
) -> str:
    """Create the compact text context sent to the model."""

    validate_trade_journal(trades)
    summary = summarize_trade_journal(trades)
    dimension_table = build_dimension_table(regime)

    market_columns = [
        "Latest Price",
        "1D Change (%)",
        "5D Change (%)",
        "20D Change (%)",
        "1Y Level Percentile",
    ]
    available_columns = [column for column in market_columns if column in metrics.columns]
    market_snapshot = metrics[available_columns].round(2)

    return dedent(
        f"""
        Current dashboard regime:
        - Label: {regime.label}
        - Score: {regime.score:+d}
        - Reasons: {' '.join(regime.reasons)}

        Market dimension table:
        {dimension_table.to_csv()}

        Market snapshot:
        {market_snapshot.to_csv()}

        Trade journal summary:
        {summary.round(2).to_csv(index=False)}

        Trade journal rows:
        {trades.to_csv(index=False)}
        """
    ).strip()


def generate_offline_trade_review(
    trades: pd.DataFrame,
    metrics: pd.DataFrame,
    regime: RegimeResult,
) -> str:
    """Generate a deterministic review when no API key is available."""

    validate_trade_journal(trades)
    summary = summarize_trade_journal(trades).iloc[0]
    losses = trades[pd.to_numeric(trades["pnl"], errors="coerce").fillna(0) < 0]
    regime_mismatches = trades[
        trades["market_regime_before_trade"].fillna("") != regime.label
    ]

    notes = [
        f"## 离线交易复盘摘要",
        f"- 当前市场状态：**{regime.label}**，综合分数 {regime.score:+d}。",
        f"- 样本交易数：{int(summary['Trades'])}，总 PnL：{summary['Total PnL']:.2f}，胜率：{summary['Win Rate (%)']:.1f}%。",
        f"- 平均 R 倍数：{summary['Average R Multiple']:.2f}。",
    ]

    if len(losses):
        common_emotions = losses["emotion_tag"].value_counts().head(3)
        notes.append(
            "- 亏损交易中最常见的情绪标签："
            + "，".join(f"{name}({count})" for name, count in common_emotions.items())
            + "。"
        )
    if len(regime_mismatches):
        notes.append(
            f"- 有 {len(regime_mismatches)} 笔交易的记录环境与当前仪表盘状态不同，复盘时要区分历史环境和现在环境。"
        )

    notes.extend(
        [
            "### 下一步建议",
            "- 把每笔交易的“入场前市场状态”和“执行偏差”写清楚。",
            "- 对 Risk-Off 或 Neutral / Mixed 环境中的进攻型交易降低默认仓位。",
            "- 每周统计亏损交易的情绪标签，优先修正重复出现的行为错误。",
        ]
    )
    return "\n".join(notes)


def review_trades_with_openai(
    trades: pd.DataFrame,
    metrics: pd.DataFrame,
    regime: RegimeResult,
    model: str | None = None,
) -> str:
    """Use the OpenAI Responses API to produce a trader-coach review."""

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not set.")

    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    selected_model = model or os.getenv("OPENAI_MODEL", "gpt-5-mini")
    context = build_trade_review_context(trades, metrics, regime)
    response = client.responses.create(
        model=selected_model,
        input=[
            {
                "role": "developer",
                "content": (
                    "You are a disciplined trading review coach. "
                    "Do not provide buy/sell instructions. "
                    "Focus on process quality, risk control, execution mistakes, "
                    "market-regime fit, and repeatable improvement rules. "
                    "Write in concise Chinese."
                ),
            },
            {
                "role": "user",
                "content": (
                    "请基于下面的交易日志和市场仪表盘上下文，输出：\n"
                    "1. 本周交易质量评分（0-100）\n"
                    "2. 最主要的三个执行问题\n"
                    "3. 与市场状态不匹配的交易\n"
                    "4. 下周最重要的一条交易纪律\n"
                    "5. 一段简短鼓励但不纵容的教练反馈\n\n"
                    f"{context}"
                ),
            },
        ],
    )
    return response.output_text
