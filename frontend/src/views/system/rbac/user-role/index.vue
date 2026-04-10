<template>
  <PageContainer title="用户角色绑定" description="将系统账号绑定到角色组。">
    <template #filters>
      <div class="toolbar">
        <el-button type="success" @click="openCreate">新增绑定</el-button>
      </div>
    </template>
    <el-table :data="list" v-loading="loading" border>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="username" label="用户名" />
      <el-table-column prop="role_name" label="角色名称" />
      <el-table-column label="操作" width="120">
        <template #default="{ row }">
          <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
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

    <el-dialog v-model="dialogVisible" title="新增用户角色绑定" width="520px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="用户">
          <el-select v-model="form.user" filterable style="width: 100%">
            <el-option v-for="item in users" :key="item.id" :label="item.username" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="form.role" filterable style="width: 100%">
            <el-option v-for="item in roles" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreate">保存</el-button>
      </template>
    </el-dialog>
  </PageContainer>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import PageContainer from '@/components/common/PageContainer.vue'
import { fetchRoleList } from '@/api/system/role'
import { fetchUsersList } from '@/api/system/users'
import { createUserRole, deleteUserRole, fetchUserRoleList } from '@/api/system/rbac'
import { useCrud } from '@/composables/useCrud'

const dialogVisible = ref(false)
const users = ref<any[]>([])
const roles = ref<any[]>([])
const { list, loading, total, currentPage, pageSize, fetchList, handleCurrentChange, handleSizeChange } = useCrud<any>(fetchUserRoleList)

const form = reactive<any>({
  user: undefined,
  role: undefined,
})

const loadOptions = async () => {
  const [userPayload, rolePayload] = await Promise.all([
    fetchUsersList().catch(() => []),
    fetchRoleList().catch(() => []),
  ])
  users.value = Array.isArray(userPayload) ? userPayload : userPayload?.results || []
  roles.value = Array.isArray(rolePayload) ? rolePayload : rolePayload?.results || []
}

const openCreate = async () => {
  form.user = undefined
  form.role = undefined
  await loadOptions()
  dialogVisible.value = true
}

const handleCreate = async () => {
  await createUserRole({ user: form.user, role: form.role })
  ElMessage.success('绑定成功')
  dialogVisible.value = false
  fetchList()
}

const handleDelete = async (row: any) => {
  await ElMessageBox.confirm(`确认删除绑定【${row.username} - ${row.role_name}】吗？`, '提示')
  await deleteUserRole(row.id)
  ElMessage.success('删除成功')
  fetchList()
}

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
