<template>
  <div class="bias-view">

    <!-- 顶部摘要栏 -->
    <section class="section">
      <div class="section-header">
        <h2 class="section-title">数据集概览</h2>
        <p class="section-desc">三份数据集收录了委员会成员的活动记录，在节点数量与议题覆盖上各有差异</p>
      </div>
      <DatasetSummaryCards :node-types="store.nodeTypeCounts" />
    </section>

    <!-- 偏见指数 + 节点类型 -->
    <section class="section">
      <div class="grid-2">
        <!-- 左列：偏见天平 -->
        <div class="card">
          <div class="card-header">
            <span class="card-title">各数据集采样偏见指数</span>
            <span class="card-hint">正值=渔业偏向；负值=旅游偏向</span>
          </div>
          <div class="bias-gauges">
            <div
              v-for="dsInfo in datasetInfos" :key="dsInfo.key"
              class="gauge-item"
              :class="linking.isDatasetActive(dsInfo.key) && 'gauge-item--on'"
              @click="linking.toggleDataset(dsInfo.key)"
            >
              <div class="gauge-ds-label" :style="{ color: dsInfo.color }">
                {{ dsInfo.label }}
              </div>
              <BiasGauge
                :value="getBiasValue(dsInfo.key)"
                :label="dsInfo.label"
                :color="dsInfo.color"
              />
            </div>
          </div>
          <div class="bias-conclusion">
            <div class="conclusion-badge">
              <span class="badge-dot" :style="{ background: '#f59e0b' }" />
              FILAH 代表渔业立场（bias&gt;0），TROUT 代表旅游立场（bias&lt;0），
              记者数据集作为独立基准相对中立。三份数据集的<strong>采样立场明显对立</strong>，
              分析任一单一数据源均存在偏见风险。
            </div>
          </div>
        </div>

        <!-- 右列：节点类型 -->
        <div class="card">
          <div class="card-header">
            <span class="card-title">节点类型构成对比</span>
            <span class="card-hint">按数据集展示各类型节点数量分布</span>
          </div>
          <NodeTypeChart :data="filteredNodeTypes" />
        </div>
      </div>
    </section>

    <!-- 话题行业分布 -->
    <section class="section">
      <div class="section-header">
        <h2 class="section-title">话题行业分布</h2>
        <p class="section-desc">各数据集收录议题的行业构成——渔业占比越高，说明该数据集越关注渔业利益</p>
      </div>
      <div class="grid-3">
        <div v-for="dsInfo in activeDatasetsInfos" :key="dsInfo.key" class="card">
          <div class="card-header">
            <span class="card-ds-dot" :style="{ background: dsInfo.color }" />
            <span class="card-title">{{ dsInfo.label }}</span>
          </div>
          <IndustryDonut
            :data="store.getTopicDistByDataset(dsInfo.key)"
            :dataset="dsInfo.key"
          />
        </div>
      </div>
    </section>

    <!-- 缺失证据 -->
    <section class="section">
      <div class="grid-2">
        <div class="card">
          <div class="card-header">
            <span class="card-title">FILAH 缺失节点行业分布</span>
            <span class="card-hint">{{ store.missingFilah.length }} 个节点在记者数据集有记录但在 FILAH 中缺失</span>
          </div>
          <MissingNodeChart :data="store.missingFilah" dataset="filah" />
        </div>
        <div class="card">
          <div class="card-header">
            <span class="card-title">TROUT 缺失节点行业分布</span>
            <span class="card-hint">{{ store.missingTrout.length }} 个节点在记者数据集有记录但在 TROUT 中缺失</span>
          </div>
          <MissingNodeChart :data="store.missingTrout" dataset="trout" />
        </div>
      </div>
      <div class="evidence-summary card">
        <div class="summary-icon">▲</div>
        <div class="summary-content">
          <strong>证据完整性结论：</strong>
          FILAH 缺失的节点中渔业相关较多（隐藏对自身不利的行程），
          TROUT 缺失的节点中旅游相关较多，两份数据集均存在<strong>选择性遗漏</strong>证据的行为，
          支持 COOTEFOO 委员会的调查结论。
        </div>
      </div>
    </section>

  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useDataStore } from '../stores/dataStore'
import { uselinkingStore } from '../stores/linkingStore'
import { DATASET_COLORS, DATASET_LABELS } from '../types'
import type { DatasetKey } from '../types'

import DatasetSummaryCards from '../components/charts/DatasetSummaryCards.vue'
import BiasGauge           from '../components/charts/BiasGauge.vue'
import NodeTypeChart       from '../components/charts/NodeTypeChart.vue'
import IndustryDonut       from '../components/charts/IndustryDonut.vue'
import MissingNodeChart    from '../components/charts/MissingNodeChart.vue'

const store   = useDataStore()
const linking = uselinkingStore()

const datasetInfos = [
  { key: 'filah'      as DatasetKey, label: DATASET_LABELS.filah,      color: DATASET_COLORS.filah },
  { key: 'trout'      as DatasetKey, label: DATASET_LABELS.trout,      color: DATASET_COLORS.trout },
  { key: 'journalist' as DatasetKey, label: DATASET_LABELS.journalist, color: DATASET_COLORS.journalist },
]

const activeDatasetsInfos = computed(() =>
  datasetInfos.filter(d => linking.isDatasetActive(d.key))
)

function getBiasValue(ds: DatasetKey): number {
  const item = store.overallBias.find(d => d.dataset === ds)
  return item?.bias_index ?? 0
}

const filteredNodeTypes = computed(() =>
  store.nodeTypeCounts.filter(d => linking.isDatasetActive(d.dataset as DatasetKey))
)
</script>

<style scoped>
.bias-view { padding: 24px; display: flex; flex-direction: column; gap: 28px; }

.section { display: flex; flex-direction: column; gap: 14px; }
.section-title { font-size: 16px; font-weight: 700; color: #1e293b; margin: 0 0 4px; }
.section-desc { font-size: 12px; color: #64748b; margin: 0; }

.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }

.card {
  background: #fff; border: 1px solid #e2e8f0; border-radius: 10px;
  padding: 16px; overflow: hidden;
}
.card-header {
  display: flex; align-items: center; gap: 8px; margin-bottom: 14px;
}
.card-title { font-size: 13px; font-weight: 700; color: #1e293b; }
.card-hint  { font-size: 11px; color: #94a3b8; margin-left: auto; }
.card-ds-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }

/* 偏见天平区域 */
.bias-gauges {
  display: flex; gap: 12px; flex-wrap: wrap; justify-content: space-around;
}
.gauge-item {
  flex: 1; min-width: 150px; padding: 10px; border-radius: 8px;
  border: 2px solid #f1f5f9; cursor: pointer; transition: all .15s;
  display: flex; flex-direction: column; align-items: center;
}
.gauge-item:hover { border-color: #bfdbfe; background: #f8fafc; }
.gauge-item--on { border-color: #93c5fd; background: #eff6ff; }
.gauge-ds-label { font-size: 11px; font-weight: 700; letter-spacing: .04em; margin-bottom: 6px; }

.bias-conclusion { margin-top: 12px; }
.conclusion-badge {
  background: #fffbeb; border: 1px solid #fde68a; border-radius: 8px;
  padding: 10px 14px; font-size: 12px; color: #78350f; display: flex; gap: 8px; align-items: flex-start;
}
.badge-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; margin-top: 3px; }

/* 证据摘要 */
.evidence-summary {
  display: flex; gap: 14px; align-items: flex-start; margin-top: 4px;
  background: #fef2f2; border-color: #fecaca;
}
.summary-icon { font-size: 18px; color: #dc2626; flex-shrink: 0; margin-top: 2px; }
.summary-content { font-size: 12px; color: #7f1d1d; line-height: 1.6; }
.summary-content strong { font-weight: 700; }
</style>
