<template>
  <div class="radar-container">
    <svg ref="svgEl" :width="W" :height="H" />
    <div class="legend">
      <div class="legend-item"><span class="dot filah" /> FILAH</div>
      <div class="legend-item"><span class="dot trout" /> TROUT</div>
    </div>
  </div>
</template>

<script lang="ts">
export default {}
</script>
<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import * as d3 from 'd3'
import type { NodeTypeCountItem, TopicDistItem } from '../../types'

const props = defineProps<{
  nodeTypes: NodeTypeCountItem[]
  topicDist: TopicDistItem[]
}>()

const W = 400
const H = 360
const svgEl = ref<SVGSVGElement>()

interface RadarMetric { axis: string; value: number }
interface RadarSeries { name: string; color: string; values: RadarMetric[] }

function calculateMetrics(): RadarSeries[] {
  const filahNodes = props.nodeTypes.filter(d => d.dataset === 'filah')
  const troutNodes = props.nodeTypes.filter(d => d.dataset === 'trout')
  const filahTopics = props.topicDist.filter(d => d.dataset === 'filah')
  const troutTopics = props.topicDist.filter(d => d.dataset === 'trout')

  const countByType = (items: NodeTypeCountItem[], nodeType: string) =>
    items.find(n => n.node_type === nodeType)?.count ?? 0

  const getMetric = (
    ds: 'filah' | 'trout',
    nodeItems: NodeTypeCountItem[],
    topics: TopicDistItem[],
  ): RadarMetric[] => {
    const totalNodes = nodeItems.reduce((s, n) => s + n.count, 0) || 1
    const tripCount = countByType(nodeItems, 'trip')
    const meetingCount = countByType(nodeItems, 'meeting')
    const fishing = topics.find(t => t.industry === 'fishing')?.count ?? 0
    const tourism = topics.find(t => t.industry === 'tourism')?.count ?? 0
    const topicTotal = (fishing + tourism) || 1

    return [
      { axis: '人员覆盖率', value: ds === 'filah' ? 0.5 : 1.0 },
      { axis: 'Trip 密度', value: Math.min(1, (tripCount / totalNodes) * 2) },
      { axis: '渔业议题占比', value: fishing / topicTotal },
      { axis: '旅游议题占比', value: tourism / topicTotal },
      { axis: '会议覆盖率', value: meetingCount / 16 },
    ]
  }

  return [
    { name: 'FILAH', color: '#f59e0b', values: getMetric('filah', filahNodes, filahTopics) },
    { name: 'TROUT', color: '#3b82f6', values: getMetric('trout', troutNodes, troutTopics) },
  ]
}

function axisAnchor(i: number, angleSlice: number): string {
  const angle = angleSlice * i
  if (angle === 0 || angle === Math.PI) return 'middle'
  return angle < Math.PI ? 'start' : 'end'
}

function draw() {
  if (!svgEl.value) return
  const data = calculateMetrics()
  const svg = d3.select(svgEl.value)
  svg.selectAll('*').remove()

  const radius = Math.min(W, H) / 2 - 50
  const g = svg.append('g').attr('transform', `translate(${W / 2},${H / 2})`)

  const axes = data[0].values.map(m => m.axis)
  const angleSlice = (Math.PI * 2) / axes.length
  const rScale = d3.scaleLinear().domain([0, 1]).range([0, radius])

  for (let j = 0; j < 5; j++) {
    const r = (radius / 5) * (j + 1)
    g.append('circle')
      .attr('cx', 0).attr('cy', 0).attr('r', r)
      .attr('fill', 'none').attr('stroke', '#e2e8f0').attr('stroke-dasharray', '4,4')
  }

  const axisG = g.selectAll<SVGGElement, string>('.axis')
    .data(axes)
    .join('g')
    .attr('class', 'axis')

  axisG.append('line')
    .attr('x1', 0).attr('y1', 0)
    .attr('x2', (_axis: string, i: number) => rScale(1.1) * Math.cos(angleSlice * i - Math.PI / 2))
    .attr('y2', (_axis: string, i: number) => rScale(1.1) * Math.sin(angleSlice * i - Math.PI / 2))
    .attr('stroke', '#cbd5e1').attr('stroke-width', 1)

  axisG.append('text')
    .attr('x', (_axis: string, i: number) => rScale(1.2) * Math.cos(angleSlice * i - Math.PI / 2))
    .attr('y', (_axis: string, i: number) => rScale(1.2) * Math.sin(angleSlice * i - Math.PI / 2))
    .attr('text-anchor', (_axis: string, i: number) => axisAnchor(i, angleSlice))
    .attr('dy', '0.35em')
    .attr('fill', '#64748b').style('font-size', '11px')
    .text((axis: string) => axis)

  const radarLine = d3.lineRadial<RadarMetric>()
    .radius(m => rScale(m.value))
    .angle((_m, i) => i * angleSlice)
    .curve(d3.curveLinearClosed)

  data.forEach(series => {
    g.append('path')
      .datum(series.values)
      .attr('d', radarLine)
      .attr('fill', series.color).attr('fill-opacity', 0.2)
      .attr('stroke', series.color).attr('stroke-width', 2)

    g.selectAll<SVGCircleElement, RadarMetric>(`.dot-${series.name}`)
      .data(series.values)
      .join('circle')
      .attr('cx', (m: RadarMetric, i: number) => rScale(m.value) * Math.cos(angleSlice * i - Math.PI / 2))
      .attr('cy', (m: RadarMetric, i: number) => rScale(m.value) * Math.sin(angleSlice * i - Math.PI / 2))
      .attr('r', 3).attr('fill', series.color)
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
