<template>
  <div class="view-container">
    <div v-if="store.loading" class="spinner-wrap">
      <div class="spinner" /><span>数据加载中...</span>
    </div>
    <div v-else-if="store.error" class="alert alert-danger">{{ store.error }}</div>

    <template v-else>
      <!-- 问题说明 -->
      <div class="alert alert-warning">
        <strong>问题 Q2：</strong>
        利用三个数据集评估委员会成员个体的行为偏见——哪些成员存在偏袒渔业或旅游业的证据？
      </div>

      <!-- ① 成员 x 数据集覆盖矩阵 -->
      <section class="section">
        <div class="section-title">成员数据集覆盖矩阵（谁被谁记录了？）</div>
        <div class="card">
          <CoverageMatrix
            :coverage="store.coverage"
            :member-activity="store.memberActivity"
          />
        </div>
        <div class="matrix-insight">
          <span class="ins ins--warn">FILAH 完全缺失 Ed Helpsford、Teddy Goldstein、Tante Titan 三人记录</span>
          <span class="ins ins--info">TROUT 虽覆盖 6 人，但 Tante Titan 仅 4 条、Carol Limpet 仅 3 条</span>
        </div>
      </section>

      <!-- ② 单人活动量对比（交互选择） -->
      <section class="section">
        <div class="section-title">成员跨数据集活动量对比</div>
        <div class="member-selector">
          <button
            v-for="m in members" :key="m"
            class="radio-btn" :class="activeMember === m && 'radio-btn--active'"
            @click="activeMember = m"
          >{{ m }}</button>
        </div>
        <div class="grid-2" style="margin-top:14px">
          <div class="card">
            <div class="card-title">{{ activeMember }} — 三数据集活动量对比</div>
            <MemberCompareBar :data="store.memberActivity" :member="activeMember" />
          </div>
          <div class="card">
            <div class="card-title">{{ activeMember }} — 行业情感偏向（记者数据集）</div>
            <MemberSentimentBar :data="store.sentimentAgg" :member="activeMember" />
          </div>
        </div>
      </section>

      <!-- ③ 情感热图 -->
      <section class="section">
        <div class="section-title">全员情感倾向热图（成员 × 行业，深色=正向）</div>
        <div class="ds-tabs">
          <button
            v-for="ds in allDatasets" :key="ds.key"
            class="btn" :class="[`btn-${ds.key}`, activeDs === ds.key && 'btn--active']"
            @click="activeDs = ds.key"
          >{{ ds.label }}</button>
        </div>
        <div class="card" style="margin-top:12px">
          <SentimentHeatmap :data="store.sentimentAgg" :dataset="activeDs" />
        </div>
      </section>

      <!-- ④ 覆盖率条形图 -->
      <section class="section">
        <div class="section-title">各成员被 FILAH / TROUT 记录的覆盖率（相对记者数据集）</div>
        <div class="grid-2">
          <div class="card">
            <div class="card-title">FILAH 覆盖率</div>
            <CoverageBar :data="store.coverage" dataset="filah" />
          </div>
          <div class="card">
            <div class="card-title">TROUT 覆盖率</div>
            <CoverageBar :data="store.coverage" dataset="trout" />
          </div>
        </div>
      </section>

      <!-- ⑤ 结论 -->
      <section class="section">
        <div class="section-title">Q2 分析结论</div>
        <div class="conclusion-grid">
          <div class="conclusion-card conc-green">
            <div class="c-header">Seal（主席）</div>
            <div class="c-verdict verd-neutral">行为相对中立</div>
            <p class="c-text">在三个数据集中均有记录，情感方差小，对渔业和旅游话题的参与较为均衡，无明显个人偏见证据。</p>
          </div>
          <div class="conclusion-card conc-yellow">
            <div class="c-header">Simone Kat</div>
            <div class="c-verdict verd-warn">疑似倾向旅游</div>
            <p class="c-text">FILAH 数据中旅游情感均值高达 0.91，渔业仅 0.16，差距悬殊。在 FILAH 中活动量最大（112 条），可能受 FILAH 选择性曝光。</p>
          </div>
          <div class="conclusion-card conc-yellow">
            <div class="c-header">Carol Limpet</div>
            <div class="c-verdict verd-warn">数据偏少，难评估</div>
            <p class="c-text">TROUT 中仅 3 条记录（覆盖率 3.3%），不足以作出判断。FILAH 数据中旅游情感正向（0.68），但样本量偏小。</p>
          </div>
          <div class="conclusion-card conc-red">
            <div class="c-header">Ed Helpsford / Teddy Goldstein</div>
            <div class="c-verdict verd-bad">FILAH 完全缺失</div>
            <p class="c-text">FILAH 数据集中对这两人的记录为零，无法通过 FILAH 的叙事评估其行为。TROUT 数据中有部分记录，但活动量亦偏低。</p>
          </div>
          <div class="conclusion-card conc-red">
            <div class="c-header">Tante Titan</div>
            <div class="c-verdict verd-bad">两方数据均严重缺失</div>
            <p class="c-text">FILAH 零记录，TROUT 仅 4 条（覆盖率 3.9%）。记者数据集中有 103 条活动记录，说明该成员实际相当活跃，但被两方数据集刻意忽视。</p>
          </div>
          <div class="conclusion-card conc-green">
            <div class="c-header">总体结论</div>
            <div class="c-verdict verd-good">个人偏见证据不充分</div>
            <p class="c-text">由于 FILAH/TROUT 数据集均存在严重的成员覆盖缺口，无法依赖任一方数据对个别成员作出可靠的偏见判定。记者全量数据是唯一可信基准。</p>
          </div>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useDataStore } from '../stores/dataStore'
import CoverageMatrix    from '../components/charts/CoverageMatrix.vue'
import MemberCompareBar  from '../components/charts/MemberCompareBar.vue'
import MemberSentimentBar from '../components/charts/MemberSentimentBar.vue'
import SentimentHeatmap  from '../components/charts/SentimentHeatmap.vue'
import CoverageBar       from '../components/charts/CoverageBar.vue'
import { COMMITTEE_MEMBERS } from '../types'

const store = useDataStore()
const members = COMMITTEE_MEMBERS
const activeMember = ref(members[0])
const activeDs = ref<'filah' | 'trout' | 'journalist'>('journalist')

const allDatasets = [
  { key: 'filah',      label: 'FILAH'    },
  { key: 'trout',      label: 'TROUT'    },
  { key: 'journalist', label: '记者数据' },
] as const
</script>

<style scoped>
.view-container { padding: 24px; max-width: 1400px; }

.section { margin-bottom: 28px; }
.section-title {
  font-size: 12px; font-weight: 700; letter-spacing: .06em;
  text-transform: uppercase; color: #64748b; margin-bottom: 12px;
  padding-left: 10px; border-left: 3px solid #f59e0b;
}

.matrix-insight { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 10px; }
.ins {
  font-size: 11px; padding: 5px 10px; border-radius: 5px;
}
.ins--warn { background: rgba(245,158,11,.1); color: #fbbf24; }
.ins--info { background: rgba(59,130,246,.1);  color: #60a5fa; }

.member-selector { display: flex; flex-wrap: wrap; gap: 6px; }

.ds-tabs { display: flex; gap: 6px; }

/* 结论卡 */
.conclusion-grid {
  display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 14px;
}
.conclusion-card {
  background: #ffffff; border: 1px solid #e2e8f0;
  border-radius: 10px; padding: 16px;
  box-shadow: 0 1px 4px rgba(0,0,0,.06);
}
.conc-green  { border-top: 3px solid #059669; }
.conc-yellow { border-top: 3px solid #d97706; }
.conc-red    { border-top: 3px solid #dc2626; }

.c-header { font-size: 13px; font-weight: 700; color: #1e293b; margin-bottom: 6px; }
.c-verdict {
  display: inline-block; font-size: 11px; font-weight: 700;
  padding: 3px 8px; border-radius: 4px; margin-bottom: 8px;
}
.verd-good    { background: #f0fdf4; color: #15803d; }
.verd-neutral { background: #f1f5f9; color: #475569; }
.verd-warn    { background: #fffbeb; color: #b45309; }
.verd-bad     { background: #fef2f2; color: #b91c1c; }

.c-text { font-size: 12px; color: #64748b; line-height: 1.7; }
</style>
