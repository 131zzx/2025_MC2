<template>
  <div class="view-container">
    <div v-if="store.loading" class="spinner-wrap">
      <div class="spinner" /><span>数据加载中…</span>
    </div>
    <div v-else-if="store.error" class="alert alert-danger">{{ store.error }}</div>

    <template v-else>
      <div class="alert alert-success">
        <strong>Q4 核心发现：</strong>
        两个数据集均存在明显的"缺失节点"现象——FILAH 缺失大量旅游相关活动记录，TROUT 则遗漏了渔业侧的关键会议证据。记者数据集提供了最接近完整事实的基准。
      </div>

      <div class="grid-2">
        <div class="card">
          <div class="card-title">缺失节点行业分布（FILAH）</div>
          <MissingNodeChart :data="store.missingFilah" dataset="filah" />
        </div>
        <div class="card">
          <div class="card-title">缺失节点行业分布（TROUT）</div>
          <MissingNodeChart :data="store.missingTrout" dataset="trout" />
        </div>
      </div>

      <!-- 成员选择 -->
      <div style="margin: 24px 0 8px">
        <span style="font-size:12px;color:#94a3b8;margin-right:8px">选择成员查看 TROUT 中的缺失证据：</span>
        <div class="radio-group">
          <button
            v-for="m in members" :key="m"
            class="radio-btn" :class="activeMember === m && 'radio-btn--active'"
            @click="activeMember = m"
          >{{ m }}</button>
        </div>
      </div>

      <div class="grid-2">
        <div class="card">
          <div class="card-title">{{ activeMember }} — TROUT 中的缺失证据</div>
          <MissingEvidenceTable :missing="store.missingTrout" :member="activeMember" />
        </div>
        <div class="card">
          <div class="card-title">会议覆盖对比</div>
          <MeetingCoverageTable :data="store.meetingCoverage" :member="activeMember" />
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useDataStore } from '../stores/dataStore'
import MissingNodeChart      from '../components/charts/MissingNodeChart.vue'
import MissingEvidenceTable  from '../components/shared/MissingEvidenceTable.vue'
import MeetingCoverageTable  from '../components/shared/MeetingCoverageTable.vue'
import { COMMITTEE_MEMBERS } from '../types'

const store = useDataStore()
const members = COMMITTEE_MEMBERS
const activeMember = ref(members[0])
</script>

<style scoped>
.view-container { padding: 24px; max-width: 1400px; }
</style>
