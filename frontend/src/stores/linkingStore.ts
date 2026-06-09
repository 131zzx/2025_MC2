/**
 * linkingStore.ts
 * 全局图表联动状态中心
 *
 * 设计参照 BAIT 项目的 Filter + Highlight 双通道模式：
 *   activeFilters  → 持久过滤（点击选中），影响所有图表的数据范围
 *   hoverHighlight → 临时高亮（鼠标悬停），不改变数据范围，只改变视觉强调
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { DatasetKey } from '../types'

// ── 类型定义 ─────────────────────────────────────────────────
export type FilterType = 'member' | 'dataset' | 'industry' | 'zone'

export interface ActiveFilter {
  type: FilterType
  value: string
}

export const uselinkingStore = defineStore('linking', () => {
  // ── 持久选择状态 ─────────────────────────────────────────
  /** 当前选中的委员会成员（null = 全部） */
  const selectedMember = ref<string | null>(null)

  /** 当前激活的数据集（空数组 = 全部） */
  const selectedDatasets = ref<DatasetKey[]>(['filah', 'trout', 'journalist'])

  /** 当前选中的行业（null = 全部） */
  const selectedIndustry = ref<string | null>(null)

  // ── 悬停高亮状态 ─────────────────────────────────────────
  /** 当前悬停的成员名 */
  const hoveredMember = ref<string | null>(null)

  /** 当前悬停的话题/节点 ID */
  const hoveredTopic = ref<string | null>(null)

  /** 当前悬停的行程 ID */
  const hoveredTrip = ref<string | null>(null)

  // ── 操作方法 ─────────────────────────────────────────────
  function selectMember(name: string | null) {
    selectedMember.value = selectedMember.value === name ? null : name
  }

  function toggleDataset(ds: DatasetKey) {
    const idx = selectedDatasets.value.indexOf(ds)
    if (idx >= 0) {
      if (selectedDatasets.value.length > 1) {
        selectedDatasets.value.splice(idx, 1)
      }
    } else {
      selectedDatasets.value.push(ds)
    }
  }

  function setDatasets(datasets: DatasetKey[]) {
    selectedDatasets.value = datasets
  }

  function selectIndustry(ind: string | null) {
    selectedIndustry.value = selectedIndustry.value === ind ? null : ind
  }

  function setHoveredMember(name: string | null) {
    hoveredMember.value = name
  }

  function setHoveredTopic(id: string | null) {
    hoveredTopic.value = id
  }

  function setHoveredTrip(id: string | null) {
    hoveredTrip.value = id
  }

  function clearAll() {
    selectedMember.value = null
    selectedDatasets.value = ['filah', 'trout', 'journalist']
    selectedIndustry.value = null
    hoveredMember.value = null
    hoveredTopic.value = null
    hoveredTrip.value = null
  }

  // ── 计算属性 ──────────────────────────────────────────────
  /** 当前高亮的成员（选中或悬停，选中优先） */
  const highlightedMember = computed(() =>
    hoveredMember.value ?? selectedMember.value
  )

  /** 某成员是否被高亮 */
  function isMemberHighlighted(name: string): boolean {
    if (hoveredMember.value) return hoveredMember.value === name
    if (selectedMember.value) return selectedMember.value === name
    return false
  }

  /** 某成员是否被淡化（有高亮目标且不是自己） */
  function isMemberDimmed(name: string): boolean {
    const target = hoveredMember.value ?? selectedMember.value
    return target !== null && target !== name
  }

  /** 某数据集是否激活 */
  function isDatasetActive(ds: DatasetKey): boolean {
    return selectedDatasets.value.includes(ds)
  }

  return {
    // 状态
    selectedMember, selectedDatasets, selectedIndustry,
    hoveredMember, hoveredTopic, hoveredTrip,
    // 计算
    highlightedMember,
    // 方法
    selectMember, toggleDataset, setDatasets, selectIndustry,
    setHoveredMember, setHoveredTopic, setHoveredTrip,
    clearAll,
    isMemberHighlighted, isMemberDimmed, isDatasetActive,
  }
})
