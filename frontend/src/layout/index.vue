<template>
  <el-container class="layout-shell">
    <el-aside :width="collapsed ? '64px' : '220px'" class="layout-shell__aside">
      <div class="layout-shell__brand">
        <el-button text @click="collapsed = !collapsed">{{ collapsed ? '展开' : '收起' }}</el-button>
        <span v-if="!collapsed">AI OS 2.0</span>
      </div>

      <UserSessionCard v-if="!collapsed" :session-info="sessionInfo" :data-scopes="dataScopes" />

      <el-menu
        :default-active="activeMenu"
        :collapse="collapsed"
        router
        class="layout-shell__menu"
      >
        <template v-for="menu in sidebarMenus" :key="menu.id ?? menu.path">
          <el-sub-menu v-if="menu.children?.length" :index="menu.path || menu.code || String(menu.id)">
            <template #title>{{ menu.name }}</template>
            <el-menu-item v-for="child in menu.children" :key="child.path" :index="child.path">
              {{ child.name }}
            </el-menu-item>
          </el-sub-menu>
          <el-menu-item v-else :index="menu.path">{{ menu.name }}</el-menu-item>
        </template>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="layout-shell__header">
        <div />
        <div class="layout-shell__header-actions">
          <el-dropdown @command="handleUserCommand">
            <span class="layout-shell__user">{{ sessionInfo.full_name || sessionInfo.username || '管理员' }}</span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                <el-dropdown-item command="logout">退出系统</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="layout-shell__main">
        <el-card shadow="never" class="app-card layout-shell__tabs">
          <el-tabs
            :model-value="activeTab"
            type="card"
            @tab-change="handleTabChange"
            @tab-remove="handleTabRemove"
          >
            <el-tab-pane
              v-for="tab in visitedTabs"
              :key="tab.path"
              :name="tab.path"
              :label="tab.title"
              :closable="tab.closable"
            />
          </el-tabs>
        </el-card>

        <router-view :key="routerViewKey" />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { usePermissionStore } from '@/store/permission'
import { fetchSessionInfo, logoutApi } from '@/api/auth'
import { clearAuthTokens } from '@/utils/token'
import UserSessionCard from './components/UserSessionCard.vue'

const permissionStore = usePermissionStore()
const { menus, dataScopes } = storeToRefs(permissionStore)
const route = useRoute()
const router = useRouter()
const sessionInfo = ref<Record<string, any>>({})
const collapsed = ref(false)
const reloadSeed = ref(0)
const visitedTabs = ref<Array<{ path: string; title: string; closable: boolean }>>([])

const fallbackMenus = [
  { id: 'dashboard', name: '系统首页', path: '/system/dashboard', parent: null, menu_type: 'menu', visible: true, sort: 0 },
  { id: 'users', name: '用户管理', path: '/system/users', parent: null, menu_type: 'menu', visible: true, sort: 10 },
  { id: 'organization', name: '组织管理', path: '/system/organization', parent: null, menu_type: 'menu', visible: true, sort: 20 },
  { id: 'role', name: '角色管理', path: '/system/role', parent: null, menu_type: 'menu', visible: true, sort: 30 },
  { id: 'menu', name: '菜单管理', path: '/system/menu', parent: null, menu_type: 'menu', visible: true, sort: 40 },
]

const sourceMenus = computed(() => (menus.value?.length ? menus.value : fallbackMenus))
const activeMenu = computed(() => route.path)
const activeTab = computed(() => route.path)
const routerViewKey = computed(() => `${route.fullPath}-${reloadSeed.value}`)

const sidebarMenus = computed(() => {
  const map = new Map<string | number, any>()
  const roots: any[] = []

  const normalizedMenus = (sourceMenus.value || [])
    .filter((item: any) => item && item.visible !== false && ['directory', 'menu', undefined].includes(item.menu_type))
    .sort((left: any, right: any) => {
      const sortDiff = Number(left.sort || 0) - Number(right.sort || 0)
      return sortDiff !== 0 ? sortDiff : Number(left.id || 0) - Number(right.id || 0)
    })

  normalizedMenus.forEach((item: any) => map.set(item.id ?? item.path, { ...item, children: [] }))
  normalizedMenus.forEach((item: any) => {
    const current = map.get(item.id ?? item.path)
    const parentKey = item.parent
    if (parentKey && map.has(parentKey)) {
      map.get(parentKey).children.push(current)
    } else {
      roots.push(current)
    }
  })

  return roots
    .filter((item: any) => item.menu_type === 'directory' || item.path || item.children?.length)
    .map((item: any) => ({
      ...item,
      children: (item.children || []).filter((child: any) => child.path || child.children?.length),
    }))
})

const ensureTab = () => {
  const path = route.path
  const title = String(route.meta.title || '未命名页面')
  const existing = visitedTabs.value.find((item) => item.path === path)
  if (existing) {
    existing.title = title
    return
  }
  visitedTabs.value.push({ path, title, closable: path !== '/system/dashboard' })
}

const handleTabChange = (path: string | number) => {
  if (typeof path === 'string' && path !== route.path) {
    router.push(path)
  }
}

const handleTabRemove = (path: string | number) => {
  if (typeof path !== 'string') return
  const target = visitedTabs.value.find((item) => item.path === path)
  if (!target?.closable) return
  visitedTabs.value = visitedTabs.value.filter((item) => item.path !== path)
  if (route.path === path) {
    const nextTab = visitedTabs.value[visitedTabs.value.length - 1] || { path: '/system/dashboard' }
    router.push(nextTab.path)
  }
}

const handleUserCommand = async (command: string) => {
  if (command === 'profile') {
    ElMessage.info('个人中心骨架待补充')
    return
  }
  await logoutApi().catch(() => undefined)
  clearAuthTokens()
  permissionStore.setMenus([])
  permissionStore.setPermissions([])
  permissionStore.setDataScopes([])
  permissionStore.setDynamicRoutesReady(false)
  router.push('/login')
}

watch(() => route.path, ensureTab, { immediate: true })

onMounted(async () => {
  sessionInfo.value = await fetchSessionInfo().catch(() => ({}))
})
</script>

<style scoped>
.layout-shell {
  min-height: 100vh;
}

.layout-shell__aside {
  border-right: 1px solid var(--el-border-color-light);
  background: #fff;
  transition: width 0.2s ease;
}

.layout-shell__brand {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 60px;
  padding: 0 12px;
  border-bottom: 1px solid var(--el-border-color-light);
  font-weight: 600;
}

.layout-shell__menu {
  border-right: none;
}

.layout-shell__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 1px solid var(--el-border-color-light);
}

.layout-shell__header-actions {
  margin-left: auto;
}

.layout-shell__user {
  cursor: pointer;
  font-weight: 600;
}

.layout-shell__main {
  padding: 16px;
  background: var(--app-bg);
}

.layout-shell__tabs {
  margin-bottom: 16px;
}

:deep(.el-card),
:deep(.el-input__wrapper),
:deep(.el-button),
:deep(.el-dialog),
:deep(.el-tabs__item.is-top:nth-child(2)),
:deep(.el-tabs__item.is-top:last-child),
:deep(.el-tabs--card > .el-tabs__header .el-tabs__item) {
  border-radius: var(--app-radius);
}
</style>
