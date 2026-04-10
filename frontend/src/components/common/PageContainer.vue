<template>
  <div class="page-container">
    <div v-if="title || description || $slots.actions" class="page-container__header">
      <div>
        <h2 v-if="title" class="page-container__title">{{ title }}</h2>
        <p v-if="description" class="page-container__description">{{ description }}</p>
      </div>
      <div v-if="$slots.actions" class="page-container__actions">
        <slot name="actions" />
      </div>
    </div>
    <div v-if="$slots.filters" class="page-container__filters">
      <slot name="filters" />
    </div>
    <slot />
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title?: string
  description?: string
}>()
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
  margin: 0;
  font-size: 20px;
}

.page-container__description {
  margin: 6px 0 0;
  color: #909399;
  font-size: 13px;
}

.page-container__filters,
.page-container__actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
</style>
