<template>
  <PageContainer title="角色权限绑定" description="按业务菜单筛选权限，再分配给角色。">
    <template #filters>
      <div class="toolbar">
        <el-select v-model="menuFilter" clearable placeholder="按菜单筛选" style="width: 240px">
          <el-option v-for="item in menus" :key="item.id" :label="item.name" :value="item.id" />
        </el-select>
        <el-button type="success" @click="openCreate">新增绑定</el-button>
      </div>
    </template>
    <el-table :data="filteredList" v-loading="loading" border>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="role_name" label="角色名称" />
      <el-table-column prop="permission_name" label="权限名称" />
      <el-table-column prop="permission_code" label="权限编码" />
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

    <el-dialog v-model="dialogVisible" title="新增角色权限绑定" width="520px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="角色">
          <el-select v-model="form.role" filterable style="width: 100%">
            <el-option v-for="item in roles" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="业务菜单">
          <el-select v-model="form.menu" clearable filterable style="width: 100%">
            <el-option v-for="item in menus" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="权限">
          <el-select v-model="form.permission" filterable style="width: 100%">
            <el-option
              v-for="item in permissionOptions"
              :key="item.id"
              :label="`${item.name} / ${item.code}`"
              :value="item.id"
            />
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
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRoute } from 'vue-router'
import PageContainer from '@/components/common/PageContainer.vue'
import { fetchMenuList } from '@/api/system/menu'
import { fetchPermissionList } from '@/api/system/permission'
import { fetchRoleList } from '@/api/system/role'
import { createRolePermission, deleteRolePermission, fetchRolePermissionList } from '@/api/system/rbac'
import { useCrud } from '@/composables/useCrud'

const dialogVisible = ref(false)
const menuFilter = ref<number | undefined>()
const route = useRoute()
const roles = ref<any[]>([])
const permissions = ref<any[]>([])
const menus = ref<any[]>([])
const { list, loading, total, currentPage, pageSize, fetchList, handleCurrentChange, handleSizeChange } = useCrud<any>(fetchRolePermissionList)

const form = reactive<any>({
  role: undefined,
  menu: undefined,
  permission: undefined,
})

const permissionMenuMap = computed(() => {
  const map = new Map<number, number[]>()
  permissions.value.forEach((item: any) => {
    map.set(item.id, item.menu_ids || [])
  })
  return map
})

const filteredList = computed(() => {
  if (!menuFilter.value) return list.value
  const currentMenuId = Number(menuFilter.value)
  return list.value.filter((item: any) => {
    const menuIds = permissionMenuMap.value.get(item.permission) || []
    return menuIds.includes(currentMenuId)
  })
})

const permissionOptions = computed(() => {
  if (!form.menu) return permissions.value
  return permissions.value.filter((item: any) => (item.menu_ids || []).includes(form.menu))
})

const loadOptions = async () => {
  const [rolePayload, permissionPayload, menuPayload] = await Promise.all([
    fetchRoleList().catch(() => []),
    fetchPermissionList().catch(() => []),
    fetchMenuList().catch(() => []),
  ])
  roles.value = Array.isArray(rolePayload) ? rolePayload : rolePayload?.results || []
  permissions.value = Array.isArray(permissionPayload) ? permissionPayload : permissionPayload?.results || []
  menus.value = (Array.isArray(menuPayload) ? menuPayload : menuPayload?.results || []).filter((item: any) => item.menu_type !== 'directory')
}

const openCreate = async () => {
  form.role = undefined
  form.menu = undefined
  form.permission = undefined
  await loadOptions()
  dialogVisible.value = true
}

const handleCreate = async () => {
  await createRolePermission({ role: form.role, permission: form.permission })
  ElMessage.success('绑定成功')
  dialogVisible.value = false
  fetchList()
}

const handleDelete = async (row: any) => {
  await ElMessageBox.confirm(`确认删除绑定【${row.role_name} - ${row.permission_name}】吗？`, '提示')
  await deleteRolePermission(row.id)
  ElMessage.success('删除成功')
  fetchList()
}

onMounted(async () => {
  await Promise.all([loadOptions(), fetchList()])
  const roleQuery = Number(route.query.role)
  if (roleQuery) {
    form.role = roleQuery
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
