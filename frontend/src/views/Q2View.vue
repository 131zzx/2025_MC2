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
        全量知识图谱下——委员会的时间分配如何？是否存在整体偏袒？
      </div>

      <!-- ① 整体偏见指数仪表盘 -->
      <section class="section">
        <div class="section-title">全量数据集（Journalist）整体偏见指数</div>
        <div class="card bias-dashboard">
          <BiasGauge
            :value="biasOf('journalist')"
            label="Journalist"
            color="#10b981"
          />
          <div class="bias-info">
            <div class="bias-status" :class="biasOf('journalist') > 0 ? 'status-fish' : 'status-tour'">
              {{ biasOf('journalist') > 0 ? '整体偏向渔业' : '整体偏向旅游' }}
            </div>
            <p class="bias-text">
              基于全量数据，委员会的议题参与和情感表达显示出
              <strong>{{ Math.abs(biasOf('journalist')).toFixed(3) }}</strong> 
              的偏见指数。
            </p>
          </div>
        </div>
      </section>

      <!-- ② 会议议题时间分布 -->
      <section class="section">
        <div class="section-title">议题时间分配趋势（按会议）</div>
        <div class="card">
          <StreamGraph :data="store.meetingTopicDist" />
        </div>
      </section>

      <!-- ③ 成员参与热力图 -->
      <section class="section">
        <div class="section-title">成员 × 产业 参与热力图（全量数据）</div>
        <div class="card">
          <SentimentHeatmap :data="store.sentimentAgg" dataset="journalist" />
        </div>
      </section>

      <!-- ④ 行程空间分布 -->
      <section class="section">
        <div class="section-title">委员会行程空间分布（按 Zone）</div>
        <div class="grid-2">
          <div class="card">
            <div class="card-title">全量行程 Zone 分布</div>
            <TripZoneChart :data="store.tripZoneDist" />
          </div>
          <div class="card">
            <div class="card-title">行程轨迹（全量数据）</div>
            <TripMap 
              :places="store.placeNodes"
              :trips="store.tripRecords" 
              dataset="journalist" 
            />
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
import BiasGauge         from '../components/charts/BiasGauge.vue'
import StreamGraph        from '../components/charts/StreamGraph.vue'
import SentimentHeatmap  from '../components/charts/SentimentHeatmap.vue'
import TripZoneChart     from '../components/charts/TripZoneChart.vue'
import TripMap           from '../components/map/TripMap.vue'
import { COMMITTEE_MEMBERS } from '../types'

const store = useDataStore()

/** 获取某数据集整体偏见指数 */
function biasOf(ds: string): number {
  return store.biasIndex.find(d => d.dataset === ds && d.member === 'ALL')?.bias_index ?? 0
}
</script>

<style scoped>
.view-container { padding: 24px; max-width: 1400px; }

.section { margin-bottom: 28px; }
.section-title {
  font-size: 12px; font-weight: 700; letter-spacing: .06em;
  text-transform: uppercase; color: #64748b; margin-bottom: 12px;
  padding-left: 10px; border-left: 3px solid #10b981;
}

.bias-dashboard {
  display: flex; align-items: center; justify-content: space-around;
  padding: 20px;
}
.bias-info { flex: 1; max-width: 400px; padding-left: 40px; }
.bias-status {
  font-size: 18px; font-weight: 700; margin-bottom: 10px;
}
.status-fish { color: #f59e0b; }
.status-tour { color: #3b82f6; }
.bias-text { font-size: 14px; color: #64748b; line-height: 1.6; }

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
