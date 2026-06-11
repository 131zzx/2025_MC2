# COOTEFOO 可视化分析系统
VAST Challenge 2025 Mini-Challenge 2

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

## 环境要求

在运行项目之前，请确保您的电脑已安装以下环境：

- **Node.js**: 建议安装 **LTS (长期支持版)**，如 v20 或 v22。
- **Python**: 建议安装 **v3.11 或 v3.12** 稳定版（不建议使用 v3.14 等开发版）。

## 快速开始

### 1. 数据预处理 (Python)

首先需要运行后端脚本，将原始 JSON 数据解析并计算为前端可用的指标文件：

```powershell
# 进入后端目录
cd backend

# 安装 Python 依赖
pip install -r requirements.txt

# 依次运行预处理脚本
python parse_graph.py     # 解析原始图谱
python compute_metrics.py # 计算分析指标
python export_api_data.py # 导出前端数据
```

### 2. 启动可视化系统 (Node.js)

数据准备就绪后，启动 Vue 3 开发服务器：

```powershell
# 进入前端目录
cd frontend

# 安装依赖 (仅首次运行需要)
npm install

# 启动开发服务器
npm run dev
```

启动成功后，在浏览器访问控制台输出的地址（通常是 `http://localhost:5173/`）即可查看。

## 常见问题
- **npm 命令无法识别**: 请确保已安装 Node.js 并将其添加到系统环境变量 PATH 中。
- **Python 运行报错**: 建议使用 Python 3.12，并确保已运行 `pip install -r requirements.txt`。
- **数据未更新**: 确保 `backend/export_api_data.py` 运行成功，它会将数据输出到 `frontend/public/data` 目录。

详细分析结论与数据异常推测见 [Summary_Report.md](./Summary_Report.md)。
