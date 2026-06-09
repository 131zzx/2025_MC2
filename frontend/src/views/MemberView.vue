<template>
  <div class="mv-root">

    <!-- ══ 第一行：两个宽图并排 ══ -->
    <div class="row row-top">

      <!-- 偏见定位散点图（英雄图） -->
      <div class="card flex-6">
        <div class="card-hd">
          <span class="card-title">委员偏见定位图</span>
          <span class="card-hint">X = 渔业情感 · Y = 旅游情感 · 气泡大小 = 样本量 · 点击选中</span>
          <transition name="fade">
            <div v-if="selectedMember" class="sel-chip">
              <span class="sel-av">{{ initials }}</span>
              <span class="sel-name">{{ selectedMember }}</span>
              <button class="sel-x" @click="selectedMember = null">×</button>
            </div>
          </transition>
        </div>
        <MemberBiasScatter
          :data="store.sentimentAgg"
          :selected-member="selectedMember"
          @select="onSelect"
          @hover="hoveredMember = $event"
        />
      </div>

      <!-- 平行坐标图 -->
      <div class="card flex-4">
        <div class="card-hd">
          <span class="card-title">活动量平行坐标</span>
          <span class="card-hint">点击线条选中成员</span>
        </div>
        <MemberPCP
          :data="store.memberActivity"
          :selected-member="selectedMember"
          @select="onSelect"
          @hover="hoveredMember = $event"
        />
      </div>

    </div>

    <!-- ══ 第二行：覆盖率矩阵 + 情感热图 + 右侧面板 ══ -->
    <div class="row row-main">

      <!-- 覆盖率矩阵（左） -->
      <div class="card flex-4">
        <div class="card-hd">
          <span class="card-title">活动<TermExplanation term="覆盖率">覆盖率</TermExplanation></span>
          <span class="card-hint">点击成员行</span>
        </div>
        <div class="scroll-x-container">
          <CoverageMatrix
            :coverage="store.coverage"
            :member-activity="store.memberActivity"
            :selected-member="selectedMember ?? undefined"
            @select-member="onSelect"
          />
        </div>
      </div>

      <!-- 情感热图（中） -->
      <div class="card flex-4">
        <div class="card-hd">
          <span class="card-title"><TermExplanation term="情感">情感</TermExplanation>倾向热图</span>
          <div class="ds-tabs">
            <button
              v-for="ds in DS_LIST" :key="ds.key"
              class="ds-tab" :class="{ 'ds-tab--on': sentimentDs === ds.key }"
              :style="sentimentDs === ds.key
                ? { borderBottomColor: ds.color, color: ds.color }
                : {}"
              @click="sentimentDs = ds.key"
            >{{ ds.label }}</button>
          </div>
        </div>
        <SentimentHeatmap
          :data="store.sentimentAgg"
          :dataset="sentimentDs"
          :highlighted-member="selectedMember ?? undefined"
          @member-click="onSelect"
          @member-hover="hoveredMember = $event"
        />
      </div>

      <!-- 右侧：无选中→情感摘要；有选中→跨数据集活动 -->
      <div class="card flex-3">
        <template v-if="!selectedMember">
          <div class="card-hd">
            <span class="card-title">各成员行业<TermExplanation term="情感">情感</TermExplanation>均值</span>
            <span class="card-hint">记者数据集</span>
          </div>
          <MemberSentimentSummary :data="store.sentimentAgg" />
        </template>
        <template v-else>
          <div class="card-hd">
            <span class="card-title">{{ shortLast(selectedMember) }} · 跨数据集活动</span>
          </div>
          <MemberCompareBar :data="store.memberActivity" :member="selectedMember" />
        </template>
      </div>

    </div>

    <!-- ══ 第三行：仅在选中成员时展开 ══ -->
    <transition name="slide-down">
      <div v-if="selectedMember" class="row row-detail">

        <!-- 行业情感偏向 -->
        <div class="card flex-3">
          <div class="card-hd">
            <span class="card-title">行业<TermExplanation term="情感">情感</TermExplanation>偏向</span>
            <span class="card-hint">正 = 支持 · 负 = 反对</span>
          </div>
          <MemberSentimentBar :data="store.sentimentAgg" :member="selectedMember" />
        </div>

        <!-- 关系网络 -->
        <div class="card flex-7 ego-card">
          <div class="card-hd" style="padding: 14px 14px 0">
            <span class="card-title"><TermExplanation term="Ego 网络">关系网络</TermExplanation></span>
          </div>
          <EgoNetwork :member="selectedMember" :graph-data="store.fullGraph" />
        </div>

      </div>
    </transition>

  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useDataStore } from '../stores/dataStore'
import { DATASET_COLORS } from '../types'
import type { DatasetKey } from '../types'

import MemberBiasScatter      from '../components/charts/MemberBiasScatter.vue'
import MemberPCP               from '../components/charts/MemberPCP.vue'
import SentimentHeatmap        from '../components/charts/SentimentHeatmap.vue'
import CoverageMatrix          from '../components/charts/CoverageMatrix.vue'
import MemberCompareBar        from '../components/charts/MemberCompareBar.vue'
import MemberSentimentBar      from '../components/charts/MemberSentimentBar.vue'
import MemberSentimentSummary  from '../components/charts/MemberSentimentSummary.vue'
import EgoNetwork              from '../components/graph/EgoNetwork.vue'
import TermExplanation         from '../components/shared/TermExplanation.vue'

const store = useDataStore()

const selectedMember = ref<string | null>(null)
const hoveredMember  = ref<string | null>(null)
const sentimentDs    = ref<DatasetKey>('journalist')

const DS_LIST = [
  { key: 'filah'      as DatasetKey, label: 'FILAH', color: DATASET_COLORS.filah },
  { key: 'trout'      as DatasetKey, label: 'TROUT', color: DATASET_COLORS.trout },
  { key: 'journalist' as DatasetKey, label: '记者',  color: DATASET_COLORS.journalist },
]

const initials = computed(() =>
  (selectedMember.value ?? '').split(' ').map(p => p[0]).join('').toUpperCase().slice(0, 2)
)

function onSelect(name: string | null) {
  selectedMember.value = selectedMember.value === name ? null : name
}

function shortLast(name: string) {
  return name.split(' ').slice(-1)[0] ?? name
}
</script>

<style scoped>
.mv-root {
  display: flex; flex-direction: column; gap: 0;
  background: #f1f5f9; min-height: 100%;
}

.sel-chip {
  margin-left: auto; display: flex; align-items: center; gap: 6px;
  padding: 4px 10px 4px 5px; border-radius: 20px;
  background: #eff6ff; border: 1px solid #bfdbfe;
}
.sel-av {
  width: 22px; height: 22px; border-radius: 50%;
  background: linear-gradient(135deg, #2563eb, #7c3aed);
  color: #fff; font-size: 9px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
}
.sel-name { font-size: 12px; font-weight: 700; color: #1d4ed8; }
.sel-x { background: none; border: none; color: #93c5fd; cursor: pointer; font-size: 15px; padding: 0 2px; }
.sel-x:hover { color: #1d4ed8; }

/* 行布局 */
.row {
  display: flex; gap: 12px; padding: 12px 20px 0;
  flex-shrink: 0;
}
.row:last-child { padding-bottom: 20px; }

/* flex 比例类 */
.flex-3 { flex: 3; min-width: 0; }
.flex-4 { flex: 4; min-width: 0; }
.flex-5 { flex: 5; min-width: 0; }
.flex-6 { flex: 6; min-width: 0; }
.flex-7 { flex: 7; min-width: 0; }

/* 卡片 */
.card {
  background: #fff; border: 1px solid #e2e8f0; border-radius: 10px;
  padding: 14px; overflow: hidden;
}
.card-hd {
  display: flex; align-items: center; gap: 8px; margin-bottom: 12px; flex-wrap: wrap;
}
.card-title { font-size: 13px; font-weight: 700; color: #1e293b; }
.card-hint  { font-size: 11px; color: #94a3b8; }

.ds-tabs {
  margin-left: auto; display: flex;
  border: 1px solid #f1f5f9; border-radius: 6px; overflow: hidden;
}
.ds-tab {
  padding: 3px 9px; border: none; background: transparent; cursor: pointer;
  font-size: 11px; color: #94a3b8; border-bottom: 2px solid transparent; transition: all .1s;
}
.ds-tab--on { font-weight: 700; background: #f8fafc; }

.ego-card { padding: 0; }

/* 展开动画 */
.slide-down-enter-active { transition: all .2s ease-out; }
.slide-down-leave-active { transition: all .15s ease-in; }
.slide-down-enter-from { opacity: 0; transform: translateY(-8px); }
.slide-down-leave-to   { opacity: 0; transform: translateY(-4px); }

/* 淡入 */
.fade-enter-active, .fade-leave-active { transition: opacity .15s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
