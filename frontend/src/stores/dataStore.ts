/**
 * dataStore.ts
 * 全局数据仓库：加载 public/data/ 下的所有预处理 JSON，
 * 并提供各视图所需的派生数据。
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  OverviewItem, BiasIndexItem, CoverageItem, TopicDistItem,
  SentimentAggItem, NodeTypeCountItem, TripZoneItem, MemberActivityItem,
  MeetingCoverageItem, TopicMetaItem, PlaceNode, TripRecord, MissingNode,
  DatasetKey, MemberName,
} from '../types'

const BASE = import.meta.env.BASE_URL + 'data/'

async function fetchJSON<T>(file: string): Promise<T> {
  const res = await fetch(BASE + file)
  if (!res.ok) throw new Error(`Failed to load ${file}: ${res.status}`)
  return res.json()
}

export const useDataStore = defineStore('data', () => {
  // ── 加载状态 ────────────────────────────────────────────
  const loading  = ref(false)
  const loaded   = ref(false)
  const error    = ref<string | null>(null)

  // ── 原始数据 ────────────────────────────────────────────
  const overview         = ref<OverviewItem[]>([])
  const biasIndex        = ref<BiasIndexItem[]>([])
  const coverage         = ref<CoverageItem[]>([])
  const topicDist        = ref<TopicDistItem[]>([])
  const sentimentAgg     = ref<SentimentAggItem[]>([])
  const nodeTypeCounts   = ref<NodeTypeCountItem[]>([])
  const tripZoneDist     = ref<TripZoneItem[]>([])
  const memberActivity   = ref<MemberActivityItem[]>([])
  const meetingCoverage  = ref<MeetingCoverageItem[]>([])
  const topicMeta        = ref<TopicMetaItem[]>([])
  const meetingTopicDist = ref<Array<{ meeting_id: string, industry: string, count: number }>>([])
  const fullGraph        = ref<{ nodes: any[], edges: any[] }>({ nodes: [], edges: [] })
  const placeNodes       = ref<PlaceNode[]>([])
  const tripRecords      = ref<TripRecord[]>([])
  const missingFilah     = ref<MissingNode[]>([])
  const missingTrout     = ref<MissingNode[]>([])

  // ── 加载入口 ────────────────────────────────────────────
  async function loadAll() {
    if (loaded.value) return
    loading.value = true
    error.value   = null
    try {
      const [
        ov, bi, cov, td, sa, ntc, tzd, ma, mc, tm, mtd, graph, pn, tr, mf, mt,
      ] = await Promise.all([
        fetchJSON<OverviewItem[]>('overview.json'),
        fetchJSON<BiasIndexItem[]>('bias_index.json'),
        fetchJSON<CoverageItem[]>('coverage.json'),
        fetchJSON<TopicDistItem[]>('topic_distribution.json'),
        fetchJSON<SentimentAggItem[]>('sentiment_agg.json'),
        fetchJSON<NodeTypeCountItem[]>('node_type_counts.json'),
        fetchJSON<TripZoneItem[]>('trip_zone_dist.json'),
        fetchJSON<MemberActivityItem[]>('member_activity.json'),
        fetchJSON<MeetingCoverageItem[]>('meeting_coverage.json'),
        fetchJSON<TopicMetaItem[]>('topic_meta.json'),
        fetchJSON<any[]>('meeting_topic_dist.json'),
        fetchJSON<any>('full_graph.json'),
        fetchJSON<PlaceNode[]>('place_nodes.json'),
        fetchJSON<TripRecord[]>('trip_records.json'),
        fetchJSON<MissingNode[]>('missing_filah.json'),
        fetchJSON<MissingNode[]>('missing_trout.json'),
      ])
      overview.value        = ov
      biasIndex.value       = bi
      coverage.value        = cov
      topicDist.value       = td
      sentimentAgg.value    = sa
      nodeTypeCounts.value  = ntc
      tripZoneDist.value    = tzd
      memberActivity.value  = ma
      meetingCoverage.value = mc
      topicMeta.value       = tm
      meetingTopicDist.value = mtd
      fullGraph.value       = graph
      placeNodes.value      = pn
      tripRecords.value     = tr
      missingFilah.value    = mf
      missingTrout.value    = mt
      loaded.value = true
    } catch (e: any) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  // ── 派生计算 ────────────────────────────────────────────

  /** 整体 bias_index（member === 'ALL'），按数据集返回 */
  const overallBias = computed(() =>
    biasIndex.value.filter(d => d.member === 'ALL')
  )

  /** 个人 bias_index，过滤出委员会成员 */
  const memberBias = computed(() =>
    biasIndex.value.filter(d => d.member !== 'ALL')
  )

  /** 按成员返回 coverage（FILAH + TROUT） */
  function getCoverageByMember(member: MemberName) {
    return coverage.value.filter(d => d.member === member)
  }

  /** 按数据集返回 member_activity */
  function getMemberActivityByDataset(ds: DatasetKey) {
    return memberActivity.value.filter(d => d.dataset === ds)
  }

  /** 按数据集返回 topic 产业分布 */
  function getTopicDistByDataset(ds: DatasetKey) {
    return topicDist.value.filter(d => d.dataset === ds)
  }

  /** 全量独有的会议 */
  const exclusiveMeetings = computed(() =>
    meetingCoverage.value.filter(m => m.exclusive_to_journalist)
  )

  /** 按成员 + 数据集筛选 trip 记录 */
  function getTripsByPerson(person: string, ds?: DatasetKey) {
    return tripRecords.value.filter(
      t => t.person === person && (ds ? t.dataset === ds : true)
    )
  }

  return {
    // 状态
    loading, loaded, error,
    // 原始数据
    overview, biasIndex, coverage, topicDist, sentimentAgg,
    nodeTypeCounts, tripZoneDist, memberActivity, meetingCoverage,
    topicMeta, meetingTopicDist, fullGraph, placeNodes, tripRecords, missingFilah, missingTrout,
    // 方法
    loadAll,
    // 派生
    overallBias, memberBias, exclusiveMeetings,
    getCoverageByMember, getMemberActivityByDataset,
    getTopicDistByDataset, getTripsByPerson,
  }
})
