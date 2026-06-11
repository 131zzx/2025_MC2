<template>
  <div class="bias-view">

    <!-- ── 第一行：关键指标卡 ── -->
    <div class="kpi-row">
      <div v-for="ds in DS_LIST" :key="ds.key" class="kpi-card">
        <div class="kpi-header">
          <span class="kpi-dot" :style="{ background: ds.color }" />
          <span class="kpi-name">{{ ds.label }}</span>
          <span class="kpi-tag" :style="{ color: ds.color }">{{ ds.tag }}</span>
        </div>
        <div class="kpi-metrics">
          <div v-for="m in getMetrics(ds.key)" :key="m.label" class="kpi-m">
            <div class="kpi-val">{{ m.val }}</div>
            <div class="kpi-label">
              <TermExplanation v-if="['节点', '边', '行程'].includes(m.label)" :term="m.label">{{ m.label }}</TermExplanation>
              <template v-else>{{ m.label }}</template>
            </div>
          </div>
        </div>
        <div class="kpi-bias" :style="{ color: getBiasColor(ds.key) }">
          <TermExplanation term="偏差指数">偏差指数</TermExplanation>：{{ formatBias(ds.key) }}
        </div>
      </div>
    </div>

    <!-- ── 第二行：偏见对比 + 数据集指标对比 ── -->
    <div class="row-2">
      <div class="card">
        <div class="card-hd">
          <span class="card-title"><TermExplanation term="采样偏见">采样偏见</TermExplanation>指数对比</span>
          <span class="card-hint">正值偏旅游，负值偏渔业；越偏离中心线偏见越明显</span>
        </div>
        <BiasCompareChart :data="store.biasIndex" />
      </div>

      <div class="card">
        <div class="card-hd">
          <span class="card-title">数据集关键指标对比</span>
          <span class="card-hint">各数据集在<TermExplanation term="节点">节点</TermExplanation>/<TermExplanation term="边">边</TermExplanation>/<TermExplanation term="行程">行程</TermExplanation>/会议四个维度的规模差异</span>
        </div>
        <DatasetCompareBar :data="store.overview" />
      </div>
    </div>

    <!-- ── 第三行：话题行业分布 ── -->
    <div class="card">
      <div class="card-hd">
        <span class="card-title">各数据集<TermExplanation term="议题">话题</TermExplanation>行业构成</span>
        <span class="card-hint">点击图例行业可过滤；渔业占比越高说明该数据集越关注渔业利益</span>
      </div>
      <TopicIndustryBar :data="store.topicDist" />
    </div>

    <!-- ── 第四行：缺失证据 ── -->
    <div class="row-2">
      <div class="card">
        <div class="card-hd">
          <span class="card-title">FILAH 缺失<TermExplanation term="节点">节点</TermExplanation>分布</span>
          <span class="card-hint">{{ store.missingFilah.length }} 个节点在记者数据集有记录，FILAH 中缺失</span>
        </div>
        <MissingNodeChart :data="store.missingFilah" dataset="filah" />
      </div>
      <div class="card">
        <div class="card-hd">
          <span class="card-title">TROUT 缺失<TermExplanation term="节点">节点</TermExplanation>分布</span>
          <span class="card-hint">{{ store.missingTrout.length }} 个节点在记者数据集有记录，TROUT 中缺失</span>
        </div>
        <MissingNodeChart :data="store.missingTrout" dataset="trout" />
      </div>
    </div>


  </div>
</template>

<script setup lang="ts">
import { useDataStore } from '../stores/dataStore'
import { DATASET_COLORS, INDUSTRY_COLORS } from '../types'
import type { DatasetKey } from '../types'

import BiasCompareChart from '../components/charts/BiasCompareChart.vue'
import DatasetCompareBar from '../components/charts/DatasetCompareBar.vue'
import TopicIndustryBar from '../components/charts/TopicIndustryBar.vue'
import MissingNodeChart from '../components/charts/MissingNodeChart.vue'
import TermExplanation from '../components/shared/TermExplanation.vue'

const store = useDataStore()

const DS_LIST = [
  { key: 'filah'      as DatasetKey, label: 'FILAH',  tag: '渔业方',   color: DATASET_COLORS.filah },
  { key: 'trout'      as DatasetKey, label: 'TROUT',  tag: '旅游方',   color: DATASET_COLORS.trout },
  { key: 'journalist' as DatasetKey, label: '记者',   tag: '独立基准', color: DATASET_COLORS.journalist },
]

function getMetrics(ds: DatasetKey) {
  const ov = store.overview.find(d => d.dataset === ds)
  if (!ov) return []
  return [
    { label: '节点', val: ov.node_count },
    { label: '边',   val: ov.edge_count },
    { label: '行程', val: ov.trip_count },
    { label: '成员', val: ov.member_count },
  ]
}

function getBiasValue(ds: DatasetKey): number {
  return store.overallBias.find(d => d.dataset === ds)?.bias_index ?? 0
}
function formatBias(ds: DatasetKey): string {
  const v = getBiasValue(ds)
  return (v > 0 ? '+' : '') + v.toFixed(3)
}
function getBiasColor(ds: DatasetKey): string {
  const v = getBiasValue(ds)
  if (v > 0.15) return INDUSTRY_COLORS.tourism
  if (v < -0.15) return INDUSTRY_COLORS.fishing
  return '#64748b'
}
</script>

<style scoped>
.bias-view { padding: 20px; display: flex; flex-direction: column; gap: 16px; }

/* KPI 卡行 */
.kpi-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.kpi-card {
  background: #fff; border: 1px solid #e2e8f0; border-radius: 10px;
  padding: 14px 16px;
}
.kpi-header { display: flex; align-items: center; gap: 7px; margin-bottom: 12px; }
.kpi-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.kpi-name { font-size: 14px; font-weight: 700; color: #1e293b; }
.kpi-tag  { font-size: 10px; margin-left: auto; font-weight: 600; }

.kpi-metrics { display: grid; grid-template-columns: repeat(4, 1fr); gap: 4px; margin-bottom: 10px; }
.kpi-m { text-align: center; }
.kpi-val   { font-size: 18px; font-weight: 800; color: #1e293b; line-height: 1.2; }
.kpi-label { font-size: 10px; color: #94a3b8; margin-top: 2px; }
.kpi-bias  { font-size: 12px; font-weight: 700; padding-top: 8px; border-top: 1px solid #f1f5f9; }

/* 两列行 */
.row-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }

/* 通用卡片 */
.card { background: #fff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 16px; }
.card-hd { display: flex; align-items: baseline; gap: 8px; margin-bottom: 14px; flex-wrap: wrap; }
.card-title { font-size: 13px; font-weight: 700; color: #1e293b; }
.card-hint  { font-size: 11px; color: #94a3b8; }

</style>
