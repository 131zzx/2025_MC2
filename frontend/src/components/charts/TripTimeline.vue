<template>
  <div ref="el" class="timeline-wrap">
    <svg ref="svgEl" class="timeline-svg" />
    <div
      v-if="tooltip.show"
      class="tl-tooltip"
      :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px' }"
    >
      <div class="tt-title">{{ tooltip.person }}</div>
      <div class="tt-row">日期：{{ tooltip.date }}</div>
      <div class="tt-row" v-if="tooltip.places">地点：{{ tooltip.places }}</div>
      <div class="tt-row">数据集：{{ tooltip.dataset }}</div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
export default defineComponent({ name: 'TripTimeline' })
</script>
<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import * as d3 from 'd3'
import type { TripRecord, DatasetKey } from '../../types'
import { DATASET_COLORS, COMMITTEE_MEMBERS } from '../../types'

const props = defineProps<{
  trips: (TripRecord & { presence?: Set<DatasetKey>; journalistEvidenceMode?: boolean })[]
  activeDatasets?: DatasetKey[]
  selectedMember?: string
  hoveredTrip?: string
}>()

const emit = defineEmits<{
  (e: 'trip-hover', id: string | null): void
  (e: 'member-click', name: string): void
}>()

const el    = ref<HTMLDivElement>()
const svgEl = ref<SVGSVGElement>()
const tooltip = ref({ show: false, x: 0, y: 0, person: '', date: '', places: '', dataset: '' })

let resizeObs: ResizeObserver | null = null
let drawTimer = 0

/** 将 0040 等异常年份修正为 2040 */
function parseTripDate(raw: string): Date | null {
  const m = raw.match(/^(\d{4})-(\d{2})-(\d{2})/)
  if (!m) return null
  let year = parseInt(m[1], 10)
  if (year < 100) year += 2000
  else if (year < 1900) year += 2000
  const d = new Date(year, parseInt(m[2], 10) - 1, parseInt(m[3], 10))
  return isNaN(d.getTime()) ? null : d
}

function dotColor(presence: Set<DatasetKey>, journalistEvidenceMode: boolean): string {
  if (journalistEvidenceMode) {
    const hasFilah = presence.has('filah')
    const hasTrout = presence.has('trout')
    const hasJournalist = presence.has('journalist')
    if (hasFilah && hasTrout) return '#064e3b'
    if (hasFilah || hasTrout) return '#10b981'
    if (hasJournalist) return '#a7f3d0'
    return '#94a3b8'
  }
  // FILAH / TROUT 模式：红色仅当全库中双方共有；不掺入记者
  const hasFilah = presence.has('filah')
  const hasTrout = presence.has('trout')
  if (hasFilah && hasTrout) return '#ef4444'
  if (hasFilah) return DATASET_COLORS.filah
  if (hasTrout) return DATASET_COLORS.trout
  return '#94a3b8'
}

function draw() {
  if (!el.value || !svgEl.value) return

  const svg = d3.select(svgEl.value)
  svg.selectAll('*').remove()
  tooltip.value.show = false

  if (!props.trips.length) {
    const W = el.value.clientWidth || 700
    svg.attr('width', W).attr('height', 72)
    svg.append('text')
      .attr('x', W / 2).attr('y', 40)
      .attr('text-anchor', 'middle')
      .attr('fill', '#94a3b8').attr('font-size', 12)
      .text('当前筛选无行程记录')
    return
  }

  const containerW = el.value.clientWidth || 700
  const margin = { top: 30, right: 20, bottom: 30, left: 130 }
  const rowH = 22
  const members = COMMITTEE_MEMBERS.filter(m =>
    props.trips.some(t => t.person === m)
  )

  const H = margin.top + members.length * rowH + margin.bottom
  svg.attr('width', containerW).attr('height', H)

  const innerW = containerW - margin.left - margin.right

  // 时间域
  const dates = props.trips.map(t => parseTripDate(t.date)).filter((d): d is Date => d !== null)
  if (!dates.length) return
  const minDate = d3.min(dates)!
  const maxDate = d3.max(dates)!

  const padMs = 7 * 24 * 3600 * 1000
  const xScale = d3.scaleTime()
    .domain([new Date(minDate.getTime() - padMs), new Date(maxDate.getTime() + padMs)])
    .range([0, innerW])

  const yScale = d3.scaleBand()
    .domain(members as unknown as string[])
    .range([0, members.length * rowH])
    .padding(0.15)

  const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`)

  // 背景行条
  members.forEach((m, i) => {
    g.append('rect')
      .attr('x', 0).attr('y', i * rowH)
      .attr('width', innerW).attr('height', rowH)
      .attr('fill', i % 2 === 0 ? '#f8fafc' : '#ffffff')
      .attr('rx', 0)
  })

  // X轴（月份刻度）
  const xAxis = d3.axisBottom(xScale)
    .ticks(d3.timeMonth.every(1))
    .tickFormat(d3.timeFormat('%m月') as any)
    .tickSize(3)

  g.append('g')
    .attr('transform', `translate(0,${members.length * rowH})`)
    .call(xAxis)
    .select('.domain').remove()

  g.selectAll('.tick text').attr('font-size', 9).attr('fill', '#94a3b8')
  g.selectAll('.tick line').attr('stroke', '#e2e8f0')

  // Y轴（成员名）
  members.forEach((m, i) => {
    const y = i * rowH + rowH / 2
    g.append('text')
      .attr('x', -8).attr('y', y)
      .attr('text-anchor', 'end')
      .attr('dominant-baseline', 'middle')
      .attr('font-size', 11)
      .attr('fill', props.selectedMember === m ? '#2563eb' : '#475569')
      .attr('font-weight', props.selectedMember === m ? 700 : 400)
      .attr('cursor', 'pointer')
      .text(m.split(' ').slice(-1)[0] ?? m)
      .on('click', () => emit('member-click', m))
  })

  // 同日同成员多点横向错开，避免完全重叠
  const slotMap = new Map<string, number>()
  const placed = props.trips
    .map(trip => {
      const mIdx = members.indexOf(trip.person as any)
      const date = parseTripDate(trip.date)
      if (mIdx < 0 || !date) return null
      const dayKey = `${trip.person}|${date.toISOString().slice(0, 10)}`
      const slot = slotMap.get(dayKey) ?? 0
      slotMap.set(dayKey, slot + 1)
      return { trip, mIdx, date, slot }
    })
    .filter((x): x is NonNullable<typeof x> => x !== null)

  const maxSlot = d3.max(placed, d => d.slot) ?? 0
  const jitterStep = maxSlot > 0 ? Math.min(10, innerW / 80) : 0

  placed.forEach(({ trip, mIdx, date, slot }) => {
    const presence = trip.presence ?? new Set([trip.dataset])
    const color = dotColor(presence, !!trip.journalistEvidenceMode)
    const x = xScale(date) + slot * jitterStep - (maxSlot * jitterStep) / 2
    const y = mIdx * rowH + rowH / 2

    const isHighlighted = props.selectedMember ? trip.person === props.selectedMember : true
    const isHovered = props.hoveredTrip === trip.trip_id

    const dsLabel = trip.journalistEvidenceMode
      ? [...presence].map(ds => (ds === 'journalist' ? '记者' : ds.toUpperCase())).join('、')
      : (presence.has('filah') && presence.has('trout') ? 'FILAH + TROUT'
        : presence.has('filah') ? 'FILAH' : presence.has('trout') ? 'TROUT' : trip.dataset)

    g.append('circle')
      .attr('cx', x).attr('cy', y)
      .attr('r', isHovered ? 7 : 4)
      .attr('fill', color)
      .attr('fill-opacity', isHighlighted ? 0.85 : 0.25)
      .attr('stroke', isHovered ? '#1e293b' : 'none')
      .attr('stroke-width', 1.5)
      .attr('cursor', 'pointer')
      .on('mouseenter', (event) => {
        emit('trip-hover', trip.trip_id)
        const placeNames = (trip.places || []).map(p => p.name).filter(Boolean).join(' → ')
        tooltip.value = {
          show: true,
          x: event.clientX + 12,
          y: event.clientY - 8,
          person: trip.person,
          date: trip.date,
          places: placeNames,
          dataset: dsLabel,
        }
      })
      .on('mousemove', event => {
        tooltip.value.x = event.clientX + 12
        tooltip.value.y = event.clientY - 8
      })
      .on('mouseleave', () => {
        emit('trip-hover', null)
        tooltip.value.show = false
      })
  })

  // 今天/范围线
  const now = new Date()
  if (now >= minDate && now <= maxDate) {
    const nx = xScale(now)
    g.append('line')
      .attr('x1', nx).attr('x2', nx)
      .attr('y1', 0).attr('y2', members.length * rowH)
      .attr('stroke', '#ef4444')
      .attr('stroke-dasharray', '3,3')
      .attr('stroke-width', 1)
      .attr('opacity', 0.5)
  }
}

onMounted(async () => {
  await nextTick()
  draw()
  resizeObs = new ResizeObserver(() => draw())
  if (el.value) resizeObs.observe(el.value)
})

onUnmounted(() => { resizeObs?.disconnect(); clearTimeout(drawTimer) })

function scheduleDraw() {
  clearTimeout(drawTimer)
  drawTimer = window.setTimeout(async () => {
    await nextTick()
    draw()
  }, 80)
}

watch([() => props.trips, () => props.activeDatasets, () => props.selectedMember, () => props.hoveredTrip], scheduleDraw)
</script>

<style scoped>
.timeline-wrap {
  position: relative; width: 100%; min-height: 120px;
  overflow-x: auto;
}
.timeline-svg { display: block; }
.tl-tooltip {
  position: fixed; pointer-events: none; z-index: 10000;
  background: rgba(255,255,255,0.96); border: 1px solid #e2e8f0;
  border-radius: 8px; padding: 8px 11px; font-size: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,.1); max-width: 220px;
}
.tt-title { font-weight: 700; color: #1e293b; margin-bottom: 3px; }
.tt-row { color: #64748b; font-size: 11px; margin-top: 2px; }
</style>
