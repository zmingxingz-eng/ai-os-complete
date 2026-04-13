<template>
  <PageContainer title="用户管理" description="维护系统账号、角色以及组织岗位隶属。">
    <template #filters>
      <div class="toolbar">
        <el-input v-model="keyword" placeholder="用户名/姓名/手机号" style="width: 260px;" />
        <el-button type="primary" @click="fetchList">查询</el-button>
        <el-button @click="handleReset">重置</el-button>
        <el-button type="success" @click="openCreate">新增</el-button>
      </div>
    </template>

    <div class="user-layout">
      <div class="user-layout__tree">
        <div class="user-layout__tree-header">
          <span>组织机构</span>
          <el-button link type="primary" @click="handleSelectOrganization()">全部用户</el-button>
        </div>
        <el-tree
          :data="organizationTree"
          node-key="id"
          highlight-current
          default-expand-all
          :props="{ label: 'name', children: 'children' }"
          @node-click="handleSelectOrganization"
        />
      </div>

      <div class="user-layout__table">
        <div class="user-layout__table-header">
          <div class="user-layout__table-title">
            当前组织：{{ currentOrganizationTitle }}
          </div>
        </div>

        <el-table :data="list" v-loading="loading" border empty-text="暂无用户数据">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="username" label="用户名" />
          <el-table-column prop="full_name" label="姓名" />
          <el-table-column prop="mobile" label="手机号" />
          <el-table-column prop="organization_name" label="隶属组织" show-overflow-tooltip />
          <el-table-column prop="position_name" label="任职岗位" show-overflow-tooltip />
          <el-table-column prop="email" label="邮箱" show-overflow-tooltip />
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'info'">{{ row.is_active ? '启用' : '停用' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="340">
            <template #default="{ row }">
              <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
              <el-button link type="warning" @click="openAssignRoles(row)">分配角色</el-button>
              <el-button link type="success" @click="openAssignOrganizations(row)">组织岗位</el-button>
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
            @current-change="onPageChange"
            @size-change="onPageSizeChange"
          />
        </div>
      </div>
    </div>

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑用户' : '新增用户'" width="560px" destroy-on-close>
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
        <el-form-item label="隶属组织" prop="organization_id">
          <el-tree-select
            v-model="form.organization_id"
            :data="organizationTree"
            node-key="id"
            check-strictly
            clearable
            filterable
            default-expand-all
            :props="{ label: 'name', children: 'children' }"
            placeholder="请选择隶属组织"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="任职岗位" prop="position_id">
          <el-select v-model="form.position_id" clearable filterable style="width: 100%">
            <el-option v-for="item in positions" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
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

    <el-dialog v-model="assignDialogVisible" title="分配角色" width="520px" destroy-on-close>
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

    <el-dialog v-model="relationDialogVisible" title="组织岗位" width="920px" destroy-on-close>
      <div class="assign-header">当前用户：{{ assignUser?.full_name || assignUser?.username || '-' }}</div>
      <div class="relation-summary-row">
        <div class="relation-summary-row__content">
          <el-alert
            v-if="activePrimaryRelation"
            class="relation-hint relation-hint--inline"
            type="info"
            :closable="false"
            :title="`当前隶属组织：${activePrimaryRelation.organization_name}${activePrimaryRelation.position_name ? ` / ${activePrimaryRelation.position_name}` : ''}`"
          />
          <el-alert
            v-else
            class="relation-hint relation-hint--inline"
            type="warning"
            :closable="false"
            title="当前隶属组织：未设置"
          />
        </div>
        <div class="relation-summary-row__action">
          <el-button type="primary" @click="openCreateRelation">新增</el-button>
        </div>
      </div>
      <el-table :data="userOrganizationRelations" border empty-text="暂无组织岗位数据">
        <el-table-column prop="organization_name" label="组织" min-width="180" />
        <el-table-column prop="position_name" label="岗位" min-width="140" />
        <el-table-column prop="duty" label="职务说明" min-width="160" />
        <el-table-column prop="relation_type" label="关系类型" width="120">
          <template #default="{ row }">
            <el-tag :type="row.relation_type === 'primary' ? 'success' : 'info'">
              {{ relationTypeLabelMap[row.relation_type] || row.relation_type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">{{ row.status === 'active' ? '有效' : '失效' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140">
          <template #default="{ row }">
            <el-button link type="primary" @click="openEditRelation(row)">编辑</el-button>
            <el-button link type="danger" @click="handleDeleteRelation(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <template v-if="relationEditorVisible">
        <el-divider>{{ relationForm.id ? '编辑组织岗位' : '新增组织岗位' }}</el-divider>

        <el-alert
          v-if="duplicateRelation"
          class="relation-hint"
          type="warning"
          :closable="false"
          :title="`组织【${duplicateRelation.organization_name}】已存在，请直接编辑原有关系。`"
        />

        <el-alert
          v-else-if="relationForm.relation_type === 'primary' && activePrimaryRelation && activePrimaryRelation.id !== relationForm.id && currentOrganizationLabel"
          class="relation-hint"
          type="info"
          :closable="false"
          :title="`保存后将把隶属组织从【${activePrimaryRelation.organization_name}】切换为【${currentOrganizationLabel}】`"
        />

        <el-form ref="relationFormRef" :model="relationForm" :rules="relationFormRules" label-width="90px" class="relation-form">
          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="组织" prop="organization">
                <el-tree-select
                  v-model="relationForm.organization"
                  :data="organizationTree"
                  node-key="id"
                  check-strictly
                  clearable
                  filterable
                  default-expand-all
                  :props="{ label: 'name', children: 'children' }"
                  placeholder="请选择组织"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="岗位">
                <el-select v-model="relationForm.position" clearable filterable style="width: 100%">
                  <el-option v-for="item in positions" :key="item.id" :label="item.name" :value="item.id" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="关系类型" prop="relation_type">
                <el-select v-model="relationForm.relation_type" style="width: 100%">
                  <el-option label="隶属" value="primary" />
                  <el-option label="兼职" value="part_time" />
                  <el-option label="借调" value="borrowed" />
                  <el-option label="临时加入" value="temporary" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="状态" prop="status">
                <el-select v-model="relationForm.status" style="width: 100%">
                  <el-option label="有效" value="active" />
                  <el-option label="失效" value="inactive" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="职务说明">
                <el-input v-model="relationForm.duty" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <div class="relation-inline-actions">
                <el-button @click="closeRelationEditor">取消</el-button>
                <el-button type="primary" @click="handleSaveRelation">保存</el-button>
              </div>
            </el-col>
          </el-row>
        </el-form>
      </template>

      <template #footer>
        <el-button @click="relationDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </PageContainer>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, reactive, ref, watch } from 'vue'
import { ElMessage, ElMessageBox, type ElForm, type ElTree, type FormRules } from 'element-plus'
import PageContainer from '@/components/common/PageContainer.vue'
import { createUser, deleteUser, fetchUsersList, updateUser } from '@/api/system/users'
import {
  createUserOrganizationRelation,
  deleteUserOrganizationRelation,
  fetchOrganizationList,
  fetchPositionList,
  fetchUserOrganizationRelationList,
  updateUserOrganizationRelation,
} from '@/api/system/organization'
import { fetchRoleList } from '@/api/system/role'
import { createUserRole, deleteUserRole, fetchUserRoleList } from '@/api/system/rbac'
import { useCrud } from '@/composables/useCrud'

const relationTypeLabelMap: Record<string, string> = {
  primary: '隶属',
  part_time: '兼职',
  borrowed: '借调',
  temporary: '临时加入',
}

const keyword = ref('')
const dialogVisible = ref(false)
const assignDialogVisible = ref(false)
const relationDialogVisible = ref(false)
const relationEditorVisible = ref(false)
const organizations = ref<any[]>([])
const positions = ref<any[]>([])
const roles = ref<any[]>([])
const userRoleBindings = ref<any[]>([])
const userOrganizationRelations = ref<any[]>([])
const assignUser = ref<any>()
const selectedOrganizationId = ref<number | undefined>()
const roleTreeRef = ref<InstanceType<typeof ElTree>>()
const formRef = ref<InstanceType<typeof ElForm>>()
const relationFormRef = ref<InstanceType<typeof ElForm>>()
const { list, loading, total, currentPage, pageSize, fetchList } = useCrud<any>(fetchUsersList)

const form = reactive<any>({
  id: undefined,
  username: '',
  full_name: '',
  mobile: '',
  email: '',
  organization_id: undefined,
  position_id: undefined,
  password: 'Admin123456',
  is_active: true,
})

const relationForm = reactive<any>({
  id: undefined,
  user: undefined,
  organization: undefined,
  position: undefined,
  relation_type: 'primary',
  duty: '',
  status: 'active',
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
    { pattern: /^1\d{10}$/, message: '请输入有效的手机号', trigger: 'blur' },
  ],
  email: [
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' },
  ],
  organization_id: [{ required: true, message: '请选择隶属组织', trigger: 'change' }],
  position_id: [{ required: true, message: '请选择任职岗位', trigger: 'change' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少 6 位', trigger: 'blur' },
  ],
}

const relationFormRules: FormRules = {
  organization: [{ required: true, message: '请选择组织', trigger: 'change' }],
  position: [{ required: true, message: '请选择任职岗位', trigger: 'change' }],
  relation_type: [{ required: true, message: '请选择关系类型', trigger: 'change' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }],
}

const activePrimaryRelation = computed(() =>
  userOrganizationRelations.value.find((item: any) => item.relation_type === 'primary' && item.status === 'active')
)

const duplicateRelation = computed(() => {
  if (!relationForm.organization) return null
  return userOrganizationRelations.value.find((item: any) =>
    item.organization === relationForm.organization && item.id !== relationForm.id
  )
})

const organizationTree = computed(() => buildTree(organizations.value))
const currentOrganizationTitle = computed(() => {
  if (!selectedOrganizationId.value) {
    return '全部用户'
  }
  const current = organizations.value.find((item: any) => item.id === selectedOrganizationId.value)
  return current?.path_name || current?.name || '全部用户'
})

const currentOrganizationLabel = computed(() => {
  if (!relationForm.organization) return ''
  const current = organizations.value.find((item: any) => item.id === relationForm.organization)
  return current?.path_name || current?.name || ''
})

const buildTree = (items: any[]) => {
  const map = new Map<number, any>()
  const roots: any[] = []
  items.forEach((item) => {
    map.set(item.id, { ...item, children: [] })
  })
  map.forEach((node) => {
    if (node.parent && map.has(node.parent)) {
      map.get(node.parent).children.push(node)
    } else {
      roots.push(node)
    }
  })
  return roots
}

const resetForm = () => {
  form.id = undefined
  form.username = ''
  form.full_name = ''
  form.mobile = ''
  form.email = ''
  form.organization_id = undefined
  form.position_id = undefined
  form.password = 'Admin123456'
  form.is_active = true
}

const resetRelationForm = () => {
  relationForm.id = undefined
  relationForm.user = assignUser.value?.id
  relationForm.organization = undefined
  relationForm.position = undefined
  relationForm.relation_type = 'primary'
  relationForm.duty = ''
  relationForm.status = 'active'
  nextTick(() => relationFormRef.value?.clearValidate())
}

const closeRelationEditor = () => {
  relationEditorVisible.value = false
  resetRelationForm()
}

const handleReset = () => {
  keyword.value = ''
  selectedOrganizationId.value = undefined
  currentPage.value = 1
  loadUsers()
}

const loadUsers = async () => {
  await fetchList({
    keyword: keyword.value || undefined,
    organization: selectedOrganizationId.value || undefined,
  })
}

const loadOrganizations = async () => {
  const payload = await fetchOrganizationList({ page_size: 1000 }).catch(() => [])
  organizations.value = Array.isArray(payload) ? payload : payload?.results || []
}

const loadPositions = async () => {
  const payload = await fetchPositionList({ page_size: 1000, status: 'active' }).catch(() => [])
  positions.value = Array.isArray(payload) ? payload : payload?.results || []
}

const handleSelectOrganization = (node?: any) => {
  selectedOrganizationId.value = node?.id
  currentPage.value = 1
  loadUsers()
}

const loadRoleOptions = async () => {
  const [rolePayload, bindingPayload] = await Promise.all([
    fetchRoleList({ page_size: 1000 }).catch(() => []),
    fetchUserRoleList({ page_size: 1000 }).catch(() => []),
  ])
  roles.value = Array.isArray(rolePayload) ? rolePayload : rolePayload?.results || []
  userRoleBindings.value = Array.isArray(bindingPayload) ? bindingPayload : bindingPayload?.results || []
}

const loadUserOrganizationRelations = async (userId: number) => {
  const payload = await fetchUserOrganizationRelationList({ page_size: 1000, user: userId }).catch(() => [])
  const rows = Array.isArray(payload) ? payload : payload?.results || []
  userOrganizationRelations.value = [...rows].sort((left: any, right: any) => {
    const leftWeight = left.relation_type === 'primary' ? 0 : 1
    const rightWeight = right.relation_type === 'primary' ? 0 : 1
    if (leftWeight !== rightWeight) {
      return leftWeight - rightWeight
    }
    return Number(left.id || 0) - Number(right.id || 0)
  })
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
  await Promise.all([loadOrganizations(), loadPositions()])
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
  form.organization_id = row.organization
  form.position_id = row.position
  form.password = ''
  form.is_active = row.is_active
  await Promise.all([loadOrganizations(), loadPositions()])
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

const openAssignOrganizations = async (row: any) => {
  assignUser.value = row
  await Promise.all([loadOrganizations(), loadPositions(), loadUserOrganizationRelations(row.id)])
  relationDialogVisible.value = true
  relationEditorVisible.value = false
  resetRelationForm()
}

const openCreateRelation = () => {
  relationEditorVisible.value = true
  resetRelationForm()
}

const openEditRelation = (row: any) => {
  relationEditorVisible.value = true
  relationForm.id = row.id
  relationForm.user = row.user
  relationForm.organization = row.organization
  relationForm.position = row.position
  relationForm.relation_type = row.relation_type
  relationForm.duty = row.duty || ''
  relationForm.status = row.status
  nextTick(() => relationFormRef.value?.clearValidate())
}

const handleSubmit = async () => {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  const payload = {
    username: form.username,
    full_name: form.full_name,
    mobile: form.mobile,
    email: form.email,
    organization_id: form.organization_id,
    position_id: form.position_id,
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
  loadUsers()
}

const handleDelete = async (row: any) => {
  await ElMessageBox.confirm(`确认删除用户【${row.username}】吗？`, '提示')
  await deleteUser(row.id)
  ElMessage.success('删除成功')
  loadUsers()
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

const handleSaveRelation = async () => {
  if (!assignUser.value) return
  const valid = await relationFormRef.value?.validate().catch(() => false)
  if (!valid) return
  if (duplicateRelation.value) {
    ElMessage.warning(`组织【${duplicateRelation.value.organization_name}】已存在，请直接编辑该关系。`)
    return
  }
  const payload = {
    user: assignUser.value.id,
    organization: relationForm.organization,
    position: relationForm.position || null,
    relation_type: relationForm.relation_type,
    duty: relationForm.duty,
    status: relationForm.status,
  }
  if (relationForm.id) {
    await updateUserOrganizationRelation(relationForm.id, payload)
    ElMessage.success('组织岗位更新成功')
  } else {
    await createUserOrganizationRelation(payload)
    ElMessage.success('组织岗位新增成功')
  }
  await loadUserOrganizationRelations(assignUser.value.id)
  await loadUsers()
  relationEditorVisible.value = false
  resetRelationForm()
}

const handleDeleteRelation = async (row: any) => {
  await ElMessageBox.confirm(`确认删除组织关系【${row.organization_name}】吗？`, '提示')
  await deleteUserOrganizationRelation(row.id)
  ElMessage.success('删除成功')
  if (assignUser.value) {
    await loadUserOrganizationRelations(assignUser.value.id)
    await loadUsers()
  }
}

onMounted(async () => {
  await loadOrganizations()
  await loadUsers()
})

watch(
  () => relationForm.relation_type,
  (value) => {
    if (value !== 'primary' || !activePrimaryRelation.value || activePrimaryRelation.value.id === relationForm.id) {
      return
    }
    ElMessage.info(`当前隶属组织是【${activePrimaryRelation.value.organization_name}】，保存后将自动切换为新的隶属组织。`)
  }
)

const onPageChange = (page: number) => {
  currentPage.value = page
  loadUsers()
}

const onPageSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
  loadUsers()
}
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

.user-layout {
  display: grid;
  grid-template-columns: 260px minmax(0, 1fr);
  gap: 16px;
}

.user-layout__tree,
.user-layout__table {
  min-width: 0;
}

.user-layout__tree {
  border: 1px solid var(--el-border-color-light);
  border-radius: 5px;
  padding: 16px 12px;
}

.user-layout__tree-header,
.user-layout__table-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.user-layout__table-title {
  color: var(--el-text-color-regular);
  font-weight: 500;
}

.assign-header {
  margin-bottom: 12px;
  color: var(--el-text-color-regular);
}

.relation-form {
  margin-top: 16px;
}

.relation-summary-row {
  margin-bottom: 12px;
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 12px;
  align-items: center;
}

.relation-summary-row__content {
  min-width: 0;
}

.relation-summary-row__action {
  display: flex;
  align-items: flex-start;
}

.relation-toolbar {
  margin-bottom: 12px;
  display: flex;
  justify-content: flex-end;
}

.relation-inline-actions {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  display: flex;
  gap: 12px;
}

.relation-hint {
  margin-bottom: 0;
}

.relation-hint--inline {
  margin-bottom: 0;
}

</style>
