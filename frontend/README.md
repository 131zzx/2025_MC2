# COOTEFOO 可视化前端

VAST Challenge 2025 MC2 · Vue 3 交互式分析界面。

## 技术栈

| 类别 | 技术 |
|------|------|
| 框架 | Vue 3 + TypeScript + Vite |
| 状态 | Pinia |
| 路由 | Vue Router（Hash 模式） |
| 图表 | D3.js |
| 图谱 | AntV G6 |
| 地图 | 自研 SVG 地图（`OceanusMap.vue`，基于地点坐标） |

## 目录结构

```
src/
├── views/           # 三个主页面
│   ├── BiasView.vue    # 偏见全景
│   ├── MemberView.vue  # 委员行为
│   └── TripView.vue    # 行程地图
├── components/
│   ├── charts/      # D3 图表组件
│   ├── graph/       # Ego 关系网络
│   ├── map/         # 地图与时间轴
│   └── shared/      # 术语说明、数据集选择器等
├── stores/          # dataStore（加载 JSON）、uiStore、linkingStore
└── types/           # 类型定义与配色常量

public/
├── data/            # 后端导出的指标 JSON（需先运行 backend/export_api_data.py）
└── oceanus_map.geojson
```

## 快速开始

**前置条件**：在项目根目录的 `backend/` 中运行 `python export_api_data.py`，生成 `public/data/` 下的 JSON 文件。

```powershell
npm install          # 首次安装依赖
npm run dev          # 开发服务器，默认 http://localhost:5173/
npm run build        # 生产构建，输出至 dist/
npm run preview      # 预览构建结果
```

## 三个分析模块

| 路由 | 页面 | 主要图表 |
|------|------|----------|
| `/bias` | 偏见全景 | KPI 卡、偏差指数对比、数据集规模对比、话题行业构成、缺失节点环图 |
| `/member` | 委员行为 | 偏见定位散点、平行坐标、覆盖率矩阵、情感热图、跨数据集活动、Ego 网络 |
| `/trip` | 行程地图 | Oceanus 地图、行程时间轴、区域分布、成员行程统计 |

委员行为页支持点击成员联动多图；行程页时间轴与区域分布的数据集筛选相互独立，读图时注意当前选中状态。

## 数据加载

前端通过 `dataStore` 从 `public/data/*.json` 拉取预处理结果，不直接读取原始 `MC2_release/` JSON。更新数据后刷新页面即可，开发模式下修改 JSON 通常无需重启服务。
