<template>
  <el-container class="layout-shell">
    <el-aside :width="collapsed ? '64px' : '250px'" class="layout-shell__aside">
      <div class="layout-shell__brand">
        <span class="layout-shell__brand-logo">A</span>
        <span v-if="!collapsed" class="layout-shell__brand-text">AI OS Admin</span>
      </div>

      <el-scrollbar class="layout-shell__menu-scroll">
        <el-menu
          :default-active="activeMenu"
          :default-openeds="defaultOpeneds"
          :collapse="collapsed"
          :collapse-transition="false"
          :unique-opened="false"
          router
          background-color="transparent"
          text-color="var(--app-sidebar-text)"
          active-text-color="var(--app-sidebar-text-active)"
          class="layout-shell__menu"
        >
          <template v-for="menu in sidebarMenus" :key="menu.id ?? menu.path">
            <el-sub-menu v-if="menu.children?.length" :index="menu.path || menu.code || String(menu.id)">
              <template #title>
                <el-icon><component :is="resolveMenuIcon(menu)" /></el-icon>
                <span>{{ menu.name }}</span>
              </template>
              <el-menu-item v-for="child in menu.children" :key="child.path || child.id" :index="child.path">
                <el-icon><component :is="resolveMenuIcon(child)" /></el-icon>
                {{ child.name }}
              </el-menu-item>
            </el-sub-menu>
            <el-menu-item v-else :index="menu.path">
              <el-icon><component :is="resolveMenuIcon(menu)" /></el-icon>
              <span>{{ menu.name }}</span>
            </el-menu-item>
          </template>
        </el-menu>
      </el-scrollbar>
    </el-aside>

    <el-container>
      <el-header class="layout-shell__header">
        <div class="layout-shell__header-left">
          <el-button text circle class="layout-shell__header-icon-button" @click="collapsed = !collapsed">
            <el-icon><component :is="collapsed ? Expand : Fold" /></el-icon>
          </el-button>
          <el-breadcrumb separator="/" class="layout-shell__breadcrumb">
            <el-breadcrumb-item @click="router.push('/system/dashboard')">系统管理</el-breadcrumb-item>
            <el-breadcrumb-item>{{ route.meta.title || '当前页面' }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="layout-shell__header-actions">
          <el-tooltip content="全屏" placement="bottom">
            <el-button text circle class="layout-shell__header-icon-button" @click="toggleFullscreen">
              <el-icon><FullScreen /></el-icon>
            </el-button>
          </el-tooltip>
          <el-tooltip content="消息" placement="bottom">
            <el-badge :value="messageList.length" class="layout-shell__message-badge">
              <el-button text circle class="layout-shell__header-icon-button" @click="messageDrawerVisible = true">
                <el-icon><Bell /></el-icon>
              </el-button>
            </el-badge>
          </el-tooltip>
          <el-dropdown @command="handleUserCommand">
            <div class="layout-shell__user">
              <el-avatar :size="32">{{ (sessionInfo.full_name || sessionInfo.username || 'A').slice(0, 1) }}</el-avatar>
              <span>{{ sessionInfo.full_name || sessionInfo.username || '管理员' }}</span>
            </div>
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
        <router-view />
      </el-main>

      <el-footer class="layout-shell__footer">
        <span>Copyright (C) AI OS 2026</span>
        <span>AdminLTE3 风格布局</span>
      </el-footer>
    </el-container>
  </el-container>

  <el-drawer
    v-model="messageDrawerVisible"
    title="消息中心"
    direction="rtl"
    size="320px"
  >
    <el-empty v-if="!messageList.length" description="暂无消息" />
    <el-timeline v-else>
      <el-timeline-item
        v-for="item in messageList"
        :key="item.title"
        :timestamp="item.time"
        placement="top"
      >
        <el-card shadow="never">
          <div class="layout-shell__message-title">{{ item.title }}</div>
          <div class="layout-shell__message-text">{{ item.text }}</div>
        </el-card>
      </el-timeline-item>
    </el-timeline>
  </el-drawer>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { storeToRefs } from 'pinia'
import { useRoute, useRouter } from 'vue-router'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import { Bell, Expand, Fold, FullScreen, HomeFilled, House, OfficeBuilding, Postcard, Setting, User, UserFilled } from '@element-plus/icons-vue'
import { usePermissionStore } from '@/store/permission'
import { fetchSessionInfo, logoutApi } from '@/api/auth'
import { clearAuthTokens } from '@/utils/token'

const permissionStore = usePermissionStore()
const { menus } = storeToRefs(permissionStore)
const route = useRoute()
const router = useRouter()
const sessionInfo = ref<Record<string, any>>({})
const collapsed = ref(false)
const messageDrawerVisible = ref(false)
const messageList = [
  { title: '系统通知', text: '系统管理模块已完成当前阶段优化。', time: '刚刚' },
  { title: '待办提醒', text: '可以继续完善个人中心编辑与消息中心。', time: '今天' },
]

const fallbackMenus = [
  { id: 'dashboard', name: '系统首页', code: 'system.dashboard', path: '/system/dashboard', parent: null, menu_type: 'menu', visible: true, sort: 0, icon: 'House' },
  { id: 'system', name: '系统管理', code: 'system', path: '/system', parent: null, menu_type: 'directory', visible: true, sort: 1, icon: 'Setting' },
  { id: 'users', name: '用户管理', code: 'system.users', path: '/system/users', parent: 'system', menu_type: 'menu', visible: true, sort: 10, icon: 'User' },
  { id: 'organization', name: '组织管理', code: 'system.organization', path: '/system/organization', parent: 'system', menu_type: 'menu', visible: true, sort: 20, icon: 'OfficeBuilding' },
  { id: 'position', name: '岗位管理', code: 'system.position', path: '/system/position', parent: 'system', menu_type: 'menu', visible: true, sort: 30, icon: 'Postcard' },
  { id: 'role', name: '角色管理', code: 'system.role', path: '/system/role', parent: 'system', menu_type: 'menu', visible: true, sort: 40, icon: 'UserFilled' },
  { id: 'menu', name: '菜单管理', code: 'system.menu', path: '/system/menu', parent: 'system', menu_type: 'menu', visible: true, sort: 50, icon: 'Setting' },
]

const sourceMenus = computed(() => (menus.value?.length ? menus.value : fallbackMenus))
const activeMenu = computed(() => route.path)
const defaultOpeneds = computed(() =>
  collapsed.value
    ? []
    : sidebarMenus.value.filter((item: any) => item.children?.length).map((item: any) => item.path || item.code || String(item.id))
)
const normalizedMenus = computed(() => {
  const items = (sourceMenus.value || []).map((item: any) => ({ ...item }))
  const systemRoot =
    items.find((item: any) => item.code === 'system' || item.path === '/system') ||
    { id: 'system', name: '系统管理', code: 'system', path: '/system', menu_type: 'directory', visible: true, sort: 1, icon: 'Setting', parent: null }

  const ensureIcon = (item: any) => {
    if (item.icon) {
      return item
    }
    const key = String(item.code || item.path || '')
    if (key.includes('dashboard')) return { ...item, icon: 'House' }
    if (key.includes('users')) return { ...item, icon: 'User' }
    if (key.includes('organization')) return { ...item, icon: 'OfficeBuilding' }
    if (key.includes('role')) return { ...item, icon: 'UserFilled' }
    return { ...item, icon: 'Setting' }
  }

  const hasSystemRoot = items.some((item: any) => (item.id ?? item.path) === (systemRoot.id ?? systemRoot.path))
  const normalized = hasSystemRoot ? items : [systemRoot, ...items]

  return normalized.map((item: any) => {
    const current = ensureIcon(item)
    if (current.code === 'system.dashboard' || current.path === '/system/dashboard') {
      return { ...current, parent: null, sort: 0 }
    }
    if (
      current.code === 'system.users' ||
      current.code === 'system.organization' ||
      current.code === 'system.position' ||
      current.code === 'system.role' ||
      current.code === 'system.menu'
    ) {
      return { ...current, parent: systemRoot.id ?? systemRoot.path }
    }
    if (current.code === 'system' || current.path === '/system') {
      return { ...current, parent: null, menu_type: 'directory', icon: current.icon || 'Setting' }
    }
    return current
  })
})

const sidebarMenus = computed(() => {
  const map = new Map<string | number, any>()
  const roots: any[] = []

  const visibleMenus = (normalizedMenus.value || [])
    .filter((item: any) => item && item.visible !== false && ['directory', 'menu', undefined].includes(item.menu_type))
    .sort((left: any, right: any) => {
      const sortDiff = Number(left.sort || 0) - Number(right.sort || 0)
      return sortDiff !== 0 ? sortDiff : Number(left.id || 0) - Number(right.id || 0)
    })

  visibleMenus.forEach((item: any) => map.set(item.id ?? item.path, { ...item, children: [] }))
  visibleMenus.forEach((item: any) => {
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

const resolveMenuIcon = (menu: any) => {
  const iconMap = ElementPlusIconsVue as Record<string, any>
  if (menu.icon && iconMap[menu.icon]) {
    return iconMap[menu.icon]
  }
  const key = String(menu.code || menu.path || '')
  if (key.includes('dashboard')) return HomeFilled
  if (key.includes('users')) return User
  if (key.includes('organization')) return OfficeBuilding
  if (key.includes('position')) return Postcard
  if (key.includes('role')) return UserFilled
  if (key.includes('menu')) return Setting
  return Setting
}

const handleUserCommand = async (command: string) => {
  if (command === 'profile') {
    router.push('/profile')
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

const toggleFullscreen = async () => {
  if (!document.fullscreenElement) {
    await document.documentElement.requestFullscreen().catch(() => undefined)
    return
  }
  await document.exitFullscreen().catch(() => undefined)
}

onMounted(async () => {
  sessionInfo.value = await fetchSessionInfo().catch(() => ({}))
})
</script>

<style scoped>
.layout-shell {
  min-height: 100vh;
}

.layout-shell__aside {
  background: var(--app-sidebar-bg);
  color: var(--app-sidebar-text);
  transition: width 0.2s ease;
}

.layout-shell__brand {
  display: flex;
  align-items: center;
  gap: 12px;
  min-height: 57px;
  padding: 0 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  color: #fff;
}

.layout-shell__brand-logo {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border-radius: 5px;
  background: var(--app-primary);
  font-weight: 700;
}

.layout-shell__brand-text {
  font-size: 18px;
  font-weight: 600;
}

.layout-shell__menu-scroll {
  height: calc(100vh - 57px);
}

.layout-shell__menu {
  border-right: none;
  padding-top: 12px;
}

:deep(.layout-shell__menu .el-menu-item),
:deep(.layout-shell__menu .el-sub-menu__title) {
  min-height: 42px;
  border-radius: 5px;
  margin: 4px 12px;
}

:deep(.layout-shell__menu .el-menu-item:hover),
:deep(.layout-shell__menu .el-sub-menu__title:hover) {
  background: var(--app-sidebar-hover);
}

:deep(.layout-shell__menu .el-sub-menu.is-active > .el-sub-menu__title) {
  color: var(--app-sidebar-text-active);
}

:deep(.layout-shell__menu .el-menu-item.is-active) {
  background: var(--app-primary);
  color: #fff;
}

.layout-shell__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--app-header-bg);
  border-bottom: 1px solid var(--el-border-color-light);
}

.layout-shell__header-left,
.layout-shell__header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.layout-shell__header-icon-button {
  font-size: 18px;
}

.layout-shell__breadcrumb {
  margin-left: 8px;
}

:deep(.layout-shell__breadcrumb .el-breadcrumb__item:first-child .el-breadcrumb__inner) {
  cursor: pointer;
}

.layout-shell__message-badge {
  display: inline-flex;
}

.layout-shell__message-title {
  font-weight: 600;
}

.layout-shell__message-text {
  margin-top: 4px;
  color: var(--el-text-color-secondary);
  font-size: 12px;
  line-height: 1.4;
}

.layout-shell__user {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  font-weight: 600;
}

:deep(.el-drawer__body) {
  padding-top: 8px;
}

.layout-shell__main {
  padding: 20px;
  background: var(--app-bg);
}

.layout-shell__footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--app-footer-bg);
  border-top: 1px solid var(--el-border-color-light);
  color: var(--el-text-color-secondary);
  font-size: 13px;
}
</style>
