<template>
  <div class="view-container">
    <!-- 加载 / 报错 -->
    <div v-if="store.loading" class="spinner-wrap">
      <div class="spinner" /><span>数据加载中…</span>
    </div>
    <div v-else-if="store.error" class="alert alert-danger">{{ store.error }}</div>

    <template v-else>
      <!-- 结论摘要 -->
      <div class="alert alert-info">
        <strong>Q1 核心发现：</strong>
        FILAH 数据集在"主题偏差指数"指标上显著倾向渔业（Fishing 行业占比偏高），而 TROUT 数据集则相反。记者数据集覆盖最全面，可作为中立基准对比。
      </div>

      <!-- 数据集切换 -->
      <div class="btn-group" style="margin-bottom:20px">
        <button
          v-for="ds in datasets" :key="ds.key"
          class="btn" :class="[`btn-${ds.key}`, activeDs === ds.key && 'btn--active']"
          @click="activeDs = ds.key"
        >{{ ds.label }}</button>
      </div>

      <!-- 图表网格 -->
      <div class="grid-2">
        <div class="card">
          <div class="card-title">偏差指数（Bias Index）</div>
          <BiasIndexBar :data="store.biasIndex" :dataset="activeDs" />
        </div>
        <div class="card">
          <div class="card-title">话题行业分布</div>
          <TopicDistChart :data="store.topicDist" :dataset="activeDs" />
        </div>
        <div class="card">
          <div class="card-title">节点类型计数</div>
          <NodeTypeChart :data="store.nodeTypeCounts" :dataset="activeDs" />
        </div>
        <div class="card">
          <div class="card-title">FILAH 偏差摘要</div>
          <FilahBiasSummary :data="store.biasIndex" />
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useDataStore } from '../stores/dataStore'
import BiasIndexBar    from '../components/charts/BiasIndexBar.vue'
import TopicDistChart  from '../components/charts/TopicDistChart.vue'
import NodeTypeChart   from '../components/charts/NodeTypeChart.vue'
import FilahBiasSummary from '../components/shared/FilahBiasSummary.vue'

const store = useDataStore()
const activeDs = ref<'filah' | 'trout' | 'journalist'>('filah')
const datasets = [
  { key: 'filah',      label: 'FILAH'    },
  { key: 'trout',      label: 'TROUT'    },
  { key: 'journalist', label: '记者数据' },
] as const
</script>

<style scoped>
.view-container { padding: 24px; max-width: 1400px; }
</style>
