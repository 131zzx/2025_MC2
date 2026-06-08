<template>
  <div class="view-container">
    <!-- 加载 / 报错 -->
    <div v-if="store.loading" class="spinner-wrap">
      <div class="spinner" /><span>数据加载中...</span>
    </div>
    <div v-else-if="store.error" class="alert alert-danger">{{ store.error }}</div>

    <template v-else>
      <!-- ① 问题说明 -->
      <div class="alert alert-info">
        <strong>问题 Q1：</strong>
        利用 FILAH 与 TROUT 提供的数据，评估各方数据集的可靠性——它们能否真正支撑各自的指控？
      </div>

      <!-- ② 数据集概览卡片 -->
      <section class="section">
        <div class="section-title">数据集规模对比</div>
        <DatasetSummaryCards :node-types="store.nodeTypeCounts" />
      </section>

      <!-- ③ 偏见对比与可靠性评估 -->
      <section class="section">
        <div class="section-title">数据集特征对比（雷达图）</div>
        <div class="grid-2">
          <div class="card">
            <div class="card-title">FILAH vs TROUT 多维度对比</div>
            <RadarCompare :node-types="store.nodeTypeCounts" :topic-dist="store.topicDist" />
          </div>
          <div class="card">
            <div class="card-title">偏见指数对比（正值=偏向渔业，负值=偏向旅游）</div>
            <div class="gauge-row-compact">
              <div class="gauge-item">
                <BiasGauge :value="biasOf('filah')" label="FILAH" color="#f59e0b" />
                <div class="gauge-ds-label">FILAH</div>
              </div>
              <div class="gauge-item">
                <BiasGauge :value="biasOf('trout')" label="TROUT" color="#3b82f6" />
                <div class="gauge-ds-label">TROUT</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ④ 话题行业分布 -->
      <section class="section">
        <div class="section-title">话题行业构成（渔业 vs 旅游 vs 混合 vs 中立）</div>
        <div class="donut-row">
          <div class="card donut-card">
            <div class="card-title">FILAH</div>
            <IndustryDonut :data="store.topicDist" dataset="filah" />
          </div>
          <div class="card donut-card">
            <div class="card-title">TROUT</div>
            <IndustryDonut :data="store.topicDist" dataset="trout" />
          </div>
        </div>
      </section>

      <!-- ⑤ 节点类型构成 -->
      <section class="section">
        <div class="section-title">节点类型构成对比（揭示各数据集"记录了什么"）</div>
        <div class="card">
          <NodeTypeChart :data="store.nodeTypeCounts" />
        </div>
      </section>

      <!-- ⑥ 分析结论 -->
      <section class="section">
        <div class="section-title">Q1 分析结论</div>
        <div class="conclusion-grid">
          <div class="conclusion-card conclusion-filah">
            <div class="c-header">FILAH 数据集</div>
            <div class="c-verdict verdict-warn">可靠性：中等偏低</div>
            <ul class="c-points">
              <li>仅覆盖 6 名成员中的 <strong>3 名</strong>，Ed Helpsford、Teddy Goldstein 等人完全缺席</li>
              <li>行程记录 <strong>189 条</strong>（是 TROUT 的 10 倍），但大量集中在特定地点</li>
              <li>话题行业构成中渔业与旅游均衡，但成员覆盖不足使结论可信度下降</li>
              <li>偏见指数 <strong>+{{ biasOf('filah').toFixed(3) }}</strong>，轻微偏向渔业方</li>
            </ul>
          </div>
          <div class="conclusion-card conclusion-trout">
            <div class="c-header">TROUT 数据集</div>
            <div class="c-verdict verdict-bad">可靠性：较低</div>
            <ul class="c-points">
              <li>覆盖全部 6 名成员，但总节点数仅 <strong>164</strong>（记者数据的 22%）</li>
              <li>行程记录仅 <strong>18 条</strong>，严重缺乏实地活动证据</li>
              <li>话题行业分布偏向旅游（旅游占比最高），与其指控渔业偏袒的立场吻合——数据经过筛选</li>
              <li>偏见指数 <strong>{{ biasOf('trout').toFixed(3) }}</strong>，偏向旅游方</li>
            </ul>
          </div>
          <div class="conclusion-card conclusion-journalist">
            <div class="c-header">记者数据集（基准）</div>
            <div class="c-verdict verdict-good">可靠性：最高</div>
            <ul class="c-points">
              <li>节点总数 <strong>740</strong>，边数 <strong>2436</strong>，覆盖最完整</li>
              <li>行程记录 <strong>342 条</strong>，6 名成员全覆盖</li>
              <li>会议记录 <strong>16 场</strong>（FILAH 12 场 / TROUT 13 场），包含独家记录</li>
              <li>话题覆盖 <strong>15 个</strong>（FILAH/TROUT 各 14 个），揭示更完整的议程</li>
            </ul>
          </div>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useDataStore } from '../stores/dataStore'
import DatasetSummaryCards from '../components/charts/DatasetSummaryCards.vue'
import BiasGauge           from '../components/charts/BiasGauge.vue'
import IndustryDonut       from '../components/charts/IndustryDonut.vue'
import NodeTypeChart       from '../components/charts/NodeTypeChart.vue'
import RadarCompare        from '../components/charts/RadarCompare.vue'

const store = useDataStore()

/** 获取某数据集整体偏见指数（member === 'ALL'） */
function biasOf(ds: string): number {
  return store.biasIndex.find(d => d.dataset === ds && d.member === 'ALL')?.bias_index ?? 0
}
</script>

<style scoped>
.view-container { padding: 24px; max-width: 1400px; }

.section { margin-bottom: 28px; }
.section-title {
  font-size: 12px; font-weight: 700; letter-spacing: .06em;
  text-transform: uppercase; color: #64748b; margin-bottom: 14px;
  padding-left: 10px; border-left: 3px solid #3b82f6;
}

/* 仪表盘行 */
.gauge-row-compact { display: flex; justify-content: space-around; align-items: center; height: 100%; }
.gauge-item { display: flex; flex-direction: column; align-items: center; }
.gauge-ds-label { font-size: 13px; font-weight: 700; color: #1e293b; margin-top: -10px; }

/* 甜甜圈行 */
.donut-row { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; }
.donut-card { display: flex; flex-direction: column; align-items: center; }

/* 结论卡 */
.conclusion-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; }
.conclusion-card {
  background: #ffffff; border-radius: 12px; padding: 18px;
  border: 1px solid #e2e8f0; box-shadow: 0 1px 4px rgba(0,0,0,.06);
}
.conclusion-filah      { border-top: 3px solid #d97706; }
.conclusion-trout      { border-top: 3px solid #2563eb; }
.conclusion-journalist { border-top: 3px solid #059669; }

.c-header {
  font-size: 13px; font-weight: 700; color: #1e293b; margin-bottom: 8px;
}
.c-verdict {
  font-size: 11px; font-weight: 700; padding: 4px 8px; border-radius: 4px;
  display: inline-block; margin-bottom: 12px;
}
.verdict-good { background: #f0fdf4; color: #15803d; }
.verdict-warn { background: #fffbeb; color: #b45309; }
.verdict-bad  { background: #fef2f2; color: #b91c1c; }

.c-points { padding-left: 16px; color: #64748b; font-size: 12px; line-height: 1.9; }
.c-points strong { color: #1e293b; }
</style>
