<template>
  <div class="page-container">
    <div class="page-container__header">
      <div>
        <div class="page-container__title">{{ title || routeTitle }}</div>
        <div v-if="description" class="page-container__description">{{ description }}</div>
      </div>
      <div v-if="$slots.actions" class="page-container__actions">
        <slot name="actions" />
      </div>
    </div>

    <el-card v-if="$slots.filters" shadow="never" class="app-card">
      <slot name="filters" />
    </el-card>

    <el-card shadow="never" class="app-card">
      <slot />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const props = defineProps<{
  title?: string
  description?: string
}>()

const route = useRoute()
const routeTitle = computed(() => String(props.title || route.meta.title || '未命名页面'))
</script>

<style scoped>
.page-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.page-container__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.page-container__title {
  font-size: 24px;
  font-weight: 600;
  line-height: 1.2;
}

.page-container__description {
  margin-top: 6px;
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.page-container__actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
</style>
