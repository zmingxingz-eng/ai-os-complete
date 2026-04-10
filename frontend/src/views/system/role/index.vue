<template>
  <PageContainer title="角色管理" description="维护角色，并通过弹窗树形组件直接分配菜单和权限。">
    <template #filters>
      <div class="toolbar">
        <el-input v-model="keyword" placeholder="角色名称/编码" style="width: 240px;" />
        <el-button type="primary" @click="fetchList">查询</el-button>
        <el-button type="success" @click="openCreate">新增</el-button>
      </div>
    </template>

    <el-table :data="filteredList" v-loading="loading" border>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="角色名称" />
      <el-table-column prop="code" label="角色编码" />
      <el-table-column prop="description" label="描述" />
      <el-table-column label="操作" width="320">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
          <el-button link type="warning" @click="openAssignDialog(row)">菜单权限</el-button>
          <el-button link type="success" @click="openDataScopeDialog(row)">数据权限</el-button>
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

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑角色' : '新增角色'" width="520px">
      <el-form ref="formRef" :model="form" :rules="formRules" label-width="100px">
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="角色编码" prop="code">
          <el-input v-model="form.code" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" />
        </el-form-item>
        <el-form-item label="启用状态">
          <el-switch v-model="form.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="assignDialogVisible" title="菜单权限" width="620px">
      <div class="assign-header">当前角色：{{ assignRole?.name || '-' }}</div>
      <el-tree
        ref="assignTreeRef"
        :data="assignTree"
        node-key="node_key"
        show-checkbox
        default-expand-all
        :props="{ label: 'name', children: 'children' }"
      />
      <template #footer>
        <el-button @click="assignDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveAssignments">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="dataScopeDialogVisible" title="设置数据权限" width="520px">
      <div class="assign-header">当前角色：{{ dataScopeRole?.name || '-' }}</div>
      <el-form ref="dataScopeFormRef" :model="dataScopeForm" :rules="dataScopeRules" label-width="100px">
        <el-form-item label="数据范围" prop="scope_type">
          <el-select v-model="dataScopeForm.scope_type" style="width: 100%">
            <el-option label="全部数据" value="all" />
            <el-option label="本组织" value="org" />
            <el-option label="本组织及下级" value="org_and_children" />
            <el-option label="自定义" value="custom" />
            <el-option label="仅本人" value="self" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="dataScopeForm.scope_type === 'custom'" label="指定组织" prop="organizations">
          <el-select v-model="dataScopeForm.organizations" multiple collapse-tags collapse-tags-tooltip filterable style="width: 100%">
            <el-option v-for="item in organizations" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dataScopeDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveDataScope">保存</el-button>
      </template>
    </el-dialog>
  </PageContainer>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, reactive, ref, watch } from 'vue'
import { ElMessage, ElMessageBox, type ElForm, type ElTree, type FormRules } from 'element-plus'
import PageContainer from '@/components/common/PageContainer.vue'
import { fetchMenuList } from '@/api/system/menu'
import { fetchPermissionList } from '@/api/system/permission'
import { fetchOrganizationList } from '@/api/system/organization'
import { createRole, deleteRole, fetchRoleList, updateRole } from '@/api/system/role'
import {
  createRoleMenu,
  createRolePermission,
  createRoleDataScope,
  deleteRoleMenu,
  deleteRolePermission,
  fetchRoleDataScopeList,
  fetchRoleMenuList,
  fetchRolePermissionList,
  updateRoleDataScope,
} from '@/api/system/rbac'
import { useCrud } from '@/composables/useCrud'

const keyword = ref('')
const dialogVisible = ref(false)
const assignDialogVisible = ref(false)
const dataScopeDialogVisible = ref(false)
const assignRole = ref<any>()
const dataScopeRole = ref<any>()
const assignTreeRef = ref<InstanceType<typeof ElTree>>()
const formRef = ref<InstanceType<typeof ElForm>>()
const dataScopeFormRef = ref<InstanceType<typeof ElForm>>()
const menuBindings = ref<any[]>([])
const permissionBindings = ref<any[]>([])
const dataScopeBindings = ref<any[]>([])
const menus = ref<any[]>([])
const permissions = ref<any[]>([])
const organizations = ref<any[]>([])

const { list, loading, total, currentPage, pageSize, fetchList, handleCurrentChange, handleSizeChange } = useCrud<any>(fetchRoleList)

const form = reactive<any>({
  id: undefined,
  name: '',
  code: '',
  description: '',
  is_active: true,
})

const formRules: FormRules = {
  name: [
    { required: true, message: '请输入角色名称', trigger: 'blur' },
    { min: 2, max: 50, message: '角色名称长度为 2-50 位', trigger: 'blur' },
  ],
  code: [
    { required: true, message: '请输入角色编码', trigger: 'blur' },
    { pattern: /^[A-Za-z][A-Za-z0-9_]*$/, message: '角色编码仅支持字母、数字和下划线，且需以字母开头', trigger: 'blur' },
  ],
}

const dataScopeForm = reactive<any>({
  id: undefined,
  role: undefined,
  scope_type: 'self',
  organization: undefined,
  organizations: [] as number[],
})

const dataScopeRules: FormRules = {
  scope_type: [{ required: true, message: '请选择数据范围', trigger: 'change' }],
  organizations: [{
    validator: (_rule, value, callback) => {
      if (dataScopeForm.scope_type === 'custom' && (!value || !value.length)) {
        callback(new Error('请选择至少一个组织'))
        return
      }
      callback()
    },
    trigger: 'change',
  }],
}

const filteredList = computed(() => {
  if (!keyword.value) return list.value
  return list.value.filter((item: any) =>
    String(item.name || '').includes(keyword.value) || String(item.code || '').includes(keyword.value)
  )
})

const assignTree = computed(() => {
  const menuMap = new Map<number, any>()
  const roots: any[] = []

  menus.value.forEach((item: any) => {
    menuMap.set(item.id, {
      ...item,
      node_key: `menu-${item.id}`,
      node_type: 'menu',
      children: [],
    })
  })

  menuMap.forEach((node) => {
    if (node.parent && menuMap.has(node.parent)) {
      menuMap.get(node.parent).children.push(node)
    } else {
      roots.push(node)
    }
  })

  permissions.value.forEach((item: any) => {
    const node = {
      ...item,
      name: `${item.name} [${item.binding_type === 'api' ? '接口' : '按钮'}]`,
      node_key: `permission-${item.id}`,
      node_type: 'permission',
      children: [],
    }
    const menuId = item.menu_ids?.[0]
    if (menuId && menuMap.has(menuId)) {
      menuMap.get(menuId).children.push(node)
    } else {
      let otherNode = roots.find((current: any) => current.node_key === 'menu-other-permissions')
      if (!otherNode) {
        otherNode = {
          id: null,
          node_key: 'menu-other-permissions',
          name: '其他配置权限',
          node_type: 'virtual',
          children: [],
        }
        roots.push(otherNode)
      }
      otherNode.children.push(node)
    }
  })

  return roots
})

const currentCheckedKeys = computed(() => {
  if (!assignRole.value) return []
  const roleId = assignRole.value.id
  const menuKeys = menuBindings.value.filter((item: any) => item.role === roleId).map((item: any) => `menu-${item.menu}`)
  const permissionKeys = permissionBindings.value.filter((item: any) => item.role === roleId).map((item: any) => `permission-${item.permission}`)
  return [...menuKeys, ...permissionKeys]
})

const loadAssignData = async () => {
  const [menuPayload, permissionPayload, roleMenuPayload, rolePermissionPayload] = await Promise.all([
    fetchMenuList({ page_size: 1000 }).catch(() => []),
    fetchPermissionList({ page_size: 1000 }).catch(() => []),
    fetchRoleMenuList({ page_size: 1000 }).catch(() => []),
    fetchRolePermissionList({ page_size: 1000 }).catch(() => []),
  ])
  menus.value = Array.isArray(menuPayload) ? menuPayload : menuPayload?.results || []
  permissions.value = Array.isArray(permissionPayload) ? permissionPayload : permissionPayload?.results || []
  menuBindings.value = Array.isArray(roleMenuPayload) ? roleMenuPayload : roleMenuPayload?.results || []
  permissionBindings.value = Array.isArray(rolePermissionPayload) ? rolePermissionPayload : rolePermissionPayload?.results || []
}

const loadDataScopeOptions = async () => {
  const [organizationPayload, roleDataScopePayload] = await Promise.all([
    fetchOrganizationList({ page_size: 1000 }).catch(() => []),
    fetchRoleDataScopeList({ page_size: 1000 }).catch(() => []),
  ])
  organizations.value = Array.isArray(organizationPayload) ? organizationPayload : organizationPayload?.results || []
  dataScopeBindings.value = Array.isArray(roleDataScopePayload) ? roleDataScopePayload : roleDataScopePayload?.results || []
}

const resetForm = () => {
  form.id = undefined
  form.name = ''
  form.code = ''
  form.description = ''
  form.is_active = true
}

const openCreate = () => {
  resetForm()
  dialogVisible.value = true
  nextTick(() => formRef.value?.clearValidate())
}

const openEdit = (row: any) => {
  form.id = row.id
  form.name = row.name
  form.code = row.code
  form.description = row.description
  form.is_active = row.is_active
  dialogVisible.value = true
  nextTick(() => formRef.value?.clearValidate())
}

const handleSubmit = async () => {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  const payload = {
    name: form.name,
    code: form.code,
    description: form.description,
    is_active: form.is_active,
  }
  if (form.id) {
    await updateRole(form.id, payload)
    ElMessage.success('编辑成功')
  } else {
    await createRole(payload)
    ElMessage.success('新增成功')
  }
  dialogVisible.value = false
  fetchList()
}

const handleDelete = async (row: any) => {
  await ElMessageBox.confirm(`确认删除角色【${row.name}】吗？`, '提示')
  await deleteRole(row.id)
  ElMessage.success('删除成功')
  fetchList()
}

const openAssignDialog = async (row: any) => {
  assignRole.value = row
  await loadAssignData()
  assignDialogVisible.value = true
  await nextTick()
  assignTreeRef.value?.setCheckedKeys(currentCheckedKeys.value)
}

const openDataScopeDialog = async (row: any) => {
  dataScopeRole.value = row
  await loadDataScopeOptions()
  const currentBinding = dataScopeBindings.value.find((item: any) => item.role === row.id)
  dataScopeForm.id = currentBinding?.id
  dataScopeForm.role = row.id
  dataScopeForm.scope_type = currentBinding?.scope_type || 'self'
  dataScopeForm.organization = currentBinding?.organization
  dataScopeForm.organizations = currentBinding?.organizations || []
  dataScopeDialogVisible.value = true
  await nextTick()
  dataScopeFormRef.value?.clearValidate()
}

const handleSaveAssignments = async () => {
  if (!assignRole.value) return
  const roleId = assignRole.value.id
  const checked = new Set<string>((assignTreeRef.value?.getCheckedKeys(false) as string[]) || [])

  const currentRoleMenus = menuBindings.value.filter((item: any) => item.role === roleId)
  const currentRolePermissions = permissionBindings.value.filter((item: any) => item.role === roleId)

  const checkedMenuIds = Array.from(checked)
    .filter((item) => item.startsWith('menu-'))
    .map((item) => Number(item.replace('menu-', '')))
    .filter((id) => !Number.isNaN(id))
  const checkedPermissionIds = Array.from(checked)
    .filter((item) => item.startsWith('permission-'))
    .map((item) => Number(item.replace('permission-', '')))
    .filter((id) => !Number.isNaN(id))

  const createMenuTasks = checkedMenuIds
    .filter((id) => !currentRoleMenus.some((item: any) => item.menu === id))
    .map((menu) => createRoleMenu({ role: roleId, menu }))
  const deleteMenuTasks = currentRoleMenus
    .filter((item: any) => !checkedMenuIds.includes(item.menu))
    .map((item: any) => deleteRoleMenu(item.id))

  const createPermissionTasks = checkedPermissionIds
    .filter((id) => !currentRolePermissions.some((item: any) => item.permission === id))
    .map((permission) => createRolePermission({ role: roleId, permission }))
  const deletePermissionTasks = currentRolePermissions
    .filter((item: any) => !checkedPermissionIds.includes(item.permission))
    .map((item: any) => deleteRolePermission(item.id))

  await Promise.all([
    ...createMenuTasks,
    ...deleteMenuTasks,
    ...createPermissionTasks,
    ...deletePermissionTasks,
  ])

  ElMessage.success('分配成功')
  assignDialogVisible.value = false
}

const handleSaveDataScope = async () => {
  const valid = await dataScopeFormRef.value?.validate().catch(() => false)
  if (!valid) return
  const payload = {
    role: dataScopeForm.role,
    scope_type: dataScopeForm.scope_type,
    organization: dataScopeForm.scope_type === 'custom' ? dataScopeForm.organization || null : null,
    organizations: dataScopeForm.scope_type === 'custom' ? dataScopeForm.organizations || [] : [],
  }
  if (dataScopeForm.id) {
    await updateRoleDataScope(dataScopeForm.id, payload)
  } else {
    await createRoleDataScope(payload)
  }
  ElMessage.success('数据权限保存成功')
  dataScopeDialogVisible.value = false
  await loadDataScopeOptions()
}

onMounted(fetchList)

watch(
  () => dataScopeForm.scope_type,
  (scopeType) => {
    if (scopeType !== 'custom') {
      dataScopeForm.organization = undefined
      dataScopeForm.organizations = []
      dataScopeFormRef.value?.clearValidate(['organizations'])
    }
  }
)
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
