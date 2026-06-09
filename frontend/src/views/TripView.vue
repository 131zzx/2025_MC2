<template>
  <div class="trip-view">

    <!-- 主区域：地图 + 时间轴 -->
    <div class="main-area">

      <!-- 地图 -->
      <div class="map-section">
        <OceanusMap
          :trips="filteredTrips"
          :places="store.placeNodes"
          @place-click="onPlaceClick"
        />
      </div>

      <!-- 时间轴：甘特图风格 -->
      <div class="timeline-section card">
        <div class="card-header">
          <span class="card-title">行程时间轴</span>
          <div class="timeline-controls">
            <label class="show-label">
              <input type="checkbox" v-model="showAllMembers" @change="onFilterChange" /> 全员
            </label>
            <span class="trip-count">共 {{ filteredTrips.length }} 条行程</span>
          </div>
        </div>
        <TripTimeline
          :trips="filteredTrips"
          :selected-member="linking.selectedMember ?? undefined"
          :hovered-trip="linking.hoveredTrip ?? undefined"
          @trip-hover="linking.setHoveredTrip"
          @member-click="linking.selectMember"
        />
      </div>
    </div>

    <!-- 右侧辅助面板 -->
    <div class="side-panel">

      <!-- 区域分布 -->
      <div class="card">
        <div class="card-header">
          <span class="card-title">行程区域分布</span>
          <span class="card-hint">各区域被访问次数</span>
        </div>
        <TripZoneChart :data="filteredTripZone" />
      </div>

      <!-- 成员行程统计 -->
      <div class="card">
        <div class="card-header">
          <span class="card-title">成员行程统计</span>
        </div>
        <div class="member-trip-list">
          <div
            v-for="item in memberTripStats" :key="item.member"
            class="member-trip-row"
            :class="{
              'row--selected': linking.selectedMember === item.member,
              'row--dimmed': linking.isMemberDimmed(item.member),
            }"
            @click="linking.selectMember(item.member)"
            @mouseenter="linking.setHoveredMember(item.member)"
            @mouseleave="linking.setHoveredMember(null)"
          >
            <span class="row-name">{{ item.member }}</span>
            <div class="row-bars">
              <div class="ds-bar-wrap" v-for="dsi in dsBarInfos" :key="dsi.key">
                <div
                  class="ds-bar"
                  :style="{ width: (item.counts[dsi.key] / maxTripCount * 80) + 'px', background: dsi.color }"
                />
                <span class="ds-bar-val">{{ item.counts[dsi.key] }}</span>
              </div>
            </div>
          </div>
        </div>
        <div class="legend-row">
          <span v-for="dsi in dsBarInfos" :key="dsi.key" class="legend-item">
            <span class="legend-dot" :style="{ background: dsi.color }" />
            {{ dsi.label }}
          </span>
        </div>
      </div>

      <!-- 结论 -->
      <div class="card conclusion-card">
        <div class="conclusion-icon">◎</div>
        <div class="conclusion-text">
          <strong>行程地域规律：</strong>
          部分委员会成员的行程在渔场和生态保护区高度集中，
          而另一些成员则更多访问旅游区域和港口。
          结合时间轴可观察到，争议高发期前后的行程数量明显变化。
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useDataStore } from '../stores/dataStore'
import { uselinkingStore } from '../stores/linkingStore'
import { DATASET_COLORS, DATASET_LABELS, COMMITTEE_MEMBERS } from '../types'
import type { DatasetKey, TripRecord } from '../types'

import OceanusMap    from '../components/map/OceanusMap.vue'
import TripTimeline  from '../components/charts/TripTimeline.vue'
import TripZoneChart from '../components/charts/TripZoneChart.vue'

const store   = useDataStore()
const linking = uselinkingStore()

const dsBarInfos = [
  { key: 'filah'      as DatasetKey, label: DATASET_LABELS.filah,      color: DATASET_COLORS.filah },
  { key: 'trout'      as DatasetKey, label: DATASET_LABELS.trout,      color: DATASET_COLORS.trout },
  { key: 'journalist' as DatasetKey, label: DATASET_LABELS.journalist, color: DATASET_COLORS.journalist },
]

const showAllMembers = ref(true)

function isActiveDs(ds: string): boolean {
  return linking.isDatasetActive(ds as DatasetKey)
}

const filteredTrips = computed<TripRecord[]>(() => {
  let trips = store.tripRecords.filter(t => isActiveDs(t.dataset))
  if (!showAllMembers.value && linking.selectedMember) {
    trips = trips.filter(t => t.person === linking.selectedMember)
  }
  return trips
})

const filteredTripZone = computed(() =>
  store.tripZoneDist.filter(d => isActiveDs(d.dataset))
)

function onFilterChange() {
  // showAllMembers 由 v-model 控制，无需额外处理
}

function onPlaceClick(placeId: string) {
  // 可以在未来联动到时间轴过滤
  console.log('place clicked:', placeId)
}

// ── 成员行程统计 ──────────────────────────────────────────
const memberTripStats = computed(() => {
  return COMMITTEE_MEMBERS.map(member => {
    const counts: Record<string, number> = { filah: 0, trout: 0, journalist: 0 }
    store.tripRecords
      .filter(t => t.person === member)
      .forEach(t => { counts[t.dataset] = (counts[t.dataset] || 0) + 1 })
    return { member, counts }
  }).sort((a, b) =>
    (b.counts.filah + b.counts.trout + b.counts.journalist) -
    (a.counts.filah + a.counts.trout + a.counts.journalist)
  )
})

const maxTripCount = computed(() => {
  let max = 1
  memberTripStats.value.forEach(item => {
    Object.values(item.counts).forEach(v => { if (v > max) max = v })
  })
  return max
})
</script>

<style scoped>
.trip-view {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 16px;
  padding: 24px;
  align-items: start;
}

.main-area { display: flex; flex-direction: column; gap: 16px; }
.side-panel { display: flex; flex-direction: column; gap: 16px; }

.map-section { border-radius: 10px; overflow: hidden; }

.card {
  background: #fff; border: 1px solid #e2e8f0; border-radius: 10px;
  padding: 16px; overflow: hidden;
}
.card-header {
  display: flex; align-items: center; gap: 8px; margin-bottom: 14px; flex-wrap: wrap;
}
.card-title { font-size: 13px; font-weight: 700; color: #1e293b; }
.card-hint  { font-size: 11px; color: #94a3b8; margin-left: auto; }

.timeline-controls { display: flex; align-items: center; gap: 10px; margin-left: auto; }
.show-label { font-size: 11px; color: #64748b; display: flex; align-items: center; gap: 4px; cursor: pointer; }
.trip-count { font-size: 11px; color: #94a3b8; }

/* 成员行程列表 */
.member-trip-list { display: flex; flex-direction: column; gap: 4px; }
.member-trip-row {
  display: flex; align-items: center; gap: 8px;
  padding: 6px 8px; border-radius: 6px; cursor: pointer; transition: all .12s;
}
.member-trip-row:hover { background: #f8fafc; }
.row--selected { background: #eff6ff; }
.row--dimmed { opacity: .35; }
.row-name { font-size: 11px; font-weight: 600; color: #374151; width: 90px; flex-shrink: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.row-bars { display: flex; flex-direction: column; gap: 2px; flex: 1; }
.ds-bar-wrap { display: flex; align-items: center; gap: 4px; }
.ds-bar { height: 6px; border-radius: 3px; min-width: 2px; transition: width .3s; }
.ds-bar-val { font-size: 10px; color: #94a3b8; width: 20px; }

.legend-row { display: flex; gap: 10px; margin-top: 8px; flex-wrap: wrap; padding-top: 8px; border-top: 1px solid #f1f5f9; }
.legend-item { display: flex; align-items: center; gap: 4px; font-size: 10px; color: #64748b; }
.legend-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }

/* 结论卡 */
.conclusion-card { display: flex; gap: 12px; align-items: flex-start; background: #f0f9ff; border-color: #bae6fd; }
.conclusion-icon { font-size: 20px; color: #0369a1; flex-shrink: 0; }
.conclusion-text { font-size: 12px; color: #0c4a6e; line-height: 1.6; }
.conclusion-text strong { font-weight: 700; }
</style>
