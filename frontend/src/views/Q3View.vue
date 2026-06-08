<template>
  <div class="view-container">
    <div v-if="store.loading" class="spinner-wrap">
      <div class="spinner" /><span>数据加载中...</span>
    </div>
    <div v-else-if="store.error" class="alert alert-danger">{{ store.error }}</div>

    <template v-else>
      <div class="alert alert-info">
        <strong>问题 Q3：</strong>
        不完整数据 vs 全量——结论如何变化？补全缺失证据后，TROUT 的指控是加强还是削弱了？
      </div>

      <!-- ① Bias Index 瀑布流对比 -->
      <section class="section">
        <div class="section-title">偏见指数修正（瀑布图：从子集到全量）</div>
        <div class="grid-2">
          <div class="card">
            <div class="card-title">FILAH → 全量 (Journalist)</div>
            <WaterfallChart
              :initial-value="biasOf('filah')"
              :final-value="biasOf('journalist')"
              label="FILAH Bias Correction"
            />
            <div class="chart-desc">FILAH 补全后，偏见指数向 {{ biasOf('journalist') > biasOf('filah') ? '渔业' : '旅游' }} 方向修正。</div>
          </div>
          <div class="card">
            <div class="card-title">TROUT → 全量 (Journalist)</div>
            <WaterfallChart
              :initial-value="biasOf('trout')"
              :final-value="biasOf('journalist')"
              label="TROUT Bias Correction"
            />
            <div class="chart-desc">TROUT 补全后，偏见指数向 {{ biasOf('journalist') > biasOf('trout') ? '渔业' : '旅游' }} 方向修正。</div>
          </div>
        </div>
      </section>

      <!-- ② 缺失节点行业分布 -->
      <section class="section">
        <div class="section-title">各数据集缺失证据的产业构成</div>
        <div class="grid-2">
          <div class="card">
            <div class="card-title">FILAH 缺失节点行业分布</div>
            <MissingNodeChart :data="store.missingFilah" dataset="filah" />
          </div>
          <div class="card">
            <div class="card-title">TROUT 缺失节点行业分布</div>
            <MissingNodeChart :data="store.missingTrout" dataset="trout" />
          </div>
        </div>
      </section>

      <!-- ③ 关键结论对比 -->
      <section class="section">
        <div class="section-title">指控裁定：加强还是削弱？</div>
        <div class="verdict-grid">
          <div class="verdict-card" :class="troutVerdictClass">
            <div class="verdict-header">
              <span class="v-label">TROUT 指控裁定</span>
              <span class="v-badge">{{ troutVerdictBadge }}</span>
            </div>
            <p class="v-text">
              TROUT 指控委员会偏袒渔业。全量数据显示，虽然委员会确实存在偏向渔业的迹象（Bias Index {{ biasOf('journalist').toFixed(3) }}），
              但 TROUT 自身数据由于缺失了大量的旅游相关活动（尤其是 Trip 记录），导致其指控的力度在全量背景下被<strong>削弱</strong>了。
              真实的偏见程度并没有 TROUT 描述得那么极端。
            </p>
          </div>
          <div class="verdict-card" :class="filahVerdictClass">
            <div class="verdict-header">
              <span class="v-label">FILAH 指控裁定</span>
              <span class="v-badge">{{ filahVerdictBadge }}</span>
            </div>
            <p class="v-text">
              FILAH 指控委员会偏袒旅游。全量数据显示，FILAH 严重遗漏了 3 名关键成员的活动，且缺失了大量的渔业侧讨论。
              补全数据后，偏见方向发生了反转，证明 FILAH 的指控<strong>不成立</strong>，且其自身存在严重的采样偏见。
            </p>
          </div>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useDataStore } from '../stores/dataStore'
import WaterfallChart   from '../components/charts/WaterfallChart.vue'
import MissingNodeChart from '../components/charts/MissingNodeChart.vue'

const store = useDataStore()

function biasOf(ds: string): number {
  return store.biasIndex.find(d => d.dataset === ds && d.member === 'ALL')?.bias_index ?? 0
}

const troutVerdictBadge = computed(() => {
  const diff = biasOf('journalist') - biasOf('trout')
  return diff < -0.1 ? '指控削弱' : (diff > 0.1 ? '指控加强' : '指控维持')
})

const troutVerdictClass = computed(() => {
  const diff = biasOf('journalist') - biasOf('trout')
  return diff < -0.1 ? 'v-weaken' : (diff > 0.1 ? 'v-strengthen' : 'v-neutral')
})

const filahVerdictBadge = computed(() => '指控不成立 / 被推翻')
const filahVerdictClass = computed(() => 'v-refuted')
</script>

<style scoped>
.view-container { padding: 24px; max-width: 1400px; }
.section { margin-bottom: 28px; }
.section-title {
  font-size: 12px; font-weight: 700; letter-spacing: .06em;
  text-transform: uppercase; color: #64748b; margin-bottom: 12px;
  padding-left: 10px; border-left: 3px solid #6366f1;
}

.chart-desc {
  font-size: 11px; color: #94a3b8; text-align: center; margin-top: 10px;
}

.verdict-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.verdict-card {
  background: #ffffff; border-radius: 12px; padding: 20px;
  border: 1px solid #e2e8f0; box-shadow: 0 1px 4px rgba(0,0,0,.05);
}

.verdict-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.v-label { font-size: 11px; font-weight: 700; text-transform: uppercase; color: #64748b; }
.v-badge { font-size: 12px; font-weight: 700; padding: 4px 10px; border-radius: 20px; }

.v-weaken .v-badge { background: #fff1f2; color: #e11d48; }
.v-strengthen .v-badge { background: #f0fdf4; color: #16a34a; }
.v-neutral .v-badge { background: #f1f5f9; color: #475569; }
.v-refuted .v-badge { background: #fef2f2; color: #991b1b; }

.v-text { font-size: 13px; color: #475569; line-height: 1.8; }
.v-text strong { color: #1e293b; }
</style>
