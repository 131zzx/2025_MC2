<template>
  <div class="view-container">
    <div v-if="store.loading" class="spinner-wrap">
      <div class="spinner" /><span>数据加载中...</span>
    </div>
    <div v-else-if="store.error" class="alert alert-danger">{{ store.error }}</div>

    <template v-else>
      <div class="alert alert-success">
        <strong>问题 Q4：</strong>
        个人行为下钻分析——谁受采样偏见影响最大？补全全量数据后，他们的故事如何变化？
      </div>

      <!-- ① 成员覆盖率分析 -->
      <section class="section">
        <div class="section-title">谁受采样偏见影响最大？（人员覆盖率对比）</div>
        <div class="card">
          <div class="coverage-row">
            <div class="coverage-item">
              <div class="card-title">FILAH 数据覆盖率</div>
              <CoverageBar :data="store.coverage" dataset="filah" />
            </div>
            <div class="coverage-item">
              <div class="card-title">TROUT 数据覆盖率</div>
              <CoverageBar :data="store.coverage" dataset="trout" />
            </div>
          </div>
          <div class="coverage-insight">
            <span class="ins-red">Ed Helpsford, Teddy Goldstein, Tante Titan 在 FILAH 中覆盖率为 0%</span>
            <span class="ins-blue">Tante Titan, Carol Limpet 在 TROUT 中覆盖率不足 5%</span>
          </div>
        </div>
      </section>

      <!-- ② 成员深度分析（Ego Network + 缺失证据） -->
      <section class="section">
        <div class="section-title">成员深度分析：{{ activeMember }}</div>
        
        <div class="member-toolbar">
          <div class="radio-group">
            <button
              v-for="m in members" :key="m"
              class="radio-btn" :class="activeMember === m && 'radio-btn--active'"
              @click="activeMember = m"
            >{{ m }}</button>
          </div>
        </div>

        <div class="grid-ego">
          <div class="card">
            <div class="card-title">全量 Ego Network：{{ activeMember }} 的关系圈</div>
            <EgoNetwork :member="activeMember" :graph-data="store.fullGraph" />
          </div>
          
          <div class="evidence-stack">
            <div class="card">
              <div class="card-title">{{ activeMember }} 在 TROUT 中的缺失证据</div>
              <MissingEvidenceTable :missing="store.missingTrout" :member="activeMember" />
            </div>
            <div class="card" style="margin-top: 16px;">
              <div class="card-title">会议记录完整度对比</div>
              <MeetingCoverageTable :data="store.meetingCoverage" :member="activeMember" />
            </div>
          </div>
        </div>
      </section>

      <!-- ③ 行业情感倾向（补全后） -->
      <section class="section">
        <div class="section-title">{{ activeMember }} 的真实行业倾向（基于全量数据）</div>
        <div class="card">
          <MemberSentimentBar :data="store.sentimentAgg" :member="activeMember" />
        </div>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useDataStore } from '../stores/dataStore'
import CoverageBar          from '../components/charts/CoverageBar.vue'
import EgoNetwork           from '../components/graph/EgoNetwork.vue'
import MissingEvidenceTable from '../components/shared/MissingEvidenceTable.vue'
import MeetingCoverageTable from '../components/shared/MeetingCoverageTable.vue'
import MemberSentimentBar   from '../components/charts/MemberSentimentBar.vue'
import { COMMITTEE_MEMBERS } from '../types'

const store = useDataStore()
const members = COMMITTEE_MEMBERS
const activeMember = ref(members[0])
</script>

<style scoped>
.view-container { padding: 24px; max-width: 1400px; }
.section { margin-bottom: 28px; }
.section-title {
  font-size: 12px; font-weight: 700; letter-spacing: .06em;
  text-transform: uppercase; color: #64748b; margin-bottom: 12px;
  padding-left: 10px; border-left: 3px solid #10b981;
}

.coverage-row { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.coverage-insight { margin-top: 12px; display: flex; gap: 15px; }
.ins-red { font-size: 11px; color: #e11d48; background: #fff1f2; padding: 4px 10px; border-radius: 4px; }
.ins-blue { font-size: 11px; color: #2563eb; background: #eff6ff; padding: 4px 10px; border-radius: 4px; }

.member-toolbar { margin-bottom: 16px; }

.grid-ego { display: grid; grid-template-columns: 1.2fr 0.8fr; gap: 20px; }
.evidence-stack { display: flex; flex-direction: column; }
</style>
