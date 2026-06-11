<template>
  <div class="map-root">
    <div class="map-bar">
      <span class="bar-stat">
        <template v-if="tripStats.places > 0">
          {{ tripStats.places }} 个地点 · {{ tripStats.trips }} 条行程 · {{ tripStats.visits }} 次到访
          <template v-if="selectedMember"> · {{ selectedMember }}</template>
        </template>
        <template v-else>当前筛选无带坐标行程</template>
      </span>
      <div v-if="zoneFilterOptions.length" class="zone-filters">
        <span class="filter-label">区域</span>
        <button
          v-for="z in zoneFilterOptions" :key="z.zone"
          class="zone-chip"
          :class="{ 'zone-chip--on': activeZoneSet.has(z.zone) }"
          :style="activeZoneSet.has(z.zone) ? { background: z.color + '22', borderColor: z.color, color: z.color } : {}"
          @click="toggleZone(z.zone)"
        >{{ z.label }}</button>
      </div>
      <div class="bar-actions">
        <button v-if="selectedPlaceId" class="bar-btn" @click="clearPlaceSelection">取消选中</button>
        <button class="bar-btn" @click="resetZoom">重置视图</button>
      </div>
    </div>

    <div ref="wrapEl" class="map-wrap">
      <svg ref="svgEl" class="map-svg" />
      <div class="map-hint">顶部『区域』按钮可筛选落点类型</div>

      <div class="legend-box legend-geo">
        <div class="leg-title">地理要素</div>
        <div v-for="it in geoLegend" :key="it.label" class="leg-row">
          <span class="leg-sw" :class="it.shape" :style="legStyle(it)" />{{ it.label }}
        </div>
      </div>

      <div v-if="zoneLegend.length" class="legend-box legend-trip">
        <div class="leg-title">行程落点 · 区域</div>
        <div v-for="it in zoneLegend" :key="it.zone" class="leg-row">
          <span class="leg-dot" :style="{ background: it.color }" />{{ it.label }}
        </div>
      </div>

      <div v-if="mapState === 'loading'" class="map-mask">加载地图…</div>
      <div v-if="mapState === 'error'" class="map-mask map-err">{{ errMsg }}</div>
    </div>

    <Teleport to="body">
      <div v-show="tt.show" class="map-tt" :style="{ left: tt.x + 'px', top: tt.y + 'px' }">
        <div class="tt-name">{{ tt.name }}</div>
        <div v-for="(line, i) in tt.lines" :key="i" class="tt-line">{{ line }}</div>
      </div>
    </Teleport>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
export default defineComponent({ name: 'OceanusMap' })
</script>
<script setup lang="ts">
import { ref, reactive, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import * as d3 from 'd3'
import type { TripRecord } from '../../types'
import { DATASET_COLORS } from '../../types'

const props = withDefaults(defineProps<{
  trips?: TripRecord[]
  selectedMember?: string
}>(), {
  trips: () => [],
  selectedMember: '',
})

const OCEAN = '#c5dce8'
const REGION_COLORS: Record<string, string> = {
  Island: '#e8d5a8',
  'Fishing Ground': '#9ecae1',
  'Ecological Preserve': '#a8d4b4',
  default: '#d1d5db',
}

const ZONE_COLORS: Record<string, string> = {
  tourism: '#16a34a', commercial: '#9333ea', residential: '#64748b',
  government: '#f59e0b', industrial: '#0369a1', fishing: '#0d9488',
  nature: '#22c55e', connector: '#94a3b8', unknown: '#374151',
}

const ZONE_LABELS: Record<string, string> = {
  tourism: '旅游', commercial: '商业', residential: '居住',
  government: '政府', industrial: '工业', fishing: '渔业',
  nature: '自然', connector: '连接', unknown: '其他',
}

const KIND_ZH: Record<string, string> = {
  Island: '岛屿', 'Fishing Ground': '渔场', 'Ecological Preserve': '生态保护区',
  City: '城市', city: '城市', buoy: '导航浮标',
}

const FEAT_R = 5
/** 与 BAIT 示例一致：固定小圆点，不按访问次数放大 */
const PLACE_R = 4.5

interface PlaceAgg {
  id: string
  name: string
  zone: string
  coord: [number, number]
  count: number
  members: Set<string>
  datasets: Set<string>
}

interface PlacedMarker extends PlaceAgg {
  x: number
  y: number
}

const wrapEl = ref<HTMLDivElement>()
const svgEl = ref<SVGSVGElement>()
const tt = reactive({ show: false, x: 0, y: 0, name: '', lines: [] as string[] })
const mapState = ref<'idle' | 'loading' | 'ready' | 'error'>('idle')
const errMsg = ref('')
const geoLegend = ref<Array<{ label: string; fill: string; stroke: string; shape: string }>>([])
const zoneLegend = ref<Array<{ zone: string; label: string; color: string }>>([])
const activeZoneSet = reactive(new Set<string>())
/** 用户主动取消勾选的区域；切换数据集时仅补全未在此集合中的新区域 */
const userDisabledZones = reactive(new Set<string>())
const hoveredPlaceId = ref<string | null>(null)
const selectedPlaceId = ref<string | null>(null)

let geoData: GeoJSON.FeatureCollection | null = null
let projection: d3.GeoIdentityTransform | null = null
let pathGen: d3.GeoPath | null = null
let zoom: d3.ZoomBehavior<SVGSVGElement, unknown> | null = null
let zoomG: d3.Selection<SVGGElement, unknown, null, undefined> | null = null
let currentZoomK = 1

/** 多数据集联选时按 trip_id 去重，优先保留记者全量记录 */
const DS_PRIORITY: Record<string, number> = { journalist: 3, filah: 2, trout: 1 }

function dedupeTrips(trips: TripRecord[]): TripRecord[] {
  const map = new Map<string, TripRecord>()
  trips.forEach(t => {
    const existing = map.get(t.trip_id)
    if (!existing || (DS_PRIORITY[t.dataset] ?? 0) > (DS_PRIORITY[existing.dataset] ?? 0)) {
      map.set(t.trip_id, t)
    }
  })
  return Array.from(map.values())
}

function effectiveTrips(): TripRecord[] {
  return dedupeTrips(props.trips)
}

const tripStats = computed(() => {
  let visits = 0
  const tripIds = new Set<string>()
  effectiveTrips().forEach(t => {
    const valid = (t.places || []).filter(p => p.lat != null && p.lon != null)
    if (valid.length) tripIds.add(t.trip_id)
    visits += valid.length
  })
  const places = filterPlaces(aggregatePlacesFrom(effectiveTrips())).length
  return { trips: tripIds.size, visits, places }
})

const zoneFilterOptions = computed(() => {
  const zones = new Set<string>()
  aggregatePlacesFrom(effectiveTrips()).forEach(p => zones.add(p.zone))
  return [...zones].sort().map(z => ({
    zone: z,
    label: ZONE_LABELS[z] || z,
    color: ZONE_COLORS[z] || ZONE_COLORS.unknown,
  }))
})

function syncZoneFilters() {
  const zones = zoneFilterOptions.value.map(z => z.zone)
  for (const z of [...activeZoneSet]) {
    if (!zones.includes(z)) activeZoneSet.delete(z)
  }
  for (const z of [...userDisabledZones]) {
    if (!zones.includes(z)) userDisabledZones.delete(z)
  }
  // 当前数据中的区域默认显示；用户曾主动取消的保持隐藏；新数据集带来的新区域自动补上
  zones.forEach(z => {
    if (userDisabledZones.has(z)) activeZoneSet.delete(z)
    else activeZoneSet.add(z)
  })
  if (activeZoneSet.size === 0) {
    zones.forEach(z => activeZoneSet.add(z))
    userDisabledZones.clear()
  }
}

function toggleZone(zone: string) {
  if (activeZoneSet.has(zone)) {
    if (activeZoneSet.size > 1) {
      activeZoneSet.delete(zone)
      userDisabledZones.add(zone)
    }
  } else {
    activeZoneSet.add(zone)
    userDisabledZones.delete(zone)
  }
  selectedPlaceId.value = null
  drawTripLayer()
}

function clearPlaceSelection() {
  selectedPlaceId.value = null
  applyPlaceStyles()
}

function aggregatePlacesFrom(trips: TripRecord[]): PlaceAgg[] {
  const map = new Map<string, PlaceAgg>()
  trips.forEach(trip => {
    (trip.places || []).forEach(p => {
      const coord = placeGeoCoord(p)
      if (!coord) return
      const id = String(p.id || `${coord[0]},${coord[1]}`)
      const zone = p.zone || 'unknown'
      if (!map.has(id)) {
        map.set(id, {
          id,
          name: p.name || id,
          zone,
          coord,
          count: 0,
          members: new Set(),
          datasets: new Set(),
        })
      }
      const agg = map.get(id)!
      agg.count += 1
      agg.members.add(trip.person)
      agg.datasets.add(trip.dataset)
    })
  })
  return Array.from(map.values())
}

function normalizeKind(kind: string | undefined): string {
  const k = (kind ?? '').trim()
  if (k === 'city') return 'City'
  return k || 'default'
}

/** 数据中 lat≈经度、lon≈纬度，与 GeoJSON [lon,lat] 顺序一致 */
function placeGeoCoord(p: { lat: number | null; lon: number | null }): [number, number] | null {
  if (p.lat == null || p.lon == null) return null
  return [p.lat, p.lon]
}

function showTooltip(ev: MouseEvent, name: string, lines: string[]) {
  tt.name = name
  tt.lines = lines
  tt.show = true
  tt.x = ev.clientX + 14
  tt.y = ev.clientY - 12
}

function moveTooltip(ev: MouseEvent) {
  tt.x = ev.clientX + 14
  tt.y = ev.clientY - 12
}

function hideTooltip() { tt.show = false }

function legStyle(it: { fill: string; stroke: string }) {
  return { background: it.fill, borderColor: it.stroke }
}

function placeRadius(k: number): number {
  return PLACE_R / k
}

function aggregatePlaces(): PlaceAgg[] {
  return aggregatePlacesFrom(effectiveTrips())
}

function filterPlaces(aggs: PlaceAgg[]): PlaceAgg[] {
  let list = aggs
  if (props.selectedMember) {
    list = list.filter(p => p.members.has(props.selectedMember))
  }
  if (activeZoneSet.size > 0) {
    list = list.filter(p => activeZoneSet.has(p.zone))
  }
  return list
}

function focusPlaceId(): string | null {
  return hoveredPlaceId.value || selectedPlaceId.value
}

function placeOpacity(placeId: string): number {
  const focus = focusPlaceId()
  if (!focus) return 0.82
  return placeId === focus ? 1 : 0.12
}

function placeStroke(placeId: string): string {
  const focus = focusPlaceId()
  if (!focus) return '#fff'
  return placeId === focus ? '#0f172a' : 'rgba(255,255,255,0.35)'
}

function placeStrokeWidth(placeId: string, k: number): number {
  const focus = focusPlaceId()
  if (!focus) return 1.5 / k
  return placeId === focus ? 2.5 / k : 1 / k
}

function applyPlaceStyles() {
  if (!zoomG) return
  const k = currentZoomK
  zoomG.selectAll<SVGCircleElement, PlacedMarker>('circle.trip-place')
    .attr('fill-opacity', d => placeOpacity(d.id))
    .attr('stroke', d => placeStroke(d.id))
    .attr('stroke-width', d => placeStrokeWidth(d.id, k))
}

/** 落点固定在真实地理坐标（与 BAIT 示例一致，不做碰撞推开） */
function projectPlaces(aggs: PlaceAgg[], proj: d3.GeoIdentityTransform): PlacedMarker[] {
  const out: PlacedMarker[] = []
  aggs.forEach(agg => {
    const pt = proj(agg.coord)
    if (!pt) return
    out.push({ ...agg, x: pt[0], y: pt[1] })
  })
  return out
}

async function loadGeo(): Promise<boolean> {
  if (geoData) return true
  try {
    const res = await fetch('/oceanus_map.geojson')
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    geoData = await res.json()
    buildGeoLegend()
    return true
  } catch (e: unknown) {
    errMsg.value = '地图加载失败：' + (e instanceof Error ? e.message : String(e))
    mapState.value = 'error'
    return false
  }
}

function buildGeoLegend() {
  geoLegend.value = [
    { label: '岛屿', fill: REGION_COLORS.Island, stroke: '#64748b', shape: '' },
    { label: '渔场', fill: REGION_COLORS['Fishing Ground'], stroke: '#64748b', shape: '' },
    { label: '生态保护区', fill: REGION_COLORS['Ecological Preserve'], stroke: '#64748b', shape: '' },
    { label: '城市', fill: '#ffffff', stroke: '#64748b', shape: 'leg-dot' },
    { label: '导航浮标', fill: '#60a5fa', stroke: '#2563eb', shape: 'leg-buoy' },
  ]
}

function getSize() {
  return { W: wrapEl.value?.clientWidth || 700, H: wrapEl.value?.clientHeight || 400 }
}

function updateMarkerSizes(k: number) {
  currentZoomK = k
  if (!zoomG) return
  zoomG.selectAll<SVGCircleElement, GeoJSON.Feature>('circle.feat-city, circle.feat-buoy')
    .attr('r', FEAT_R / k)
    .attr('stroke-width', 1.5 / k)
  zoomG.selectAll<SVGCircleElement, GeoJSON.Feature>('circle.feat-buoy-inner')
    .attr('r', 2 / k)
  zoomG.selectAll<SVGCircleElement, PlacedMarker>('circle.trip-place')
    .attr('r', placeRadius(k))
    .attr('stroke-width', 1.5 / k)
  zoomG.selectAll<SVGPathElement, unknown>('path.trip-route')
    .attr('stroke-width', 2 / k)
  applyPlaceStyles()
}

function setupZoom(svg: d3.Selection<SVGSVGElement, unknown, null, undefined>) {
  zoom = d3.zoom<SVGSVGElement, unknown>()
    .scaleExtent([0.35, 10])
    .filter(e => !e.ctrlKey && (e.type === 'wheel' || e.button === 0))
    .on('zoom', ev => {
      if (!zoomG) return
      zoomG.attr('transform', ev.transform.toString())
      currentZoomK = ev.transform.k
      updateMarkerSizes(ev.transform.k)
    })
  svg.call(zoom)
}

function bindMarkerEvents(
  sel: d3.Selection<SVGCircleElement, PlacedMarker, SVGGElement, unknown>,
  k: number,
) {
  sel
    .attr('fill', d => ZONE_COLORS[d.zone] || ZONE_COLORS.unknown)
    .attr('fill-opacity', d => placeOpacity(d.id))
    .attr('stroke', d => placeStroke(d.id))
    .attr('stroke-width', d => placeStrokeWidth(d.id, k))
    .style('cursor', 'pointer')
    .on('mouseenter', (ev, d) => {
      hoveredPlaceId.value = d.id
      applyPlaceStyles()
      const members = [...d.members].join('、')
      const ds = [...d.datasets].map(x => x.toUpperCase()).join('、')
      showTooltip(ev, d.name || d.id, [
        `区域：${ZONE_LABELS[d.zone] || d.zone}`,
        `到访 ${d.count} 次`,
        `成员：${members}`,
        `数据集：${ds}`,
      ])
    })
    .on('mousemove', moveTooltip)
    .on('mouseleave', () => {
      hideTooltip()
      hoveredPlaceId.value = null
      applyPlaceStyles()
    })
    .on('click', (ev, d) => {
      ev.stopPropagation()
      selectedPlaceId.value = selectedPlaceId.value === d.id ? null : d.id
      applyPlaceStyles()
    })
}

function drawTripLayer() {
  if (!zoomG || !projection) return
  syncZoneFilters()
  const proj = projection
  const k = currentZoomK

  hoveredPlaceId.value = null
  zoomG.selectAll('g.trips-layer').remove()
  const tripsG = zoomG.append('g').attr('class', 'trips-layer')

  const aggs = filterPlaces(aggregatePlaces())
  if (!aggs.length) {
    zoneLegend.value = []
    if (selectedPlaceId.value) selectedPlaceId.value = null
    return
  }

  if (selectedPlaceId.value && !aggs.some(p => p.id === selectedPlaceId.value)) {
    selectedPlaceId.value = null
  }

  const zones = [...new Set(aggs.map(a => a.zone))].sort()
  zoneLegend.value = zones.map(z => ({
    zone: z,
    label: ZONE_LABELS[z] || z,
    color: ZONE_COLORS[z] || ZONE_COLORS.unknown,
  }))

  if (props.selectedMember) {
    const memberTrips = effectiveTrips().filter(t => t.person === props.selectedMember)
    memberTrips.forEach(trip => {
      const pts = (trip.places || [])
        .map(p => placeGeoCoord(p))
        .filter((c): c is [number, number] => c !== null)
        .map(c => proj(c))
        .filter((p): p is [number, number] => p != null)
      if (pts.length < 2) return
      const color = DATASET_COLORS[trip.dataset] || '#64748b'
      tripsG.append('path')
        .attr('class', 'trip-route')
        .attr('d', d3.line()(pts) ?? '')
        .attr('fill', 'none')
        .attr('stroke', color)
        .attr('stroke-width', 2 / k)
        .attr('stroke-opacity', 0.45)
        .attr('stroke-linejoin', 'round')
        .attr('stroke-linecap', 'round')
        .attr('pointer-events', 'none')
    })
  }

  const markers = projectPlaces(aggs, proj)
  const sel = tripsG.selectAll<SVGCircleElement, PlacedMarker>('circle.trip-place')
    .data(markers, d => d.id)
    .join('circle')
    .attr('class', 'trip-place')
    .attr('cx', d => d.x)
    .attr('cy', d => d.y)
    .attr('r', placeRadius(k))
  bindMarkerEvents(sel, k)
  applyPlaceStyles()
}

function drawBaseMap(W: number, H: number) {
  if (!geoData || !svgEl.value) return

  d3.select(svgEl.value).selectAll('*').remove()
  currentZoomK = 1
  const svg = d3.select(svgEl.value)
    .attr('width', W)
    .attr('height', H)
    .style('background', OCEAN)

  projection = d3.geoIdentity().reflectY(true)
  projection.fitSize([W, H], geoData)
  pathGen = d3.geoPath().projection(projection)

  zoomG = svg.append('g').attr('class', 'zoom-g')
  const polys = geoData.features.filter(f => f.geometry.type !== 'Point')
  const points = geoData.features.filter(f => f.geometry.type === 'Point')

  zoomG.selectAll<SVGPathElement, GeoJSON.Feature>('path.region')
    .data(polys)
    .join('path')
    .attr('class', 'region')
    .attr('d', d => pathGen!(d) ?? '')
    .attr('fill', d => REGION_COLORS[normalizeKind((d.properties as Record<string, string>)?.Kind)] || REGION_COLORS.default)
    .attr('fill-opacity', d => {
      const kind = normalizeKind((d.properties as Record<string, string>)?.Kind)
      return ['Fishing Ground', 'Ecological Preserve'].includes(kind) ? 0.28 : 0.65
    })
    .attr('stroke', '#475569')
    .attr('stroke-width', 1)
    .style('cursor', 'default')
    .on('mouseenter', (ev, d) => {
      const p = (d.properties ?? {}) as Record<string, unknown>
      const name = String(p.Name ?? 'Unknown')
      const kind = KIND_ZH[normalizeKind(String(p.Kind ?? ''))] || String(p.Kind ?? '')
      const acts = (p.Activities as string[] | undefined)?.join('、') || '无'
      showTooltip(ev, name, [`类型：${kind}`, `主要活动：${acts}`])
      d3.select(ev.currentTarget).attr('fill', '#fde68a').attr('fill-opacity', 0.9)
    })
    .on('mousemove', moveTooltip)
    .on('mouseleave', (ev, d) => {
      hideTooltip()
      const kind = normalizeKind((d.properties as Record<string, string>)?.Kind)
      d3.select(ev.currentTarget)
        .attr('fill', REGION_COLORS[kind] || REGION_COLORS.default)
        .attr('fill-opacity', ['Fishing Ground', 'Ecological Preserve'].includes(kind) ? 0.28 : 0.65)
    })

  const k = 1
  const proj = projection
  if (!proj) return
  const ptCoord = (d: GeoJSON.Feature) => {
    const c = (d.geometry as GeoJSON.Point).coordinates as [number, number]
    return proj(c) ?? [0, 0]
  }
  const cities = points.filter(d => (d.properties as Record<string, string>)?.Kind === 'city')
  const buoys = points.filter(d => (d.properties as Record<string, string>)?.Kind === 'buoy')

  const bindFeatEvents = (
    sel: d3.Selection<SVGCircleElement, GeoJSON.Feature, SVGGElement, unknown>,
  ) => sel
    .style('cursor', 'help')
    .on('mouseenter', (ev, d) => {
      const p = (d.properties ?? {}) as Record<string, unknown>
      const name = String(p.Name ?? 'Unknown')
      const kind = KIND_ZH[normalizeKind(String(p.Kind ?? ''))] || String(p.Kind ?? '')
      const acts = (p.Activities as string[] | undefined)?.join('、') || '无'
      showTooltip(ev, name, [`类型：${kind}`, `主要活动：${acts}`])
    })
    .on('mousemove', moveTooltip)
    .on('mouseleave', hideTooltip)

  bindFeatEvents(
    zoomG.selectAll<SVGCircleElement, GeoJSON.Feature>('circle.feat-city')
      .data(cities)
      .join('circle')
      .attr('class', 'feat-city')
      .attr('cx', d => ptCoord(d)[0])
      .attr('cy', d => ptCoord(d)[1])
      .attr('r', FEAT_R / k)
      .attr('fill', '#ffffff')
      .attr('stroke', '#64748b')
      .attr('stroke-width', 1.5 / k),
  )

  bindFeatEvents(
    zoomG.selectAll<SVGCircleElement, GeoJSON.Feature>('circle.feat-buoy')
      .data(buoys)
      .join('circle')
      .attr('class', 'feat-buoy')
      .attr('cx', d => ptCoord(d)[0])
      .attr('cy', d => ptCoord(d)[1])
      .attr('r', FEAT_R / k)
      .attr('fill', '#60a5fa')
      .attr('stroke', '#2563eb')
      .attr('stroke-width', 1.5 / k),
  )

  zoomG.selectAll<SVGCircleElement, GeoJSON.Feature>('circle.feat-buoy-inner')
    .data(buoys)
    .join('circle')
    .attr('class', 'feat-buoy-inner')
    .attr('cx', d => ptCoord(d)[0])
    .attr('cy', d => ptCoord(d)[1])
    .attr('r', 2 / k)
    .attr('fill', '#ffffff')
    .attr('stroke', 'none')
    .attr('pointer-events', 'none')

  setupZoom(svg)
  svg.on('click', () => {
    if (selectedPlaceId.value) {
      selectedPlaceId.value = null
      applyPlaceStyles()
    }
  })
  drawTripLayer()
}

function refreshMap() {
  if (!svgEl.value || !geoData) return
  const { W, H } = getSize()
  drawBaseMap(W, H)
}

async function init() {
  mapState.value = 'loading'
  const ok = await loadGeo()
  if (!ok) return
  await nextTick()
  refreshMap()
  mapState.value = 'ready'
}

function resetZoom() {
  if (!svgEl.value || !zoom) return
  d3.select(svgEl.value).transition().duration(300).call(zoom.transform, d3.zoomIdentity)
}

watch(
  () => [props.trips, props.selectedMember] as const,
  () => {
    selectedPlaceId.value = null
    if (mapState.value === 'ready' && zoomG && projection) drawTripLayer()
  },
  { deep: true },
)

let resizeTimer = 0
let ro: ResizeObserver | null = null
onMounted(async () => {
  await nextTick()
  requestAnimationFrame(() => init())
  ro = new ResizeObserver(() => {
    clearTimeout(resizeTimer)
    resizeTimer = window.setTimeout(() => {
      if (mapState.value === 'ready') refreshMap()
    }, 200)
  })
  if (wrapEl.value) ro.observe(wrapEl.value)
})

onUnmounted(() => {
  ro?.disconnect()
  clearTimeout(resizeTimer)
})
</script>

<style scoped>
.map-root {
  display: flex; flex-direction: column;
  border: 1px solid #e2e8f0; border-radius: 10px; overflow: hidden; background: #fff;
}
.map-bar {
  display: flex; align-items: center; flex-wrap: wrap; gap: 8px 10px;
  padding: 6px 10px; background: #f8fafc; border-bottom: 1px solid #e2e8f0;
}
.bar-stat { font-size: 11px; color: #64748b; flex-shrink: 0; }
.zone-filters {
  display: flex; align-items: center; flex-wrap: wrap; gap: 4px; flex: 1; min-width: 0;
}
.filter-label { font-size: 10px; color: #94a3b8; margin-right: 2px; flex-shrink: 0; }
.zone-chip {
  padding: 2px 8px; border-radius: 20px; border: 1px solid #e2e8f0;
  background: #fff; font-size: 10px; color: #94a3b8; cursor: pointer; font-weight: 500;
}
.zone-chip--on { font-weight: 700; }
.bar-actions { display: flex; gap: 6px; margin-left: auto; flex-shrink: 0; }
.bar-btn {
  font-size: 11px; padding: 4px 10px; border-radius: 5px; flex-shrink: 0;
  border: 1px solid #e2e8f0; background: #fff; color: #64748b; cursor: pointer;
}
.bar-btn:hover { background: #f1f5f9; }
.map-wrap { position: relative; flex: 1; min-height: 420px; overflow: hidden; }
.map-svg { width: 100%; height: 100%; display: block; cursor: grab; }
.map-svg:active { cursor: grabbing; }
.map-hint {
  position: absolute; top: 8px; left: 10px; font-size: 10px; color: #64748b;
  background: rgba(255,255,255,0.92); padding: 3px 8px; border-radius: 4px;
  pointer-events: none; border: 1px solid #e2e8f0;
}
.legend-box {
  position: absolute;
  background: rgba(255,255,255,0.96); border: 1px solid #e2e8f0;
  border-radius: 6px; padding: 8px 10px; font-size: 10px; color: #475569;
  pointer-events: none; max-width: 140px;
}
.legend-geo { bottom: 10px; right: 10px; }
.legend-trip { bottom: 10px; left: 10px; }
.leg-row { display: flex; align-items: center; gap: 6px; margin-top: 3px; }
.leg-sw { width: 12px; height: 9px; border-radius: 2px; border: 1px solid rgba(0,0,0,0.12); flex-shrink: 0; }
.leg-dot { width: 9px; height: 9px; border-radius: 50%; border: 1px solid rgba(255,255,255,0.9); flex-shrink: 0; }
.leg-buoy {
  position: relative; border-radius: 50%; width: 8px; height: 8px;
  background: #60a5fa; border: 1px solid #2563eb;
}
.leg-buoy::after {
  content: ''; position: absolute; inset: 0; margin: auto;
  width: 3px; height: 3px; border-radius: 50%; background: #fff;
}
.leg-title { font-size: 9px; font-weight: 700; color: #94a3b8; margin-bottom: 4px; }
.map-mask {
  position: absolute; inset: 0; display: flex; align-items: center; justify-content: center;
  background: rgba(255,255,255,0.7); font-size: 13px; color: #64748b;
}
.map-err { color: #dc2626; }
.map-tt {
  position: fixed; pointer-events: none; z-index: 9999;
  background: #fff; border: 1px solid #e2e8f0; border-radius: 8px;
  padding: 8px 12px; font-size: 12px; box-shadow: 0 4px 14px rgba(0,0,0,.12);
  max-width: 300px;
}
.tt-name { font-weight: 700; color: #0f172a; font-size: 13px; margin-bottom: 4px; }
.tt-line { font-size: 11px; color: #475569; line-height: 1.55; }
</style>
