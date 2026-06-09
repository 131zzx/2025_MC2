<template>
  <div class="member-view">

    <!-- 左侧：成员活动总览 + 情感矩阵 -->
    <div class="left-col">

      <!-- 覆盖率矩阵（可点击成员行） -->
      <section class="card">
        <div class="card-header">
          <span class="card-title">成员活动覆盖率矩阵</span>
          <span class="card-hint">点击成员行查看详细分析↓</span>
        </div>
        <CoverageMatrix
          :coverage="store.coverage"
          :member-activity="store.memberActivity"
          :selected-member="linking.selectedMember ?? undefined"
          @select-member="linking.selectMember"
        />
      </section>

      <!-- 情感热图 -->
      <section class="card">
        <div class="card-header">
          <span class="card-title">全员情感倾向热图</span>
          <div class="ds-tabs">
            <button
              v-for="dsInfo in datasetTabInfos" :key="dsInfo.key"
              class="ds-tab" :class="sentimentDataset === dsInfo.key && 'ds-tab--on'"
              :style="sentimentDataset === dsInfo.key ? { borderBottomColor: dsInfo.color } : {}"
              @click="sentimentDataset = dsInfo.key"
            >{{ dsInfo.label }}</button>
          </div>
        </div>
        <SentimentHeatmap
          :data="store.sentimentAgg"
          :dataset="sentimentDataset"
          :highlighted-member="linking.highlightedMember ?? undefined"
          @member-click="linking.selectMember"
          @member-hover="linking.setHoveredMember"
        />
      </section>

    </div>

    <!-- 右侧：成员详情（选中成员后展示） -->
    <div class="right-col">

      <!-- 成员选中提示 / 详情头部 -->
      <div v-if="!linking.selectedMember" class="select-prompt card">
        <div class="prompt-icon">◈</div>
        <div class="prompt-text">从左侧矩阵或热图点击选择一名委员会成员，查看其详细行为分析</div>
      </div>

      <template v-else>
        <!-- 成员头部信息 -->
        <div class="member-detail-header card">
          <div class="member-avatar">{{ memberInitials }}</div>
          <div class="member-info">
            <div class="member-name">{{ linking.selectedMember }}</div>
            <div class="member-sub">委员会成员 · 点击↗关系网络查看连接</div>
          </div>
          <button class="close-btn" @click="linking.selectMember(null)">×</button>
        </div>

        <!-- 跨数据集活动对比 -->
        <section class="card">
          <div class="card-header">
            <span class="card-title">跨数据集活动对比</span>
            <span class="card-hint">参与量 / 行程数 / 会议数</span>
          </div>
          <MemberCompareBar
            :data="store.memberActivity"
            :member="linking.selectedMember"
          />
        </section>

        <!-- 按行业情感分布 -->
        <section class="card">
          <div class="card-header">
            <span class="card-title">行业情感偏向</span>
            <span class="card-hint">正值=支持，负值=反对</span>
          </div>
          <MemberSentimentBar
            :data="store.sentimentAgg"
            :member="linking.selectedMember"
          />
        </section>

        <!-- 关系网络 -->
        <section class="card ego-card">
          <EgoNetwork
            :member="linking.selectedMember"
            :graph-data="store.fullGraph"
            @node-click="onNodeClick"
          />
        </section>
      </template>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useDataStore } from '../stores/dataStore'
import { uselinkingStore } from '../stores/linkingStore'
import { DATASET_COLORS, DATASET_LABELS } from '../types'
import type { DatasetKey } from '../types'

import CoverageMatrix   from '../components/charts/CoverageMatrix.vue'
import SentimentHeatmap from '../components/charts/SentimentHeatmap.vue'
import MemberCompareBar from '../components/charts/MemberCompareBar.vue'
import MemberSentimentBar from '../components/charts/MemberSentimentBar.vue'
import EgoNetwork       from '../components/graph/EgoNetwork.vue'

const store   = useDataStore()
const linking = uselinkingStore()

const sentimentDataset = ref<DatasetKey>('journalist')

const datasetTabInfos = [
  { key: 'filah'      as DatasetKey, label: DATASET_LABELS.filah,      color: DATASET_COLORS.filah },
  { key: 'trout'      as DatasetKey, label: DATASET_LABELS.trout,      color: DATASET_COLORS.trout },
  { key: 'journalist' as DatasetKey, label: DATASET_LABELS.journalist, color: DATASET_COLORS.journalist },
]

const memberInitials = computed(() => {
  const name = linking.selectedMember || ''
  return name.split(' ').map(p => p[0]).join('').toUpperCase().slice(0, 2)
})

function onNodeClick(id: string, type: string) {
  if (type?.includes('person') || type?.includes('entity')) {
    linking.selectMember(id)
  }
}
</script>

<style scoped>
.member-view {
  display: grid;
  grid-template-columns: 1fr 380px;
  gap: 16px;
  padding: 24px;
  align-items: start;
  min-height: 0;
}

.left-col, .right-col {
  display: flex; flex-direction: column; gap: 16px;
}

.card {
  background: #fff; border: 1px solid #e2e8f0; border-radius: 10px;
  padding: 16px; overflow: hidden;
}
.card-header {
  display: flex; align-items: center; gap: 8px; margin-bottom: 14px; flex-wrap: wrap;
}
.card-title { font-size: 13px; font-weight: 700; color: #1e293b; }
.card-hint  { font-size: 11px; color: #94a3b8; margin-left: auto; }

/* 数据集 Tab */
.ds-tabs { display: flex; gap: 0; margin-left: auto; border: 1px solid #e2e8f0; border-radius: 6px; overflow: hidden; }
.ds-tab {
  padding: 4px 10px; border: none; background: transparent; cursor: pointer;
  font-size: 11px; color: #64748b; transition: all .12s;
  border-bottom: 2px solid transparent;
}
.ds-tab:hover { background: #f8fafc; }
.ds-tab--on { background: #f0f9ff; color: #1e293b; font-weight: 600; }

/* 右侧面板 */
.select-prompt {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 12px; padding: 40px 20px; text-align: center;
  color: #94a3b8; font-size: 13px; min-height: 200px;
}
.prompt-icon { font-size: 36px; opacity: .3; }

.member-detail-header {
  display: flex; align-items: center; gap: 12px;
}
.member-avatar {
  width: 42px; height: 42px; border-radius: 50%;
  background: linear-gradient(135deg, #2563eb, #7c3aed);
  color: #fff; font-size: 14px; font-weight: 700;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.member-name { font-size: 14px; font-weight: 700; color: #1e293b; }
.member-sub  { font-size: 11px; color: #94a3b8; margin-top: 2px; }
.close-btn {
  margin-left: auto; background: none; border: none; font-size: 18px;
  color: #94a3b8; cursor: pointer; padding: 4px 8px; border-radius: 4px;
}
.close-btn:hover { background: #f1f5f9; color: #475569; }

.ego-card { padding: 0; }
</style>
