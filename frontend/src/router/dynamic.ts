import type { Router, RouteRecordRaw } from 'vue-router'
import ButtonDemoPage from '@/views/system/permission/button-demo/index.vue'

const componentMap: Record<string, any> = {
  '/system/permission/button-demo': ButtonDemoPage
}

export function buildDynamicRoutesFromMenus(menus: any[]): RouteRecordRaw[] {
  return (menus || [])
    .filter((item) => item.path && componentMap[item.path])
    .map((item) => ({
      path: item.path,
      component: componentMap[item.path],
      meta: { title: item.name || item.path, dynamic: true }
    }))
}

export function registerDynamicRoutes(router: Router, menus: any[]) {
  const routes = buildDynamicRoutesFromMenus(menus)
  routes.forEach((route) => {
    if (!router.hasRoute(route.path)) {
      router.addRoute('/', route)
    }
  })
}
