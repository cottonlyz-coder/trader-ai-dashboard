# Trader AI Dashboard

一个面向个人交易研究的长期项目。项目从简洁、透明的市场仪表盘开始，逐步扩展为可用于市场观察、交易复盘与宏观雷达的个人研究系统。

## 项目目标

- 聚合关键跨资产市场指标，快速判断风险偏好和交易环境。
- 用易于验证的规则输出第一版市场状态与交易员视角解读。
- 保持代码适合新手阅读，并为后续 AI、预测、数据库与 Web 界面留下扩展空间。

## 当前版本：v1.5 Decision Dashboard

v1.5 使用 `yfinance` 下载日线数据，并追踪：

| 市场 | 优先 ticker | fallback |
| --- | --- | --- |
| China A50 / 替代指数 | `XIN9.FGI` | `000300.SS`、`510050.SS` |
| Nasdaq 100 | `^NDX` | `QQQ` |
| VIX | `^VIX` | - |
| Gold | `GC=F` | `GLD` |
| Crude Oil | `CL=F` | `USO` |
| US Dollar Index | `DX-Y.NYB` | `UUP` |
| US 10Y Yield | `^TNX` | - |

仪表盘输出：

- 最新价格、1 日/5 日/20 日涨跌幅。
- 50 日趋势、20 日年化波动率、相对于过去一年的价格和波动率百分位。
- `Risk-On`、`Risk-Off` 或 `Neutral / Mixed` 总状态，以及权益动能、波动压力、美元/利率压力、中国资产和商品背景分层。
- 资产强弱排名与四区域综合概览图。
- 基于透明规则的中文盘前摘要与观察清单。
- ticker 下载失败时的 fallback 选择记录或清晰错误提示。

> 注：如果某个序列没有合适且方向一致的替代品，例如 VIX 或 US 10Y Yield，v1 会显示下载失败提示，而不是用可能造成误读的 proxy。

## 项目结构

```text
Trader AI Dashboard/
├── README.md
├── roadmap.md
├── requirements.txt
├── notebooks/
│   ├── trader_dashboard_v1_colab.ipynb
│   └── trader_dashboard_v1_5_colab.ipynb
└── src/
    ├── __init__.py
    ├── dashboard.py
    ├── data_loader.py
    ├── indicators.py
    ├── regime.py
    └── report.py
```

## 如何在 Google Colab 运行

推荐直接打开最新版决策仪表盘：

[在 Colab 中打开 Trader AI Dashboard v1.5](https://colab.research.google.com/github/cottonlyz-coder/trader-ai-dashboard/blob/main/notebooks/trader_dashboard_v1_5_colab.ipynb)

也可以在 Colab 中新建一个 Notebook，再执行：

```python
!git clone https://github.com/cottonlyz-coder/trader-ai-dashboard.git
%cd trader-ai-dashboard
!pip -q install -r requirements.txt
```

如果通过 GitHub 链接直接打开，Notebook 会在首次运行时自动克隆公开仓库，以取得 `src/` 模块。依次运行所有单元格即可；下载代码和市场数据均需要网络连接。

在本地 Jupyter 中运行也很简单：

```bash
pip install -r requirements.txt
jupyter notebook notebooks/trader_dashboard_v1_5_colab.ipynb
```

## 设计说明

- `src/data_loader.py` 负责数据下载与 fallback。
- `src/indicators.py` 负责收益、趋势、波动率、百分位和强弱排名。
- `src/regime.py` 用分层可读规则生成市场状态，不把判断藏在黑盒中。
- `src/report.py` 根据结果生成中文盘前摘要和观察清单。
- `src/dashboard.py` 负责适合 Colab 展示的综合概览图。
- Notebook 只负责串联流程和显示图表，便于未来迁移到 Streamlit。

## 后续路线图

后续阶段包含 AI 交易复盘、市场相似度搜索、异常探测、Chronos 预测、自动宏观日报、Streamlit 交易驾驶舱、交易日志数据库、回测与个人交易教练。详细规划见 [roadmap.md](roadmap.md)。

## 免责声明

本项目用于个人研究和学习，仪表盘输出不构成投资建议或交易信号。历史表现和规则判断不能保证未来结果。
