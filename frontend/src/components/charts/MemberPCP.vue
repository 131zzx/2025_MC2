<!--
  委员活动量平行坐标图 (PCP)
  每条线 = 某委员在某数据集中的多维活动量
  轴：行程数 / 参与数 / 会议数 / 话题数
  颜色 = 数据集；悬停 / 点击选中委员
-->
<template>
  <div ref="el" class="pcp-wrap" />
</template>

<script lang="ts">
export default {}
</script>
<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from 'vue'
import * as d3 from 'd3'
import type { MemberActivityItem } from '../../types'
import { COMMITTEE_MEMBERS, DATASET_COLORS, DATASET_LABELS } from '../../types'

const props = defineProps<{
  data: MemberActivityItem[]
  selectedMember?: string | null
}>()

const emit = defineEmits<{
  (e: 'select', name: string | null): void
  (e: 'hover', name: string | null): void
}>()

const el = ref<HTMLElement>()

const AXES = [
  { key: 'trip_cnt',        label: '行程' },
  { key: 'participant_cnt', label: '参与' },
  { key: 'meeting_cnt',     label: '会议' },
  { key: 'topic_cnt',       label: '话题' },
]

let tooltip: HTMLDivElement | null = null

function draw() {
  if (!el.value || !props.data.length) return
  el.value.innerHTML = ''
  tooltip?.remove()

  const W = el.value.clientWidth || 480
  const H = 260
  const m = { top: 28, right: 24, bottom: 16, left: 132 }
  const iw = W - m.left - m.right
  const ih = H - m.top - m.bottom

  const svg = d3.select(el.value).append('svg').attr('width', W).attr('height', H)
  const g = svg.append('g').attr('transform', `translate(${m.left},${m.top})`)

  // 计算每个轴的最大值
  const maxVals: Record<string, number> = {}
  AXES.forEach(a => {
    maxVals[a.key] = d3.max(props.data, d => (d as any)[a.key]) || 1
  })

  const xScale = d3.scalePoint().domain(AXES.map(a => a.key)).range([0, iw]).padding(0.2)
  const yScales: Record<string, d3.ScaleLinear<number, number>> = {}
  AXES.forEach(a => {
    yScales[a.key] = d3.scaleLinear().domain([0, maxVals[a.key]]).range([ih, 0])
  })

  // 背景轨道
  AXES.forEach(a => {
    const x = xScale(a.key)!
    g.append('line').attr('x1', x).attr('x2', x).attr('y1', 0).attr('y2', ih)
      .attr('stroke', '#e2e8f0').attr('stroke-width', 1)
  })

  // Tooltip
  tooltip = document.createElement('div')
  tooltip.style.cssText = `position:fixed;pointer-events:none;z-index:9999;
    background:rgba(255,255,255,0.97);border:1px solid #e2e8f0;border-radius:8px;
    padding:7px 11px;font-size:12px;box-shadow:0 4px 14px rgba(0,0,0,.1);display:none;`
  document.body.appendChild(tooltip)

  // 绘制路径
  const hasSel = !!props.selectedMember

  props.data.forEach(item => {
    if (!item.in_dataset) return
    const member = item.member
    const ds = item.dataset
    const isSel = props.selectedMember === member
    const color = DATASET_COLORS[ds as keyof typeof DATASET_COLORS]

    const lineGen = d3.line<{ key: string }>()
      .x(d => xScale(d.key)!)
      .y(d => yScales[d.key]((item as any)[d.key] ?? 0))

    const path = g.append('path')
      .datum(AXES)
      .attr('d', lineGen)
      .attr('fill', 'none')
      .attr('stroke', color)
      .attr('stroke-width', hasSel ? (isSel ? 2.5 : 0.8) : 1.5)
      .attr('opacity', hasSel ? (isSel ? 1 : 0.12) : 0.65)
      .attr('cursor', 'pointer')

    path
      .on('mouseenter', (event) => {
        emit('hover', member)
        if (tooltip) {
          tooltip.innerHTML = `
            <div style="font-weight:700;color:#1e293b">${member}</div>
            <div style="font-size:11px;color:${color};font-weight:700;margin-bottom:5px">${DATASET_LABELS[ds as keyof typeof DATASET_LABELS]}</div>
            ${AXES.map(a => `<div style="font-size:11px;color:#64748b">${a.label}：<b style="color:#1e293b">${(item as any)[a.key] ?? 0}</b></div>`).join('')}
          `
          tooltip.style.display = 'block'
          tooltip.style.left = (event.clientX + 14) + 'px'
          tooltip.style.top = (event.clientY - 10) + 'px'
        }
        path.attr('stroke-width', 3).attr('opacity', 1)
      })
      .on('mousemove', (event) => {
        if (tooltip) {
          tooltip.style.left = (event.clientX + 14) + 'px'
          tooltip.style.top = (event.clientY - 10) + 'px'
        }
      })
      .on('mouseleave', () => {
        emit('hover', null)
        if (tooltip) tooltip.style.display = 'none'
        path.attr('stroke-width', hasSel ? (isSel ? 2.5 : 0.8) : 1.5)
          .attr('opacity', hasSel ? (isSel ? 1 : 0.12) : 0.65)
      })
      .on('click', () => emit('select', isSel ? null : member))
  })

  // 轴标签 + 刻度
  AXES.forEach(a => {
    const x = xScale(a.key)!
    const ax = d3.axisLeft(yScales[a.key]).ticks(3).tickSize(3)
    const axG = g.append('g').attr('transform', `translate(${x},0)`).call(ax)
    axG.select('.domain').attr('stroke', '#e2e8f0')
    // 首轴刻度右移，为左侧成员名留出空间
    const tickDx = a.key === AXES[0].key ? 6 : -2
    axG.selectAll('text').attr('font-size', 9).attr('fill', '#94a3b8').attr('dx', tickDx)
    axG.selectAll('.tick line').attr('stroke', '#e2e8f0')

    g.append('text').attr('x', x).attr('y', -12)
      .attr('text-anchor', 'middle').attr('font-size', 11).attr('font-weight', 700).attr('fill', '#374151')
      .text(a.label)
  })

  // 左侧成员标签：固定等距排列 + 连线到数据点，避免重叠
  const members = [...COMMITTEE_MEMBERS]
  const firstAxis = AXES[0].key
  const x0 = xScale(firstAxis)!

  // 只取有数据的成员
  const activeMems = members.filter(m => {
    const it = props.data.find(d => d.member === m && d.dataset === 'journalist') ||
               props.data.find(d => d.member === m)
    return it && it.in_dataset
  })

  // 等距分布 y 位置
  const totalH = ih
  const step   = totalH / Math.max(activeMems.length, 1)
  activeMems.forEach((member, idx) => {
    const item = props.data.find(d => d.member === member && d.dataset === 'journalist') ||
                 props.data.find(d => d.member === member)
    if (!item || !item.in_dataset) return

    const dataY  = yScales[firstAxis]((item as any)[firstAxis] ?? 0)
    const labelY = step * idx + step / 2   // 等距
    const isSel  = props.selectedMember === member

    // 标签（等距排列，置于首轴左侧，避免与刻度重叠）
    g.append('text')
      .attr('x', -36).attr('y', labelY)
      .attr('text-anchor', 'end').attr('dominant-baseline', 'middle')
      .attr('font-size', 11).attr('font-weight', isSel ? 800 : 500)
      .attr('fill', isSel ? '#2563eb' : '#374151')
      .attr('cursor', 'pointer')
      .text(member)
      .on('click', () => emit('select', isSel ? null : member))
  })
}

const ro = new ResizeObserver(draw)
onMounted(() => { ro.observe(el.value!); draw() })
onUnmounted(() => { ro.disconnect(); tooltip?.remove() })
watch([() => props.data, () => props.selectedMember], draw, { deep: true })
</script>
<style scoped>.pcp-wrap { width: 100%; }</style>
