// ── 数据集标识 ────────────────────────────────────────────
export type DatasetKey = 'filah' | 'trout' | 'journalist'

export const DATASET_LABELS: Record<DatasetKey, string> = {
  filah:      'FILAH',
  trout:      'TROUT',
  journalist: '全量（journalist）',
}

export const DATASET_COLORS: Record<DatasetKey, string> = {
  filah:      '#f59e0b',   // 琥珀色 → 渔业方
  trout:      '#3b82f6',   // 蓝色   → 旅游方
  journalist: '#10b981',   // 绿色   → 全量/真相
}

// ── 产业类型 ──────────────────────────────────────────────
export type Industry = 'fishing' | 'tourism' | 'mixed' | 'neutral' | 'unknown'

export const INDUSTRY_LABELS: Record<Industry, string> = {
  fishing:  '渔业',
  tourism:  '旅游',
  mixed:    '混合',
  neutral:  '中性',
  unknown:  '未知',
}

export const INDUSTRY_COLORS: Record<Industry, string> = {
  fishing:  '#0369a1',  // 深蓝
  tourism:  '#16a34a',  // 深绿
  mixed:    '#9333ea',  // 紫
  neutral:  '#6b7280',  // 灰
  unknown:  '#d1d5db',  // 浅灰
}

// ── 数据结构类型 ───────────────────────────────────────────
export interface OverviewItem {
  dataset:        DatasetKey
  dataset_label:  string
  node_count:     number
  edge_count:     number
  member_count:   number
  members:        string[]
  meeting_count:  number
  topic_count:    number
  trip_count:     number
}

export interface BiasIndexItem {
  dataset:     DatasetKey
  member:      string        // 'ALL' 表示整体
  bias_index:  number        // [-1, +1]
}

export interface CoverageItem {
  member:           string
  dataset:          'filah' | 'trout'
  ds_activity_cnt:  number
  jo_activity_cnt:  number
  overlap_cnt:      number
  coverage:         number   // [0, 1]
}

export interface TopicDistItem {
  dataset:    DatasetKey
  industry:   Industry
  count:      number
}

export interface SentimentAggItem {
  dataset:        DatasetKey
  member:         string
  industry:       Industry
  sentiment_mean: number
  sentiment_std:  number
  count:          number
}

export interface NodeTypeCountItem {
  dataset:    DatasetKey
  node_type:  string
  count:      number
}

export interface TripZoneItem {
  dataset:    DatasetKey
  zone:       string
  count:      number
  zone_score: number
}

export interface MemberActivityItem {
  member:           string
  dataset:          DatasetKey
  participant_cnt:  number
  trip_cnt:         number
  meeting_cnt:      number
  topic_cnt:        number
  total_activity:   number
  in_dataset:       boolean
}

export interface MeetingCoverageItem {
  id:                     string
  date:                   string
  label:                  string
  present_in:             DatasetKey[]
  in_filah:               boolean
  in_trout:               boolean
  in_journalist:          boolean
  exclusive_to_journalist:boolean
}

export interface TopicMetaItem {
  topic_key:   string
  industry:    Industry
  bias_score:  number
  label:       string
}

export interface PlaceNode {
  id:          string
  name:        string
  lat:         number | null
  lon:         number | null
  zone:        string
  zone_detail: string
}

export interface TripRecord {
  trip_id:  string
  person:   string
  date:     string
  start:    string
  end:      string
  places:   Array<{ id: string; name: string; zone: string; lat: number | null; lon: number | null }>
  dataset:  DatasetKey
}

export interface MissingNode {
  id:               string
  type:             string
  date?:            string
  label?:           string
  topic_key:        string | null
  topic_industry:   Industry
  topic_bias_score: number
  related_members:  string[]
}

// 所有 6 名委员会成员
export const COMMITTEE_MEMBERS = [
  'Seal',
  'Ed Helpsford',
  'Teddy Goldstein',
  'Simone Kat',
  'Tante Titan',
  'Carol Limpet',
] as const

export type MemberName = typeof COMMITTEE_MEMBERS[number]
