<!--
  成员活动气泡矩阵
  X = 数据集，Y = 成员，气泡大小 = 总活动量，颜色 = 数据集
  点击气泡 → 选中该成员
-->
<template>
  <div ref="el" class="bubble-chart" />
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from 'vue'
import * as d3 from 'd3'
import type { MemberActivityItem } from '../../types'
import { COMMITTEE_MEMBERS, DATASET_COLORS, DATASET_LABELS } from '../../types'

const props = defineProps<{
  data: MemberActivityItem[]
  selectedMember?: string
}>()

const emit = defineEmits<{
  (e: 'select', name: string | null): void
}>()

const el = ref<HTMLElement>()

const DS = ['filah', 'trout', 'journalist'] as const

function draw() {
  if (!el.value) return
  el.value.innerHTML = ''

  const W = el.value.clientWidth || 500
  const members = [...COMMITTEE_MEMBERS] as string[]
  const H = members.length * 52 + 60
  const m = { top: 36, right: 20, bottom: 14, left: 120 }
  const iw = W - m.left - m.right
  const colW = iw / DS.length

  const maxActivity = d3.max(props.data, d => d.total_activity) || 1
  const rScale = d3.scaleSqrt().domain([0, maxActivity]).range([4, 22])

  const svg = d3.select(el.value).append('svg').attr('width', W).attr('height', H)
  const g = svg.append('g').attr('transform', `translate(${m.left},${m.top})`)

  // 列标题
  DS.forEach((ds, di) => {
    g.append('text')
      .attr('x', di * colW + colW / 2).attr('y', -16)
      .attr('text-anchor', 'middle').attr('font-size', 12).attr('font-weight', 700)
      .attr('fill', DATASET_COLORS[ds])
      .text(DATASET_LABELS[ds])
  })

  members.forEach((member, mi) => {
    const rowY = mi * 52 + 26
    const isSelected = props.selectedMember === member
    const hasSel = !!props.selectedMember

    // 行背景（选中时高亮）
    svg.insert('rect', ':first-child')
      .attr('x', 0).attr('y', m.top + mi * 52)
      .attr('width', W).attr('height', 52)
      .attr('fill', isSelected ? '#eff6ff' : mi % 2 === 0 ? '#f8fafc' : '#fff')

    // 成员名（左侧，可点击）
    g.append('text')
      .attr('x', -8).attr('y', rowY)
      .attr('text-anchor', 'end').attr('dominant-baseline', 'middle')
      .attr('font-size', 12).attr('font-weight', isSelected ? 800 : 600)
      .attr('fill', isSelected ? '#2563eb' : '#374151')
      .attr('cursor', 'pointer')
      .text(member)
      .on('click', () => emit('select', isSelected ? null : member))

    DS.forEach((ds, di) => {
      const item = props.data.find(d => d.member === member && d.dataset === ds)
      if (!item || !item.in_dataset) {
        // 不在该数据集
        g.append('text')
          .attr('x', di * colW + colW / 2).attr('y', rowY)
          .attr('text-anchor', 'middle').attr('dominant-baseline', 'middle')
          .attr('font-size', 18).attr('fill', '#e2e8f0')
          .text('—')
        return
      }
      const r = rScale(item.total_activity)
      const color = DATASET_COLORS[ds]
      const opacity = hasSel && !isSelected ? 0.2 : 0.85

      const circle = g.append('circle')
        .attr('cx', di * colW + colW / 2).attr('cy', rowY)
        .attr('r', r).attr('fill', color)
        .attr('fill-opacity', opacity)
        .attr('stroke', isSelected ? '#1e293b' : 'none')
        .attr('stroke-width', 1.5)
        .attr('cursor', 'pointer')

      // 数值标签
      if (r > 11) {
        g.append('text')
          .attr('x', di * colW + colW / 2).attr('y', rowY)
          .attr('text-anchor', 'middle').attr('dominant-baseline', 'middle')
          .attr('font-size', 10).attr('fill', '#fff').attr('font-weight', 700)
          .attr('pointer-events', 'none')
          .text(item.total_activity)
      }

      // tooltip
      circle.append('title').text(
        `${member} · ${DATASET_LABELS[ds]}\n` +
        `参与：${item.participant_cnt}  行程：${item.trip_cnt}  会议：${item.meeting_cnt}  话题：${item.topic_cnt}`
      )
      circle.on('click', () => emit('select', isSelected ? null : member))
    })
  })

  // 图例（气泡大小）
  const legendX = W - 130
  const legendY = H - 12
  ;[10, 50, 100].forEach((v, i) => {
    const r = rScale(v)
    const lx = legendX + i * 42
    g.append('circle').attr('cx', lx).attr('cy', legendY - r).attr('r', r)
      .attr('fill', '#94a3b8').attr('fill-opacity', 0.3)
      .attr('stroke', '#94a3b8').attr('stroke-width', 1)
    g.append('text').attr('x', lx).attr('y', legendY + 3)
      .attr('text-anchor', 'middle').attr('font-size', 9).attr('fill', '#94a3b8').text(v)
  })
  g.append('text').attr('x', legendX - 10).attr('y', legendY + 3)
    .attr('text-anchor', 'end').attr('font-size', 9).attr('fill', '#94a3b8').text('活动量：')
}

const ro = new ResizeObserver(draw)
onMounted(() => { ro.observe(el.value!); draw() })
onUnmounted(() => ro.disconnect())
watch([() => props.data, () => props.selectedMember], draw, { deep: true })
</script>
<style scoped>.bubble-chart { width: 100%; }</style>
