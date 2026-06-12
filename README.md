# COOTEFOO 可视化分析系统

VAST Challenge 2025 Mini-Challenge 2

## 项目简介

本项目为记者 Edwina Darling Moray 构建可交互的视觉分析系统，通过对比 FILAH（渔业方）、TROUT（旅游方）和全量新闻记者数据集（journalist），揭示各方数据集的采样偏见及委员会成员的真实行为。

## 核心文档

- **[docs/2025MC2_Solution.md](./docs/2025MC2_Solution.md)**：正式分析报告。
- **[Challenge.md](./Challenge.md)**：赛题原文说明。

## 目录结构

```
├── backend/              # Python 数据预处理脚本
├── frontend/             # Vue 3 前端应用
├── MC2_release/          # 官方原始数据集（FILAH / TROUT / journalist.json 等）
├── docs/                 # 分析报告、答辩 PPT 等文档
├── images/               # 报告配图（与 docs/2025MC2_Solution.md 对应）
├── Challenge.md          # 赛题说明
└── README.md
```

## 环境要求

在运行项目之前，请确保您的电脑已安装以下环境：

- **Node.js**：建议 LTS 版本（如 v20 或 v22）。
- **Python**：建议 v3.11 或 v3.12（不建议使用 v3.14 等预览版）。

## 快速开始

### 1. 数据预处理（Python）

原始 JSON 位于 `MC2_release/`。运行导出脚本即可解析图谱、计算指标并生成前端数据：

```powershell
cd backend
pip install -r requirements.txt
python export_api_data.py
```

输出目录为 `frontend/public/data/`（约 17 个 JSON 文件）。若需单独检查解析结果，可运行 `python parse_graph.py`。

### 2. 启动可视化系统（Node.js）

```powershell
cd frontend
npm install          # 仅首次需要
npm run dev          # 开发模式，默认 http://localhost:5173/
```

生产构建与预览：

```powershell
npm run build
npm run preview
```

