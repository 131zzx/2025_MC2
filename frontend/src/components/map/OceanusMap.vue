<template>
  <div class="map-wrap">
    <div class="map-header">
      <span class="map-title">Oceanus 地区地图</span>
      <div class="map-controls">
        <button class="map-btn" @click="resetZoom">重置缩放</button>
        <label class="show-label">
          <input type="checkbox" v-model="showTripLines" /> 行程路线
        </label>
        <label class="show-label">
          <input type="checkbox" v-model="showPlaceMarkers" /> 地点标记
        </label>
      </div>
    </div>

    <div ref="mapWrap" class="map-svg-wrap">
      <svg ref="svgEl" class="map-svg">
        <g ref="rootG">
          <g ref="featuresG" class="features-layer" />
          <g ref="tripsG"    class="trips-layer" />
          <g ref="placesG"   class="places-layer" />
        </g>
      </svg>

      <!-- 图例 -->
      <div class="map-legend">
        <div class="legend-title">区域类型</div>
        <div v-for="item in zoneLegend" :key="item.label" class="legend-row">
          <span class="legend-swatch" :style="{ background: item.fill, border: `1px solid ${item.stroke}` }" />
          {{ item.label }}
        </div>
      </div>

      <!-- 悬停 Tooltip -->
      <div v-if="tooltip.show" class="map-tooltip"
        :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px' }">
        <div class="tt-name">{{ tooltip.name }}</div>
        <div class="tt-row" v-if="tooltip.kind">类型：{{ tooltip.kind }}</div>
        <div class="tt-row" v-if="tooltip.activity">活动：{{ tooltip.activity }}</div>
        <div class="tt-row" v-if="tooltip.trips">行程数：{{ tooltip.trips }}</div>
      </div>
    </div>

    <div v-if="loading" class="map-loading">
      <div class="spinner" /> 加载地图数据中...
    </div>
    <div v-if="error" class="map-error">{{ error }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted, nextTick, computed } from 'vue'
import * as d3 from 'd3'
import type { TripRecord, PlaceNode } from '../../types'
import { DATASET_COLORS } from '../../types'
import { uselinkingStore } from '../../stores/linkingStore'

const props = defineProps<{
  trips:  TripRecord[]
  places: PlaceNode[]
}>()

const emit = defineEmits<{ (e: 'place-click', placeId: string): void }>()

const linking = uselinkingStore()

const mapWrap  = ref<HTMLDivElement>()
const svgEl    = ref<SVGSVGElement>()
const rootG    = ref<SVGGElement>()
const featuresG = ref<SVGGElement>()
const tripsG   = ref<SVGGElement>()
const placesG  = ref<SVGGElement>()

const loading  = ref(false)
const error    = ref('')
const showTripLines    = ref(true)
const showPlaceMarkers = ref(true)

let geoData: any = null
let projection: d3.GeoProjection | null = null
let pathGen: d3.GeoPath | null = null
let zoomBehavior: d3.ZoomBehavior<SVGSVGElement, unknown> | null = null

const tooltip = ref({ show: false, x: 0, y: 0, name: '', kind: '', activity: '', trips: 0 })

// ── 颜色方案 ──────────────────────────────────────────────
const ZONE_FILL: Record<string, string> = {
  Island:              '#dbeafe',
  'Fishing Ground':    '#fef3c7',
  'Ecological Preserve': '#d1fae5',
  Port:                '#f3e8ff',
  City:                '#fce7f3',
  default:             '#e2e8f0',
}
const ZONE_STROKE: Record<string, string> = {
  Island:              '#93c5fd',
  'Fishing Ground':    '#fcd34d',
  'Ecological Preserve': '#6ee7b7',
  Port:                '#c4b5fd',
  City:                '#f9a8d4',
  default:             '#cbd5e1',
}

const zoneLegend = [
  { label: '岛屿',     fill: ZONE_FILL.Island,              stroke: ZONE_STROKE.Island },
  { label: '渔场',     fill: ZONE_FILL['Fishing Ground'],   stroke: ZONE_STROKE['Fishing Ground'] },
  { label: '生态保护区', fill: ZONE_FILL['Ecological Preserve'], stroke: ZONE_STROKE['Ecological Preserve'] },
  { label: '港口',     fill: ZONE_FILL.Port,                stroke: ZONE_STROKE.Port },
]

// ── 加载 GeoJSON ─────────────────────────────────────────
async function loadGeoJSON() {
  loading.value = true
  error.value   = ''
  try {
    const resp = await fetch('/oceanus_map.geojson')
    if (!resp.ok) throw new Error(`GeoJSON 加载失败：HTTP ${resp.status}`)
    geoData = await resp.json()
  } catch (e: any) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

// ── 构建投影 ─────────────────────────────────────────────
function buildProjection(W: number, H: number) {
  if (!geoData) return
  // 使用 geoIdentity + fitSize 适应 GeoJSON 坐标范围
  projection = d3.geoIdentity().reflectY(true)
  pathGen = d3.geoPath().projection(projection)
  ;(projection as any).fitSize([W, H], geoData)
}

// ── 渲染地图要素 ─────────────────────────────────────────
function renderFeatures() {
  if (!geoData || !pathGen) return

  const sel = d3.select(featuresG.value!)
    .selectAll<SVGPathElement, any>('path')
    .data(geoData.features)

  sel.enter().append('path')
    .merge(sel as any)
    .attr('d', (d: any) => pathGen!(d) ?? '')
    .attr('fill', (d: any) => {
      const kind = d.properties?.Kind || 'default'
      return ZONE_FILL[kind] ?? ZONE_FILL.default
    })
    .attr('stroke', (d: any) => {
      const kind = d.properties?.Kind || 'default'
      return ZONE_STROKE[kind] ?? ZONE_STROKE.default
    })
    .attr('stroke-width', 1)
    .style('cursor', 'pointer')
    .on('mouseenter', (event, d: any) => {
      const props_ = d.properties || {}
      tooltip.value = {
        show: true,
        x: event.offsetX + 12,
        y: event.offsetY - 8,
        name: props_.Name || '未知区域',
        kind: props_.Kind || '',
        activity: props_.Activities || '',
        trips: 0,
      }
      d3.select(event.currentTarget).attr('stroke-width', 2.5)
    })
    .on('mousemove', event => {
      tooltip.value.x = event.offsetX + 12
      tooltip.value.y = event.offsetY - 8
    })
    .on('mouseleave', event => {
      tooltip.value.show = false
      d3.select(event.currentTarget).attr('stroke-width', 1)
    })

  sel.exit().remove()
}

// ── 渲染行程路线（聚合 → 宽度映射） ──────────────────────
function renderTripLines() {
  const g = d3.select(tripsG.value!)
  g.selectAll('*').remove()
  if (!showTripLines.value || !pathGen || !projection) return

  // 计算地点访问频次
  const countMap = new Map<string, number>()
  props.trips.forEach(trip => {
    trip.places?.forEach(p => {
      countMap.set(p.id, (countMap.get(p.id) || 0) + 1)
    })
  })

  // 过滤有坐标的地点并绘制路径
  const placeMap = new Map(props.places.map(p => [p.id, p]))

  props.trips.forEach(trip => {
    const validPlaces = (trip.places || [])
      .map(p => placeMap.get(p.id))
      .filter(p => p && p.lat != null && p.lon != null) as PlaceNode[]

    if (validPlaces.length < 2) return

    const member = trip.person
    const isHighlighted = linking.selectedMember
      ? member === linking.selectedMember
      : linking.hoveredMember
        ? member === linking.hoveredMember
        : true

    const ds   = (trip.dataset || 'journalist') as keyof typeof DATASET_COLORS
    const color = DATASET_COLORS[ds] || '#94a3b8'

    const line = d3.line<PlaceNode>()
      .x(p => (projection!([p.lon!, p.lat!]) ?? [0, 0])[0])
      .y(p => (projection!([p.lon!, p.lat!]) ?? [0, 0])[1])
      .curve(d3.curveCatmullRom)

    g.append('path')
      .datum(validPlaces)
      .attr('d', line)
      .attr('fill', 'none')
      .attr('stroke', color)
      .attr('stroke-width', isHighlighted ? 1.8 : 0.7)
      .attr('stroke-opacity', isHighlighted ? 0.7 : 0.2)
      .attr('stroke-dasharray', isHighlighted ? 'none' : '4,3')
  })
}

// ── 渲染地点标记 ─────────────────────────────────────────
function renderPlaces() {
  const g = d3.select(placesG.value!)
  g.selectAll('*').remove()
  if (!showPlaceMarkers.value || !projection) return

  const tripCountMap = new Map<string, number>()
  props.trips.forEach(trip => {
    trip.places?.forEach(p => {
      tripCountMap.set(p.id, (tripCountMap.get(p.id) || 0) + 1)
    })
  })

  const validPlaces = props.places.filter(p => p.lat != null && p.lon != null)
  const rScale = d3.scaleSqrt()
    .domain([0, d3.max(Array.from(tripCountMap.values())) || 1])
    .range([3, 12])

  const groups = g.selectAll<SVGGElement, PlaceNode>('g.place')
    .data(validPlaces, d => d.id)
    .enter().append('g').attr('class', 'place')
    .attr('transform', d => {
      const [x, y] = projection!([d.lon!, d.lat!]) ?? [0, 0]
      return `translate(${x},${y})`
    })
    .style('cursor', 'pointer')
    .on('click', (_, d) => emit('place-click', d.id))
    .on('mouseenter', (event, d) => {
      const cnt = tripCountMap.get(d.id) || 0
      tooltip.value = {
        show: true,
        x: event.offsetX + 12,
        y: event.offsetY - 8,
        name: d.name || d.id,
        kind: d.zone || '',
        activity: '',
        trips: cnt,
      }
    })
    .on('mousemove', event => {
      tooltip.value.x = event.offsetX + 12
      tooltip.value.y = event.offsetY - 8
    })
    .on('mouseleave', () => { tooltip.value.show = false })

  groups.append('circle')
    .attr('r', d => rScale(tripCountMap.get(d.id) || 0))
    .attr('fill', '#2563eb')
    .attr('fill-opacity', 0.7)
    .attr('stroke', '#fff')
    .attr('stroke-width', 1.5)

  groups.append('title').text(d => d.name || d.id)
}

// ── 绑定 Zoom ────────────────────────────────────────────
function bindZoom(W: number, H: number) {
  if (zoomBehavior) return
  zoomBehavior = d3.zoom<SVGSVGElement, unknown>()
    .scaleExtent([0.5, 8])
    .on('zoom', ev => {
      d3.select(rootG.value!).attr('transform', ev.transform)
    })
  d3.select(svgEl.value!).call(zoomBehavior)
}

function resetZoom() {
  if (!svgEl.value || !zoomBehavior) return
  d3.select(svgEl.value)
    .transition().duration(400)
    .call(zoomBehavior.transform, d3.zoomIdentity)
}

// ── 主渲染入口 ───────────────────────────────────────────
async function renderAll() {
  await nextTick()
  if (!mapWrap.value || !svgEl.value) return
  const W = mapWrap.value.clientWidth  || 700
  const H = mapWrap.value.clientHeight || 420

  d3.select(svgEl.value).attr('width', W).attr('height', H)

  if (!geoData) await loadGeoJSON()
  if (!geoData) return

  buildProjection(W, H)
  bindZoom(W, H)
  renderFeatures()
  renderTripLines()
  renderPlaces()
}

// ── resize ────────────────────────────────────────────────
let resizeObs: ResizeObserver | null = null

onMounted(async () => {
  await renderAll()
  resizeObs = new ResizeObserver(() => renderAll())
  if (mapWrap.value) resizeObs.observe(mapWrap.value)
})

onUnmounted(() => { resizeObs?.disconnect() })

watch([() => props.trips, () => props.places, showTripLines, showPlaceMarkers], renderTripLines)
watch(() => linking.selectedMember, renderTripLines)
watch(() => linking.hoveredMember,  renderTripLines)
</script>

<style scoped>
.map-wrap { position: relative; width: 100%; display: flex; flex-direction: column; background: #fff; border: 1px solid #e2e8f0; border-radius: 10px; overflow: hidden; }

.map-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 14px; border-bottom: 1px solid #f1f5f9; background: #f8fafc; flex-shrink: 0;
}
.map-title { font-size: 13px; font-weight: 600; color: #1e293b; }
.map-controls { display: flex; align-items: center; gap: 12px; }
.map-btn {
  padding: 3px 8px; border-radius: 4px; border: 1px solid #e2e8f0;
  background: #fff; font-size: 11px; cursor: pointer; color: #64748b;
}
.map-btn:hover { background: #f1f5f9; }
.show-label { font-size: 11px; color: #64748b; display: flex; align-items: center; gap: 4px; cursor: pointer; }

.map-svg-wrap {
  position: relative; width: 100%; height: 440px;
  background: linear-gradient(150deg, #e0f2fe 0%, #f0fdf4 100%);
  overflow: hidden;
}
.map-svg { width: 100%; height: 100%; display: block; }

.map-legend {
  position: absolute; bottom: 14px; right: 14px;
  background: rgba(255,255,255,0.92); border: 1px solid #e2e8f0;
  border-radius: 8px; padding: 8px 10px; font-size: 11px;
  box-shadow: 0 2px 8px rgba(0,0,0,.07);
}
.legend-title { font-weight: 700; color: #374151; margin-bottom: 5px; font-size: 10px; }
.legend-row { display: flex; align-items: center; gap: 6px; color: #475569; margin-top: 3px; }
.legend-swatch { width: 12px; height: 12px; border-radius: 3px; flex-shrink: 0; }

.map-tooltip {
  position: absolute; pointer-events: none; z-index: 10;
  background: rgba(255,255,255,0.96); border: 1px solid #e2e8f0;
  border-radius: 8px; padding: 8px 11px; font-size: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,.1); max-width: 200px;
}
.tt-name { font-weight: 700; color: #1e293b; margin-bottom: 3px; }
.tt-row  { color: #64748b; font-size: 11px; margin-top: 2px; }

.map-loading, .map-error {
  position: absolute; inset: 0; display: flex; align-items: center; justify-content: center;
  font-size: 13px; color: #64748b; background: rgba(248,250,252,0.9); gap: 8px;
}
.map-error { color: #dc2626; }
</style>
