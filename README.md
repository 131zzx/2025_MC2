# COOTEFOO 可视化分析系统
> VAST Challenge 2025 Mini-Challenge 2

## 项目简介
本项目为记者 Edwina Darling Moray 构建可交互的视觉分析系统，通过对比 FILAH（渔业方）、TROUT（旅游方）和全量新闻记者数据集（journalist），揭示各方数据集的采样偏见及委员会成员的真实行为。

## 核心文档
- **[Summary_Report.md](./Summary_Report.md)**: 项目总结与全量分析报告（包含 Q1-Q4 的详细结论）。
- **[submission_materials/Answers.md](./submission_materials/Answers.md)**: 最终提交的答题稿。

## 目录结构
```
├── backend/          # Python 数据预处理脚本
├── frontend/         # Vue 3 前端应用
├── submission_materials/ # 提交材料（答题稿与图表）
├── Summary_Report.md # 项目分析总结报告
└── README.md
```

## 快速开始
1. **数据预处理**: 运行 `backend/` 下的 Python 脚本解析原始 JSON。
2. **启动前端**: 进入 `frontend/` 目录运行 `npm run dev`。

详细分析结论与数据异常推测见 [Summary_Report.md](./Summary_Report.md)。
