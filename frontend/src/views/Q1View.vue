<template>
  <div class="q1-view">
    <!-- 问题说明 -->
    <a-alert
      message="Q1 · 各方指控是否被其自身数据集支持？"
      description="基于 FILAH 和 TROUT 各自提供的数据，分析数据集本身的采样偏见与成员行为偏见。不使用全量数据（journalist）。"
      type="info"
      show-icon
      style="margin-bottom: 20px; background: var(--color-surface); border-color: var(--color-border)"
    />

    <template v-if="dataStore.loaded.value">
      <!-- 第一行：数据集概览对比 -->
      <div class="grid-2" style="margin-bottom: 20px">
        <div class="card">
          <div class="card-title">数据集节点构成对比</div>
          <NodeTypeChart :data="nodeTypeData" />
        </div>
        <div class="card">
          <div class="card-title">议题产业占比对比</div>
          <TopicDistChart :data="topicDistData" />
        </div>
      </div>

      <!-- 第二行：成员参与矩阵 + 偏见指数 -->
      <div class="grid-2" style="margin-bottom: 20px">
        <div class="card">
          <div class="card-title">成员 × 数据集 活动量矩阵</div>
          <MemberActivityMatrix :data="memberActivityData" />
        </div>
        <div class="card">
          <div class="card-title">偏见指数（Bias Index）对比</div>
          <BiasIndexBar :data="biasData" show-datasets="['filah','trout']" />
        </div>
      </div>

      <!-- 第三行：Q1 结论卡片 -->
      <div class="grid-3">
        <div class="card conclusion-card filah-card">
          <div class="card-title">FILAH 自证分析</div>
          <p>FILAH 数据集仅覆盖 <strong>3/6</strong> 名委员会成员（Seal、Simone Kat、Carol Limpet），<strong>Ed Helpsford、Teddy Goldstein、Tante Titan 的记录完全缺失</strong>。</p>
          <p>在有记录的 3 名成员中，旅游议题的参与记录占多数，表面上支持 FILAH 的指控，但由于人员覆盖严重不足，<strong>无法代表委员会整体倾向</strong>。</p>
          <a-tag color="#f59e0b">采样偏见：人员覆盖仅 50%</a-tag>
        </div>
        <div class="card conclusion-card trout-card">
          <div class="card-title">TROUT 自证分析</div>
          <p>TROUT 数据集覆盖全部 <strong>6/6</strong> 名成员，但总节点数仅 164，<strong>trip 记录只有 18 条</strong>（全量的 5.3%）。</p>
          <p>成员行为分析可在 TROUT 中进行，但地理实地活动的证据极为薄弱，导致叙事集中在会议室而非实际调研行动。</p>
          <a-tag color="#3b82f6">采样偏见：活动记录严重不足</a-tag>
        </div>
        <div class="card conclusion-card">
          <div class="card-title">成员行为偏见？</div>
          <p><strong>FILAH 中</strong>：仅 3 人有意义，可观察到这 3 人在旅游议题参与略多，但样本过小。</p>
          <p><strong>TROUT 中</strong>：6 人均可分析，渔业议题的 participant 记录略多于旅游，情感倾向需进一步验证。</p>
          <a-tag color="#6b7280">结论：有线索，无定论</a-tag>
        </div>
      </div>
    </template>

    <a-spin v-else-if="dataStore.loading.value" tip="加载数据中..." style="display: block; margin: 80px auto" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useDataStore } from '../stores/dataStore'
import NodeTypeChart from '../components/charts/NodeTypeChart.vue'
import TopicDistChart from '../components/charts/TopicDistChart.vue'
import MemberActivityMatrix from '../components/charts/MemberActivityMatrix.vue'
import BiasIndexBar from '../components/charts/BiasIndexBar.vue'

const dataStore = useDataStore()

const nodeTypeData = computed(() =>
  dataStore.nodeTypeCounts.value.filter(d => d.dataset !== 'journalist')
)

const topicDistData = computed(() =>
  dataStore.topicDist.value.filter(d => d.dataset !== 'journalist')
)

const memberActivityData = computed(() =>
  dataStore.memberActivity.value.filter(d => d.dataset !== 'journalist')
)

const biasData = computed(() =>
  dataStore.biasIndex.value.filter(d => d.dataset !== 'journalist')
)
</script>

<style scoped>
.q1-view { max-width: 1400px; }
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; }

.conclusion-card p {
  font-size: 13px;
  color: var(--color-text-muted);
  line-height: 1.7;
  margin-bottom: 10px;
}
.conclusion-card strong { color: var(--color-text); }
.filah-card { border-color: rgba(245,158,11,0.4); }
.trout-card { border-color: rgba(59,130,246,0.4); }
</style>
