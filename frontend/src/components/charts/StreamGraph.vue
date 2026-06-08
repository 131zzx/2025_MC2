<template>
  <div class="chart-container">
    <svg ref="svgEl" :width="W" :height="H" />
    <div class="legend">
      <div v-for="(color, industry) in INDUSTRY_COLORS" :key="industry" class="legend-item">
        <span class="dot" :style="{ background: color }"></span>
        {{ INDUSTRY_LABELS[industry] }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import * as d3 from 'd3'
import { INDUSTRY_COLORS, INDUSTRY_LABELS } from '../../types'

const props = defineProps<{
  data: Array<{ meeting_id: string, industry: string, count: number }>
}>()

const W = 800, H = 300
const margin = { top: 20, right: 30, bottom: 40, left: 40 }
const svgEl = ref<SVGElement>()

function draw() {
  if (!svgEl.value || !props.data.length) return
  const svg = d3.select(svgEl.value)
  svg.selectAll('*').remove()

  const industries = ['fishing', 'tourism', 'mixed', 'neutral']
  
  // 数据透视：按 meeting_id 分组
  const meetingsMap = d3.group(props.data, d => d.meeting_id)
  const meetingIds = Array.from(meetingsMap.keys()).sort((a, b) => {
    // 提取数字进行排序，如 Meeting_1, Meeting_2
    const numA = parseInt(a.split('_')[1]) || 0
    const numB = parseInt(b.split('_')[1]) || 0
    return numA - numB
  })

  const stackedData = meetingIds.map(id => {
    const row: any = { meeting: id }
    industries.forEach(ind => {
      row[ind] = meetingsMap.get(id)?.find(d => d.industry === ind)?.count ?? 0
    })
    return row
  })

  const stack = d3.stack().keys(industries)
  const series = stack(stackedData)

  const x = d3.scaleBand()
    .domain(meetingIds)
    .range([margin.left, W - margin.right])
    .padding(0.2)

  const y = d3.scaleLinear()
    .domain([0, d3.max(series, d => d3.max(d, d => d[1])) ?? 10])
    .nice()
    .range([H - margin.bottom, margin.top])

  const g = svg.append('g')

  // 绘制轴
  g.append('g')
    .attr('transform', `translate(0,${H - margin.bottom})`)
    .call(d3.axisBottom(x).tickFormat(d => d.split('_')[1])) // 只显示序号
    .selectAll('text')
    .style('font-size', '10px')

  g.append('g')
    .attr('transform', `translate(${margin.left},0)`)
    .call(d3.axisLeft(y).ticks(5))

  // 绘制条形
  g.selectAll('.serie')
    .data(series)
    .join('g')
    .attr('fill', d => (INDUSTRY_COLORS as any)[d.key])
    .selectAll('rect')
    .data(d => d)
    .join('rect')
    .attr('x', d => x(d.data.meeting)!)
    .attr('y', d => y(d[1]))
    .attr('height', d => y(d[0]) - y(d[1]))
    .attr('width', x.bandwidth())
    .append('title')
    .text(d => `${d.data.meeting}: ${d[1] - d[0]}`)
}

onMounted(draw)
watch(() => props.data, draw, { deep: true })
</script>

<style scoped>
.chart-container { display: flex; flex-direction: column; align-items: center; }
.legend { display: flex; gap: 15px; margin-top: 10px; flex-wrap: wrap; justify-content: center; }
.legend-item { display: flex; align-items: center; font-size: 11px; color: #64748b; }
.dot { width: 8px; height: 8px; border-radius: 2px; margin-right: 4px; }
</style>
