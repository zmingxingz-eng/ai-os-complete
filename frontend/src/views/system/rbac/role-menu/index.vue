<template>
  <PageContainer title="角色菜单绑定" description="按角色勾选可访问菜单，菜单按树结构维护。">
    <template #filters>
      <div class="toolbar">
        <el-select v-model="selectedRoleId" filterable placeholder="选择角色" style="width: 260px" @change="handleRoleChange">
          <el-option v-for="item in roles" :key="item.id" :label="item.name" :value="item.id" />
        </el-select>
        <el-button type="primary" :disabled="!selectedRoleId" @click="openAssign">菜单分配</el-button>
      </div>
    </template>

    <el-table :data="filteredList" v-loading="loading" border>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="role_name" label="角色名称" />
      <el-table-column prop="menu_name" label="菜单名称" />
      <el-table-column prop="menu_path" label="菜单路径" />
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

    <el-dialog v-model="dialogVisible" title="菜单分配" width="560px">
      <div class="assign-header">当前角色：{{ currentRoleName || '未选择' }}</div>
      <el-tree
        ref="treeRef"
        :data="menuTree"
        node-key="id"
        show-checkbox
        default-expand-all
        :props="{ label: 'name', children: 'children' }"
      />
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :disabled="!selectedRoleId" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </PageContainer>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox, type ElTree } from 'element-plus'
import { useRoute } from 'vue-router'
import PageContainer from '@/components/common/PageContainer.vue'
import { fetchMenuList } from '@/api/system/menu'
import { fetchRoleList } from '@/api/system/role'
import { createRoleMenu, deleteRoleMenu, fetchRoleMenuList } from '@/api/system/rbac'
import { useCrud } from '@/composables/useCrud'

const dialogVisible = ref(false)
const selectedRoleId = ref<number | undefined>()
const route = useRoute()
const roles = ref<any[]>([])
const menus = ref<any[]>([])
const treeRef = ref<InstanceType<typeof ElTree>>()
const { list, loading, total, currentPage, pageSize, fetchList, handleCurrentChange, handleSizeChange } = useCrud<any>(fetchRoleMenuList)

const currentRoleName = computed(
  () => roles.value.find((item) => item.id === selectedRoleId.value)?.name || ''
)

const filteredList = computed(() => {
  if (!selectedRoleId.value) return list.value
  return list.value.filter((item: any) => item.role === selectedRoleId.value)
})

const menuTree = computed(() => {
  const nodeMap = new Map<number, any>()
  const roots: any[] = []
  menus.value.forEach((item: any) => {
    nodeMap.set(item.id, { ...item, children: [] })
  })
  nodeMap.forEach((node) => {
    if (node.parent && nodeMap.has(node.parent)) {
      nodeMap.get(node.parent).children.push(node)
    } else {
      roots.push(node)
    }
  })
  return roots
})

const currentCheckedMenuIds = computed(() =>
  list.value.filter((item: any) => item.role === selectedRoleId.value).map((item: any) => item.menu)
)

const loadOptions = async () => {
  const [rolePayload, menuPayload] = await Promise.all([
    fetchRoleList().catch(() => []),
    fetchMenuList().catch(() => []),
  ])
  roles.value = Array.isArray(rolePayload) ? rolePayload : rolePayload?.results || []
  menus.value = Array.isArray(menuPayload) ? menuPayload : menuPayload?.results || []
}

const handleRoleChange = async () => {
  if (selectedRoleId.value) {
    await fetchList()
  }
}

const openAssign = async () => {
  await loadOptions()
  dialogVisible.value = true
  await nextTick()
  treeRef.value?.setCheckedKeys(currentCheckedMenuIds.value)
}

const handleSave = async () => {
  const checked = new Set<number>(treeRef.value?.getCheckedKeys(false) as number[] || [])
  const currentBindings = list.value.filter((item: any) => item.role === selectedRoleId.value)
  const currentMenuIds = new Set<number>(currentBindings.map((item: any) => item.menu))

  const createTasks = Array.from(checked)
    .filter((menuId) => !currentMenuIds.has(menuId))
    .map((menuId) => createRoleMenu({ role: selectedRoleId.value, menu: menuId }))
  const deleteTasks = currentBindings
    .filter((item: any) => !checked.has(item.menu))
    .map((item: any) => deleteRoleMenu(item.id))

  await Promise.all([...createTasks, ...deleteTasks])
  ElMessage.success('保存成功')
  dialogVisible.value = false
  fetchList()
}

const handleDelete = async (row: any) => {
  await ElMessageBox.confirm(`确认删除绑定【${row.role_name} - ${row.menu_name}】吗？`, '提示')
  await deleteRoleMenu(row.id)
  ElMessage.success('删除成功')
  fetchList()
}

onMounted(async () => {
  await Promise.all([loadOptions(), fetchList()])
  const roleQuery = Number(route.query.role)
  if (roleQuery) {
    selectedRoleId.value = roleQuery
  }
})
</script>

<style scoped>
.toolbar {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.assign-header {
  margin-bottom: 12px;
  color: var(--el-text-color-regular);
}

.pagination-bar {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>
