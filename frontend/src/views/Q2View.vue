<template>
  <div class="view-container">
    <div v-if="store.loading" class="spinner-wrap">
      <div class="spinner" /><span>数据加载中…</span>
    </div>
    <div v-else-if="store.error" class="alert alert-danger">{{ store.error }}</div>

    <template v-else>
      <div class="alert alert-warning">
        <strong>Q2 核心发现：</strong>
        部分委员会成员在 FILAH/TROUT 数据集中的活动记录与记者数据集存在明显差异，情感倾向矩阵揭示了不同成员对渔业 vs 旅游业的偏好模式。
      </div>

      <!-- 活动矩阵/情感热图数据集选择 -->
      <div class="btn-group" style="margin-bottom:20px">
        <button
          v-for="ds in allDatasets" :key="ds.key"
          class="btn" :class="[`btn-${ds.key}`, activeDs === ds.key && 'btn--active']"
          @click="activeDs = ds.key"
        >{{ ds.label }}</button>
      </div>

      <div class="grid-2">
        <div class="card">
          <div class="card-title">成员活动热力矩阵</div>
          <MemberActivityMatrix :data="store.memberActivity" :dataset="activeDs" />
        </div>
        <div class="card">
          <div class="card-title">情感倾向热图（成员 × 行业）</div>
          <SentimentHeatmap :data="store.sentimentAgg" :dataset="activeDs" />
        </div>
      </div>

      <!-- 覆盖率（仅 filah / trout）-->
      <div style="margin: 24px 0 12px">
        <div class="card-title" style="margin-bottom:10px">数据集覆盖率对比</div>
        <div class="btn-group" style="margin-bottom:12px">
          <button
            v-for="ds in biDatasets" :key="ds.key"
            class="btn" :class="[`btn-${ds.key}`, coverDs === ds.key && 'btn--active']"
            @click="coverDs = ds.key"
          >{{ ds.label }}</button>
        </div>
        <div class="card">
          <CoverageBar :data="store.coverage" :dataset="coverDs" />
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useDataStore } from '../stores/dataStore'
import MemberActivityMatrix from '../components/charts/MemberActivityMatrix.vue'
import SentimentHeatmap     from '../components/charts/SentimentHeatmap.vue'
import CoverageBar          from '../components/charts/CoverageBar.vue'

const store = useDataStore()
const activeDs  = ref<'filah' | 'trout' | 'journalist'>('filah')
const coverDs   = ref<'filah' | 'trout'>('filah')

const allDatasets = [
  { key: 'filah',      label: 'FILAH'    },
  { key: 'trout',      label: 'TROUT'    },
  { key: 'journalist', label: '记者数据' },
] as const

const biDatasets = [
  { key: 'filah', label: 'FILAH' },
  { key: 'trout', label: 'TROUT' },
] as const
</script>

<style scoped>
.view-container { padding: 24px; max-width: 1400px; }
</style>
