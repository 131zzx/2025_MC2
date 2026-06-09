<!--
  成员 x 数据集覆盖矩阵
  绿色 = 全量覆盖, 黄色 = 部分, 红色 = 缺失
-->
<template>
  <div class="matrix-wrap">
    <table class="matrix-table">
      <thead>
        <tr>
          <th class="member-col">成员</th>
          <th v-for="ds in datasets" :key="ds.key" :class="'ds-col ds-col--' + ds.key">
            {{ ds.label }}
          </th>
          <th class="jo-col">记者数据集<br/><span class="sub">（基准活动量）</span></th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="member in COMMITTEE_MEMBERS" :key="member"
          :class="{ 'row--selected': selectedMember === member, 'row--clickable': true }"
          @click="onMemberClick(member)"
        >
          <td class="member-name" :class="{ 'name--selected': selectedMember === member }">{{ member }}</td>
          <td v-for="ds in datasets" :key="ds.key" class="cell">
            <div
              class="cell-inner"
              :class="getCellClass(member, ds.key)"
              :title="getCellTitle(member, ds.key)"
            >
              <span class="cell-icon">{{ getCellIcon(member, ds.key) }}</span>
              <span class="cell-pct">{{ getCellPct(member, ds.key) }}</span>
            </div>
          </td>
          <td class="cell jo-cell">
            <span class="jo-total">{{ getJoTotal(member) }} 条</span>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- 图例 -->
    <div class="legend">
      <span class="leg leg--full">全量覆盖 (100%)</span>
      <span class="leg leg--partial">部分覆盖 (1-99%)</span>
      <span class="leg leg--zero">完全缺失 (0%)</span>
    </div>
  </div>
</template>

<script lang="ts">
export default {}
</script>
<script setup lang="ts">
import type { CoverageItem, MemberActivityItem } from '../../types'
import { COMMITTEE_MEMBERS } from '../../types'

const props = defineProps<{
  /** 兼容旧接口 */
  coverage?: CoverageItem[]
  memberActivity?: MemberActivityItem[]
  /** 新接口：直接传 coverage data */
  data?: CoverageItem[]
  selectedMember?: string
}>()

const emit = defineEmits<{
  (e: 'select-member', name: string | null): void
}>()

// 兼容新旧两种传参方式
const coverageData = () => props.data ?? props.coverage ?? []
const activityData = () => props.memberActivity ?? []

const datasets = [
  { key: 'filah', label: 'FILAH' },
  { key: 'trout', label: 'TROUT' },
] as const

function getCovItem(member: string, ds: string) {
  return coverageData().find(d => d.member === member && d.dataset === ds)
}

function getCellIcon(member: string, ds: string): string {
  const cov = getCovItem(member, ds)?.coverage ?? 0
  if (cov >= 1)   return '●'
  if (cov > 0)    return '◑'
  return '○'
}

function getCellPct(member: string, ds: string): string {
  const cov = getCovItem(member, ds)?.coverage ?? 0
  return (cov * 100).toFixed(0) + '%'
}

function getCellTitle(member: string, ds: string): string {
  const item = getCovItem(member, ds)
  if (!item) return ''
  return `${member} 在 ${ds.toUpperCase()} 中: ${item.overlap_cnt}/${item.jo_activity_cnt} 条 (${(item.coverage * 100).toFixed(1)}%)`
}

function getCellClass(member: string, ds: string): string {
  const cov = getCovItem(member, ds)?.coverage ?? 0
  if (cov >= 1) return 'cell--full'
  if (cov > 0)  return 'cell--partial'
  return 'cell--zero'
}

function getJoTotal(member: string): number {
  const act = activityData().find(d => d.member === member && d.dataset === 'journalist')
  return act?.total_activity ?? 0
}

function onMemberClick(member: string) {
  emit('select-member', props.selectedMember === member ? null : member)
}
</script>

<style scoped>
.matrix-wrap { overflow-x: auto; }

.matrix-table {
  width: 100%; border-collapse: collapse; font-size: 12px;
}

.matrix-table th {
  padding: 8px 12px; text-align: center; font-size: 11px; font-weight: 700;
  letter-spacing: .04em; color: #64748b;
  border-bottom: 2px solid #e2e8f0; white-space: nowrap;
}
.member-col { text-align: left; width: 160px; }
.jo-col     { color: #059669; }
.sub        { font-size: 9px; font-weight: 400; color: #94a3b8; }

.ds-col--filah { color: #d97706; }
.ds-col--trout { color: #2563eb; }

.matrix-table td {
  padding: 6px 10px; border-bottom: 1px solid #f1f5f9;
}
.row--clickable { cursor: pointer; transition: background .12s; }
.row--clickable:hover { background: #f8fafc; }
.row--selected { background: #eff6ff !important; }
.member-name {
  color: #1e293b; font-weight: 600; font-size: 12px; padding-left: 4px;
}
.name--selected { color: #2563eb; font-weight: 700; }

.cell { text-align: center; }
.cell-inner {
  display: inline-flex; flex-direction: column; align-items: center;
  padding: 6px 12px; border-radius: 8px; min-width: 64px;
  cursor: default; transition: transform .15s;
}
.cell-inner:hover { transform: scale(1.05); }

.cell--full    { background: #f0fdf4; color: #15803d; }
.cell--partial { background: #fffbeb; color: #b45309; }
.cell--zero    { background: #fef2f2; color: #b91c1c; }

.cell-icon { font-size: 14px; line-height: 1; }
.cell-pct  { font-size: 10px; font-weight: 700; margin-top: 2px; }

.jo-cell    { text-align: center; }
.jo-total   { font-size: 13px; font-weight: 700; color: #059669; }

.legend {
  display: flex; gap: 20px; margin-top: 12px; font-size: 11px;
}
.leg { display: flex; align-items: center; gap: 6px; color: #64748b; }
.leg::before { content: ''; width: 12px; height: 12px; border-radius: 3px; }
.leg--full::before    { background: #bbf7d0; }
.leg--partial::before { background: #fde68a; }
.leg--zero::before    { background: #fecaca; }
</style>
