<template>
  <PageContainer title="按钮权限示例" description="演示按钮权限在页面中的可见性控制。">
    <div class="button-demo">
      <el-button v-permission="'notice.manage'" type="primary">允许：公告管理</el-button>
      <el-button v-permission="'user.export'" type="success">允许：用户导出</el-button>
      <el-alert title="只有当前用户拥有对应权限码时，按钮才会显示。" type="info" :closable="false" />
    </div>
  </PageContainer>
</template>

<script setup lang="ts">
import PageContainer from '@/components/common/PageContainer.vue'
</script>

<style scoped>
.button-demo {
  display: flex;
  flex-direction: column;
  gap: 12px;
  align-items: flex-start;
}
</style>
