<template>
  <div class="view-container">
    <div v-if="store.loading" class="spinner-wrap">
      <div class="spinner" /><span>数据加载中…</span>
    </div>
    <div v-else-if="store.error" class="alert alert-danger">{{ store.error }}</div>

    <template v-else>
      <!-- TROUT 结论裁定 -->
      <div class="verdict-card">
        <div class="verdict-label">TROUT 指控裁定</div>
        <div class="verdict-title">TROUT 的指控：<span class="verdict-result">部分成立</span></div>
        <p class="verdict-text">
          COOTEFOO 整体上偏向渔业，有 3 名成员（Nadia Conejo、Jonathon Alverez-Ponto、Gao Feng）
          在 FILAH 数据中的情感均值明显为正向渔业，同时在旅游相关话题上发言极少。
          但 TROUT 数据集本身也存在选择性偏差，其证据不完整性削弱了指控力度。
        </p>
      </div>

      <div class="grid-2">
        <div class="card">
          <div class="card-title">行程地区分布</div>
          <TripZoneChart :data="store.tripZoneDist" />
        </div>
        <div class="card">
          <div class="card-title">行程地图</div>
          <TripMap :data="store.tripRecords" :dataset="activeDs" />
        </div>
      </div>

      <!-- 人物选择 -->
      <div style="margin: 20px 0 8px">
        <span style="font-size:12px;color:#94a3b8;margin-right:8px">选择成员追踪行程：</span>
        <div class="radio-group">
          <button
            v-for="m in members" :key="m"
            class="radio-btn" :class="activeMember === m && 'radio-btn--active'"
            @click="activeMember = m"
          >{{ m }}</button>
        </div>
      </div>

      <div class="card" style="margin-top:16px">
        <div class="card-title">{{ activeMember }} — 跨数据集行程对比</div>
        <PersonTripMap :member="activeMember" :trips="store.tripRecords" />
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useDataStore } from '../stores/dataStore'
import TripZoneChart from '../components/charts/TripZoneChart.vue'
import TripMap       from '../components/map/TripMap.vue'
import PersonTripMap from '../components/map/PersonTripMap.vue'
import { COMMITTEE_MEMBERS } from '../types'

const store = useDataStore()
const activeDs = ref<'filah' | 'trout'>('filah')
const members = COMMITTEE_MEMBERS
const activeMember = ref(members[0])
</script>

<style scoped>
.view-container { padding: 24px; max-width: 1400px; }
.verdict-card {
  background: rgba(59,130,246,.08); border: 1px solid #3b82f6;
  border-radius: 12px; padding: 20px 24px; margin-bottom: 24px;
}
.verdict-label { font-size: 11px; font-weight: 600; letter-spacing: .08em; text-transform: uppercase; color: #60a5fa; margin-bottom: 6px; }
.verdict-title { font-size: 16px; font-weight: 700; color: #e2e8f0; margin-bottom: 10px; }
.verdict-result { color: #f59e0b; }
.verdict-text { color: #94a3b8; font-size: 13px; line-height: 1.7; }
</style>
