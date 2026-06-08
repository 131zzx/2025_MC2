"""
export_api_data.py
──────────────────
将计算好的指标导出为前端可直接 fetch 的静态 JSON 文件，
保存至 frontend/public/data/ 目录。

导出文件清单：
  overview.json         — 数据集基础统计（节点数、边数、成员覆盖等）
  bias_index.json       — 偏见指数（整体 + 逐人，跨三数据集）
  coverage.json         — 成员活动覆盖率（FILAH/TROUT vs 全量）
  topic_distribution.json — 议题产业分布
  sentiment_agg.json    — 成员 × 产业情感聚合
  node_type_counts.json — 节点类型构成（用于数据集偏见对比）
  trip_zone_dist.json   — trip 落点 zone 分布
  missing_filah.json    — 全量有而 FILAH 缺失的节点
  missing_trout.json    — 全量有而 TROUT 缺失的节点
  member_activity.json  — 成员在各数据集中的活动数量
  meeting_coverage.json — 会议覆盖情况
  trip_records.json     — 行程记录（含出行人、地点、日期）
  topic_meta.json       — 议题元数据（产业分类、bias_score）
  place_nodes.json      — 地点节点（含经纬度，用于地图）
"""

import json
import pandas as pd
from pathlib import Path

from config import OUTPUT_DIR, TOPIC_INDUSTRY, COMMITTEE_MEMBERS, DATASET_LABELS
from parse_graph import (
    load_all_datasets, build_topic_df, build_participant_df,
    build_trip_df, build_meeting_df, get_topic_industry, extract_topic_from_id,
)
from compute_metrics import run_all


def ensure_output_dir():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"输出目录: {OUTPUT_DIR}")


def clean_for_json(obj):
    """递归清理对象中的 NaN、inf 等，使其符合 JSON 规范。"""
    if isinstance(obj, list):
        return [clean_for_json(i) for i in obj]
    if isinstance(obj, dict):
        return {k: clean_for_json(v) for k, v in obj.items()}
    if isinstance(obj, float):
        if pd.isna(obj) or obj == float('inf') or obj == float('-inf'):
            return None
    return obj


def df_to_json(df: pd.DataFrame, path: Path, orient: str = "records"):
    """将 DataFrame 序列化为 JSON，处理特殊类型。"""
    # 预处理：将 NaN 转换为 None
    df_clean = df.where(pd.notnull(df), None)
    data = df_clean.to_dict(orient=orient)
    
    # 处理 set 等不可直接序列化的类型
    data = clean_for_json(data)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  -> {path.name}  ({len(data)} 条)")


def export_overview(nodes_by_ds, edges_by_ds):
    """数据集基础统计概览。"""
    records = []
    for ds, ndf in nodes_by_ds.items():
        edf = edges_by_ds[ds]
        persons = ndf[ndf["type"] == "entity.person"]["id"].tolist()
        meetings = ndf[ndf["type"] == "meeting"]["id"].tolist()
        topics = ndf[ndf["type"] == "topic"]["id"].tolist()
        trips = ndf[ndf["type"] == "trip"]["id"].tolist()

        records.append({
            "dataset":        ds,
            "dataset_label":  DATASET_LABELS[ds],
            "node_count":     len(ndf),
            "edge_count":     len(edf),
            "member_count":   len(persons),
            "members":        persons,
            "meeting_count":  len(meetings),
            "topic_count":    len(topics),
            "trip_count":     len(trips),
        })

    path = OUTPUT_DIR / "overview.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(clean_for_json(records), f, ensure_ascii=False, indent=2)
    print(f"  -> overview.json  ({len(records)} 条)")


def export_topic_meta():
    """议题元数据（产业分类表）。"""
    records = [
        {"topic_key": k, **v}
        for k, v in TOPIC_INDUSTRY.items()
    ]
    path = OUTPUT_DIR / "topic_meta.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(clean_for_json(records), f, ensure_ascii=False, indent=2)
    print(f"  -> topic_meta.json  ({len(records)} 条)")


def export_place_nodes(nodes_by_ds):
    """全量 place 节点（经纬度 + zone，用于地图可视化）。"""
    jo_ndf = nodes_by_ds["journalist"]
    places = jo_ndf[jo_ndf["type"] == "place"].copy()
    keep_cols = [c for c in ["id", "name", "lat", "lon", "zone", "zone_detail"] if c in places.columns]
    places = places[keep_cols].drop_duplicates("id")
    df_to_json(places, OUTPUT_DIR / "place_nodes.json")


def export_trip_records(trip_df, nodes_by_ds):
    """行程记录，附地点 zone 信息。"""
    jo_ndf = nodes_by_ds["journalist"]
    place_info = {}
    if "type" in jo_ndf.columns:
        for _, row in jo_ndf[jo_ndf["type"] == "place"].iterrows():
            place_info[row["id"]] = {
                "name": row.get("name", row["id"]),
                "zone": row.get("zone", ""),
                "lat":  row.get("lat", None),
                "lon":  row.get("lon", None),
            }

    records = []
    for _, row in trip_df.iterrows():
        places_detail = [
            {**place_info.get(p, {"name": p, "zone": "", "lat": None, "lon": None}), "id": p}
            for p in row["places"]
        ]
        records.append({
            "trip_id":  row["trip_id"],
            "person":   row["person"],
            "date":     row["date"],
            "start":    row["start"],
            "end":      row["end"],
            "places":   places_detail,
            "dataset":  row["dataset"],
        })

    path = OUTPUT_DIR / "trip_records.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(clean_for_json(records), f, ensure_ascii=False, indent=2)
    print(f"  -> trip_records.json  ({len(records)} 条)")


def export_missing_evidence(missing_filah, missing_trout):
    """全量有而子集缺失的节点，按产业分类。"""
    for ds, mdf in [("filah", missing_filah), ("trout", missing_trout)]:
        if mdf.empty:
            continue
        keep = [c for c in ["id", "type", "date", "label", "topic_key", "topic_industry", "topic_bias_score", "related_members"]
                if c in mdf.columns]
        df_to_json(mdf[keep], OUTPUT_DIR / f"missing_{ds}.json")


def export_graph_data(nodes_by_ds, edges_by_ds):
    """导出全量图数据（简化版，用于 G6 可视化）。"""
    jo_nodes = nodes_by_ds["journalist"]
    jo_edges = edges_by_ds["journalist"]
    
    # 简化节点：只保留 id, type, label
    nodes = []
    for _, row in jo_nodes.iterrows():
        nodes.append({
            "id": row["id"],
            "type": row["type"],
            "label": row.get("label", row["id"]),
            "industry": get_topic_industry(extract_topic_from_id(row["id"])) if row["type"] == "topic" else "unknown"
        })
        
    # 简化边：只保留 source, target, role
    edges = []
    for _, row in jo_edges.iterrows():
        edges.append({
            "source": row["source"],
            "target": row["target"],
            "role": row.get("role", "")
        })
        
    path = OUTPUT_DIR / "full_graph.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(clean_for_json({"nodes": nodes, "edges": edges}), f, ensure_ascii=False, indent=2)
    print(f"  -> full_graph.json  ({len(nodes)} nodes, {len(edges)} edges)")


def main():
    print("=== 导出前端数据 ===\n")
    ensure_output_dir()

    # 1. 加载和解析
    print("正在加载数据集...")
    nodes_by_ds, edges_by_ds = load_all_datasets()
    topic_df      = build_topic_df(nodes_by_ds)
    participant_df = build_participant_df(edges_by_ds)
    trip_df        = build_trip_df(nodes_by_ds, edges_by_ds)
    meeting_df     = build_meeting_df(nodes_by_ds)

    # 2. 计算指标
    metrics = run_all(nodes_by_ds, edges_by_ds, topic_df, participant_df, trip_df, meeting_df)

    # 3. 导出
    print("\n正在导出 JSON 文件...")
    export_overview(nodes_by_ds, edges_by_ds)
    export_topic_meta()
    export_place_nodes(nodes_by_ds)
    export_trip_records(trip_df, nodes_by_ds)
    export_graph_data(nodes_by_ds, edges_by_ds)

    df_to_json(metrics["bias_index"],          OUTPUT_DIR / "bias_index.json")
    df_to_json(metrics["sentiment_bias"],       OUTPUT_DIR / "sentiment_bias.json")
    df_to_json(metrics["coverage"],             OUTPUT_DIR / "coverage.json")
    df_to_json(metrics["topic_distribution"],   OUTPUT_DIR / "topic_distribution.json")
    df_to_json(metrics["sentiment_agg"],        OUTPUT_DIR / "sentiment_agg.json")
    df_to_json(metrics["node_type_counts"],     OUTPUT_DIR / "node_type_counts.json")
    df_to_json(metrics["trip_zone_dist"],       OUTPUT_DIR / "trip_zone_dist.json")
    df_to_json(metrics["member_activity"],      OUTPUT_DIR / "member_activity.json")
    df_to_json(metrics["meeting_coverage"],     OUTPUT_DIR / "meeting_coverage.json")
    df_to_json(metrics["meeting_topic_dist"],   OUTPUT_DIR / "meeting_topic_dist.json")

    export_missing_evidence(metrics["missing_filah"], metrics["missing_trout"])

    print(f"\n全部导出完成！共 {len(list(OUTPUT_DIR.glob('*.json')))} 个 JSON 文件。")
    print(f"输出路径: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
