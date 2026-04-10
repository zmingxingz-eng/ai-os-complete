<template>
  <PageContainer title="角色数据权限" description="为角色设置数据范围，支持全部、本组织、本组织及下级、仅本人。">
    <template #filters>
      <div class="toolbar">
        <el-select v-model="roleFilter" clearable filterable placeholder="按角色筛选" style="width: 260px">
          <el-option v-for="item in roles" :key="item.id" :label="item.name" :value="item.id" />
        </el-select>
        <el-button type="success" @click="openCreate">新增</el-button>
      </div>
    </template>

    <el-table :data="filteredList" v-loading="loading" border>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="role_name" label="角色名称" />
      <el-table-column prop="scope_type" label="数据范围" />
      <el-table-column prop="organization_name" label="指定组织" />
      <el-table-column label="操作" width="180">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
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

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑数据权限' : '新增数据权限'" width="520px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="角色">
          <el-select v-model="form.role" filterable style="width: 100%">
            <el-option v-for="item in roles" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="数据范围">
          <el-select v-model="form.scope_type" style="width: 100%">
            <el-option label="全部数据" value="all" />
            <el-option label="本组织" value="org" />
            <el-option label="本组织及下级" value="org_and_children" />
            <el-option label="仅本人" value="self" />
          </el-select>
        </el-form-item>
        <el-form-item label="指定组织">
          <el-select v-model="form.organization" clearable filterable style="width: 100%">
            <el-option v-for="item in organizations" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">保存</el-button>
      </template>
    </el-dialog>
  </PageContainer>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRoute } from 'vue-router'
import PageContainer from '@/components/common/PageContainer.vue'
import { fetchOrganizationList } from '@/api/system/organization'
import { fetchRoleList } from '@/api/system/role'
import { createRoleDataScope, deleteRoleDataScope, fetchRoleDataScopeList, updateRoleDataScope } from '@/api/system/rbac'
import { useCrud } from '@/composables/useCrud'

const route = useRoute()
const dialogVisible = ref(false)
const roleFilter = ref<number | undefined>()
const roles = ref<any[]>([])
const organizations = ref<any[]>([])
const { list, loading, total, currentPage, pageSize, fetchList, handleCurrentChange, handleSizeChange } = useCrud<any>(fetchRoleDataScopeList)

const form = reactive<any>({
  id: undefined,
  role: undefined,
  scope_type: 'self',
  organization: undefined,
})

const filteredList = computed(() => {
  if (!roleFilter.value) return list.value
  return list.value.filter((item: any) => item.role === roleFilter.value)
})

const loadOptions = async () => {
  const [rolePayload, organizationPayload] = await Promise.all([
    fetchRoleList().catch(() => []),
    fetchOrganizationList().catch(() => []),
  ])
  roles.value = Array.isArray(rolePayload) ? rolePayload : rolePayload?.results || []
  organizations.value = Array.isArray(organizationPayload) ? organizationPayload : organizationPayload?.results || []
}

const resetForm = () => {
  form.id = undefined
  form.role = roleFilter.value
  form.scope_type = 'self'
  form.organization = undefined
}

const openCreate = async () => {
  resetForm()
  await loadOptions()
  dialogVisible.value = true
}

const openEdit = async (row: any) => {
  form.id = row.id
  form.role = row.role
  form.scope_type = row.scope_type
  form.organization = row.organization
  await loadOptions()
  dialogVisible.value = true
}

const handleSubmit = async () => {
  const payload = {
    role: form.role,
    scope_type: form.scope_type,
    organization: form.organization || null,
  }
  if (form.id) {
    await updateRoleDataScope(form.id, payload)
    ElMessage.success('编辑成功')
  } else {
    await createRoleDataScope(payload)
    ElMessage.success('新增成功')
  }
  dialogVisible.value = false
  fetchList()
}

const handleDelete = async (row: any) => {
  await ElMessageBox.confirm(`确认删除【${row.role_name}】的数据权限吗？`, '提示')
  await deleteRoleDataScope(row.id)
  ElMessage.success('删除成功')
  fetchList()
}

onMounted(async () => {
  await Promise.all([loadOptions(), fetchList()])
  const roleQuery = Number(route.query.role)
  if (roleQuery) {
    roleFilter.value = roleQuery
  }
})
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
