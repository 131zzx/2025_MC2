<template>
  <div class="q2-view">
    <a-alert
      message="Q2 · 委员会如何分配时间？整体是否偏袒？"
      description="基于全量数据集（journalist），分析 COOTEFOO 六名成员的时间分配模式，判断委员会整体是否对渔业或旅游存在系统性偏袒。"
      type="success"
      show-icon
      style="margin-bottom: 20px; background: var(--color-surface); border-color: var(--color-border)"
    />

    <template v-if="dataStore.loaded.value">
      <!-- 顶部：整体偏见指数仪表盘 -->
      <div class="grid-3" style="margin-bottom: 20px">
        <div class="card metric-card">
          <div class="card-title">整体 Bias Index（全量）</div>
          <div class="metric-value" :style="{ color: biasColor }">
            {{ overallBiasValue >= 0 ? '+' : '' }}{{ overallBiasValue.toFixed(3) }}
          </div>
          <div class="metric-desc">
            {{ biasLabel }}
          </div>
        </div>
        <div class="card metric-card">
          <div class="card-title">渔业活动占比</div>
          <div class="metric-value" style="color: var(--color-fishing)">
            {{ fishingPct }}%
          </div>
          <div class="metric-desc">基于 participant 边的 topic_industry 统计</div>
        </div>
        <div class="card metric-card">
          <div class="card-title">旅游活动占比</div>
          <div class="metric-value" style="color: var(--color-tourism)">
            {{ tourismPct }}%
          </div>
          <div class="metric-desc">基于 participant 边的 topic_industry 统计</div>
        </div>
      </div>

      <!-- 第二行：成员热力矩阵 + 会议覆盖 -->
      <div class="grid-2" style="margin-bottom: 20px">
        <div class="card">
          <div class="card-title">成员 × 产业 情感热力矩阵（全量）</div>
          <SentimentHeatmap :data="sentimentData" />
        </div>
        <div class="card">
          <div class="card-title">逐人偏见指数（全量）</div>
          <BiasIndexBar :data="memberBiasData" />
        </div>
      </div>

      <!-- 第三行：Trip 地图 + Zone 分布 -->
      <div class="grid-2">
        <div class="card">
          <div class="card-title">行程地点分布（全量 trip，按 zone 着色）</div>
          <TripMap :places="dataStore.placeNodes.value" :trips="joTrips" />
        </div>
        <div class="card">
          <div class="card-title">Trip 落点 Zone 分布对比</div>
          <TripZoneChart :data="dataStore.tripZoneDist.value" />
        </div>
      </div>
    </template>

    <a-spin v-else-if="dataStore.loading.value" tip="加载数据中..." style="display: block; margin: 80px auto" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useDataStore } from '../stores/dataStore'
import BiasIndexBar from '../components/charts/BiasIndexBar.vue'
import SentimentHeatmap from '../components/charts/SentimentHeatmap.vue'
import TripMap from '../components/map/TripMap.vue'
import TripZoneChart from '../components/charts/TripZoneChart.vue'

const dataStore = useDataStore()

const overallBiasValue = computed(() => {
  const item = dataStore.overallBias.value.find(d => d.dataset === 'journalist')
  return item?.bias_index ?? 0
})

const biasColor = computed(() => {
  const v = overallBiasValue.value
  if (v > 0.1) return 'var(--color-tourism)'
  if (v < -0.1) return 'var(--color-fishing)'
  return '#94a3b8'
})

const biasLabel = computed(() => {
  const v = overallBiasValue.value
  if (v > 0.15) return '委员会整体偏向旅游议题'
  if (v < -0.15) return '委员会整体偏向渔业议题'
  return '委员会整体较为均衡'
})

const topicDistJo = computed(() =>
  dataStore.topicDist.value.filter(d => d.dataset === 'journalist')
)

const fishingPct = computed(() => {
  const total = topicDistJo.value.reduce((s, d) => s + d.count, 0)
  const fishing = topicDistJo.value.find(d => d.industry === 'fishing')?.count ?? 0
  return total ? ((fishing / total) * 100).toFixed(1) : '0'
})

const tourismPct = computed(() => {
  const total = topicDistJo.value.reduce((s, d) => s + d.count, 0)
  const tourism = topicDistJo.value.find(d => d.industry === 'tourism')?.count ?? 0
  return total ? ((tourism / total) * 100).toFixed(1) : '0'
})

const sentimentData = computed(() =>
  dataStore.sentimentAgg.value.filter(d => d.dataset === 'journalist')
)

const memberBiasData = computed(() =>
  dataStore.memberBias.value.filter(d => d.dataset === 'journalist')
)

const joTrips = computed(() =>
  dataStore.tripRecords.value.filter(d => d.dataset === 'journalist')
)
</script>

<style scoped>
.q2-view { max-width: 1400px; }
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; }

.metric-card { text-align: center; }
.metric-value {
  font-size: 36px;
  font-weight: 700;
  margin: 16px 0 8px;
}
.metric-desc {
  font-size: 12px;
  color: var(--color-text-muted);
}
</style>
