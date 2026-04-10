<template>
  <PageContainer title="用户管理" description="维护系统账号、组织归属与基础资料。">
    <template #filters>
      <div class="toolbar">
        <el-input v-model="keyword" placeholder="用户名/姓名/手机号" style="width: 260px;" />
        <el-button type="primary" @click="fetchList">查询</el-button>
        <el-button type="success" @click="openCreate">新增</el-button>
      </div>
    </template>

    <el-table :data="filteredList" v-loading="loading" border>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="username" label="用户名" />
      <el-table-column prop="full_name" label="姓名" />
      <el-table-column prop="mobile" label="手机号" />
      <el-table-column prop="organization_name" label="组织" />
      <el-table-column prop="email" label="邮箱" />
      <el-table-column label="操作" width="260">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
          <el-button link type="warning" @click="openAssignRoles(row)">分配角色</el-button>
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

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑用户' : '新增用户'" width="560px">
      <el-form ref="formRef" :model="form" :rules="formRules" label-width="90px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" />
        </el-form-item>
        <el-form-item label="姓名" prop="full_name">
          <el-input v-model="form.full_name" />
        </el-form-item>
        <el-form-item label="手机号" prop="mobile">
          <el-input v-model="form.mobile" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" />
        </el-form-item>
        <el-form-item label="组织" prop="organization">
          <el-select v-model="form.organization" clearable style="width: 100%">
            <el-option v-for="item in organizations" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="岗位" prop="position_name">
          <el-input v-model="form.position_name" />
        </el-form-item>
        <el-form-item v-if="!form.id" label="密码" prop="password">
          <el-input v-model="form.password" type="password" show-password />
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="form.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="assignDialogVisible" title="分配角色" width="520px">
      <div class="assign-header">当前用户：{{ assignUser?.full_name || assignUser?.username || '-' }}</div>
      <el-tree
        ref="roleTreeRef"
        :data="roleTree"
        node-key="id"
        show-checkbox
        default-expand-all
        :props="{ label: 'name', children: 'children' }"
      />
      <template #footer>
        <el-button @click="assignDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveRoles">保存</el-button>
      </template>
    </el-dialog>
  </PageContainer>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox, type ElForm, type ElTree, type FormRules } from 'element-plus'
import PageContainer from '@/components/common/PageContainer.vue'
import { createUser, deleteUser, fetchUsersList, updateUser } from '@/api/system/users'
import { fetchOrganizationList } from '@/api/system/organization'
import { fetchRoleList } from '@/api/system/role'
import { createUserRole, deleteUserRole, fetchUserRoleList } from '@/api/system/rbac'
import { useCrud } from '@/composables/useCrud'

const keyword = ref('')
const dialogVisible = ref(false)
const assignDialogVisible = ref(false)
const organizations = ref<any[]>([])
const roles = ref<any[]>([])
const userRoleBindings = ref<any[]>([])
const assignUser = ref<any>()
const roleTreeRef = ref<InstanceType<typeof ElTree>>()
const formRef = ref<InstanceType<typeof ElForm>>()
const { list, loading, total, currentPage, pageSize, fetchList, handleCurrentChange, handleSizeChange } = useCrud<any>(fetchUsersList)
const filteredList = computed(() => {
  if (!keyword.value) return list.value
  return list.value.filter((item: any) =>
    [item.username, item.full_name, item.mobile].some((value) => String(value || '').includes(keyword.value))
  )
})

const form = reactive<any>({
  id: undefined,
  username: '',
  full_name: '',
  mobile: '',
  email: '',
  organization: undefined,
  position_name: '',
  password: 'Admin123456',
  is_active: true,
})

const formRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 50, message: '用户名长度为 2-50 位', trigger: 'blur' },
  ],
  full_name: [
    { required: true, message: '请输入姓名', trigger: 'blur' },
    { min: 2, max: 50, message: '姓名长度为 2-50 位', trigger: 'blur' },
  ],
  mobile: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1\\d{10}$/, message: '请输入有效的手机号', trigger: 'blur' },
  ],
  email: [
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' },
  ],
  organization: [
    { required: true, message: '请选择组织', trigger: 'change' },
  ],
  position_name: [
    { required: true, message: '请输入岗位', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少 6 位', trigger: 'blur' },
  ],
}

const resetForm = () => {
  form.id = undefined
  form.username = ''
  form.full_name = ''
  form.mobile = ''
  form.email = ''
  form.organization = undefined
  form.position_name = ''
  form.password = 'Admin123456'
  form.is_active = true
}

const loadOrganizations = async () => {
  const payload = await fetchOrganizationList().catch(() => [])
  organizations.value = Array.isArray(payload) ? payload : payload?.results || []
}

const loadRoleOptions = async () => {
  const [rolePayload, bindingPayload] = await Promise.all([
    fetchRoleList({ page_size: 1000 }).catch(() => []),
    fetchUserRoleList({ page_size: 1000 }).catch(() => []),
  ])
  roles.value = Array.isArray(rolePayload) ? rolePayload : rolePayload?.results || []
  userRoleBindings.value = Array.isArray(bindingPayload) ? bindingPayload : bindingPayload?.results || []
}

const roleTree = computed(() => roles.value.map((item: any) => ({ ...item, children: [] })))

const currentCheckedRoleIds = computed(() => {
  if (!assignUser.value) return []
  return userRoleBindings.value
    .filter((item: any) => item.user === assignUser.value.id)
    .map((item: any) => item.role)
})

const openCreate = async () => {
  resetForm()
  await loadOrganizations()
  dialogVisible.value = true
  await nextTick()
  formRef.value?.clearValidate()
}

const openEdit = async (row: any) => {
  form.id = row.id
  form.username = row.username
  form.full_name = row.full_name
  form.mobile = row.mobile
  form.email = row.email
  form.organization = row.organization
  form.position_name = row.position_name
  form.password = ''
  form.is_active = row.is_active
  await loadOrganizations()
  dialogVisible.value = true
  await nextTick()
  formRef.value?.clearValidate()
}

const openAssignRoles = async (row: any) => {
  assignUser.value = row
  await loadRoleOptions()
  assignDialogVisible.value = true
  await nextTick()
  roleTreeRef.value?.setCheckedKeys(currentCheckedRoleIds.value)
}

const handleSubmit = async () => {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  const payload = {
    username: form.username,
    full_name: form.full_name,
    mobile: form.mobile,
    email: form.email,
    organization: form.organization || null,
    position_name: form.position_name,
    is_active: form.is_active,
    ...(form.password ? { password: form.password } : {}),
  }
  if (form.id) {
    await updateUser(form.id, payload)
    ElMessage.success('编辑成功')
  } else {
    await createUser(payload)
    ElMessage.success('新增成功')
  }
  dialogVisible.value = false
  fetchList()
}

const handleDelete = async (row: any) => {
  await ElMessageBox.confirm(`确认删除用户【${row.username}】吗？`, '提示')
  await deleteUser(row.id)
  ElMessage.success('删除成功')
  fetchList()
}

const handleSaveRoles = async () => {
  if (!assignUser.value) return
  const userId = assignUser.value.id
  const checkedRoleIds = ((roleTreeRef.value?.getCheckedKeys(false) as number[]) || []).map((item) => Number(item))
  const currentBindings = userRoleBindings.value.filter((item: any) => item.user === userId)

  const createTasks = checkedRoleIds
    .filter((roleId) => !currentBindings.some((item: any) => item.role === roleId))
    .map((role) => createUserRole({ user: userId, role }))

  const deleteTasks = currentBindings
    .filter((item: any) => !checkedRoleIds.includes(item.role))
    .map((item: any) => deleteUserRole(item.id))

  await Promise.all([...createTasks, ...deleteTasks])
  ElMessage.success('角色分配成功')
  assignDialogVisible.value = false
  await loadRoleOptions()
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

.assign-header {
  margin-bottom: 12px;
  color: var(--el-text-color-regular);
}
</style>
