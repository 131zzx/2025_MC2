/**
 * uiStore.ts
 * 全局 UI 状态：当前选中数据集、选中人物等交互状态。
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { DatasetKey, MemberName } from '../types'

export const useUiStore = defineStore('ui', () => {
  // Q1/Q3 数据集切换（可多选对比）
  const selectedDatasets = ref<DatasetKey[]>(['filah', 'trout', 'journalist'])

  // Q4 选中人物
  const selectedMember = ref<MemberName>('Tante Titan')

  // 高亮 / 筛选
  const highlightIndustry = ref<string | null>(null)

  function toggleDataset(ds: DatasetKey) {
    const idx = selectedDatasets.value.indexOf(ds)
    if (idx === -1) selectedDatasets.value.push(ds)
    else if (selectedDatasets.value.length > 1) selectedDatasets.value.splice(idx, 1)
  }

  function setMember(m: MemberName) {
    selectedMember.value = m
  }

  return {
    selectedDatasets,
    selectedMember,
    highlightIndustry,
    toggleDataset,
    setMember,
  }
})
