<template>
  <div class="q4-view">
    <a-alert
      message="Q4 · 人物级对比分析"
      description="选择一名委员会成员，对比该成员在 FILAH、TROUT、journalist 三个数据集中的行为差异，聚焦各数据集讲述的故事对比。"
      type="error"
      show-icon
      style="margin-bottom: 20px; background: var(--color-surface); border-color: var(--color-border)"
    />

    <!-- 人物选择器 -->
    <div class="card" style="margin-bottom: 20px; display: flex; align-items: center; gap: 20px">
      <span class="card-title" style="margin-bottom: 0">选择成员：</span>
      <a-radio-group v-model:value="uiStore.selectedMember" button-style="solid" size="small">
        <a-radio-button
          v-for="m in COMMITTEE_MEMBERS"
          :key="m"
          :value="m"
        >{{ m }}</a-radio-button>
      </a-radio-group>
    </div>

    <template v-if="dataStore.loaded.value">
      <!-- 三数据集活动对比卡片 -->
      <div class="grid-3" style="margin-bottom: 20px">
        <div
          v-for="ds in (['filah', 'trout', 'journalist'] as DatasetKey[])"
          :key="ds"
          class="card dataset-card"
          :style="{ borderColor: DATASET_COLORS[ds] + '66' }"
        >
          <div class="card-title" :style="{ color: DATASET_COLORS[ds] }">
            {{ DATASET_LABELS[ds] }}
          </div>
          <div class="activity-stats">
            <div v-if="getActivity(ds)" class="stat-row">
              <span>参与讨论/计划</span>
              <strong>{{ getActivity(ds)?.participant_cnt ?? 0 }}</strong>
            </div>
            <div class="stat-row">
              <span>行程记录</span>
              <strong>{{ getActivity(ds)?.trip_cnt ?? 0 }}</strong>
            </div>
            <div class="stat-row">
              <span>参与会议</span>
              <strong>{{ getActivity(ds)?.meeting_cnt ?? 0 }}</strong>
            </div>
            <div class="stat-row">
              <span>涉及议题</span>
              <strong>{{ getActivity(ds)?.topic_cnt ?? 0 }}</strong>
            </div>
            <div v-if="ds !== 'journalist'" class="coverage-row">
              <span>覆盖率</span>
              <a-progress
                :percent="Math.round((getCoverage(ds as 'filah' | 'trout')?.coverage ?? 0) * 100)"
                size="small"
                :stroke-color="DATASET_COLORS[ds]"
                :trail-color="'var(--color-border)'"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- 行程地图（三数据集联动） -->
      <div class="grid-2" style="margin-bottom: 20px">
        <div class="card">
          <div class="card-title">行程轨迹对比（{{ uiStore.selectedMember }}）</div>
          <PersonTripMap
            :member="uiStore.selectedMember"
            :trips="dataStore.tripRecords.value"
            :places="dataStore.placeNodes.value"
          />
        </div>
        <div class="card">
          <div class="card-title">Q4.2 · 关键缺失证据（来自 TROUT）</div>
          <MissingEvidenceTable
            :missing="dataStore.missingTrout.value"
            :member="uiStore.selectedMember"
          />
        </div>
      </div>

      <!-- FILAH 覆盖率排行 + FILAH 偏见总结 -->
      <div class="grid-2">
        <div class="card">
          <div class="card-title">Q4.3 · FILAH 对各成员的覆盖率排行</div>
          <CoverageBar :data="dataStore.coverage.value" dataset="filah" />
        </div>
        <div class="card">
          <div class="card-title">Q4.4 · FILAH 偏见总结（相对全量）</div>
          <FilahBiasSummary
            :node-types="dataStore.nodeTypeCounts.value"
            :topic-dist="dataStore.topicDist.value"
            :coverage="dataStore.coverage.value"
          />
        </div>
      </div>
    </template>

    <a-spin v-else-if="dataStore.loading.value" tip="加载数据中..." style="display: block; margin: 80px auto" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useDataStore } from '../stores/dataStore'
import { useUiStore } from '../stores/uiStore'
import { COMMITTEE_MEMBERS, DATASET_LABELS, DATASET_COLORS } from '../types'
import type { DatasetKey } from '../types'
import CoverageBar from '../components/charts/CoverageBar.vue'
import PersonTripMap from '../components/map/PersonTripMap.vue'
import MissingEvidenceTable from '../components/shared/MissingEvidenceTable.vue'
import FilahBiasSummary from '../components/shared/FilahBiasSummary.vue'

const dataStore = useDataStore()
const uiStore   = useUiStore()

const member = computed(() => uiStore.selectedMember)

function getActivity(ds: DatasetKey) {
  return dataStore.memberActivity.value.find(
    d => d.member === member.value && d.dataset === ds
  )
}

function getCoverage(ds: 'filah' | 'trout') {
  return dataStore.coverage.value.find(
    d => d.member === member.value && d.dataset === ds
  )
}
</script>

<style scoped>
.q4-view { max-width: 1400px; }
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; }

.activity-stats { display: flex; flex-direction: column; gap: 10px; margin-top: 8px; }
.stat-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  color: var(--color-text-muted);
}
.stat-row strong { color: var(--color-text); font-size: 15px; }
.coverage-row {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 12px;
  color: var(--color-text-muted);
}
</style>
