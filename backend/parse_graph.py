"""
parse_graph.py
──────────────
将三个知识图谱 JSON 文件解析为结构化 DataFrame，供后续指标计算使用。

输出（均为 pandas DataFrame）：
  nodes_df  — 所有节点（含 dataset 列标识来源）
  edges_df  — 所有边（含 dataset 列）
  topic_df  — 议题节点（附产业分类）
  person_df — 人员节点（entity.person）
  trip_df   — 行程节点（附出行人、途经地点）
  meeting_df— 会议节点
  participant_df — participant 边（sentiment / industry / reason）
"""

import json
import re
import pandas as pd
from pathlib import Path

from config import DATA_FILES, TOPIC_INDUSTRY, COMMITTEE_MEMBERS


# ── 工具函数 ──────────────────────────────────────────────

def load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def extract_topic_from_id(node_id) -> str | None:
    """从节点 ID 前缀提取对应的 topic key。"""
    node_id = str(node_id) if not isinstance(node_id, str) else node_id
    for topic_key in TOPIC_INDUSTRY:
        if node_id.startswith(topic_key):
            return topic_key
    return None


def get_topic_industry(topic_key: str | None) -> str:
    if topic_key and topic_key in TOPIC_INDUSTRY:
        return TOPIC_INDUSTRY[topic_key]["industry"]
    return "unknown"


def get_topic_bias_score(topic_key: str | None) -> float:
    if topic_key and topic_key in TOPIC_INDUSTRY:
        return TOPIC_INDUSTRY[topic_key]["bias_score"]
    return 0.0


# ── 主解析函数 ────────────────────────────────────────────

def parse_dataset(name: str, path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    解析单个数据集 JSON。
    返回 (nodes_df, edges_df)，均附带 'dataset' 列。
    """
    data = load_json(path)
    nodes = data.get("nodes", [])
    links = data.get("links", [])

    nodes_df = pd.DataFrame(nodes)
    nodes_df["dataset"] = name

    edges_df = pd.DataFrame(links)
    edges_df["dataset"] = name
    # 统一 role 缺失值
    if "role" not in edges_df.columns:
        edges_df["role"] = ""
    edges_df["role"] = edges_df["role"].fillna("")

    return nodes_df, edges_df


def load_all_datasets() -> tuple[dict[str, pd.DataFrame], dict[str, pd.DataFrame]]:
    """
    加载三个数据集，返回：
      nodes_by_ds: {"filah": df, "trout": df, "journalist": df}
      edges_by_ds: 同上
    """
    nodes_by_ds, edges_by_ds = {}, {}
    for name, path in DATA_FILES.items():
        n, e = parse_dataset(name, path)
        nodes_by_ds[name] = n
        edges_by_ds[name] = e
        print(f"[{name}] 节点: {len(n)}, 边: {len(e)}")
    return nodes_by_ds, edges_by_ds


# ── 派生表构建 ────────────────────────────────────────────

def build_topic_df(nodes_by_ds: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    全量 journalist 数据集中的议题节点，附产业分类信息。
    """
    jo = nodes_by_ds["journalist"]
    topics = jo[jo["type"] == "topic"].copy()
    topics["industry"] = topics["id"].apply(
        lambda x: get_topic_industry(extract_topic_from_id(x))
    )
    topics["bias_score"] = topics["id"].apply(
        lambda x: get_topic_bias_score(extract_topic_from_id(x))
    )
    topics["topic_key"] = topics["id"].apply(extract_topic_from_id)
    return topics.reset_index(drop=True)


def build_participant_df(edges_by_ds: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    所有数据集的 participant 边，附议题产业分类。
    columns: source, target, sentiment, reason, industry_list, dataset,
             topic_key, topic_industry, topic_bias_score,
             is_committee_member
    """
    frames = []
    for ds, edf in edges_by_ds.items():
        p = edf[edf["role"] == "participant"].copy()
        p["dataset"] = ds
        frames.append(p)

    df = pd.concat(frames, ignore_index=True)

    # industry 字段可能是 list 或 str，统一转为 list
    def _norm_industry(val):
        if isinstance(val, list):
            return val
        if isinstance(val, str) and val:
            return [val]
        return []

    df["industry_list"] = df.get("industry", pd.Series(dtype=object)).apply(_norm_industry)

    # 从 source ID 提取 topic_key
    df["topic_key"] = df["source"].apply(extract_topic_from_id)
    df["topic_industry"] = df["topic_key"].apply(get_topic_industry)
    df["topic_bias_score"] = df["topic_key"].apply(get_topic_bias_score)

    # 标记是否委员会成员
    df["is_committee_member"] = df["target"].isin(COMMITTEE_MEMBERS)

    # sentiment 转 float，缺失值填 0
    df["sentiment"] = pd.to_numeric(df.get("sentiment", 0), errors="coerce").fillna(0.0)

    return df.reset_index(drop=True)


def build_trip_df(
    nodes_by_ds: dict[str, pd.DataFrame],
    edges_by_ds: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """
    行程记录：trip 节点 + 关联的出行人 + 途经地点。
    每行 = 一段 trip → 一个 person + 地点列表（按时间排序）。
    """
    records = []
    for ds, ndf in nodes_by_ds.items():
        edf = edges_by_ds[ds]
        trips = ndf[ndf["type"] == "trip"]
        no_role = edf[edf["role"] == ""]

        for _, trip in trips.iterrows():
            tid = trip["id"]
            # 出行人（target 是人名）
            persons = no_role[
                (no_role["source"] == tid) & (no_role["target"].isin(COMMITTEE_MEMBERS))
            ]["target"].tolist()
            # 途经地点（target 是 place ID）
            places = no_role[
                (no_role["source"] == tid) & (~no_role["target"].isin(COMMITTEE_MEMBERS))
            ]
            place_list = places["target"].tolist() if not places.empty else []

            for person in persons:
                records.append({
                    "trip_id":  tid,
                    "person":   person,
                    "date":     trip.get("date", ""),
                    "start":    trip.get("start", ""),
                    "end":      trip.get("end", ""),
                    "places":   place_list,
                    "dataset":  ds,
                })

    return pd.DataFrame(records)


def build_meeting_df(nodes_by_ds: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    各数据集中的会议节点，并标记该会议存在于哪些数据集。
    """
    frames = []
    for ds, ndf in nodes_by_ds.items():
        m = ndf[ndf["type"] == "meeting"][["id", "date", "label"]].copy()
        m["dataset"] = ds
        frames.append(m)

    df = pd.concat(frames, ignore_index=True)
    # 每个会议存在于哪些数据集
    presence = df.groupby("id")["dataset"].apply(list).reset_index()
    presence.columns = ["id", "present_in"]

    meeting_meta = df.drop_duplicates("id")[["id", "date", "label"]].merge(presence, on="id")
    return meeting_meta.reset_index(drop=True)


# ── 入口 ──────────────────────────────────────────────────

def main():
    print("=== 解析知识图谱 JSON ===")
    nodes_by_ds, edges_by_ds = load_all_datasets()

    print("\n--- 节点类型分布 ---")
    for ds, ndf in nodes_by_ds.items():
        dist = ndf["type"].value_counts().to_dict()
        print(f"  [{ds}]: {dist}")

    print("\n--- 边 role 分布 ---")
    for ds, edf in edges_by_ds.items():
        dist = edf["role"].value_counts().to_dict()
        print(f"  [{ds}]: {dist}")

    topic_df = build_topic_df(nodes_by_ds)
    print(f"\n议题数（全量）: {len(topic_df)}")
    print(topic_df[["id", "industry", "bias_score"]].to_string(index=False))

    participant_df = build_participant_df(edges_by_ds)
    print(f"\nparticipant 边总数: {len(participant_df)}")

    trip_df = build_trip_df(nodes_by_ds, edges_by_ds)
    print(f"\n行程记录总数: {len(trip_df)}")

    meeting_df = build_meeting_df(nodes_by_ds)
    print(f"\n会议节点总数（去重）: {len(meeting_df)}")
    print(meeting_df[["id", "date", "present_in"]].to_string(index=False))

    return nodes_by_ds, edges_by_ds, topic_df, participant_df, trip_df, meeting_df


if __name__ == "__main__":
    main()
