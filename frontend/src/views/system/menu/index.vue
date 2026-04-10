<template>
  <PageContainer title="菜单管理" description="使用树形结构统一维护目录、菜单和菜单下的权限。未关联菜单的权限统一归属到“其他配置权限”。">
    <template #filters>
      <div class="toolbar">
        <el-input v-model="keyword" placeholder="菜单名称/权限名称/编码" style="width: 280px;" />
        <el-button type="primary" @click="loadAll">查询</el-button>
        <el-button type="success" @click="openCreateMenu()">新增目录/菜单</el-button>
        <el-button type="warning" @click="openCreatePermission()">新增权限</el-button>
      </div>
    </template>

    <el-table :data="treeData" v-loading="loading" border row-key="node_key" default-expand-all :tree-props="{ children: 'children' }">
      <el-table-column prop="name" label="名称" min-width="220" />
      <el-table-column prop="display_type" label="类型" width="120" />
      <el-table-column prop="code" label="编码" min-width="180" />
      <el-table-column prop="path" label="路由/权限" min-width="180" />
      <el-table-column prop="component" label="组件路径" min-width="180" />
      <el-table-column prop="content_type_label" label="业务模型" min-width="160" />
      <el-table-column label="操作" width="320">
        <template #default="{ row }">
          <template v-if="row.node_type === 'menu'">
            <el-button link type="primary" @click="openCreateMenu(row)">新增下级菜单</el-button>
            <el-button link type="warning" @click="openCreatePermission(row)">新增权限</el-button>
            <el-button link type="primary" @click="openEditMenu(row)">编辑</el-button>
            <el-button link type="danger" @click="handleDeleteMenu(row)">删除</el-button>
          </template>
          <template v-else-if="row.node_type === 'permission'">
            <el-button link type="primary" @click="openEditPermission(row)">编辑</el-button>
            <el-button link type="danger" @click="handleDeletePermission(row)">删除</el-button>
          </template>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination-bar">
      <el-pagination
        background
        layout="total, sizes, prev, pager, next"
        :total="paginationTotal"
        :current-page="currentPage"
        :page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        @current-change="handleCurrentChange"
        @size-change="handleSizeChange"
      />
    </div>

    <el-dialog v-model="menuDialogVisible" :title="menuForm.id ? '编辑菜单' : '新增菜单'" width="620px">
      <el-form ref="menuFormRef" :model="menuForm" :rules="menuRules" label-width="100px">
        <el-form-item label="菜单名称" prop="name">
          <el-input v-model="menuForm.name" />
        </el-form-item>
        <el-form-item label="菜单编码" prop="code">
          <el-input v-model="menuForm.code" />
        </el-form-item>
        <el-form-item label="菜单类型" prop="menu_type">
          <el-select v-model="menuForm.menu_type" style="width: 100%;">
            <el-option label="目录" value="directory" />
            <el-option label="菜单" value="menu" />
          </el-select>
        </el-form-item>
        <el-form-item label="上级菜单">
          <el-select v-model="menuForm.parent" clearable style="width: 100%;">
            <el-option v-for="item in menuParentOptions" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="路由地址" prop="path">
          <el-input v-model="menuForm.path" />
        </el-form-item>
        <el-form-item v-if="menuForm.menu_type === 'menu'" label="组件路径" prop="component">
          <el-input v-model="menuForm.component" />
        </el-form-item>
        <el-form-item label="图标">
          <el-input v-model="menuForm.icon" />
        </el-form-item>
        <el-form-item label="业务模型">
          <el-select v-model="menuForm.content_type" clearable filterable style="width: 100%;">
            <el-option v-for="item in contentTypes" :key="item.id" :label="item.label" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="menuForm.sort" :min="0" />
        </el-form-item>
        <el-form-item label="左侧可见">
          <el-switch v-model="menuForm.visible" />
        </el-form-item>
        <el-form-item label="启用状态">
          <el-switch v-model="menuForm.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="menuDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveMenu">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="permissionDialogVisible" :title="permissionForm.id ? '编辑权限' : '新增权限'" width="620px">
      <el-form ref="permissionFormRef" :model="permissionForm" :rules="permissionRules" label-width="100px">
        <el-form-item label="权限名称" prop="name">
          <el-input v-model="permissionForm.name" />
        </el-form-item>
        <el-form-item label="Codename" prop="codename">
          <el-input v-model="permissionForm.codename" />
        </el-form-item>
        <el-form-item label="业务模型" prop="content_type">
          <el-select v-model="permissionForm.content_type" filterable style="width: 100%;">
            <el-option v-for="item in contentTypes" :key="item.id" :label="item.label" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="归属菜单">
          <el-select v-model="permissionForm.menu" clearable style="width: 100%;">
            <el-option label="其他配置权限" :value="undefined" />
            <el-option v-for="item in permissionMenuOptions" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="绑定类型" prop="perm_type">
          <el-select v-model="permissionForm.perm_type" style="width: 100%;">
            <el-option label="按钮" value="button" />
            <el-option label="接口" value="api" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="permissionForm.description" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="permissionDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSavePermission">保存</el-button>
      </template>
    </el-dialog>
  </PageContainer>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox, type ElForm, type FormRules } from 'element-plus'
import PageContainer from '@/components/common/PageContainer.vue'
import { createMenu, deleteMenu, fetchMenuList, updateMenu } from '@/api/system/menu'
import {
  createPermission,
  deletePermission,
  fetchPermissionContentTypes,
  fetchPermissionList,
  updatePermission,
} from '@/api/system/permission'

const loading = ref(false)
const keyword = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const menuDialogVisible = ref(false)
const permissionDialogVisible = ref(false)
const menuFormRef = ref<InstanceType<typeof ElForm>>()
const permissionFormRef = ref<InstanceType<typeof ElForm>>()
const menus = ref<any[]>([])
const permissions = ref<any[]>([])
const contentTypes = ref<any[]>([])

const OTHER_PERMISSION_NODE_KEY = '__other_permissions__'

const menuForm = reactive<any>({
  id: undefined,
  name: '',
  code: '',
  menu_type: 'menu',
  parent: undefined,
  path: '',
  component: '',
  icon: '',
  content_type: undefined,
  sort: 0,
  visible: true,
  is_active: true,
})

const menuRules: FormRules = {
  name: [
    { required: true, message: '请输入菜单名称', trigger: 'blur' },
    { min: 2, max: 50, message: '菜单名称长度为 2-50 位', trigger: 'blur' },
  ],
  code: [
    { required: true, message: '请输入菜单编码', trigger: 'blur' },
    { pattern: /^[A-Za-z][A-Za-z0-9_.]*$/, message: '菜单编码仅支持字母、数字、下划线和点，且需以字母开头', trigger: 'blur' },
  ],
  menu_type: [{ required: true, message: '请选择菜单类型', trigger: 'change' }],
  path: [{
    validator: (_rule, value, callback) => {
      if (menuForm.menu_type === 'menu' && !value) {
        callback(new Error('请输入路由地址'))
        return
      }
      callback()
    },
    trigger: 'blur',
  }],
  component: [{
    validator: (_rule, value, callback) => {
      if (menuForm.menu_type === 'menu' && !value) {
        callback(new Error('请输入组件路径'))
        return
      }
      callback()
    },
    trigger: 'blur',
  }],
}

const permissionForm = reactive<any>({
  id: undefined,
  name: '',
  codename: '',
  content_type: undefined,
  menu: undefined,
  perm_type: 'button',
  description: '',
})

const permissionRules: FormRules = {
  name: [
    { required: true, message: '请输入权限名称', trigger: 'blur' },
    { min: 2, max: 50, message: '权限名称长度为 2-50 位', trigger: 'blur' },
  ],
  codename: [
    { required: true, message: '请输入 Codename', trigger: 'blur' },
    { pattern: /^[a-z][a-z0-9_]*$/, message: 'Codename 仅支持小写字母、数字和下划线，且需以字母开头', trigger: 'blur' },
  ],
  content_type: [{ required: true, message: '请选择业务模型', trigger: 'change' }],
  perm_type: [{ required: true, message: '请选择绑定类型', trigger: 'change' }],
}

const menuParentOptions = computed(() =>
  menus.value.filter((item: any) => item.id !== menuForm.id)
)

const permissionMenuOptions = computed(() =>
  menus.value.filter((item: any) => item.menu_type === 'menu')
)

const filteredMenus = computed(() => {
  if (!keyword.value) return menus.value
  return menus.value.filter((item: any) =>
    [item.name, item.code, item.path].some((value) => String(value || '').includes(keyword.value))
  )
})

const filteredPermissions = computed(() => {
  if (!keyword.value) return permissions.value
  return permissions.value.filter((item: any) =>
    [item.name, item.code, item.codename, item.menu_name].some((value) => String(value || '').includes(keyword.value))
  )
})

const filteredTreeRoots = computed(() => {
  const menuMap = new Map<number, any>()
  const roots: any[] = []

  filteredMenus.value.forEach((item: any) => {
    menuMap.set(item.id, {
      ...item,
      node_key: `menu-${item.id}`,
      node_type: 'menu',
      display_type: item.menu_type === 'directory' ? '目录' : '菜单',
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

  filteredPermissions.value.forEach((item: any) => {
    const permissionNode = {
      ...item,
      id: item.id,
      node_key: `permission-${item.id}`,
      node_type: 'permission',
      display_type: item.binding_type === 'api' ? '接口权限' : '按钮权限',
      path: item.code,
      component: '',
      content_type_label: `${item.app_label}.${item.model}`,
      children: [],
    }
    const boundMenuId = item.menu_ids?.[0]
    if (boundMenuId && menuMap.has(boundMenuId)) {
      menuMap.get(boundMenuId).children.push(permissionNode)
      return
    }
    let otherNode = roots.find((item: any) => item.node_key === OTHER_PERMISSION_NODE_KEY)
    if (!otherNode) {
      otherNode = {
        id: null,
        node_key: OTHER_PERMISSION_NODE_KEY,
        node_type: 'menu',
        name: '其他配置权限',
        code: 'system.other_permissions',
        display_type: '目录',
        path: '',
        component: '',
        parent: null,
        content_type_label: '',
        children: [],
      }
      roots.push(otherNode)
    }
    otherNode.children.push(permissionNode)
  })

  return roots
})

const treeData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  const roots = filteredTreeRoots.value
  if (roots.length === 1 && roots[0]?.display_type === '目录') {
    const root = roots[0]
    return [
      {
        ...root,
        children: (root.children || []).slice(start, end),
      },
    ]
  }
  return roots.slice(start, end)
})

const paginationTotal = computed(() => {
  const roots = filteredTreeRoots.value
  if (roots.length === 1 && roots[0]?.display_type === '目录') {
    return roots[0]?.children?.length || 0
  }
  return roots.length
})

const loadAll = async () => {
  loading.value = true
  try {
    const [menuPayload, permissionPayload, contentTypePayload] = await Promise.all([
      fetchMenuList({ page_size: 1000 }).catch(() => []),
      fetchPermissionList({ page_size: 1000 }).catch(() => []),
      fetchPermissionContentTypes().catch(() => []),
    ])
    menus.value = Array.isArray(menuPayload) ? menuPayload : menuPayload?.results || []
    permissions.value = Array.isArray(permissionPayload) ? permissionPayload : permissionPayload?.results || []
    contentTypes.value = Array.isArray(contentTypePayload) ? contentTypePayload : []
    currentPage.value = 1
  } finally {
    loading.value = false
  }
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
}

const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
}

const resetMenuForm = () => {
  menuForm.id = undefined
  menuForm.name = ''
  menuForm.code = ''
  menuForm.menu_type = 'menu'
  menuForm.parent = undefined
  menuForm.path = ''
  menuForm.component = ''
  menuForm.icon = ''
  menuForm.content_type = undefined
  menuForm.sort = 0
  menuForm.visible = true
  menuForm.is_active = true
}

const resetPermissionForm = () => {
  permissionForm.id = undefined
  permissionForm.name = ''
  permissionForm.codename = ''
  permissionForm.content_type = undefined
  permissionForm.menu = undefined
  permissionForm.perm_type = 'button'
  permissionForm.description = ''
}

const openCreateMenu = (parentRow?: any) => {
  resetMenuForm()
  if (parentRow?.node_type === 'menu' && parentRow.id) {
    menuForm.parent = parentRow.id
  }
  menuDialogVisible.value = true
  nextTick(() => menuFormRef.value?.clearValidate())
}

const openEditMenu = (row: any) => {
  menuForm.id = row.id
  menuForm.name = row.name
  menuForm.code = row.code
  menuForm.menu_type = row.menu_type
  menuForm.parent = row.parent
  menuForm.path = row.path
  menuForm.component = row.component
  menuForm.icon = row.icon
  menuForm.content_type = row.content_type
  menuForm.sort = row.sort
  menuForm.visible = row.visible
  menuForm.is_active = row.is_active
  menuDialogVisible.value = true
  nextTick(() => menuFormRef.value?.clearValidate())
}

const handleSaveMenu = async () => {
  const valid = await menuFormRef.value?.validate().catch(() => false)
  if (!valid) return
  const payload = {
    name: menuForm.name,
    code: menuForm.code,
    menu_type: menuForm.menu_type,
    parent: menuForm.parent || null,
    path: menuForm.path,
    component: menuForm.component,
    icon: menuForm.icon,
    content_type: menuForm.content_type || null,
    sort: menuForm.sort,
    visible: menuForm.visible,
    is_active: menuForm.is_active,
  }
  if (menuForm.id) {
    await updateMenu(menuForm.id, payload)
    ElMessage.success('菜单编辑成功')
  } else {
    await createMenu(payload)
    ElMessage.success('菜单新增成功')
  }
  menuDialogVisible.value = false
  loadAll()
}

const handleDeleteMenu = async (row: any) => {
  await ElMessageBox.confirm(`确认删除菜单【${row.name}】吗？`, '提示')
  await deleteMenu(row.id)
  ElMessage.success('菜单删除成功')
  loadAll()
}

const openCreatePermission = (menuRow?: any) => {
  resetPermissionForm()
  if (menuRow?.node_type === 'menu' && menuRow.id) {
    permissionForm.menu = menuRow.id
    permissionForm.content_type = menuRow.content_type
  }
  permissionDialogVisible.value = true
  nextTick(() => permissionFormRef.value?.clearValidate())
}

const openEditPermission = (row: any) => {
  permissionForm.id = row.id
  permissionForm.name = row.name
  permissionForm.codename = row.codename
  permissionForm.content_type = row.content_type
  permissionForm.menu = row.menu_ids?.[0]
  permissionForm.perm_type = row.binding_type || 'button'
  permissionForm.description = ''
  permissionDialogVisible.value = true
  nextTick(() => permissionFormRef.value?.clearValidate())
}

const handleSavePermission = async () => {
  const valid = await permissionFormRef.value?.validate().catch(() => false)
  if (!valid) return
  const payload = {
    name: permissionForm.name,
    codename: permissionForm.codename,
    content_type: permissionForm.content_type,
    menu: permissionForm.menu || null,
    perm_type: permissionForm.perm_type,
    description: permissionForm.description,
  }
  if (permissionForm.id) {
    await updatePermission(permissionForm.id, payload)
    ElMessage.success('权限编辑成功')
  } else {
    await createPermission(payload)
    ElMessage.success('权限新增成功')
  }
  permissionDialogVisible.value = false
  loadAll()
}

const handleDeletePermission = async (row: any) => {
  await ElMessageBox.confirm(`确认删除权限【${row.name}】吗？`, '提示')
  await deletePermission(row.id)
  ElMessage.success('权限删除成功')
  loadAll()
}

onMounted(loadAll)
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
