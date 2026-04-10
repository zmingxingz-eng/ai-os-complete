<template>
  <PageContainer title="审计日志" description="查看系统关键操作记录。">
    <template #filters>
      <div class="toolbar">
        <el-input v-model="keyword" placeholder="操作类型/目标对象/操作人" style="width: 280px;" />
        <el-button type="primary" @click="fetchList">查询</el-button>
      </div>
    </template>

    <el-table :data="filteredList" v-loading="loading" border>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="action" label="操作类型" min-width="120" />
      <el-table-column prop="target" label="目标对象" min-width="160" />
      <el-table-column prop="content" label="内容" min-width="220" />
      <el-table-column prop="operator_name" label="操作人" min-width="120" />
      <el-table-column prop="created_at" label="创建时间" min-width="180" />
    </el-table>

    <div class="pagination-bar">
      <el-pagination
        background
        layout="total, sizes, prev, pager, next"
        :total="total"
        :current-page="currentPage"
        :page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        @current-change="handleCurrentChange"
        @size-change="handleSizeChange"
      />
    </div>
  </PageContainer>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import PageContainer from '@/components/common/PageContainer.vue'
import { fetchAuditLogList } from '@/api/system/audit-log'
import { useCrud } from '@/composables/useCrud'

const keyword = ref('')
const { list, loading, total, currentPage, pageSize, fetchList, handleCurrentChange, handleSizeChange } = useCrud<any>(fetchAuditLogList)

const filteredList = computed(() => {
  if (!keyword.value) return list.value
  return list.value.filter((item: any) =>
    [item.action, item.target, item.operator_name].some((value) => String(value || '').includes(keyword.value))
  )
})

onMounted(fetchList)
</script>

<style scoped>
.toolbar {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.pagination-bar {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>
