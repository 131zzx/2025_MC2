<template>
  <span
    class="term-wrapper"
    ref="triggerRef"
    @mouseenter="handleMouseEnter"
    @mouseleave="handleMouseLeave"
  >
    <slot />
    <Teleport to="body">
      <transition name="tooltip-fade">
        <div
          v-if="isVisible"
          class="term-tooltip"
          :style="tooltipStyle"
          ref="tooltipRef"
        >
          {{ explanation }}
        </div>
      </transition>
    </Teleport>
  </span>
</template>

<script setup lang="ts">
import { computed, ref, reactive } from 'vue'

const props = defineProps<{
  term: string
}>()

const triggerRef = ref<HTMLElement | null>(null)
const isVisible = ref(false)
const tooltipStyle = reactive({
  top: '0px',
  left: '0px',
})

const EXPLANATIONS: Record<string, string> = {
  '节点': '知识图谱中的核心实体，如人员、会议、议题或行程记录。',
  '边': '知识图谱中连接两个节点的线，表示它们之间的某种关系（如“参与会议”、“属于某产业”）。',
  '偏差指数': '量化委员会在不同产业（渔业 vs 旅游业）之间的时间与精力投入倾斜程度。',
  '偏见指数': '量化委员会在不同产业（渔业 vs 旅游业）之间的时间与精力投入倾斜程度。',
  '覆盖率': '衡量一个数据集相对于“全量数据”的完整程度，反映了信息的缺失情况。',
  '知识图谱': '一种将现实世界中的实体及其复杂关系通过“点”和“线”结构进行组织的数据存储方式。',
  '采样偏见': '由于数据采集不平衡（如只记录了部分人的活动）导致的结论性偏差。',
  '行程': '委员会成员离开办公室进行的实地考察或商务旅行记录。',
  '议题': '会议中讨论的具体主题，按性质分为渔业相关、旅游相关、混合型或中性。',
  '情感': '成员在参与讨论时表现出的主观态度（正值表示支持，负值表示反对）。',
  'Ego 网络': '以特定人物为中心，展示与其有直接关联的其他实体及关系的局部网络图。',
  '参与': '成员参与会议或讨论的行为记录。',
}

const explanation = computed(() => EXPLANATIONS[props.term] || '暂无详细解释')

const handleMouseEnter = () => {
  if (!triggerRef.value) return
  
  const rect = triggerRef.value.getBoundingClientRect()
  const scrollX = window.scrollX || window.pageXOffset
  const scrollY = window.scrollY || window.pageYOffset
  
  // 初始位置：上方居中
  let top = rect.top + scrollY - 10
  let left = rect.left + scrollX + rect.width / 2
  
  // 检查上方空间是否足够（假设 tooltip 高度约 80px）
  if (rect.top < 100) {
    // 空间不足，显示在下方
    top = rect.bottom + scrollY + 10
    tooltipStyle.transform = 'translate(-50%, 0)'
  } else {
    tooltipStyle.transform = 'translate(-50%, -100%)'
  }

  tooltipStyle.top = `${top}px`
  tooltipStyle.left = `${left}px`
  isVisible.value = true
}

const handleMouseLeave = () => {
  isVisible.value = false
}
</script>

<style scoped>
.term-wrapper {
  position: relative;
  display: inline-block;
  border-bottom: 1px dashed #94a3b8;
  cursor: help;
  color: inherit;
  transition: all 0.2s;
}

.term-wrapper:hover {
  color: #2563eb;
  border-bottom-color: #2563eb;
}
</style>

<style>
/* 全局样式，因为使用了 Teleport */
.term-tooltip {
  position: absolute;
  z-index: 9999;
  width: 200px;
  background-color: #1e293b;
  color: #fff;
  text-align: left;
  border-radius: 6px;
  padding: 8px 12px;
  font-size: 11px;
  line-height: 1.5;
  font-weight: normal;
  pointer-events: none;
  box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
}

.tooltip-fade-enter-active,
.tooltip-fade-leave-active {
  transition: opacity 0.2s, transform 0.2s;
}

.tooltip-fade-enter-from,
.tooltip-fade-leave-to {
  opacity: 0;
}
</style>
