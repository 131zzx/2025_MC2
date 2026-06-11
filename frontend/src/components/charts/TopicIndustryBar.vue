<!--
  话题行业构成对比：三个数据集的堆叠水平条形图
  每一行是一个数据集，每段代表一种行业的话题数量占比
  点击图例可高亮某行业
-->
<template>
  <div class="tib-wrap">
    <div ref="el" class="tib-chart" />
    <!-- 图例 -->
    <div class="tib-legend">
      <button
        v-for="ind in INDS" :key="ind.key"
        class="leg-btn" :class="{ 'leg-btn--on': highlighted === ind.key || !highlighted }"
        :style="{ '--c': ind.color }"
        @click="highlighted = highlighted === ind.key ? null : ind.key"
      >
        <span class="leg-dot" :style="{ background: ind.color }" />
        {{ ind.label }}
      </button>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
export default defineComponent({ name: 'TopicIndustryBar' })
</script>

<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from 'vue'
import * as d3 from 'd3'
import type { TopicDistItem, DatasetKey } from '../../types'
import { INDUSTRY_COLORS, INDUSTRY_LABELS, DATASET_COLORS } from '../../types'

const props = defineProps<{ data: TopicDistItem[] }>()
const el = ref<HTMLElement>()
const highlighted = ref<string | null>(null)

const INDS = [
  { key: 'fishing', label: '渔业',   color: INDUSTRY_COLORS.fishing },
  { key: 'tourism', label: '旅游',   color: INDUSTRY_COLORS.tourism },
  { key: 'mixed',   label: '混合',   color: INDUSTRY_COLORS.mixed },
  { key: 'neutral', label: '中立',   color: INDUSTRY_COLORS.neutral },
  { key: 'unknown', label: '未分类', color: INDUSTRY_COLORS.unknown },
]

const DS_ORDER: DatasetKey[] = ['filah', 'trout', 'journalist']
const DS_LABELS: Record<DatasetKey, string> = { filah: 'FILAH', trout: 'TROUT', journalist: '记者' }

function draw() {
  if (!el.value) return
  el.value.innerHTML = ''

  const W = el.value.clientWidth || 500
  const barH = 34
  const gap = 10
  const H = DS_ORDER.length * (barH + gap) + 40
  const m = { top: 10, right: 60, bottom: 20, left: 70 }
  const iw = W - m.left - m.right

  const svg = d3.select(el.value).append('svg').attr('width', W).attr('height', H)
  const g = svg.append('g').attr('transform', `translate(${m.left},${m.top})`)

  DS_ORDER.forEach((ds, di) => {
    const dsData = props.data.filter(d => d.dataset === ds)
    const total  = d3.sum(dsData, d => d.count) || 1
    const byInd  = new Map(dsData.map(d => [d.industry, d.count]))

    const baseY = di * (barH + gap)
    let offsetX = 0

    // DS 标签
    g.append('text')
      .attr('x', -8).attr('y', baseY + barH / 2)
      .attr('text-anchor', 'end').attr('dominant-baseline', 'middle')
      .attr('font-size', 12).attr('font-weight', 700)
      .attr('fill', DATASET_COLORS[ds])
      .text(DS_LABELS[ds])

    // 堆叠条
    INDS.forEach(ind => {
      const cnt = byInd.get(ind.key as any) ?? 0
      if (!cnt) return
      const segW = (cnt / total) * iw
      const isHL = !highlighted.value || highlighted.value === ind.key
      const color = isHL ? ind.color : '#e2e8f0'
      const opacity = isHL ? 0.85 : 0.3

      const rect = g.append('rect')
        .attr('x', offsetX).attr('y', baseY)
        .attr('width', segW).attr('height', barH)
        .attr('fill', color).attr('opacity', opacity)

      // 只在足够宽时显示文字
      if (segW > 28) {
        g.append('text')
          .attr('x', offsetX + segW / 2).attr('y', baseY + barH / 2)
          .attr('text-anchor', 'middle').attr('dominant-baseline', 'middle')
          .attr('font-size', 10).attr('fill', '#fff').attr('font-weight', 600)
          .attr('pointer-events', 'none')
          .text(Math.round(cnt / total * 100) + '%')
      }

      // 悬停 tooltip
      rect.append('title').text(`${DS_LABELS[ds]} · ${ind.label}：${cnt} 个话题 (${(cnt / total * 100).toFixed(1)}%)`)

      offsetX += segW
    })

    // 总数标签
    g.append('text')
      .attr('x', iw + 6).attr('y', baseY + barH / 2)
      .attr('dominant-baseline', 'middle').attr('font-size', 11)
      .attr('fill', '#94a3b8').attr('font-weight', 500)
      .text(`${total} 个`)
  })
}

const ro = new ResizeObserver(draw)
onMounted(() => { ro.observe(el.value!); draw() })
onUnmounted(() => ro.disconnect())
watch([() => props.data, highlighted], draw, { deep: true })
</script>

<style scoped>
.tib-wrap { width: 100%; }
.tib-chart { width: 100%; }
.tib-legend { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }
.leg-btn {
  display: flex; align-items: center; gap: 5px;
  padding: 4px 10px; border-radius: 20px;
  border: 1px solid #e2e8f0; background: #f8fafc;
  font-size: 11px; cursor: pointer; color: #64748b;
  transition: all .12s; opacity: 0.5;
}
.leg-btn--on { opacity: 1; border-color: var(--c); color: var(--c); background: color-mix(in srgb, var(--c) 10%, white); }
.leg-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
</style>
