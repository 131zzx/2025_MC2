# COOTEFOO 可视化分析系统

> VAST Challenge 2025 Mini-Challenge 2

## 项目简介

本项目为记者 Edwina Darling Moray 构建可交互的视觉分析系统，通过对比 FILAH（渔业方）、TROUT（旅游方）和全量新闻记者数据集（journalist），揭示：

- 各方数据集本身的**采样偏见（Sampling Bias）**
- COOTEFOO 委员会成员的**真实行为模式**
- 缺失数据如何**扭曲外界对委员的判断**

## 技术栈

| 层次 | 技术 |
|------|------|
| 前端框架 | Vue 3 + TypeScript + Vite |
| 图表库 | Apache ECharts |
| 图谱可视化 | AntV G6 |
| 地图 | Leaflet.js |
| UI 组件 | Ant Design Vue |
| 状态管理 | Pinia |
| 数据预处理 | Python + NetworkX + Pandas |

## 目录结构

```
├── backend/          # Python 数据预处理脚本
├── frontend/         # Vue 3 前端应用
├── docs/             # 分析报告与结论文档
├── 实施方案.md        # 项目完整实施方案
├── 详细介绍.md        # 数据集详细介绍
└── README.md
```

> **注意**：原始数据文件（`data/` 目录）和参考案例（`examples/` 目录）不包含在仓库中，需单独获取。

## 快速开始

### 1. 数据预处理

将三个数据集 JSON 文件放入 `data/` 目录后运行：

```bash
cd backend
pip install -r requirements.txt
python parse_graph.py
python compute_metrics.py
python export_api_data.py
```

### 2. 启动前端

```bash
cd frontend
npm install
npm run dev
```

## 四个分析问题

| 问题 | 核心内容 | 数据来源 |
|------|---------|---------|
| Q1 | 各方指控是否被其自身数据集支持？ | 仅 FILAH + TROUT |
| Q2 | 委员会如何分配时间？整体是否偏袒？ | 仅 journalist |
| Q3 | TROUT/FILAH 结论在全量下如何变化？ | 三数据集 |
| Q4 | 可选人物，各数据集讲述的故事对比 | 三数据集 |

详细分析见 [实施方案.md](./实施方案.md)。

## 贡献指南

1. 从 `main` 分支创建功能分支：`git checkout -b feature/Q1-charts`
2. 完成开发后提交 PR，描述清楚修改内容
3. 数据文件禁止上传至仓库
