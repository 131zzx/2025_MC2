"""
compute_metrics.py
──────────────────
基于 parse_graph.py 的结构化数据，计算所有可视化所需的分析指标。

指标清单：
  1. bias_index         — 每个数据集 / 每位成员的偏见指数
  2. coverage           — FILAH/TROUT 对每位成员的活动覆盖率（相对于全量）
  3. topic_distribution — 各数据集议题产业分布
  4. sentiment_agg      — 每位成员 × 每个产业的情感均值
  5. node_type_counts   — 各数据集节点类型构成
  6. trip_zone_dist     — 各数据集 trip 落点 zone 分布
  7. missing_evidence   — 全量中有而子集没有的活动节点
  8. member_activity    — 每位成员在每个数据集中的各类活动数量
  9. meeting_coverage   — 各数据集会议覆盖情况
"""

import pandas as pd
import numpy as np
from parse_graph import (
    load_all_datasets, build_topic_df, build_participant_df,
    build_trip_df, build_meeting_df, extract_topic_from_id,
    get_topic_industry, get_topic_bias_score,
)
from config import COMMITTEE_MEMBERS, TOPIC_INDUSTRY, ZONE_SCORE


# ── 1. Bias Index ──────────────────────────────────────────

def compute_bias_index(participant_df: pd.DataFrame) -> pd.DataFrame:
    """
    计算每个数据集（整体）及每位成员的偏见指数。

    bias_index = (tourism活动数 - fishing活动数) / (tourism + fishing)
    值域 [-1, +1]：+1=完全偏旅游, -1=完全偏渔业, 0=均衡

    注：仅统计 COOTEFOO 成员的 participant 活动（含 topic_industry 非 unknown）。
    """
    df = participant_df[
        participant_df["is_committee_member"] &
        participant_df["topic_industry"].isin(["fishing", "tourism"])
    ].copy()

    def _bias(grp: pd.DataFrame) -> float:
        fishing = (grp["topic_industry"] == "fishing").sum()
        tourism = (grp["topic_industry"] == "tourism").sum()
        total = fishing + tourism
        return round((tourism - fishing) / total, 4) if total > 0 else 0.0

    # 整体 bias（按数据集）
    overall = (
        df.groupby("dataset")
        .apply(_bias)
        .reset_index()
        .rename(columns={0: "bias_index"})
    )
    overall["member"] = "ALL"

    # 个人 bias（按数据集 × 成员）
    personal = (
        df.groupby(["dataset", "target"])
        .apply(_bias)
        .reset_index()
        .rename(columns={"target": "member", 0: "bias_index"})
    )

    result = pd.concat([overall, personal], ignore_index=True)
    return result


def compute_sentiment_bias_index(participant_df: pd.DataFrame) -> pd.DataFrame:
    """
    情感加权偏见指数：用 sentiment 均值代替计数。
    bias_sentiment = mean(sentiment for tourism topics) - mean(sentiment for fishing topics)
    """
    df = participant_df[
        participant_df["is_committee_member"] &
        participant_df["topic_industry"].isin(["fishing", "tourism"])
    ].copy()

    def _sent_bias(grp: pd.DataFrame) -> float:
        t = grp[grp["topic_industry"] == "tourism"]["sentiment"].mean()
        f = grp[grp["topic_industry"] == "fishing"]["sentiment"].mean()
        t = t if not np.isnan(t) else 0.0
        f = f if not np.isnan(f) else 0.0
        return round(float(t - f), 4)

    result = (
        df.groupby(["dataset", "target"])
        .apply(_sent_bias)
        .reset_index()
        .rename(columns={"target": "member", 0: "sentiment_bias"})
    )
    return result


# ── 2. Coverage ────────────────────────────────────────────

def compute_coverage(
    nodes_by_ds: dict[str, pd.DataFrame],
    edges_by_ds: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """
    FILAH 和 TROUT 对每位成员的活动覆盖率。
    coverage = |{活动节点 ID in subset 与该成员相关}| / |{...in journalist}|

    "与该成员相关"的活动节点：
      - participant 边的 source（discussion/plan 节点）
      - trip 边的 source（trip 节点）
    """
    records = []

    for member in COMMITTEE_MEMBERS:
        # 全量中与该成员相关的活动节点 ID
        jo_e = edges_by_ds["journalist"]
        jo_activities = set(
            jo_e[jo_e["target"] == member]["source"].tolist()
        )
        jo_count = len(jo_activities)

        for ds in ["filah", "trout"]:
            ds_e = edges_by_ds[ds]
            ds_activities = set(ds_e[ds_e["target"] == member]["source"].tolist())
            overlap = len(ds_activities & jo_activities)
            coverage = round(overlap / jo_count, 4) if jo_count > 0 else 0.0

            records.append({
                "member":          member,
                "dataset":         ds,
                "ds_activity_cnt": len(ds_activities),
                "jo_activity_cnt": jo_count,
                "overlap_cnt":     overlap,
                "coverage":        coverage,
            })

    return pd.DataFrame(records)


# ── 3. 议题产业分布 ────────────────────────────────────────

def compute_topic_distribution(
    nodes_by_ds: dict[str, pd.DataFrame],
    edges_by_ds: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """
    每个数据集中，discussion/plan 节点按议题产业分类的数量。
    """
    records = []
    for ds, edf in edges_by_ds.items():
        ndf = nodes_by_ds[ds]
        # 取 about / plan 边 → 找到 discussion/plan 节点 → 识别 topic
        about_edges = edf[edf["role"].isin(["about", "plan"])]
        for _, row in about_edges.iterrows():
            topic_key = extract_topic_from_id(str(row.get("target", "")))
            if not topic_key:
                topic_key = extract_topic_from_id(str(row.get("source", "")))
            industry = get_topic_industry(topic_key)
            bias = get_topic_bias_score(topic_key)
            records.append({
                "dataset":    ds,
                "topic_key":  topic_key,
                "industry":   industry,
                "bias_score": bias,
            })

    df = pd.DataFrame(records)
    dist = (
        df.groupby(["dataset", "industry"])
        .size()
        .reset_index(name="count")
    )
    return dist


# ── 4. Sentiment 聚合 ─────────────────────────────────────

def compute_sentiment_agg(participant_df: pd.DataFrame) -> pd.DataFrame:
    """
    每位成员 × 每个产业 × 每个数据集的情感均值和计数。
    """
    df = participant_df[
        participant_df["is_committee_member"] &
        participant_df["topic_industry"].isin(["fishing", "tourism", "mixed"])
    ].copy()

    agg = (
        df.groupby(["dataset", "target", "topic_industry"])
        .agg(
            sentiment_mean=("sentiment", "mean"),
            sentiment_std=("sentiment", "std"),
            count=("sentiment", "count"),
        )
        .reset_index()
        .rename(columns={"target": "member", "topic_industry": "industry"})
    )
    agg["sentiment_mean"] = agg["sentiment_mean"].round(4)
    agg["sentiment_std"] = agg["sentiment_std"].fillna(0).round(4)
    return agg


# ── 5. 节点类型构成 ────────────────────────────────────────

def compute_node_type_counts(nodes_by_ds: dict[str, pd.DataFrame]) -> pd.DataFrame:
    records = []
    for ds, ndf in nodes_by_ds.items():
        counts = ndf["type"].value_counts().reset_index()
        counts.columns = ["node_type", "count"]
        counts["dataset"] = ds
        records.append(counts)
    return pd.concat(records, ignore_index=True)


# ── 6. Trip zone 分布 ─────────────────────────────────────

def compute_trip_zone_dist(
    nodes_by_ds: dict[str, pd.DataFrame],
    edges_by_ds: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """
    各数据集 trip 节点途经 place 的 zone 分布。
    """
    records = []
    for ds, ndf in nodes_by_ds.items():
        edf = edges_by_ds[ds]
        places = ndf[ndf["type"] == "place"][["id", "zone", "zone_detail", "name", "lat", "lon"]].copy()
        trips = ndf[ndf["type"] == "trip"]["id"]
        trip_edges = edf[
            (edf["role"] == "") &
            (edf["source"].isin(trips)) &
            (~edf["target"].isin(COMMITTEE_MEMBERS))
        ]
        merged = trip_edges.merge(places, left_on="target", right_on="id", how="left")
        merged["dataset"] = ds
        zone_dist = (
            merged.groupby(["dataset", "zone"])
            .size()
            .reset_index(name="count")
        )
        records.append(zone_dist)

    result = pd.concat(records, ignore_index=True).fillna("unknown")
    result["zone_score"] = result["zone"].map(ZONE_SCORE).fillna(0)
    return result


# ── 7. 缺失证据 ───────────────────────────────────────────

def compute_missing_evidence(
    nodes_by_ds: dict[str, pd.DataFrame],
    edges_by_ds: dict[str, pd.DataFrame],
) -> dict[str, pd.DataFrame]:
    """
    全量中存在、而子集中缺失的活动节点，并标记关联的人。
    返回 {"filah": df, "trout": df}，附产业分类和关联人员。
    """
    result = {}
    jo_ndf = nodes_by_ds["journalist"]
    jo_edf = edges_by_ds["journalist"]
    
    # 建立活动节点 -> 人员的映射
    activity_to_members = jo_edf[jo_edf["target"].isin(COMMITTEE_MEMBERS)].groupby("source")["target"].apply(list).to_dict()

    for ds in ["filah", "trout"]:
        ds_nodes = set(nodes_by_ds[ds]["id"].tolist())
        jo_nodes = set(jo_ndf["id"].tolist())
        missing_ids = jo_nodes - ds_nodes

        missing_df = jo_ndf[jo_ndf["id"].isin(missing_ids)].copy()
        missing_df["topic_key"] = missing_df["id"].apply(extract_topic_from_id)
        missing_df["topic_industry"] = missing_df["topic_key"].apply(get_topic_industry)
        missing_df["topic_bias_score"] = missing_df["topic_key"].apply(get_topic_bias_score)
        
        # 关联人员
        missing_df["related_members"] = missing_df["id"].apply(lambda x: activity_to_members.get(x, []))
        
        result[ds] = missing_df.reset_index(drop=True)

    return result


# ── 8. 成员活动汇总 ────────────────────────────────────────

def compute_member_activity(
    nodes_by_ds: dict[str, pd.DataFrame],
    edges_by_ds: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """
    每位成员在每个数据集中的活动类型数量。
    活动类型：participant（含 discussion/plan）、trip、meeting
    """
    records = []
    for ds, edf in edges_by_ds.items():
        ndf = nodes_by_ds[ds]
        node_type_map = dict(zip(ndf["id"], ndf["type"]))

        for member in COMMITTEE_MEMBERS:
            member_edges = edf[edf["target"] == member]

            # 识别活动类型
            participant_cnt = int((member_edges["role"] == "participant").sum())
            
            # 统计行程数：role 为空且 source 节点类型为 trip
            trip_edges = member_edges[member_edges["role"].isna() | (member_edges["role"] == "")]
            if not trip_edges.empty:
                trip_cnt = int(trip_edges["source"].apply(
                    lambda x: node_type_map.get(x, "") == "trip"
                ).sum())
            else:
                trip_cnt = 0

            # 参与的 meeting（通过 participant 边 → source 是 discussion/plan → 找 part_of → meeting）
            part_of_edges = edf[edf["role"] == "part_of"]
            disc_plan_ids = member_edges[member_edges["role"] == "participant"]["source"].tolist()
            # 根据 compute_meeting_topic_distribution 的逻辑，通常是 DP --(part_of)--> Meeting
            meetings_via_participation = part_of_edges[
                part_of_edges["source"].isin(disc_plan_ids)
            ]["target"].unique().tolist()
            meeting_cnt = len(meetings_via_participation)

            # 参与的 topic（通过 about/plan 边）
            about_edges = edf[edf["role"].isin(["about", "plan"])]
            related_topics = about_edges[
                about_edges["source"].isin(disc_plan_ids)
            ]["target"].unique().tolist()
            topic_cnt = len([t for t in related_topics if extract_topic_from_id(t)])

            records.append({
                "member":          member,
                "dataset":         ds,
                "participant_cnt": participant_cnt,
                "trip_cnt":        trip_cnt,
                "meeting_cnt":     meeting_cnt,
                "topic_cnt":       topic_cnt,
                "total_activity":  participant_cnt + trip_cnt,
                "in_dataset":      member in nodes_by_ds[ds].get("id", pd.Series()).values
                                   if "id" in nodes_by_ds[ds].columns else False,
            })

    df = pd.DataFrame(records)

    # 修正 in_dataset：检查是否有 entity.person 节点
    for ds, ndf in nodes_by_ds.items():
        persons_in_ds = ndf[ndf["type"] == "entity.person"]["id"].tolist()
        mask = (df["dataset"] == ds)
        df.loc[mask, "in_dataset"] = df.loc[mask, "member"].isin(persons_in_ds)

    return df


# ── 9. 会议覆盖 ────────────────────────────────────────────

def compute_meeting_coverage(meeting_df: pd.DataFrame) -> pd.DataFrame:
    """标记每次会议存在于哪些数据集（全量16次，各子集覆盖多少）。"""
    meeting_df["in_filah"] = meeting_df["present_in"].apply(lambda x: "filah" in x)
    meeting_df["in_trout"] = meeting_df["present_in"].apply(lambda x: "trout" in x)
    meeting_df["in_journalist"] = meeting_df["present_in"].apply(lambda x: "journalist" in x)
    meeting_df["exclusive_to_journalist"] = (
        meeting_df["in_journalist"] & ~meeting_df["in_filah"] & ~meeting_df["in_trout"]
    )
    return meeting_df


# ── 10. 会议议题分布（用于 StreamGraph） ──────────────────────────

def compute_meeting_topic_distribution(
    nodes_by_ds: dict[str, pd.DataFrame],
    edges_by_ds: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """
    统计每个会议中讨论的不同产业议题的数量。
    """
    edf = edges_by_ds["journalist"]
    
    # 1. 找到 Meeting -> (Discussion/Plan)
    # 通常是 Discussion/Plan --(part_of)--> Meeting
    part_of = edf[edf["role"] == "part_of"]
    
    # 2. 找到 (Discussion/Plan) -> Topic
    # 通常是 Discussion --(about)--> Topic 或 Plan --(plan)--> Topic
    about_plan = edf[edf["role"].isin(["about", "plan"])]
    
    # 我们需要找到所有连通 Meeting 和 Topic 的路径
    # 路径 A: Topic <--(about/plan)-- DP --(part_of)--> Meeting
    m_to_dp = part_of[["source", "target"]].rename(columns={"source": "dp_id", "target": "meeting_id"})
    dp_to_t = about_plan[["source", "target"]].rename(columns={"source": "dp_id", "target": "topic_id"})
    
    m_dp_t = m_to_dp.merge(dp_to_t, on="dp_id")
    
    # 如果 m_dp_t 为空，尝试反向角色
    if m_dp_t.empty:
        # 尝试 Meeting --(part_of)--> DP
        m_to_dp_rev = part_of[["source", "target"]].rename(columns={"target": "dp_id", "source": "meeting_id"})
        m_dp_t = m_to_dp_rev.merge(dp_to_t, on="dp_id")

    # 提取 industry
    m_dp_t["topic_key"] = m_dp_t["topic_id"].apply(extract_topic_from_id)
    m_dp_t["industry"] = m_dp_t["topic_key"].apply(get_topic_industry)
    
    # 过滤掉 unknown
    m_dp_t = m_dp_t[m_dp_t["industry"] != "unknown"]
    
    # 按会议和产业分组计数
    dist = m_dp_t.groupby(["meeting_id", "industry"]).size().reset_index(name="count")
    
    return dist


# ── 主入口 ────────────────────────────────────────────────

def run_all(nodes_by_ds, edges_by_ds, topic_df, participant_df, trip_df, meeting_df):
    print("\n=== 计算分析指标 ===")

    bias = compute_bias_index(participant_df)
    print(f"[bias_index] {len(bias)} 条记录")

    sent_bias = compute_sentiment_bias_index(participant_df)
    print(f"[sentiment_bias] {len(sent_bias)} 条记录")

    coverage = compute_coverage(nodes_by_ds, edges_by_ds)
    print(f"[coverage] {len(coverage)} 条记录")
    print(coverage[["member", "dataset", "coverage"]].to_string(index=False))

    topic_dist = compute_topic_distribution(nodes_by_ds, edges_by_ds)
    print(f"[topic_distribution] {len(topic_dist)} 条记录")

    sentiment_agg = compute_sentiment_agg(participant_df)
    print(f"[sentiment_agg] {len(sentiment_agg)} 条记录")

    node_types = compute_node_type_counts(nodes_by_ds)
    print(f"[node_type_counts] {len(node_types)} 条记录")

    trip_zone = compute_trip_zone_dist(nodes_by_ds, edges_by_ds)
    print(f"[trip_zone_dist] {len(trip_zone)} 条记录")

    missing = compute_missing_evidence(nodes_by_ds, edges_by_ds)
    for ds, mdf in missing.items():
        print(f"[missing_from_{ds}] {len(mdf)} 个缺失节点")
        if len(mdf) > 0:
            ind_dist = mdf["topic_industry"].value_counts().to_dict()
            print(f"  产业分布: {ind_dist}")

    member_act = compute_member_activity(nodes_by_ds, edges_by_ds)
    print(f"[member_activity] {len(member_act)} 条记录")

    meeting_cov = compute_meeting_coverage(meeting_df)
    exclusive = meeting_cov[meeting_cov["exclusive_to_journalist"]]
    print(f"[meeting_coverage] 仅全量独有会议: {len(exclusive)} 次")

    meeting_topic_dist = compute_meeting_topic_distribution(nodes_by_ds, edges_by_ds)
    print(f"[meeting_topic_dist] {len(meeting_topic_dist)} 条记录")

    return {
        "bias_index":        bias,
        "sentiment_bias":    sent_bias,
        "coverage":          coverage,
        "topic_distribution": topic_dist,
        "sentiment_agg":     sentiment_agg,
        "node_type_counts":  node_types,
        "trip_zone_dist":    trip_zone,
        "missing_filah":     missing["filah"],
        "missing_trout":     missing["trout"],
        "member_activity":   member_act,
        "meeting_coverage":  meeting_cov,
        "meeting_topic_dist": meeting_topic_dist,
    }


if __name__ == "__main__":
    from parse_graph import main as parse_main
    nodes_by_ds, edges_by_ds, topic_df, participant_df, trip_df, meeting_df = parse_main()
    metrics = run_all(nodes_by_ds, edges_by_ds, topic_df, participant_df, trip_df, meeting_df)
