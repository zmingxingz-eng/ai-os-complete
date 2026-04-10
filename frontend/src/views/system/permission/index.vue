<template>
  <PageContainer title="权限管理" description="权限统一归属于菜单管理维护；当前页面仅用于查看归属关系和未归属权限。">
    <template #filters>
      <div class="toolbar">
        <el-input v-model="keyword" placeholder="权限名称/编码" style="width: 260px;" />
        <el-select v-model="menuFilter" clearable placeholder="所属菜单" style="width: 220px;">
          <el-option v-for="item in menus" :key="item.id" :label="item.name" :value="item.id" />
        </el-select>
        <el-button type="primary" @click="fetchList">查询</el-button>
        <el-button type="success" @click="goToMenuPage">前往菜单管理</el-button>
      </div>
    </template>

    <el-alert type="info" show-icon :closable="false">
      <template #title>菜单与权限归属规则</template>
      <div class="rule-list">
        <div>1. 目录只负责业务分组，不直接承载权限。</div>
        <div>2. 菜单是业务入口，按钮权限和接口权限都归属于菜单。</div>
        <div>3. 权限作为菜单的下一级节点，在菜单管理中统一新增、编辑、删除。</div>
        <div>4. 暂未归属菜单的权限，统一归属到“其他配置权限”。</div>
        <div>5. 角色分配时，在角色管理弹窗中统一勾选菜单和权限。</div>
      </div>
    </el-alert>

    <div class="summary-grid">
      <el-card shadow="never">
        <div class="summary-title">已归属权限</div>
        <div class="summary-value">{{ boundCount }}</div>
      </el-card>
      <el-card shadow="never">
        <div class="summary-title">未归属权限</div>
        <div class="summary-value">{{ orphanCount }}</div>
      </el-card>
      <el-card shadow="never">
        <div class="summary-title">菜单数量</div>
        <div class="summary-value">{{ menus.length }}</div>
      </el-card>
    </div>

    <el-table :data="filteredList" v-loading="loading" border>
      <el-table-column prop="name" label="权限名称" min-width="180" />
      <el-table-column prop="code" label="权限编码" min-width="200" />
      <el-table-column prop="binding_type" label="类型" width="120">
        <template #default="{ row }">
          {{ row.binding_type === 'api' ? '接口权限' : '按钮权限' }}
        </template>
      </el-table-column>
      <el-table-column prop="app_label" label="应用" width="120" />
      <el-table-column prop="model" label="模型" width="140" />
      <el-table-column prop="menu_name" label="所属菜单" min-width="180">
        <template #default="{ row }">
          {{ row.menu_name || '其他配置权限' }}
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
  </PageContainer>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import PageContainer from '@/components/common/PageContainer.vue'
import { fetchPermissionList } from '@/api/system/permission'
import { fetchMenuList } from '@/api/system/menu'
import { useCrud } from '@/composables/useCrud'

const router = useRouter()
const keyword = ref('')
const menuFilter = ref<number | undefined>()
const menus = ref<any[]>([])

const { list, loading, total, currentPage, pageSize, fetchList, handleCurrentChange, handleSizeChange } = useCrud<any>(
  fetchPermissionList
)

const filteredList = computed(() =>
  list.value.filter((item: any) => {
    const matchKeyword =
      !keyword.value ||
      [item.name, item.code, item.codename].some((value) => String(value || '').includes(keyword.value))
    const matchMenu = !menuFilter.value || (item.menu_ids || []).includes(menuFilter.value)
    return matchKeyword && matchMenu
  })
)

const boundCount = computed(() => list.value.filter((item: any) => (item.menu_ids || []).length > 0).length)
const orphanCount = computed(() => list.value.filter((item: any) => !(item.menu_ids || []).length).length)

const loadMenus = async () => {
  const payload = await fetchMenuList({ page_size: 1000 }).catch(() => [])
  menus.value = (Array.isArray(payload) ? payload : payload?.results || []).filter((item: any) => item.menu_type === 'menu')
}

const goToMenuPage = () => {
  router.push('/system/menu')
}

onMounted(async () => {
  await loadMenus()
  fetchList()
})
</script>

<style scoped>
.toolbar {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.rule-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-top: 8px;
}

.summary-grid {
  margin: 16px 0;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.summary-title {
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.summary-value {
  margin-top: 8px;
  font-size: 24px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.pagination-bar {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>
