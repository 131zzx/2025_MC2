<template>
  <div class="ego-container">
    <div ref="container" class="g6-container" />
    <div class="ego-legend">
      <div class="ego-legend-item"><span class="dot person"></span> 委员会成员</div>
      <div class="ego-legend-item"><span class="dot topic-fish"></span> 渔业议题</div>
      <div class="ego-legend-item"><span class="dot topic-tour"></span> 旅游议题</div>
      <div class="ego-legend-item"><span class="dot other"></span> 其他活动</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted, nextTick } from 'vue'
import { Graph, Extensions, register } from '@antv/g6'
import { INDUSTRY_COLORS } from '../../types'

const props = defineProps<{
  member: string
  graphData: { nodes: any[], edges: any[] }
}>()

const container = ref<HTMLDivElement>()
let graph: Graph | null = null

async function initGraph() {
  if (!container.value) return
  
  const width = container.value.clientWidth || 600

  graph = new Graph({
    container: container.value,
    width: width,
    height: 500,
    autoFit: 'center',
    layout: {
      type: 'force',
      preventOverlap: true,
      nodeSpacing: 50,
      linkDistance: 150,
      nodeStrength: -500,
      animated: true, // 恢复动画以确保布局过程可见
    },
    node: {
      style: {
        size: 30,
        labelText: (d: any) => {
          const label = d.data.label || d.id;
          return label.length > 10 ? label.substring(0, 8) + '...' : label;
        },
        labelFontSize: 10,
        labelFill: '#64748b',
        labelPlacement: 'bottom',
      },
    },
    edge: {
      style: {
        stroke: '#e2e8f0',
        lineWidth: 1,
        endArrow: true,
      },
    },
    behaviors: ['drag-canvas', 'zoom-canvas', 'drag-node'],
  })

  await updateData()
}

async function updateData() {
  if (!graph || !props.member || !props.graphData.nodes.length) return

  const centerNode = props.member
  const egoEdges = props.graphData.edges.filter(
    e => e.source === centerNode || e.target === centerNode
  )
  
  const neighborIds = new Set<string>()
  neighborIds.add(centerNode)
  egoEdges.forEach(e => {
    neighborIds.add(e.source)
    neighborIds.add(e.target)
  })

  const egoNodes = props.graphData.nodes.filter(n => neighborIds.has(n.id))

  const nodes = egoNodes.map(n => {
    let color = '#94a3b8'
    let size = 28
    if (n.id === centerNode) { color = '#6366f1'; size = 45; }
    else if (n.type === 'entity.person') { color = '#818cf8'; }
    else if (n.type === 'topic') {
      if (n.industry === 'fishing') color = '#0ea5e9'
      else if (n.industry === 'tourism') color = '#22c55e'
      else color = '#a855f7'
    }

    return {
      id: n.id,
      data: { ...n },
      style: { fill: color, stroke: '#fff', lineWidth: 2, size: size },
    }
  })

  const edges = egoEdges.map(e => ({
    id: `edge-${e.source}-${e.target}-${Math.random()}`,
    source: e.source,
    target: e.target,
    data: { ...e }
  }))

  graph.setData({ nodes, edges })
  await graph.render()
}

onMounted(async () => {
  await initGraph()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  if (graph) {
    graph.destroy()
    graph = null
  }
  window.removeEventListener('resize', handleResize)
})

function handleResize() {
  if (graph && container.value) {
    graph.setSize(container.value.clientWidth, 500)
  }
}

watch(() => props.member, async () => {
  await updateData()
})
watch(() => props.graphData, async () => {
  await updateData()
}, { deep: true })
</script>

<style scoped>
.ego-container { position: relative; width: 100%; border-radius: 8px; overflow: hidden; background: #fcfcfd; }
.g6-container { width: 100%; height: 500px; }
.ego-legend {
  position: absolute; bottom: 10px; right: 10px;
  background: rgba(255,255,255,0.8); padding: 8px;
  border-radius: 4px; border: 1px solid #e2e8f0;
}
.ego-legend-item { display: flex; align-items: center; font-size: 10px; color: #64748b; margin-bottom: 4px; }
.dot { width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; }
.person { background: #6366f1; }
.topic-fish { background: #0369a1; }
.topic-tour { background: #16a34a; }
.other { background: #94a3b8; }
</style>
