<template>
  <div class="ego-wrap">
    <div class="ego-header">
      <span class="ego-title">关系网络：{{ member || '（未选中成员）' }}</span>
      <div class="ego-controls">
        <label class="depth-label">深度</label>
        <button
          v-for="d in [1,2]" :key="d"
          class="depth-btn" :class="depth === d && 'depth-btn--on'"
          @click="depth = d"
        >{{ d }}</button>
        <button class="recenter-btn" @click="recenter">重置视图</button>
      </div>
    </div>

    <div ref="svgWrap" class="ego-svg-wrap">
      <svg ref="svgEl" class="ego-svg">
        <defs>
          <marker id="arrow" viewBox="0 -4 8 8" refX="14" refY="0"
            markerWidth="6" markerHeight="6" orient="auto">
            <path d="M0,-4L8,0L0,4" fill="#cbd5e1" />
          </marker>
        </defs>
        <g ref="rootG" class="root-g">
          <g class="edges-g" ref="edgesG" />
          <g class="nodes-g" ref="nodesG" />
        </g>
      </svg>

      <!-- 节点 Tooltip -->
      <div
        v-if="tooltip.show"
        class="ego-tooltip"
        :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px' }"
      >
        <div class="tt-title">{{ tooltip.title }}</div>
        <div class="tt-row" v-if="tooltip.type">类型：{{ tooltip.type }}</div>
        <div class="tt-row" v-if="tooltip.industry">行业：{{ tooltip.industry }}</div>
        <div class="tt-row" v-if="tooltip.sentiment != null">
          情感：{{ tooltip.sentiment > 0 ? '+' : '' }}{{ tooltip.sentiment.toFixed(2) }}
        </div>
      </div>
    </div>

    <div class="ego-legend">
      <div v-for="item in legendItems" :key="item.label" class="legend-item">
        <span class="legend-dot" :style="{ background: item.color, width: item.size + 'px', height: item.size + 'px' }" />
        {{ item.label }}
      </div>
    </div>

    <div v-if="!member" class="ego-placeholder">
      <div class="placeholder-icon">◈</div>
      <div>在左侧面板选择委员会成员以查看关系网络</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  ref, watch, onMounted, onUnmounted, nextTick, computed,
} from 'vue'
import * as d3 from 'd3'

const props = defineProps<{
  member: string
  graphData: { nodes: any[]; edges: any[] }
}>()

const emit = defineEmits<{ (e: 'node-click', id: string, type: string): void }>()

const depth = ref(1)

const svgWrap  = ref<HTMLDivElement>()
const svgEl    = ref<SVGSVGElement>()
const rootG    = ref<SVGGElement>()
const edgesG   = ref<SVGGElement>()
const nodesG   = ref<SVGGElement>()

let simulation: d3.Simulation<any, any> | null = null
let zoom: d3.ZoomBehavior<SVGSVGElement, unknown> | null = null

const tooltip = ref({ show: false, x: 0, y: 0, title: '', type: '', industry: '', sentiment: null as number | null })

const NODE_COLORS: Record<string, string> = {
  ego:           '#2563eb',
  person:        '#7c3aed',
  topic_fishing: '#0369a1',
  topic_tourism: '#16a34a',
  topic_mixed:   '#9333ea',
  meeting:       '#f59e0b',
  other:         '#94a3b8',
}

const legendItems = [
  { color: NODE_COLORS.ego,           size: 18, label: '中心成员' },
  { color: NODE_COLORS.person,        size: 14, label: '委员会成员' },
  { color: NODE_COLORS.topic_fishing, size: 12, label: '渔业议题' },
  { color: NODE_COLORS.topic_tourism, size: 12, label: '旅游议题' },
  { color: NODE_COLORS.meeting,       size: 12, label: '会议/计划' },
]

// ── 构建自我中心子图 ────────────────────────────────────
function buildEgoGraph(center: string, allNodes: any[], allEdges: any[], d: number) {
  const visited = new Set<string>([center])
  let frontier = new Set<string>([center])

  for (let i = 0; i < d; i++) {
    const next = new Set<string>()
    allEdges.forEach(e => {
      if (frontier.has(e.source) && !visited.has(e.target)) {
        visited.add(e.target); next.add(e.target)
      }
      if (frontier.has(e.target) && !visited.has(e.source)) {
        visited.add(e.source); next.add(e.source)
      }
    })
    frontier = next
  }

  const nodes = allNodes.filter(n => visited.has(n.id)).map(n => ({
    id:       n.id,
    label:    n.data?.label || n.label || n.id,
    type:     n.data?.type  || n.type  || 'other',
    industry: n.data?.industry || n.industry || '',
    sentiment: n.data?.sentiment ?? null,
    isEgo:    n.id === center,
  }))

  const edges = allEdges.filter(
    e => visited.has(e.source) && visited.has(e.target)
  ).map(e => ({ source: e.source, target: e.target, weight: e.weight || 1 }))

  return { nodes, edges }
}

function nodeColor(n: any): string {
  if (n.isEgo) return NODE_COLORS.ego
  const t = n.type || ''
  if (t.includes('person') || t.includes('entity')) return NODE_COLORS.person
  if (t.includes('topic')) {
    if (n.industry === 'fishing') return NODE_COLORS.topic_fishing
    if (n.industry === 'tourism') return NODE_COLORS.topic_tourism
    return NODE_COLORS.topic_mixed
  }
  if (t.includes('meeting') || t.includes('plan') || t.includes('discussion')) return NODE_COLORS.meeting
  return NODE_COLORS.other
}

function nodeRadius(n: any): number {
  if (n.isEgo) return 22
  const t = n.type || ''
  if (t.includes('person') || t.includes('entity')) return 14
  if (t.includes('topic')) return 11
  return 9
}

// ── D3 渲染 ──────────────────────────────────────────────
function render() {
  if (!svgEl.value || !svgWrap.value || !props.member) return

  const { nodes, edges } = buildEgoGraph(
    props.member, props.graphData.nodes, props.graphData.edges, depth.value
  )
  if (!nodes.length) return

  const W = svgWrap.value.clientWidth  || 600
  const H = svgWrap.value.clientHeight || 420

  d3.select(svgEl.value).attr('width', W).attr('height', H)

  // ── 停止旧 simulation ─────────────────────────────────
  if (simulation) { simulation.stop(); simulation = null }

  const svgSel = d3.select(svgEl.value)

  // ── 绑定 zoom ─────────────────────────────────────────
  if (!zoom) {
    zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.3, 3])
      .on('zoom', ev => {
        d3.select(rootG.value!).attr('transform', ev.transform)
      })
    svgSel.call(zoom)
  }

  // ── 初始位置（扇形分散） ───────────────────────────────
  const nonEgo = nodes.filter(n => !n.isEgo)
  const angleStep = (2 * Math.PI) / Math.max(nonEgo.length, 1)
  const initR = Math.min(W, H) * 0.28

  nodes.forEach((n, i) => {
    if (n.isEgo) {
      n.x = W / 2; n.y = H / 2; n.fx = W / 2; n.fy = H / 2
    } else {
      const idx = nonEgo.indexOf(n)
      n.x = W / 2 + initR * Math.cos(idx * angleStep)
      n.y = H / 2 + initR * Math.sin(idx * angleStep)
    }
  })

  // ── 边 ─────────────────────────────────────────────────
  const edgeSel = d3.select(edgesG.value!)
    .selectAll<SVGLineElement, any>('line')
    .data(edges, (d: any) => `${d.source}-${d.target}`)

  const edgeMerge = edgeSel.enter().append('line')
    .attr('stroke', '#cbd5e1')
    .attr('stroke-opacity', 0.6)
    .attr('stroke-width', 1.5)
    .attr('marker-end', 'url(#arrow)')
    .merge(edgeSel as any)

  edgeSel.exit().remove()

  // ── 节点 ───────────────────────────────────────────────
  const nodeSel = d3.select(nodesG.value!)
    .selectAll<SVGGElement, any>('g.node')
    .data(nodes, (d: any) => d.id)

  const nodeEnter = nodeSel.enter().append('g').attr('class', 'node').style('cursor', 'pointer')

  nodeEnter.append('circle')
    .attr('r', nodeRadius)
    .attr('fill', nodeColor)
    .attr('stroke', '#fff')
    .attr('stroke-width', 2)
    .attr('filter', 'drop-shadow(0 1px 3px rgba(0,0,0,.15))')

  nodeEnter.append('text')
    .attr('dy', (n: any) => nodeRadius(n) + 11)
    .attr('text-anchor', 'middle')
    .attr('font-size', 9)
    .attr('fill', '#475569')
    .text((n: any) => {
      const l = n.label || n.id
      return l.length > 14 ? l.slice(0, 12) + '…' : l
    })

  const nodeMerge = nodeEnter.merge(nodeSel as any)

  nodeMerge.select('circle')
    .attr('r', nodeRadius)
    .attr('fill', nodeColor)

  nodeSel.exit().remove()

  // ── 拖拽 ────────────────────────────────────────────────
  const drag = d3.drag<SVGGElement, any>()
    .on('start', (event, d) => {
      if (!event.active) simulation!.alphaTarget(0.15).restart()
      d.fx = d.x; d.fy = d.y
    })
    .on('drag', (event, d) => {
      d.fx = event.x; d.fy = event.y
    })
    .on('end', (event, d) => {
      if (!event.active) simulation!.alphaTarget(0)
      if (!d.isEgo) { d.fx = null; d.fy = null }
    })

  nodeMerge.call(drag)

  // ── 悬停/点击 ───────────────────────────────────────────
  nodeMerge
    .on('mouseenter', (event, d) => {
      tooltip.value = {
        show: true,
        x: event.offsetX + 12,
        y: event.offsetY - 8,
        title: d.label || d.id,
        type: d.type,
        industry: d.industry,
        sentiment: d.sentiment,
      }
      d3.select(event.currentTarget).select('circle')
        .transition().duration(100)
        .attr('r', nodeRadius(d) + 4)
        .attr('stroke-width', 3)
    })
    .on('mousemove', event => {
      tooltip.value.x = event.offsetX + 12
      tooltip.value.y = event.offsetY - 8
    })
    .on('mouseleave', (event, d) => {
      tooltip.value.show = false
      d3.select(event.currentTarget).select('circle')
        .transition().duration(100)
        .attr('r', nodeRadius(d))
        .attr('stroke-width', 2)
    })
    .on('click', (_, d) => emit('node-click', d.id, d.type))

  // ── 力导向 simulation ─────────────────────────────────
  simulation = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(edges)
      .id((d: any) => d.id)
      .distance(d => (d.source.isEgo || d.target.isEgo) ? 100 : 70)
      .strength(0.6)
    )
    .force('charge', d3.forceManyBody().strength(-200))
    .force('collision', d3.forceCollide((d: any) => nodeRadius(d) + 10))
    .alphaDecay(0.025)   // 适度衰减，不要太慢
    .velocityDecay(0.5)  // 阻尼，防止震荡
    .on('tick', () => {
      edgeMerge
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y)

      nodeMerge.attr('transform', (d: any) => `translate(${d.x},${d.y})`)
    })
    .on('end', () => {
      // simulation 结束后固定所有非 ego 节点，防止二次抖动
      nodes.forEach(n => { if (!n.isEgo) { n.fx = n.x; n.fy = n.y } })
    })
}

function recenter() {
  if (!svgEl.value || !zoom) return
  const W = svgWrap.value?.clientWidth  || 600
  const H = svgWrap.value?.clientHeight || 420
  d3.select(svgEl.value).transition().duration(400)
    .call(zoom.transform, d3.zoomIdentity.translate(W / 2, H / 2).scale(1).translate(-W / 2, -H / 2))
}

onMounted(async () => {
  await nextTick()
  render()
})

watch([() => props.member, () => props.graphData, depth], async () => {
  await nextTick()
  render()
})

onUnmounted(() => { if (simulation) { simulation.stop(); simulation = null } })
</script>

<style scoped>
.ego-wrap {
  position: relative; width: 100%; background: #fff;
  border: 1px solid #e2e8f0; border-radius: 10px; overflow: hidden;
}

.ego-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 14px; border-bottom: 1px solid #f1f5f9;
  background: #f8fafc;
}
.ego-title { font-size: 13px; font-weight: 600; color: #1e293b; }
.ego-controls { display: flex; align-items: center; gap: 6px; }
.depth-label { font-size: 11px; color: #64748b; }
.depth-btn {
  padding: 3px 8px; border-radius: 4px; border: 1px solid #e2e8f0;
  background: #fff; font-size: 11px; cursor: pointer; color: #64748b;
}
.depth-btn--on { background: #eff6ff; border-color: #93c5fd; color: #2563eb; font-weight: 700; }
.recenter-btn {
  padding: 3px 8px; border-radius: 4px; border: 1px solid #e2e8f0;
  background: #fff; font-size: 11px; cursor: pointer; color: #64748b;
  margin-left: 4px;
}
.recenter-btn:hover { background: #f1f5f9; }

.ego-svg-wrap {
  position: relative; width: 100%; height: 400px;
  background: linear-gradient(135deg, #fafafa 0%, #f0f4ff 100%);
}
.ego-svg { width: 100%; height: 100%; }

.ego-tooltip {
  position: absolute; pointer-events: none; z-index: 10;
  background: rgba(255,255,255,0.96); border: 1px solid #e2e8f0;
  border-radius: 8px; padding: 8px 11px; font-size: 12px; color: #1e293b;
  box-shadow: 0 4px 12px rgba(0,0,0,.1); max-width: 200px;
}
.tt-title { font-weight: 700; margin-bottom: 4px; }
.tt-row { color: #64748b; font-size: 11px; margin-top: 2px; }

.ego-legend {
  display: flex; flex-wrap: wrap; gap: 8px 16px;
  padding: 8px 14px; border-top: 1px solid #f1f5f9;
  background: #fafafa;
}
.legend-item { display: flex; align-items: center; gap: 5px; font-size: 11px; color: #475569; }
.legend-dot { border-radius: 50%; flex-shrink: 0; }

.ego-placeholder {
  position: absolute; inset: 0;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 10px; font-size: 13px; color: #94a3b8;
  background: rgba(248,250,252,0.9);
}
.placeholder-icon { font-size: 36px; opacity: .3; }
</style>
