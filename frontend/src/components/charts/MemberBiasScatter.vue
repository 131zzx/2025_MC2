<!--
  委员偏见定位散点图
  X 轴 = 渔业议题情感均值（正=支持渔业）
  Y 轴 = 旅游议题情感均值（正=支持旅游）
  每个点 = 某委员在某数据集中的立场（多库情感相同时自然重叠）
  四象限含义：
    右上: 同时支持渔业+旅游（中立/两面讨好）
    右下: 支持渔业、反对旅游（亲渔业）
    左上: 反对渔业、支持旅游（亲旅游）
    左下: 同时反对（批评者）
-->
<template>
  <div class="scatter-wrap">
    <div ref="el" class="scatter-svg" />

    <!-- 图例 -->
    <div class="scatter-legend">
      <div v-for="ds in DS_LIST" :key="ds.key" class="leg-item">
        <svg width="14" height="14">
          <circle cx="7" cy="7" :r="4" :fill="ds.color" />
        </svg>
        {{ ds.label }}
      </div>
    </div>
  </div>
</template>

<script lang="ts">
export default {}
</script>
<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from 'vue'
import * as d3 from 'd3'
import type { SentimentAggItem } from '../../types'
import { COMMITTEE_MEMBERS, DATASET_COLORS, DATASET_LABELS } from '../../types'

const props = defineProps<{
  data: SentimentAggItem[]
  selectedMember?: string | null
}>()

const emit = defineEmits<{
  (e: 'select', name: string | null): void
  (e: 'hover', name: string | null): void
}>()

const el = ref<HTMLElement>()

const DS_LIST = [
  { key: 'filah',      label: 'FILAH', color: DATASET_COLORS.filah },
  { key: 'trout',      label: 'TROUT', color: DATASET_COLORS.trout },
  { key: 'journalist', label: '记者',  color: DATASET_COLORS.journalist },
]

interface Point {
  member: string
  ds: string
  fishingV: number
  tourismV: number
  totalCount: number
}

function buildPoints(): Point[] {
  const pts: Point[] = []
  for (const member of COMMITTEE_MEMBERS) {
    for (const ds of DS_LIST) {
      const fish = props.data.find(d => d.member === member && d.dataset === ds.key && d.industry === 'fishing')
      const tour = props.data.find(d => d.member === member && d.dataset === ds.key && d.industry === 'tourism')
      if (!fish && !tour) continue
      pts.push({
        member,
        ds: ds.key,
        fishingV: fish?.sentiment_mean ?? 0,
        tourismV: tour?.sentiment_mean ?? 0,
        totalCount: (fish?.count ?? 0) + (tour?.count ?? 0),
      })
    }
  }
  return pts
}

let tooltip: HTMLDivElement | null = null

function draw() {
  if (!el.value) return
  el.value.innerHTML = ''
  tooltip?.remove()

  const points = buildPoints()
  if (!points.length) return

  const W = el.value.clientWidth || 480
  const H = Math.min(W * 0.72, 340)
  const m = { top: 30, right: 30, bottom: 50, left: 56 }
  const iw = W - m.left - m.right
  const ih = H - m.top - m.bottom

  const svg = d3.select(el.value).append('svg').attr('width', W).attr('height', H)
  const g = svg.append('g').attr('transform', `translate(${m.left},${m.top})`)

  // 轴域（含余量）
  const ext = 1.1
  const xScale = d3.scaleLinear().domain([-ext, ext]).range([0, iw])
  const yScale = d3.scaleLinear().domain([-ext, ext]).range([ih, 0])

  // ── 四象限背景 ──────────────────────────────────────
  const cx = xScale(0), cy = yScale(0)
  const quadrants = [
    { x: cx, y: 0,  w: iw - cx, h: cy,      fill: '#fff7ed', label: '亲渔业·亲旅游', lx: cx + (iw - cx) / 2, ly: 12 },
    { x: 0,  y: 0,  w: cx,      h: cy,      fill: '#eff6ff', label: '亲旅游·疏渔业', lx: cx / 2,             ly: 12 },
    { x: cx, y: cy, w: iw - cx, h: ih - cy, fill: '#fef2f2', label: '亲渔业·疏旅游', lx: cx + (iw - cx) / 2, ly: cy + 14 },
    { x: 0,  y: cy, w: cx,      h: ih - cy, fill: '#f1f5f9', label: '两者均疏',       lx: cx / 2,             ly: cy + 14 },
  ]

  quadrants.forEach(q => {
    g.append('rect').attr('x', q.x).attr('y', q.y).attr('width', q.w).attr('height', q.h)
      .attr('fill', q.fill).attr('opacity', 0.7)
    g.append('text').attr('x', q.lx).attr('y', q.ly)
      .attr('text-anchor', 'middle').attr('font-size', 9.5).attr('fill', '#94a3b8')
      .attr('pointer-events', 'none').text(q.label)
  })

  // 中轴线
  g.append('line').attr('x1', cx).attr('x2', cx).attr('y1', 0).attr('y2', ih)
    .attr('stroke', '#e2e8f0').attr('stroke-width', 1.5)
  g.append('line').attr('x1', 0).attr('x2', iw).attr('y1', cy).attr('y2', cy)
    .attr('stroke', '#e2e8f0').attr('stroke-width', 1.5)

  // ── 散点 ─────────────────────────────────────────────
  const rScale = d3.scaleSqrt().domain([0, d3.max(points, d => d.totalCount) || 1]).range([5, 14])

  const hasSel = !!props.selectedMember

  // Tooltip div
  tooltip = document.createElement('div')
  tooltip.style.cssText = `
    position:fixed;pointer-events:none;z-index:9999;
    background:rgba(255,255,255,0.97);border:1px solid #e2e8f0;border-radius:8px;
    padding:8px 12px;font-size:12px;box-shadow:0 4px 14px rgba(0,0,0,.1);
    display:none;max-width:200px;
  `
  document.body.appendChild(tooltip)

  const ptGroups = g.selectAll<SVGGElement, Point>('g.pt')
    .data(points, (d: Point) => d.member + d.ds)
    .join('g').attr('class', 'pt')
    .attr('transform', (d: Point) => `translate(${xScale(d.fishingV)},${yScale(d.tourismV)})`)
    .attr('cursor', 'pointer')

  ptGroups.append('circle')
    .attr('r', (d: Point) => rScale(d.totalCount))
    .attr('fill', (d: Point) => DATASET_COLORS[d.ds as keyof typeof DATASET_COLORS])
    .attr('fill-opacity', (d: Point) => hasSel ? (props.selectedMember === d.member ? 0.92 : 0.18) : 0.82)
    .attr('stroke', (d: Point) => props.selectedMember === d.member ? '#1e293b' : '#fff')
    .attr('stroke-width', (d: Point) => props.selectedMember === d.member ? 2 : 1)

  // 成员名标签（只在选中或无选中时显示）
  ptGroups.each(function(d: Point) {
    const group = d3.select(this)
    const r = rScale(d.totalCount)
    if (!hasSel || props.selectedMember === d.member) {
      group.append('text')
        .attr('y', -r - 4).attr('text-anchor', 'middle')
        .attr('font-size', 9.5).attr('font-weight', 600)
        .attr('fill', DATASET_COLORS[d.ds as keyof typeof DATASET_COLORS])
        .attr('pointer-events', 'none')
        .text(d.member.split(' ').slice(-1)[0] ?? d.member)
    }
  })

  ptGroups
    .on('mouseenter', (event: MouseEvent, d: Point) => {
      emit('hover', d.member)
      if (tooltip) {
        tooltip.innerHTML = `
          <div style="font-weight:700;color:#1e293b;margin-bottom:4px">${d.member}</div>
          <div style="font-size:11px;color:${DATASET_COLORS[d.ds as keyof typeof DATASET_COLORS]};font-weight:600">${DATASET_LABELS[d.ds as keyof typeof DATASET_LABELS]}</div>
          <div style="margin-top:5px;font-size:11px;color:#64748b">渔业情感：<b style="color:#f59e0b">${(d.fishingV > 0 ? '+' : '') + d.fishingV.toFixed(2)}</b></div>
          <div style="font-size:11px;color:#64748b">旅游情感：<b style="color:#3b82f6">${(d.tourismV > 0 ? '+' : '') + d.tourismV.toFixed(2)}</b></div>
          <div style="font-size:11px;color:#94a3b8;margin-top:3px">样本量：${d.totalCount}</div>
        `
        tooltip.style.display = 'block'
        tooltip.style.left = (event.clientX + 14) + 'px'
        tooltip.style.top = (event.clientY - 10) + 'px'
      }
    })
    .on('mousemove', (event: MouseEvent) => {
      if (tooltip) {
        tooltip.style.left = (event.clientX + 14) + 'px'
        tooltip.style.top = (event.clientY - 10) + 'px'
      }
    })
    .on('mouseleave', (_: MouseEvent, d: Point) => {
      emit('hover', null)
      if (tooltip) tooltip.style.display = 'none'
    })
    .on('click', (_: MouseEvent, d: Point) => {
      emit('select', props.selectedMember === d.member ? null : d.member)
    })

  // ── 坐标轴 ────────────────────────────────────────────
  g.append('g').attr('transform', `translate(0,${ih})`).call(
    d3.axisBottom(xScale).ticks(5).tickFormat(d => (Number(d) > 0 ? '+' : '') + Number(d).toFixed(1))
  )
    .call(ax => ax.select('.domain').attr('stroke', '#e2e8f0'))
    .call(ax => ax.selectAll('text').attr('font-size', 10).attr('fill', '#94a3b8'))
    .call(ax => ax.selectAll('.tick line').attr('stroke', '#e2e8f0'))

  g.append('g').call(
    d3.axisLeft(yScale).ticks(5).tickFormat(d => (Number(d) > 0 ? '+' : '') + Number(d).toFixed(1))
  )
    .call(ax => ax.select('.domain').attr('stroke', '#e2e8f0'))
    .call(ax => ax.selectAll('text').attr('font-size', 10).attr('fill', '#94a3b8'))
    .call(ax => ax.selectAll('.tick line').attr('stroke', '#e2e8f0'))

  // 轴标签
  g.append('text').attr('x', iw / 2).attr('y', ih + 40)
    .attr('text-anchor', 'middle').attr('font-size', 11).attr('fill', '#f59e0b').attr('font-weight', 700)
    .text('← 疏渔业  渔业议题情感均值  亲渔业 →')
  g.append('text')
    .attr('transform', `translate(-44,${ih / 2}) rotate(-90)`)
    .attr('text-anchor', 'middle').attr('font-size', 11).attr('fill', '#3b82f6').attr('font-weight', 700)
    .text('← 疏旅游  旅游议题情感均值  亲旅游 →')
}

const ro = new ResizeObserver(draw)
onMounted(() => { ro.observe(el.value!); draw() })
onUnmounted(() => { ro.disconnect(); tooltip?.remove() })
watch([() => props.data, () => props.selectedMember], draw, { deep: true })
</script>

<style scoped>
.scatter-wrap { width: 100%; }
.scatter-svg  { width: 100%; }
.scatter-legend {
  display: flex; flex-wrap: wrap; gap: 8px 16px;
  padding: 6px 0 2px; margin-top: 2px;
}
.leg-item { display: flex; align-items: center; gap: 5px; font-size: 11px; color: #475569; }
</style>
