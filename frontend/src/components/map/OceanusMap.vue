<template>
  <div class="map-root">
    <div class="map-bar">
      <button class="bar-btn" @click="resetZoom">重置视图</button>
    </div>

    <div ref="wrapEl" class="map-wrap">
      <svg ref="svgEl" class="map-svg" />
      <div class="map-hint">滚轮缩放 · 拖拽平移</div>

      <div class="legend-box">
        <div class="leg-title">地理要素</div>
        <div v-for="it in geoLegend" :key="it.label" class="leg-row">
          <span class="leg-sw" :class="it.shape" :style="legStyle(it)" />{{ it.label }}
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
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import * as d3 from 'd3'

const OCEAN = '#c5dce8'
const REGION_COLORS: Record<string, string> = {
  Island: '#e8d5a8',
  'Fishing Ground': '#9ecae1',
  'Ecological Preserve': '#a8d4b4',
  default: '#d1d5db',
}

const KIND_ZH: Record<string, string> = {
  Island: '岛屿', 'Fishing Ground': '渔场', 'Ecological Preserve': '生态保护区',
  City: '城市', city: '城市', buoy: '导航浮标',
}

const FEAT_R = 5

const wrapEl = ref<HTMLDivElement>()
const svgEl = ref<SVGSVGElement>()
const tt = reactive({ show: false, x: 0, y: 0, name: '', lines: [] as string[] })
const mapState = ref<'idle' | 'loading' | 'ready' | 'error'>('idle')
const errMsg = ref('')
const geoLegend = ref<Array<{ label: string; fill: string; stroke: string; shape: string }>>([])

let geoData: GeoJSON.FeatureCollection | null = null
let projection: d3.GeoIdentityTransform | null = null
let pathGen: d3.GeoPath | null = null
let zoom: d3.ZoomBehavior<SVGSVGElement, unknown> | null = null
let zoomG: d3.Selection<SVGGElement, unknown, null, undefined> | null = null

function normalizeKind(kind: string | undefined): string {
  const k = (kind ?? '').trim()
  if (k === 'city') return 'City'
  return k || 'default'
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

function setupZoom(svg: d3.Selection<SVGSVGElement, unknown, null, undefined>) {
  zoom = d3.zoom<SVGSVGElement, unknown>()
    .scaleExtent([0.35, 10])
    .filter(e => !e.ctrlKey && (e.type === 'wheel' || e.button === 0))
    .on('zoom', ev => {
      if (!zoomG) return
      const k = ev.transform.k
      zoomG.attr('transform', ev.transform.toString())
      zoomG.selectAll<SVGCircleElement, GeoJSON.Feature>('circle.feat-city, circle.feat-buoy')
        .attr('r', FEAT_R / k)
        .attr('stroke-width', 1.5 / k)
      zoomG.selectAll<SVGCircleElement, GeoJSON.Feature>('circle.feat-buoy-inner')
        .attr('r', 2 / k)
    })
  svg.call(zoom)
}

function drawBaseMap(W: number, H: number) {
  if (!geoData || !svgEl.value) return

  d3.select(svgEl.value).selectAll('*').remove()
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
      return ['Fishing Ground', 'Ecological Preserve'].includes(kind) ? 0.35 : 0.75
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
        .attr('fill-opacity', ['Fishing Ground', 'Ecological Preserve'].includes(kind) ? 0.35 : 0.75)
    })

  const k = 1
  const proj = projection
  if (!proj) return
  const px = (coords: [number, number]) => proj(coords) ?? [0, 0]
  const ptCoord = (d: GeoJSON.Feature) => px((d.geometry as GeoJSON.Point).coordinates as [number, number])
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
  display: flex; justify-content: flex-end;
  padding: 6px 10px; background: #f8fafc; border-bottom: 1px solid #e2e8f0;
}
.bar-btn {
  font-size: 11px; padding: 4px 10px; border-radius: 5px;
  border: 1px solid #e2e8f0; background: #fff; color: #64748b; cursor: pointer;
}
.bar-btn:hover { background: #f1f5f9; }
.map-wrap { position: relative; flex: 1; min-height: 420px; overflow: hidden; }
.map-svg { width: 100%; height: 100%; display: block; cursor: grab; }
.map-svg:active { cursor: grabbing; }
.map-hint {
  position: absolute; top: 8px; left: 10px; font-size: 10px; color: #94a3b8;
  background: rgba(255,255,255,0.8); padding: 2px 8px; border-radius: 4px;
  pointer-events: none;
}
.legend-box {
  position: absolute; bottom: 10px; right: 10px;
  background: rgba(255,255,255,0.94); border: 1px solid #e2e8f0;
  border-radius: 6px; padding: 8px 10px; font-size: 10px; color: #475569;
  pointer-events: none;
}
.leg-row { display: flex; align-items: center; gap: 6px; margin-top: 3px; }
.leg-sw { width: 12px; height: 9px; border-radius: 2px; border: 1px solid rgba(0,0,0,0.12); flex-shrink: 0; }
.leg-dot { border-radius: 50%; width: 8px; height: 8px; }
.leg-buoy {
  position: relative; border-radius: 50%; width: 8px; height: 8px;
  background: #60a5fa; border: 1px solid #2563eb;
}
.leg-buoy::after {
  content: ''; position: absolute; inset: 0; margin: auto;
  width: 3px; height: 3px; border-radius: 50%; background: #fff;
}
.leg-title { font-size: 9px; font-weight: 700; color: #94a3b8; margin-bottom: 4px; text-transform: uppercase; }
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
