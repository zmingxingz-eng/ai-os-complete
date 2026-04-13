<template>
  <el-card shadow="never" class="session-card app-card">
    <div class="session-card__avatar">A</div>
    <div class="session-card__name">{{ sessionInfo.full_name || sessionInfo.username || '管理员' }}</div>
    <div class="session-card__sub">{{ sessionInfo.username || '-' }}</div>

    <el-divider />

    <div class="session-card__row"><span>所属组织</span><strong>{{ sessionInfo.organization_name || '-' }}</strong></div>
    <div class="session-card__row"><span>岗位</span><strong>{{ sessionInfo.position_name || '-' }}</strong></div>
    <div class="session-card__row"><span>数据范围</span><strong>{{ scopeText }}</strong></div>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  sessionInfo: Record<string, any>
  dataScopes?: any[]
}>()

const scopeLabelMap: Record<string, string> = {
  all: '全部数据',
  org: '本组织',
  org_children: '本组织及下级',
  org_and_children: '本组织及下级',
  custom: '自定义组织',
  self: '仅本人',
}

const scopeText = computed(() => {
  const list = props.dataScopes || []
  if (!list.length) return '-'
  return list.map((item) => scopeLabelMap[item.scope_type] || item.scope_type).join(' / ')
})
</script>

<style scoped>
.session-card {
  text-align: center;
}

.session-card__avatar {
  width: 54px;
  height: 54px;
  margin: 0 auto 12px;
  border-radius: 50%;
  background: var(--app-primary);
  color: #fff;
  line-height: 54px;
  font-size: 22px;
  font-weight: 700;
}

.session-card__name {
  font-size: 16px;
  font-weight: 600;
}

.session-card__sub {
  margin-top: 4px;
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.session-card__row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 8px;
  text-align: left;
  font-size: 12px;
}

.session-card__row:last-child {
  margin-bottom: 0;
}
</style>
