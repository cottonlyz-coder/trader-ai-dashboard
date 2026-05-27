# Trader AI Dashboard

一个面向个人交易研究的长期项目。项目从简洁、透明的市场仪表盘开始，逐步扩展为可用于市场观察、交易复盘与宏观雷达的个人研究系统。

## 项目目标

- 聚合关键跨资产市场指标，快速判断风险偏好和交易环境。
- 用易于验证的规则输出第一版市场状态与交易员视角解读。
- 保持代码适合新手阅读，并为后续 AI、预测、数据库与 Web 界面留下扩展空间。

## 当前 v1 功能

v1 使用 `yfinance` 下载最近约六个月的日线数据，并追踪：

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
- 20 日年化波动率。
- `Risk-On`、`Risk-Off` 或 `Neutral / Mixed` 市场状态。
- 从同一起点 rebased 至 100 的归一化走势图。
- 一段基于透明规则的中文交易员视角解读。
- ticker 下载失败时的 fallback 选择记录或清晰错误提示。

> 注：如果某个序列没有合适且方向一致的替代品，例如 VIX 或 US 10Y Yield，v1 会显示下载失败提示，而不是用可能造成误读的 proxy。

## 项目结构

```text
Trader AI Dashboard/
├── README.md
├── roadmap.md
├── requirements.txt
├── notebooks/
│   └── trader_dashboard_v1.ipynb
└── src/
    ├── __init__.py
    ├── data_loader.py
    ├── indicators.py
    ├── regime.py
    └── report.py
```

## 如何在 Google Colab 运行

推荐在项目推送到 GitHub 后运行：

1. 在 Colab 中新建一个 Notebook，先执行：

```python
!git clone https://github.com/YOUR_USERNAME/trader-ai-dashboard.git
%cd trader-ai-dashboard
!pip -q install -r requirements.txt
```

2. 在左侧文件面板打开 `notebooks/trader_dashboard_v1.ipynb`，或直接通过 GitHub 链接在 Colab 打开该文件。
3. 如果通过 GitHub 链接直接打开，Notebook 会在首次运行时自动克隆公开仓库，以取得 `src/` 模块。
4. 依次运行 Notebook 中所有单元格。下载代码和市场数据均需要网络连接。

在本地 Jupyter 中运行也很简单：

```bash
pip install -r requirements.txt
jupyter notebook notebooks/trader_dashboard_v1.ipynb
```

## 设计说明

- `src/data_loader.py` 负责数据下载与 fallback。
- `src/indicators.py` 只负责指标计算和走势归一化。
- `src/regime.py` 用可读规则生成市场状态，不把判断藏在黑盒中。
- `src/report.py` 根据结果生成第一版中文市场解读。
- Notebook 只负责串联流程和显示图表，便于未来迁移到 Streamlit。

## 后续路线图

后续阶段包含 AI 交易复盘、市场相似度搜索、异常探测、Chronos 预测、自动宏观日报、Streamlit 交易驾驶舱、交易日志数据库、回测与个人交易教练。详细规划见 [roadmap.md](roadmap.md)。

## 免责声明

本项目用于个人研究和学习，仪表盘输出不构成投资建议或交易信号。历史表现和规则判断不能保证未来结果。
# Trader AI Dashboard

一个面向个人交易研究的长期项目。项目从简洁、透明的市场仪表盘开始，逐步扩展为可用于市场观察、交易复盘与宏观雷达的个人研究系统。

## 项目目标

- 聚合关键跨资产市场指标，快速判断风险偏好和交易环境。
- 用易于验证的规则输出第一版市场状态与交易员视角解读。
- 保持代码适合新手阅读，并为后续 AI、预测、数据库与 Web 界面留下扩展空间。

## 当前 v1 功能

v1 使用 `yfinance` 下载最近约六个月的日线数据，并追踪：

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
- 20 日年化波动率。
- `Risk-On`、`Risk-Off` 或 `Neutral / Mixed` 市场状态。
- 从同一起点 rebased 至 100 的归一化走势图。
- 一段基于透明规则的中文交易员视角解读。
- ticker 下载失败时的 fallback 选择记录或清晰错误提示。

> 注：如果某个序列没有合适且方向一致的替代品，例如 VIX 或 US 10Y Yield，v1 会显示下载失败提示，而不是用可能造成误读的 proxy。

## 项目结构

```text
Trader AI Dashboard/
├── README.md
├── roadmap.md
├── requirements.txt
├── notebooks/
│   └── trader_dashboard_v1.ipynb
└── src/
    ├── __init__.py
    ├── data_loader.py
    ├── indicators.py
    ├── regime.py
    └── report.py
```

## 如何在 Google Colab 运行

推荐在项目推送到 GitHub 后运行：

1. 在 Colab 中新建一个 Notebook，先执行：

```python
!git clone https://github.com/YOUR_USERNAME/trader-ai-dashboard.git
%cd trader-ai-dashboard
!pip -q install -r requirements.txt
```

2. 在左侧文件面板打开 `notebooks/trader_dashboard_v1.ipynb`，或直接通过 GitHub 链接在 Colab 打开该文件。
3. 确保当前目录是项目根目录，也就是能看到 `src` 文件夹的位置。
4. 依次运行 Notebook 中所有单元格。下载数据需要网络连接。

在本地 Jupyter 中运行也很简单：

```bash
pip install -r requirements.txt
jupyter notebook notebooks/trader_dashboard_v1.ipynb
```

## 设计说明

- `src/data_loader.py` 负责数据下载与 fallback。
- `src/indicators.py` 只负责指标计算和走势归一化。
- `src/regime.py` 用可读规则生成市场状态，不把判断藏在黑盒中。
- `src/report.py` 根据结果生成第一版中文市场解读。
- Notebook 只负责串联流程和显示图表，便于未来迁移到 Streamlit。

## 后续路线图

后续阶段包含 AI 交易复盘、市场相似度搜索、异常探测、Chronos 预测、自动宏观日报、Streamlit 交易驾驶舱、交易日志数据库、回测与个人交易教练。详细规划见 [roadmap.md](roadmap.md)。

## 免责声明

本项目用于个人研究和学习，仪表盘输出不构成投资建议或交易信号。历史表现和规则判断不能保证未来结果。
