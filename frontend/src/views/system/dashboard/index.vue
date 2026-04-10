<template>
  <PageContainer title="系统首页" description="查看当前系统管理骨架的基础统计与访问入口。">
    <div class="dashboard-grid">
      <el-card shadow="never" class="app-card">
        <template #header>当前用户</template>
        <div class="dashboard-value dashboard-value--text">{{ sessionInfo.full_name || sessionInfo.username || '-' }}</div>
        <div class="dashboard-desc">{{ sessionInfo.organization_name || '未绑定组织' }}</div>
      </el-card>
      <el-card shadow="never" class="app-card">
        <template #header>数据范围</template>
        <div class="dashboard-value">{{ dataScopes.length }}</div>
        <div class="dashboard-desc">当前生效的数据范围条目</div>
      </el-card>
      <el-card shadow="never" class="app-card">
        <template #header>菜单数量</template>
        <div class="dashboard-value">{{ menus.length }}</div>
        <div class="dashboard-desc">当前登录用户可见菜单数</div>
      </el-card>
    </div>
  </PageContainer>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { storeToRefs } from 'pinia'
import PageContainer from '@/components/common/PageContainer.vue'
import { fetchSessionInfo } from '@/api/auth'
import { usePermissionStore } from '@/store/permission'

const permissionStore = usePermissionStore()
const { menus, dataScopes } = storeToRefs(permissionStore)
const sessionInfo = ref<Record<string, any>>({})

onMounted(async () => {
  sessionInfo.value = await fetchSessionInfo().catch(() => ({}))
})
</script>

<style scoped>
.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
}

.dashboard-value {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 8px;
}

.dashboard-value--text {
  font-size: 22px;
}

.dashboard-desc {
  color: var(--el-text-color-secondary);
  font-size: 13px;
}
</style>
