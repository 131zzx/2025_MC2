<template>
  <div class="trip-view">

    <!-- 地图 -->
    <div class="map-section">
      <OceanusMap :trips="filteredTrips" :places="store.placeNodes" />
    </div>

    <!-- 时间轴（全宽） -->
    <div class="card timeline-card">
      <div class="card-hd">
        <span class="card-title"><TermExplanation term="行程">行程</TermExplanation>时间轴</span>
        
        <!-- 行程点图例：动态切换 -->
        <div class="tl-legend">
          <div class="leg-title">行程点状态：</div>
          <template v-if="isJournalistActive">
            <div class="leg-item"><span class="leg-dot" style="background: #064e3b" />多方证实</div>
            <div class="leg-item"><span class="leg-dot" style="background: #10b981" />单方验证</div>
            <div class="leg-item"><span class="leg-dot" style="background: #a7f3d0" />仅记者有</div>
          </template>
          <template v-else>
            <div class="leg-item"><span class="leg-dot" :style="{ background: DATASET_COLORS.filah }" />FILAH 独有</div>
            <div class="leg-item"><span class="leg-dot" :style="{ background: DATASET_COLORS.trout }" />TROUT 独有</div>
            <div class="leg-item"><span class="leg-dot" style="background: #ef4444" />双方共有</div>
          </template>
        </div>

        <div class="tl-controls">
          <span class="trip-count">{{ filteredTrips.length }} 条<TermExplanation term="行程">行程</TermExplanation></span>
          <div class="ds-btns">
            <button
              v-for="ds in DS_LIST" :key="ds.key"
              class="ds-chip" :class="{ 'ds-chip--on': activeDsSet.has(ds.key) }"
              :style="activeDsSet.has(ds.key) ? { background: ds.color + '18', borderColor: ds.color, color: ds.color } : {}"
              @click="toggleDs(ds.key)"
            >{{ ds.label }}</button>
          </div>
          <select class="member-sel" v-model="selectedMember">
            <option value="">全部成员</option>
            <option v-for="m in COMMITTEE_MEMBERS" :key="m" :value="m">{{ m }}</option>
          </select>
        </div>
      </div>
      <TripTimeline
        :trips="timelineTrips"
        :selected-member="selectedMember || undefined"
        @member-click="selectedMember = selectedMember === $event ? '' : $event"
      />
    </div>

    <!-- 统计图：时间轴下方并排 -->
    <div class="stats-row">
      <div class="card stats-card">
        <div class="card-hd">
          <span class="card-title"><TermExplanation term="行程">行程</TermExplanation>区域分布</span>
        </div>
        <TripZoneChart :data="filteredZone" />
      </div>

      <div class="card stats-card">
        <div class="card-hd">
          <span class="card-title">各成员<TermExplanation term="行程">行程</TermExplanation>数量</span>
        </div>
        <div class="member-stat-list">
          <div
            v-for="item in memberStats" :key="item.member"
            class="ms-row"
            :class="{ 'ms-row--sel': selectedMember === item.member }"
            @click="selectedMember = selectedMember === item.member ? '' : item.member"
          >
            <span class="ms-name">{{ shortName(item.member) }}</span>
            <div class="ms-bars">
              <div
                v-for="ds in DS_LIST" :key="ds.key"
                class="ms-bar"
                :style="{
                  width: (item.counts[ds.key] / maxCount * 100) + '%',
                  background: ds.color
                }"
                :title="`${ds.label}: ${item.counts[ds.key]}`"
              />
            </div>
            <span class="ms-total">{{ item.total }}</span>
          </div>
        </div>
        <div class="ds-legend">
          <span v-for="ds in DS_LIST" :key="ds.key" class="dl-item">
            <span class="dl-dot" :style="{ background: ds.color }" />{{ ds.label }}
          </span>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue'
import { useDataStore } from '../stores/dataStore'
import { DATASET_COLORS, COMMITTEE_MEMBERS } from '../types'
import type { DatasetKey, TripRecord } from '../types'

import OceanusMap    from '../components/map/OceanusMap.vue'
import TripTimeline  from '../components/charts/TripTimeline.vue'
import TripZoneChart from '../components/charts/TripZoneChart.vue'
import TermExplanation from '../components/shared/TermExplanation.vue'

const store = useDataStore()

type Ds = DatasetKey
const DS_LIST = [
  { key: 'filah'      as Ds, label: 'FILAH', color: DATASET_COLORS.filah },
  { key: 'trout'      as Ds, label: 'TROUT', color: DATASET_COLORS.trout },
  { key: 'journalist' as Ds, label: '记者',  color: DATASET_COLORS.journalist },
]

const activeDsSet    = reactive(new Set<Ds>(['filah', 'trout', 'journalist']))
const selectedMember = ref('')

function toggleDs(ds: Ds) {
  if (activeDsSet.has(ds)) { if (activeDsSet.size > 1) activeDsSet.delete(ds) }
  else activeDsSet.add(ds)
}

function isActiveDs(ds: string): boolean { return activeDsSet.has(ds as Ds) }

const filteredTrips = computed<TripRecord[]>(() => {
  let trips = store.tripRecords.filter(t => isActiveDs(t.dataset))
  if (selectedMember.value) trips = trips.filter(t => t.person === selectedMember.value)
  return trips
})

// 检查当前显示的行程是否包含记者
const isJournalistActive = computed(() => 
  activeDsSet.has('journalist')
)

// 为时间轴准备的去重且带证据状态的行程
const timelineTrips = computed(() => {
  const allTrips = store.tripRecords
  // 1. 预计算每个 trip_id 存在于哪些数据集
  const presenceMap = new Map<string, Set<DatasetKey>>()
  allTrips.forEach(t => {
    if (!presenceMap.has(t.trip_id)) presenceMap.set(t.trip_id, new Set())
    presenceMap.get(t.trip_id)!.add(t.dataset)
  })

  // 2. 筛选出当前需要显示的行程（去重，每个 ID 只留一个用于定位）
  const uniqueMap = new Map<string, TripRecord & { presence: Set<DatasetKey>; isJournalistActive: boolean }>()
  const journalistActive = isJournalistActive.value

  filteredTrips.value.forEach(t => {
    if (!uniqueMap.has(t.trip_id)) {
      uniqueMap.set(t.trip_id, {
        ...t,
        presence: presenceMap.get(t.trip_id)!,
        isJournalistActive: journalistActive
      })
    }
  })
  return Array.from(uniqueMap.values())
})

const filteredZone = computed(() =>
  store.tripZoneDist.filter(d => isActiveDs(d.dataset))
)

const memberStats = computed(() =>
  COMMITTEE_MEMBERS.map(member => {
    const counts: Record<string, number> = { filah: 0, trout: 0, journalist: 0 }
    store.tripRecords
      .filter(t => t.person === member && isActiveDs(t.dataset))
      .forEach(t => { counts[t.dataset] = (counts[t.dataset] || 0) + 1 })
    return { member, counts, total: Object.values(counts).reduce((a, b) => a + b, 0) }
  }).sort((a, b) => b.total - a.total)
)

const maxCount = computed(() => {
  let max = 1
  memberStats.value.forEach(m => Object.values(m.counts).forEach(v => { if (v > max) max = v }))
  return max
})

function shortName(n: string) {
  const p = n.split(' ')
  return p.length >= 2 ? p[0][0] + '. ' + p[p.length - 1] : n
}
</script>

<style scoped>
.trip-view {
  display: flex; flex-direction: column; gap: 14px;
  padding: 20px;
}

.map-section { border-radius: 10px; overflow: hidden; }

.card {
  background: #fff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px;
}
.card-hd {
  display: flex; align-items: center; gap: 8px; margin-bottom: 10px; flex-wrap: wrap;
}
.card-title { font-size: 13px; font-weight: 700; color: #1e293b; }

.tl-legend {
  margin-left: 20px; display: flex; align-items: center; gap: 12px;
}
.leg-title { font-size: 11px; color: #94a3b8; }
.leg-item  { display: flex; align-items: center; gap: 5px; font-size: 11px; color: #64748b; }
.leg-dot   { width: 8px; height: 8px; border-radius: 50%; }

.tl-controls { display: flex; align-items: center; gap: 8px; margin-left: auto; flex-wrap: wrap; }
.trip-count  { font-size: 11px; color: #94a3b8; }
.ds-btns     { display: flex; gap: 4px; }
.ds-chip {
  padding: 3px 9px; border-radius: 20px; border: 1px solid #e2e8f0;
  background: #f8fafc; font-size: 11px; cursor: pointer; color: #64748b; font-weight: 500;
}
.ds-chip--on { font-weight: 700; }
.member-sel {
  font-size: 11px; border: 1px solid #e2e8f0; border-radius: 5px;
  padding: 3px 6px; color: #475569; background: #fff; cursor: pointer;
}

/* 时间轴下方两图并排 */
.stats-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
  align-items: start;
}

.member-stat-list { display: flex; flex-direction: column; gap: 3px; }
.ms-row {
  display: flex; align-items: center; gap: 6px; padding: 5px 6px;
  border-radius: 5px; cursor: pointer; transition: background .1s;
}
.ms-row:hover { background: #f8fafc; }
.ms-row--sel { background: #eff6ff; }
.ms-name  { font-size: 11px; font-weight: 600; color: #374151; width: 72px; flex-shrink: 0; }
.ms-bars  { flex: 1; display: flex; flex-direction: column; gap: 2px; }
.ms-bar   { height: 5px; border-radius: 3px; min-width: 2px; transition: width .3s; }
.ms-total { font-size: 10px; color: #94a3b8; width: 28px; text-align: right; }

.ds-legend { display: flex; gap: 8px; margin-top: 6px; padding-top: 6px; border-top: 1px solid #f1f5f9; }
.dl-item   { display: flex; align-items: center; gap: 4px; font-size: 10px; color: #64748b; }
.dl-dot    { width: 7px; height: 7px; border-radius: 50%; }
</style>
