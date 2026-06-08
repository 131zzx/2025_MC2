<template>
  <div class="radar-container">
    <svg ref="svgEl" :width="W" :height="H" />
    <div class="legend">
      <div class="legend-item"><span class="dot filah"></span> FILAH</div>
      <div class="legend-item"><span class="dot trout"></span> TROUT</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import * as d3 from 'd3'
import type { NodeTypeCountItem, TopicDistItem } from '../../types'

const props = defineProps<{
  nodeTypes: NodeTypeCountItem[]
  topicDist: TopicDistItem[]
}>()

const W = 400, H = 360
const svgEl = ref<SVGElement>()

/**
 * 指标定义：
 * 1. 人员覆盖率 (Member Coverage) - FILAH: 3/6, TROUT: 6/6
 * 2. Trip 密度 (Trip Density) - trips / total nodes
 * 3. 渔业议题占比 (Fishing Ratio) - fishing topics / (fishing + tourism)
 * 4. 旅游议题占比 (Tourism Ratio) - tourism topics / (fishing + tourism)
 * 5. 会议完整度 (Meeting Coverage) - meetings / 16 (journalist max)
 */

function calculateMetrics() {
  const filahNodes = props.nodeTypes.find(d => d.dataset === 'filah')
  const troutNodes = props.nodeTypes.find(d => d.dataset === 'trout')
  
  const filahTopics = props.topicDist.filter(d => d.dataset === 'filah')
  const troutTopics = props.topicDist.filter(d => d.dataset === 'trout')

  const getMetric = (ds: 'filah' | 'trout', nodes: any, topics: any[]) => {
    const totalNodes = nodes?.total ?? 1
    const tripCount = nodes?.trip ?? 0
    const meetingCount = nodes?.meeting ?? 0
    
    const fishing = topics.find(t => t.industry === 'fishing')?.count ?? 0
    const tourism = topics.find(t => t.industry === 'tourism')?.count ?? 0
    const topicTotal = (fishing + tourism) || 1

    return [
      { axis: "人员覆盖率", value: ds === 'filah' ? 0.5 : 1.0 },
      { axis: "Trip 密度", value: Math.min(1, (tripCount / totalNodes) * 2) }, // 放大倍率便于观察
      { axis: "渔业议题占比", value: fishing / topicTotal },
      { axis: "旅游议题占比", value: tourism / topicTotal },
      { axis: "会议覆盖率", value: meetingCount / 16 }
    ]
  }

  return [
    { name: 'FILAH', color: '#f59e0b', values: getMetric('filah', filahNodes, filahTopics) },
    { name: 'TROUT', color: '#3b82f6', values: getMetric('trout', troutNodes, troutTopics) }
  ]
}

function draw() {
  if (!svgEl.value) return
  const data = calculateMetrics()
  const svg = d3.select(svgEl.value)
  svg.selectAll('*').remove()

  const radius = Math.min(W, H) / 2 - 50
  const g = svg.append('g').attr('transform', `translate(${W/2},${H/2})`)

  const axes = data[0].values.map(d => d.axis)
  const angleSlice = (Math.PI * 2) / axes.length

  const rScale = d3.scaleLinear().domain([0, 1]).range([0, radius])

  // 背景网格
  const levels = 5
  for (let j = 0; j < levels; j++) {
    const r = (radius / levels) * (j + 1)
    g.append('circle')
      .attr('cx', 0).attr('cy', 0).attr('r', r)
      .attr('fill', 'none').attr('stroke', '#e2e8f0').attr('stroke-dasharray', '4,4')
  }

  // 轴线
  const axisG = g.selectAll('.axis').data(axes).join('g').attr('class', 'axis')
  axisG.append('line')
    .attr('x1', 0).attr('y1', 0)
    .attr('x2', (d, i) => rScale(1.1) * Math.cos(angleSlice * i - Math.PI / 2))
    .attr('y2', (d, i) => rScale(1.1) * Math.sin(angleSlice * i - Math.PI / 2))
    .attr('stroke', '#cbd5e1').attr('stroke-width', 1)

  axisG.append('text')
    .attr('x', (d, i) => rScale(1.2) * Math.cos(angleSlice * i - Math.PI / 2))
    .attr('y', (d, i) => rScale(1.2) * Math.sin(angleSlice * i - Math.PI / 2))
    .attr('text-anchor', (d, i) => {
      const angle = angleSlice * i
      if (angle === 0 || angle === Math.PI) return 'middle'
      return angle < Math.PI ? 'start' : 'end'
    })
    .attr('dy', '0.35em')
    .attr('fill', '#64748b').style('font-size', '11px')
    .text(d => d)

  // 绘制雷达图
  const radarLine = d3.lineRadial<any>()
    .radius(d => rScale(d.value))
    .angle((d, i) => i * angleSlice)
    .curve(d3.curveLinearClosed)

  data.forEach(d => {
    g.append('path')
      .datum(d.values)
      .attr('d', radarLine)
      .attr('fill', d.color).attr('fill-opacity', 0.2)
      .attr('stroke', d.color).attr('stroke-width', 2)
    
    // 描点
    g.selectAll(`.dot-${d.name}`)
      .data(d.values).join('circle')
      .attr('cx', (v, i) => rScale(v.value) * Math.cos(angleSlice * i - Math.PI / 2))
      .attr('cy', (v, i) => rScale(v.value) * Math.sin(angleSlice * i - Math.PI / 2))
      .attr('r', 3).attr('fill', d.color)
  })
}

onMounted(draw)
watch(() => [props.nodeTypes, props.topicDist], draw, { deep: true })
</script>

<style scoped>
.radar-container { display: flex; flex-direction: column; align-items: center; }
.legend { display: flex; gap: 20px; margin-top: 10px; }
.legend-item { display: flex; align-items: center; font-size: 12px; color: #475569; }
.dot { width: 10px; height: 10px; border-radius: 50%; margin-right: 6px; }
.filah { background: #f59e0b; }
.trout { background: #3b82f6; }
</style>
