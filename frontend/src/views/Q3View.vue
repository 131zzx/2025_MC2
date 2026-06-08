<template>
  <div class="q3-view">
    <a-alert
      message="Q3 · 不完整数据 vs 全量——结论对比与 TROUT 指控变化"
      description="对比 FILAH/TROUT 各自得出的结论与全量数据中实际行为的差异，并判断 TROUT 的指控在全量背景下是被加强、削弱还是不变。"
      type="warning"
      show-icon
      style="margin-bottom: 20px; background: var(--color-surface); border-color: var(--color-border)"
    />

    <template v-if="dataStore.loaded.value">
      <!-- 三数据集 Bias Index 对比 -->
      <div class="grid-2" style="margin-bottom: 20px">
        <div class="card">
          <div class="card-title">三数据集 整体 Bias Index 对比</div>
          <BiasIndexBar :data="allOverallBias" show-all />
        </div>
        <div class="card">
          <div class="card-title">议题产业分布 三数据集对比</div>
          <TopicDistChart :data="dataStore.topicDist.value" />
        </div>
      </div>

      <!-- 缺失节点分析 -->
      <div class="grid-2" style="margin-bottom: 20px">
        <div class="card">
          <div class="card-title">missing_from_FILAH · 缺失节点产业构成</div>
          <MissingNodeChart :data="dataStore.missingFilah.value" dataset="filah" />
        </div>
        <div class="card">
          <div class="card-title">missing_from_TROUT · 缺失节点产业构成</div>
          <MissingNodeChart :data="dataStore.missingTrout.value" dataset="trout" />
        </div>
      </div>

      <!-- 会议覆盖 + TROUT 指控判定 -->
      <div class="grid-2">
        <div class="card">
          <div class="card-title">会议覆盖情况（全量 16 次）</div>
          <MeetingCoverageTable :data="dataStore.meetingCoverage.value" />
        </div>
        <div class="card verdict-card">
          <div class="card-title">Q3-③ TROUT 指控判定</div>
          <div class="verdict">
            <div class="verdict-badge">削弱（Weakened）</div>
            <div class="verdict-reasons">
              <div class="reason-item">
                <span class="reason-num">①</span>
                <span>全量新增 <strong>324 条 trip 记录</strong>，大量旅游地点的实地调研被 TROUT 数据遗漏，补全后旅游调研活动显著增加</span>
              </div>
              <div class="reason-item">
                <span class="reason-num">②</span>
                <span>全量独有 <strong>Meeting_13、14、15</strong>（3 次会议），其中含旅游议题讨论，TROUT 数据未记录这些会议</span>
              </div>
              <div class="reason-item">
                <span class="reason-num">③</span>
                <span>全量 bias_index 相比 TROUT 数据集的 bias_index 更偏旅游方向，说明委员会对旅游的关注被 TROUT 系统性低估</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <a-spin v-else-if="dataStore.loading.value" tip="加载数据中..." style="display: block; margin: 80px auto" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useDataStore } from '../stores/dataStore'
import BiasIndexBar from '../components/charts/BiasIndexBar.vue'
import TopicDistChart from '../components/charts/TopicDistChart.vue'
import MissingNodeChart from '../components/charts/MissingNodeChart.vue'
import MeetingCoverageTable from '../components/shared/MeetingCoverageTable.vue'

const dataStore = useDataStore()

const allOverallBias = computed(() =>
  dataStore.overallBias.value
)
</script>

<style scoped>
.q3-view { max-width: 1400px; }
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }

.verdict-card { border-color: rgba(59,130,246,0.4); }
.verdict-badge {
  display: inline-block;
  padding: 6px 16px;
  background: rgba(59,130,246,0.2);
  color: #3b82f6;
  border-radius: 20px;
  font-size: 18px;
  font-weight: 700;
  margin: 12px 0 16px;
}
.verdict-reasons { display: flex; flex-direction: column; gap: 12px; }
.reason-item {
  display: flex;
  gap: 10px;
  font-size: 13px;
  color: var(--color-text-muted);
  line-height: 1.6;
}
.reason-item strong { color: var(--color-text); }
.reason-num {
  flex-shrink: 0;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: rgba(59,130,246,0.2);
  color: #3b82f6;
  font-size: 12px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
