<template>
  <div class="dataset-selector">
    <span class="label">数据集：</span>
    <a-button-group>
      <a-button
        v-for="ds in datasets"
        :key="ds.key"
        :style="getButtonStyle(ds.key)"
        :type="isActive(ds.key) ? 'primary' : 'default'"
        size="small"
        @click="toggle(ds.key)"
      >
        {{ ds.label }}
      </a-button>
    </a-button-group>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { DatasetKey } from '../../types'
import { DATASET_LABELS, DATASET_COLORS } from '../../types'

const props = defineProps<{
  modelValue: DatasetKey[]
  multiple?: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [DatasetKey[]]
}>()

const datasets = (Object.keys(DATASET_LABELS) as DatasetKey[]).map(k => ({
  key: k,
  label: DATASET_LABELS[k],
  color: DATASET_COLORS[k],
}))

function isActive(ds: DatasetKey) {
  return props.modelValue.includes(ds)
}

function getButtonStyle(ds: DatasetKey) {
  if (!isActive(ds)) return {}
  return { background: DATASET_COLORS[ds], borderColor: DATASET_COLORS[ds] }
}

function toggle(ds: DatasetKey) {
  if (!props.multiple) {
    emit('update:modelValue', [ds])
    return
  }
  const current = [...props.modelValue]
  const idx = current.indexOf(ds)
  if (idx === -1) {
    emit('update:modelValue', [...current, ds])
  } else if (current.length > 1) {
    current.splice(idx, 1)
    emit('update:modelValue', current)
  }
}
</script>

<style scoped>
.dataset-selector {
  display: flex;
  align-items: center;
  gap: 10px;
}
.label {
  font-size: 12px;
  color: var(--color-text-muted);
  white-space: nowrap;
}
</style>
