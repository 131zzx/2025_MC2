<template>
  <div class="summary-wrap">
    <div v-for="item in summaryItems" :key="item.label" class="summary-item">
      <div class="item-label">
        <TermExplanation v-if="item.label.includes('偏见')" term="采样偏见">{{ item.label }}</TermExplanation>
        <TermExplanation v-else-if="item.label.includes('Trip')" term="行程">{{ item.label }}</TermExplanation>
        <TermExplanation v-else-if="item.label.includes('议题')" term="议题">{{ item.label }}</TermExplanation>
        <template v-else>{{ item.label }}</template>
      </div>
      <div class="item-value" :style="{ color: item.color }">{{ item.value }}</div>
      <div class="item-desc">{{ item.desc }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { NodeTypeCountItem, TopicDistItem, CoverageItem } from '../../types'
import TermExplanation from './TermExplanation.vue'

const props = defineProps<{
  nodeTypes:  NodeTypeCountItem[]
  topicDist:  TopicDistItem[]
  coverage:   CoverageItem[]
}>()

const summaryItems = computed(() => {
  // 1. 人员覆盖
  const zeroCoverage = props.coverage.filter(d => d.dataset === 'filah' && d.coverage === 0).length
  // 2. trip 占比
  const filahNodes = props.nodeTypes.filter(d => d.dataset === 'filah')
  const totalFilah = filahNodes.reduce((s, d) => s + d.count, 0)
  const tripCnt    = filahNodes.find(d => d.node_type === 'trip')?.count ?? 0
  const tripPct    = totalFilah ? ((tripCnt / totalFilah) * 100).toFixed(1) : '0'

  const jNodes = props.nodeTypes.filter(d => d.dataset === 'journalist')
  const totalJ = jNodes.reduce((s, d) => s + d.count, 0)
  const jTrip  = jNodes.find(d => d.node_type === 'trip')?.count ?? 0
  const jTripPct = totalJ ? ((jTrip / totalJ) * 100).toFixed(1) : '0'

  // 3. 议题产业分布偏差
  const filahDist = props.topicDist.filter(d => d.dataset === 'filah')
  const joDist    = props.topicDist.filter(d => d.dataset === 'journalist')
  const filahTotalTopics = filahDist.reduce((s, d) => s + d.count, 0)
  const joTotalTopics    = joDist.reduce((s, d) => s + d.count, 0)
  const filahTourism = (filahDist.find(d => d.industry === 'tourism')?.count ?? 0) / (filahTotalTopics || 1)
  const joTourism    = (joDist.find(d => d.industry === 'tourism')?.count ?? 0) / (joTotalTopics || 1)
  const tourismDiff  = ((filahTourism - joTourism) * 100).toFixed(1)

  return [
    {
      label: '人员采样偏见',
      value: `${zeroCoverage}/6 人 0% 覆盖`,
      desc:  'Ed Helpsford、Teddy Goldstein、Tante Titan 在 FILAH 中完全缺失，导致无法代表委员会整体',
      color: '#ef4444',
    },
    {
      label: 'Trip 记录过重',
      value: `FILAH ${tripPct}%  vs  全量 ${jTripPct}%`,
      desc:  `FILAH 中 trip 节点占总节点 ${tripPct}%，远超全量比例，数据形态偏「行程日志」而非会议记录`,
      color: '#f59e0b',
    },
    {
      label: '旅游议题占比偏差',
      value: `${Number(tourismDiff) >= 0 ? '+' : ''}${tourismDiff}%`,
      desc:  `FILAH 记录的旅游类讨论/计划占比相对全量${Number(tourismDiff) > 0 ? '偏高' : '偏低'}，说明议题采样存在系统性倾斜`,
      color: '#9333ea',
    },
  ]
})
</script>

<style scoped>
.summary-wrap { display: flex; flex-direction: column; gap: 16px; }
.summary-item { padding: 12px; background: rgba(255,255,255,0.03); border-radius: 8px; border: 1px solid var(--color-border); }
.item-label { font-size: 11px; font-weight: 600; color: var(--color-text-muted); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px; }
.item-value { font-size: 18px; font-weight: 700; margin-bottom: 6px; }
.item-desc { font-size: 12px; color: var(--color-text-muted); line-height: 1.6; }
</style>
