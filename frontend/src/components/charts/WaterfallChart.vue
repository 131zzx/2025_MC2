<template>
  <div class="chart-container">
    <svg ref="svgEl" :width="W" :height="H" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import * as d3 from 'd3'

const props = defineProps<{
  initialValue: number // FILAH or TROUT bias
  finalValue: number   // Journalist bias
  label: string        // "FILAH -> Journalist"
}>()

const W = 400, H = 250
const margin = { top: 40, right: 40, bottom: 40, left: 60 }
const svgEl = ref<SVGElement>()

function draw() {
  if (!svgEl.value) return
  const svg = d3.select(svgEl.value)
  svg.selectAll('*').remove()

  const diff = props.finalValue - props.initialValue
  const data = [
    { name: '初始 (Subset)', value: props.initialValue, type: 'base' },
    { name: '修正项', value: diff, type: diff >= 0 ? 'pos' : 'neg' },
    { name: '最终 (全量)', value: props.finalValue, type: 'total' }
  ]

  const x = d3.scaleBand()
    .domain(data.map(d => d.name))
    .range([margin.left, W - margin.right])
    .padding(0.3)

  const y = d3.scaleLinear()
    .domain([
      Math.min(0, props.initialValue, props.finalValue) - 0.1,
      Math.max(0, props.initialValue, props.finalValue) + 0.1
    ])
    .nice()
    .range([H - margin.bottom, margin.top])

  const g = svg.append('g')

  // 坐标轴
  g.append('g')
    .attr('transform', `translate(0,${H - margin.bottom})`)
    .call(d3.axisBottom(x))
    .selectAll('text').style('font-size', '11px')

  g.append('g')
    .attr('transform', `translate(${margin.left},0)`)
    .call(d3.axisLeft(y))

  // 绘制矩形
  g.selectAll('.bar')
    .data(data)
    .join('rect')
    .attr('class', 'bar')
    .attr('x', d => x(d.name)!)
    .attr('y', d => {
      if (d.type === 'base' || d.type === 'total') return y(Math.max(0, d.value))
      return y(Math.max(props.initialValue, props.finalValue))
    })
    .attr('width', x.bandwidth())
    .attr('height', d => {
      if (d.type === 'base' || d.type === 'total') return Math.abs(y(0) - y(d.value))
      return Math.abs(y(props.initialValue) - y(props.finalValue))
    })
    .attr('fill', d => {
      if (d.type === 'base') return '#94a3b8'
      if (d.type === 'total') return '#10b981'
      return d.value >= 0 ? '#f59e0b' : '#3b82f6'
    })

  // 连接线
  if (data.length > 1) {
    g.append('line')
      .attr('x1', x(data[0].name)! + x.bandwidth())
      .attr('y1', y(props.initialValue))
      .attr('x2', x(data[1].name)!)
      .attr('y2', y(props.initialValue))
      .attr('stroke', '#cbd5e1').attr('stroke-dasharray', '4,4')

    g.append('line')
      .attr('x1', x(data[1].name)! + x.bandwidth())
      .attr('y1', y(props.finalValue))
      .attr('x2', x(data[2].name)!)
      .attr('y2', y(props.finalValue))
      .attr('stroke', '#cbd5e1').attr('stroke-dasharray', '4,4')
  }

  // 数值标签
  g.selectAll('.label')
    .data(data)
    .join('text')
    .attr('x', d => x(d.name)! + x.bandwidth() / 2)
    .attr('y', d => {
        const val = d.type === 'pos' || d.type === 'neg' ? d.value : d.value
        return y(d.type === 'pos' || d.type === 'neg' ? Math.max(props.initialValue, props.finalValue) : Math.max(0, d.value)) - 5
    })
    .attr('text-anchor', 'middle')
    .style('font-size', '10px').style('font-weight', '700')
    .attr('fill', '#475569')
    .text(d => (d.value >= 0 ? '+' : '') + d.value.toFixed(3))
}

onMounted(draw)
watch(() => [props.initialValue, props.finalValue], draw)
</script>

<style scoped>
.chart-container { display: flex; justify-content: center; }
</style>
