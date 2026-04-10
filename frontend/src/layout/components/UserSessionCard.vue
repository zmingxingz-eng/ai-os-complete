<template>
  <el-card shadow="never" class="session-card app-card">
    <div class="session-card__row"><span>当前用户</span><strong>{{ sessionInfo.full_name || sessionInfo.username || '-' }}</strong></div>
    <div class="session-card__row"><span>登录账号</span><strong>{{ sessionInfo.username || '-' }}</strong></div>
    <div class="session-card__row"><span>所属组织</span><strong>{{ sessionInfo.organization_name || '-' }}</strong></div>
    <div class="session-card__row"><span>岗位</span><strong>{{ sessionInfo.position_name || '-' }}</strong></div>
    <div class="session-card__row"><span>用户ID</span><strong>{{ sessionInfo.user_id || '-' }}</strong></div>
    <div class="session-card__row"><span>管理员</span><strong>{{ sessionInfo.is_superuser ? '是' : '否' }}</strong></div>
    <div class="session-card__row"><span>数据范围</span><strong>{{ scopeText }}</strong></div>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  sessionInfo: Record<string, any>
  dataScopes?: any[]
}>()

const scopeText = computed(() => {
  const list = props.dataScopes || []
  if (!list.length) return '-'
  return list.map((item) => item.scope_type).join(' / ')
})
</script>

<style scoped>
.session-card {
  font-size: 12px;
}

.session-card__row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 8px;
}

.session-card__row:last-child {
  margin-bottom: 0;
}
</style>
