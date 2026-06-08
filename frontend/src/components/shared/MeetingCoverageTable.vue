<template>
  <div class="table-wrap">
    <table>
      <thead>
        <tr>
          <th>会议 ID</th>
          <th>日期/标签</th>
          <th style="color: var(--color-filah)">FILAH</th>
          <th style="color: var(--color-trout)">TROUT</th>
          <th style="color: var(--color-journalist)">全量</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="m in data"
          :key="m.id"
          :class="{ exclusive: m.exclusive_to_journalist }"
        >
          <td class="mono">{{ m.id }}</td>
          <td>{{ m.date }}</td>
          <td class="center">{{ m.in_filah ? '✓' : '—' }}</td>
          <td class="center">{{ m.in_trout ? '✓' : '—' }}</td>
          <td class="center">✓</td>
        </tr>
      </tbody>
    </table>
    <div class="legend">
      <span class="dot exclusive-dot" /> 仅全量独有（{{ exclusiveCount }} 次）
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { MeetingCoverageItem } from '../../types'

const props = defineProps<{ data: MeetingCoverageItem[] }>()
const exclusiveCount = computed(() => {
  const list = props.data || []
  return list.filter(d => d.exclusive_to_journalist).length
})
</script>

<style scoped>
.table-wrap { overflow-y: auto; max-height: 240px; }
table { width: 100%; border-collapse: collapse; font-size: 12px; }
th { position: sticky; top: 0; background: var(--color-surface); color: var(--color-text-muted); padding: 6px 8px; text-align: left; border-bottom: 1px solid var(--color-border); font-weight: 600; }
td { padding: 5px 8px; border-bottom: 1px solid rgba(51,65,85,0.4); color: var(--color-text-muted); }
.mono { font-family: monospace; color: var(--color-text); }
.center { text-align: center; }
.exclusive td { background: rgba(16,185,129,0.06); color: var(--color-text); }
.exclusive .mono { color: #10b981; font-weight: 600; }
.legend { display: flex; align-items: center; gap: 6px; font-size: 11px; color: var(--color-text-muted); margin-top: 8px; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 2px; }
.exclusive-dot { background: rgba(16,185,129,0.3); border: 1px solid #10b981; }
</style>
