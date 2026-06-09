<template>
  <div class="map-root">
    <div class="map-bar">
      <label class="bar-chk"><input v-model="showRoutes" type="checkbox" /><span>行程路线</span></label>
      <label class="bar-chk"><input v-model="showDots" type="checkbox" /><span>地点热点</span></label>
      
      <!-- 区域行程统计展示 -->
      <div v-if="zoneStats.length" class="zone-summary">
        <span v-for="[zone, count] in zoneStats" :key="zone" class="zone-tag">
          <span class="zt-name">{{ ZONE_LABELS[zone] || zone }}</span>
          <span class="zt-val">{{ count }}</span>
        </span>
      </div>

      <span class="bar-info">{{ props.trips.length }} 条行程 · {{ routeCount }} 条路线</span>
      <button class="bar-btn" @click="resetZoom">重置视图</button>
    </div>

    <div ref="wrapEl" class="map-wrap">
      <svg ref="svgEl" class="map-svg" />
      <canvas ref="canvasEl" class="map-canvas" />

      <div class="legend-box">
        <div class="leg-title">地理分布</div>
        <div v-for="it in GEO_LEGEND" :key="it.label" class="leg-row">
          <span class="leg-sw" :style="{ background: it.fill }" />{{ it.label }}
        </div>
        
        <div class="leg-divider" />
        <div class="leg-title">行程路线 (线)</div>
        <div class="leg-row">
          <span class="leg-sw leg-line" :style="{ background: DATASET_COLORS.filah }" />FILAH 路径
        </div>
        <div class="leg-row">
          <span class="leg-sw leg-line" :style="{ background: DATASET_COLORS.trout }" />TROUT 路径
        </div>
        <div class="leg-row">
          <span class="leg-sw leg-line" :style="{ background: DATASET_COLORS.journalist }" />记者路径
        </div>

        <div class="leg-divider" />
        <div class="leg-title">行程热点 (点)</div>
        <!-- 证据一致性图例（包含记者数据时） -->
        <template v-if="isJournalistActive">
          <div class="leg-row">
            <span class="leg-sw leg-dot" :style="{ background: EVIDENCE_COLORS.both }" />多方证实 (深绿)
          </div>
          <div class="leg-row">
            <span class="leg-sw leg-dot" :style="{ background: EVIDENCE_COLORS.single }" />单方验证 (中绿)
          </div>
          <div class="leg-row">
            <span class="leg-sw leg-dot" :style="{ background: EVIDENCE_COLORS.hidden }" />仅记者有 (浅绿)
          </div>
        </template>
        <!-- 数据集对比图例（不含记者数据时） -->
        <template v-else>
          <div class="leg-row">
            <span class="leg-sw leg-dot" :style="{ background: DATASET_COLORS.filah }" />FILAH 独有
          </div>
          <div class="leg-row">
            <span class="leg-sw leg-dot" :style="{ background: DATASET_COLORS.trout }" />TROUT 独有
          </div>
          <div class="leg-row">
            <span class="leg-sw leg-dot" :style="{ background: '#ef4444' }" />双方共有 (红色)
          </div>
        </template>
      </div>

      <div v-if="mapState === 'loading'" class="map-mask">加载地图…</div>
      <div v-if="mapState === 'error'" class="map-mask map-err">{{ errMsg }}</div>
    </div>

    <Teleport to="body">
      <div v-show="tt.show" class="map-tt" :style="{ left: tt.x + 'px', top: tt.y + 'px' }">
        <div class="tt-name">{{ tt.name }}</div>
        <div v-if="tt.kind" class="tt-sub">{{ tt.kind }}</div>
      </div>
    </Teleport>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
export default defineComponent({ name: 'OceanusMap' })
</script>
<script setup lang="ts">
import { ref, reactive, watch, onMounted, onUnmounted, nextTick, computed } from 'vue'
import * as d3 from 'd3'
import { useDataStore } from '../../stores/dataStore'
import type { TripRecord, PlaceNode } from '../../types'
import { DATASET_COLORS } from '../../types'

const props = defineProps<{
  trips: TripRecord[]
  places: PlaceNode[]
}>()

const store = useDataStore()

// 简洁浅色地图风格（与 BAIT 深蓝不同，但同样清晰）
const OCEAN = '#c5dce8'
const FEAT_STYLE: Record<string, { fill: string; stroke: string }> = {
  Island:               { fill: '#e8d5a8', stroke: '#b8956a' },
  'Fishing Ground':     { fill: '#8fbf9f', stroke: '#5a8f6e' },
  'Ecological Preserve':{ fill: '#a8d4b4', stroke: '#6a9f7a' },
  Port:                 { fill: '#f0a060', stroke: '#c07030' },
  City:                 { fill: '#e8a0a8', stroke: '#b06070' },
  default:              { fill: '#b0c4d0', stroke: '#8090a0' },
}
const GEO_LEGEND = [
  { label: '岛屿', fill: FEAT_STYLE.Island.fill },
  { label: '渔场', fill: FEAT_STYLE['Fishing Ground'].fill },
  { label: '生态保护区', fill: FEAT_STYLE['Ecological Preserve'].fill },
  { label: '港口', fill: FEAT_STYLE.Port.fill },
  { label: '城市', fill: FEAT_STYLE.City.fill },
]

// 证据一致性颜色（当包含记者数据时）
const EVIDENCE_COLORS = {
  both:   '#064e3b', // 双方都有 (深绿)
  single: '#10b981', // 仅一方有 (中绿)
  hidden: '#a7f3d0', // 仅记者有 (浅绿)
}

const wrapEl   = ref<HTMLDivElement>()
const svgEl    = ref<SVGSVGElement>()
const canvasEl = ref<HTMLCanvasElement>()
const tt = reactive({ show: false, x: 0, y: 0, name: '', kind: '' })
const mapState = ref<'idle' | 'loading' | 'ready' | 'error'>('idle')
const errMsg   = ref('')
const showRoutes = ref(true)
const showDots   = ref(true)
const routeCount = ref(0)

// 证据地图：placeId -> Set of datasets
const placeEvidenceMap = computed(() => {
  const map = new Map<string, Set<string>>()
  store.tripRecords.forEach(t => {
    (t.places || []).forEach(p => {
      const pid = String(p.id)
      if (!map.has(pid)) map.set(pid, new Set())
      map.get(pid)!.add(t.dataset)
    })
  })
  return map
})

// 检查当前显示的行程是否包含记者
const isJournalistActive = computed(() => 
  props.trips.some(t => t.dataset === 'journalist')
)

// 区域行程统计
const zoneStats = computed(() => {
  const stats: Record<string, number> = {}
  props.trips.forEach(t => {
    (t.places || []).forEach(p => {
      const zone = store.placeNodes.find(pn => pn.id === p.id)?.zone || 'unknown'
      stats[zone] = (stats[zone] || 0) + 1
    })
  })
  return Object.entries(stats)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 4)
})

const ZONE_LABELS: Record<string, string> = {
  government: '政府',
  tourism: '旅游',
  commercial: '商业',
  industrial: '工业',
  fishing: '渔业',
  nature: '自然',
  residential: '居住',
}

let geoData: GeoJSON.FeatureCollection | null = null
let projection: d3.GeoProjection | null = null
let pathGen: d3.GeoPath | null = null
let zoom: d3.ZoomBehavior<SVGSVGElement, unknown> | null = null
let currentTransform = d3.zoomIdentity
let baseReady = false
let canvasW = 0
let canvasH = 0

// 地点坐标缓存 id → [x,y]
const placeCoords = new Map<string, [number, number]>()
interface RouteLine { pts: [number, number][]; color: string; count: number }
let routes: RouteLine[] = []

function getSize() {
  return { W: wrapEl.value?.clientWidth || 700, H: wrapEl.value?.clientHeight || 400 }
}

function placeKey(id: string | number) { return String(id) }

function coordFromPlace(p: { id: string | number; lat?: number | null; lon?: number | null }): [number, number] | null {
  const cached = placeCoords.get(placeKey(p.id))
  if (cached) return cached
  if (p.lat != null && p.lon != null && projection) {
    const c = projection([p.lon, p.lat])
    if (c) return c as [number, number]
  }
  return null
}

async function loadGeo(): Promise<boolean> {
  if (geoData) return true
  try {
    const res = await fetch('/oceanus_map.geojson')
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    geoData = await res.json()
    return true
  } catch (e: unknown) {
    errMsg.value = '地图加载失败：' + (e instanceof Error ? e.message : String(e))
    mapState.value = 'error'
    return false
  }
}

function buildProjection(W: number, H: number) {
  if (!geoData) return
  projection = d3.geoIdentity().reflectY(true)
  projection.fitSize([W * 0.92, H * 0.92], geoData)
  pathGen = d3.geoPath().projection(projection)

  placeCoords.clear()
  props.places.forEach(p => {
    if (p.lat != null && p.lon != null) {
      const c = projection!([p.lon, p.lat])
      if (c) placeCoords.set(placeKey(p.id), c as [number, number])
    }
  })
}

function drawBaseMap(W: number, H: number, fullRedraw = false) {
  if (!geoData || !pathGen || !svgEl.value) return
  const svg = d3.select(svgEl.value)

  if (fullRedraw) {
    svg.selectAll('*').remove()
    svg.attr('width', W).attr('height', H).style('background', OCEAN)

    const zoomG = svg.append('g').attr('class', 'zoom-g')
    zoomG.selectAll<SVGPathElement, GeoJSON.Feature>('path.feat')
      .data(geoData.features)
      .join('path')
      .attr('class', 'feat')
      .attr('d', d => pathGen!(d) ?? '')
      .each(function (d) {
        const kind = (d.properties as Record<string, string>)?.Kind ?? 'default'
        const s = FEAT_STYLE[kind] ?? FEAT_STYLE.default
        d3.select(this).attr('fill', s.fill).attr('stroke', s.stroke).attr('stroke-width', 0.8)
      })
      .on('mouseenter', (ev, d) => {
        const p = (d.properties ?? {}) as Record<string, string>
        tt.show = true; tt.name = p.Name ?? ''; tt.kind = p.Kind ?? ''
        tt.x = ev.clientX + 12; tt.y = ev.clientY - 10
        d3.select(ev.currentTarget as Element).attr('stroke-width', 2)
      })
      .on('mousemove', ev => { tt.x = ev.clientX + 12; tt.y = ev.clientY - 10 })
      .on('mouseleave', (ev, d) => {
        tt.show = false
        const kind = ((d.properties ?? {}) as Record<string, string>).Kind ?? 'default'
        d3.select(ev.currentTarget as Element)
          .attr('stroke-width', (FEAT_STYLE[kind] ?? FEAT_STYLE.default).stroke ? 0.8 : 0.8)
      })

    if (!zoom) {
      zoom = d3.zoom<SVGSVGElement, unknown>().scaleExtent([0.5, 8])
        .on('zoom', ev => {
          currentTransform = ev.transform
          svg.select('.zoom-g').attr('transform', ev.transform.toString())
          scheduleOverlay()
        })
      svg.call(zoom)
    }
    zoomG.attr('transform', currentTransform.toString())
  } else {
    svg.attr('width', W).attr('height', H)
    svg.select('.zoom-g').selectAll<SVGPathElement, GeoJSON.Feature>('path.feat')
      .attr('d', d => pathGen!(d) ?? '')
  }
}

function buildRoutes() {
  const map = new Map<string, RouteLine>()
  props.trips.forEach(trip => {
    const pts = (trip.places ?? [])
      .map(p => coordFromPlace(p))
      .filter((c): c is [number, number] => c !== null)
    if (pts.length < 2) return
    const key = pts.map(c => `${c[0].toFixed(0)},${c[1].toFixed(0)}`).join('|')
    const color = DATASET_COLORS[trip.dataset] ?? '#64748b'
    const existing = map.get(key)
    if (existing) existing.count++
    else map.set(key, { pts, color, count: 1 })
  })
  routes = Array.from(map.values())
  routeCount.value = routes.length
}

let rafId = 0
function scheduleOverlay() {
  cancelAnimationFrame(rafId)
  rafId = requestAnimationFrame(drawOverlay)
}

function drawOverlay() {
  const canvas = canvasEl.value
  if (!canvas || !baseReady) return
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  const { W, H } = getSize()
  if (W !== canvasW || H !== canvasH) {
    canvasW = W; canvasH = H
    canvas.width = W; canvas.height = H
  }

  ctx.clearRect(0, 0, W, H)
  const t = currentTransform
  ctx.save()
  ctx.translate(t.x, t.y)
  ctx.scale(t.k, t.k)

  // 1. 绘制路线（底层）
  if (showRoutes.value && routes.length) {
    const maxCnt = Math.max(...routes.map(r => r.count), 1)
    const wScale = d3.scaleSqrt().domain([1, maxCnt]).range([1.2 / t.k, 4 / t.k])
    
    // 排序：数量多的路线画在上面
    const sortedRoutes = [...routes].sort((a, b) => a.count - b.count)
    
    sortedRoutes.forEach(r => {
      ctx.beginPath()
      ctx.moveTo(r.pts[0][0], r.pts[0][1])
      for (let i = 1; i < r.pts.length; i++) ctx.lineTo(r.pts[i][0], r.pts[i][1])
      ctx.strokeStyle = r.color
      ctx.globalAlpha = 0.6
      ctx.lineWidth = wScale(r.count)
      ctx.lineJoin = 'round'
      ctx.lineCap = 'round'
      ctx.stroke()
    })
    ctx.globalAlpha = 1
  }

  // 2. 绘制热点（顶层）
  if (showDots.value) {
    const tripCnt = new Map<string, number>()
    props.trips.forEach(trip =>
      (trip.places ?? []).forEach(p => {
        const k = placeKey(p.id)
        tripCnt.set(k, (tripCnt.get(k) ?? 0) + 1)
      }),
    )
    
    const counts = Array.from(tripCnt.values())
    const maxR = counts.length > 0 ? Math.max(...counts) : 1
    const rScale = d3.scaleSqrt().domain([0, maxR]).range([2.5 / t.k, 8 / t.k])
    
    placeCoords.forEach((coord, pid) => {
      const cnt = tripCnt.get(pid) ?? 0
      if (cnt === 0) return
      
      const r = rScale(cnt)
      
      // 决定填充颜色
      let fillColor = 'rgba(255, 255, 255, 0.9)'
      let strokeColor = '#e11d48'
      
      if (isJournalistActive.value) {
        const evidence = placeEvidenceMap.value.get(pid) || new Set()
        const hasFilah = evidence.has('filah')
        const hasTrout = evidence.has('trout')
        
        if (hasFilah && hasTrout) {
          fillColor = EVIDENCE_COLORS.both
          strokeColor = '#064e3b'
        } else if (hasFilah || hasTrout) {
          fillColor = EVIDENCE_COLORS.single
          strokeColor = '#047857'
        } else {
          fillColor = EVIDENCE_COLORS.hidden
          strokeColor = '#10b981'
        }
      } else {
        // 非记者模式：按数据集颜色
        const inFilah = props.trips.some(t => t.dataset === 'filah' && t.places?.some(p => String(p.id) === pid))
        const inTrout = props.trips.some(t => t.dataset === 'trout' && t.places?.some(p => String(p.id) === pid))
        
        if (inFilah && inTrout) {
          fillColor = '#ef4444' // 红色 (双方)
          strokeColor = '#b91c1c'
        } else if (inFilah) {
          fillColor = DATASET_COLORS.filah
          strokeColor = '#d97706'
        } else if (inTrout) {
          fillColor = DATASET_COLORS.trout
          strokeColor = '#1d4ed8'
        }
      }
      
      // 外发光/阴影效果
      ctx.shadowBlur = isJournalistActive.value ? 2 : 4
      ctx.shadowColor = strokeColor + '66'
      
      ctx.beginPath()
      ctx.arc(coord[0], coord[1], r, 0, Math.PI * 2)
      ctx.fillStyle = fillColor
      ctx.fill()
      
      ctx.shadowBlur = 0
      ctx.strokeStyle = strokeColor
      ctx.lineWidth = 1.5 / t.k
      ctx.stroke()
      
      // 中心装饰点
      ctx.beginPath()
      ctx.arc(coord[0], coord[1], 0.8 / t.k, 0, Math.PI * 2)
      ctx.fillStyle = isJournalistActive.value ? 'rgba(255,255,255,0.5)' : strokeColor
      ctx.fill()
    })
  }

  ctx.restore()
}

function refreshOverlay() {
  buildRoutes()
  scheduleOverlay()
}

async function init() {
  mapState.value = 'loading'
  const ok = await loadGeo()
  if (!ok) return
  await nextTick()
  const { W, H } = getSize()
  buildProjection(W, H)
  drawBaseMap(W, H, true)
  refreshOverlay()
  baseReady = true
  mapState.value = 'ready'
}

function resetZoom() {
  if (!svgEl.value || !zoom) return
  d3.select(svgEl.value).transition().duration(300).call(zoom.transform, d3.zoomIdentity)
}

let resizeTimer = 0
let tripSig = ''

function tripSignature(trips: TripRecord[]) {
  return `${trips.length}:${trips[0]?.trip_id ?? ''}:${trips[trips.length - 1]?.trip_id ?? ''}`
}

let ro: ResizeObserver | null = null
onMounted(async () => {
  await nextTick()
  requestAnimationFrame(() => init())
  tripSig = tripSignature(props.trips)

  ro = new ResizeObserver(() => {
    clearTimeout(resizeTimer)
    resizeTimer = window.setTimeout(() => {
      if (!baseReady) return
      const { W, H } = getSize()
      buildProjection(W, H)
      drawBaseMap(W, H, false)
      scheduleOverlay()
    }, 200)
  })
  if (wrapEl.value) ro.observe(wrapEl.value)
})

onUnmounted(() => {
  ro?.disconnect()
  cancelAnimationFrame(rafId)
  clearTimeout(resizeTimer)
})

watch(() => props.trips, (trips) => {
  if (!baseReady) return
  const sig = tripSignature(trips)
  if (sig === tripSig) return
  tripSig = sig
  refreshOverlay()
})

watch([showRoutes, showDots], () => {
  if (baseReady) scheduleOverlay()
})
</script>

<style scoped>
.map-root {
  display: flex; flex-direction: column;
  border: 1px solid #e2e8f0; border-radius: 10px; overflow: hidden; background: #fff;
}
.map-bar {
  display: flex; align-items: center; gap: 14px; flex-wrap: wrap;
  padding: 8px 14px; background: #f8fafc; border-bottom: 1px solid #e2e8f0;
}
.bar-chk {
  display: flex; align-items: center; gap: 5px;
  font-size: 12px; color: #64748b; cursor: pointer; user-select: none;
}
.zone-summary {
  display: flex; gap: 8px; margin-left: 10px;
}
.zone-tag {
  display: flex; align-items: center; gap: 4px;
  background: #f1f5f9; padding: 2px 8px; border-radius: 4px;
  font-size: 10px; color: #475569; border: 1px solid #e2e8f0;
}
.zt-name { color: #94a3b8; }
.zt-val  { font-weight: 700; color: #1e293b; }
.bar-info { font-size: 11px; color: #94a3b8; margin-left: auto; }
.bar-btn {
  font-size: 11px; padding: 4px 10px; border-radius: 5px;
  border: 1px solid #e2e8f0; background: #fff; color: #64748b; cursor: pointer;
}
.bar-btn:hover { background: #f1f5f9; }
.map-wrap { position: relative; flex: 1; min-height: 400px; overflow: hidden; }
.map-svg, .map-canvas { position: absolute; inset: 0; width: 100%; height: 100%; display: block; }
.map-canvas { pointer-events: none; }
.legend-box {
  position: absolute; bottom: 10px; right: 10px;
  background: rgba(255,255,255,0.92); border: 1px solid #e2e8f0;
  border-radius: 6px; padding: 8px 10px; font-size: 10px; color: #475569;
}
.leg-row { display: flex; align-items: center; gap: 6px; margin-top: 3px; }
.leg-row:first-child { margin-top: 0; }
.leg-sw { width: 12px; height: 9px; border-radius: 2px; border: 1px solid rgba(0,0,0,0.1); }
.leg-dot { border-radius: 50%; width: 8px; height: 8px; margin: 0 2px; }
.leg-line { height: 2px; width: 12px; border-radius: 1px; border: none; }
.leg-divider { height: 1px; background: #f1f5f9; margin: 8px 0; }
.leg-title { font-size: 9px; font-weight: 700; color: #94a3b8; margin-bottom: 4px; text-transform: uppercase; }
.map-mask {
  position: absolute; inset: 0; display: flex; align-items: center; justify-content: center;
  background: rgba(255,255,255,0.7); font-size: 13px; color: #64748b;
}
.map-err { color: #dc2626; }
.map-tt {
  position: fixed; pointer-events: none; z-index: 9999;
  background: #fff; border: 1px solid #e2e8f0; border-radius: 6px;
  padding: 6px 10px; font-size: 12px; box-shadow: 0 2px 8px rgba(0,0,0,.12);
}
.tt-name { font-weight: 700; color: #1e293b; }
.tt-sub  { font-size: 10px; color: #94a3b8; margin-top: 2px; }
</style>
