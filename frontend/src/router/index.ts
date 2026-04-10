import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import Layout from '@/layout/index.vue'
import { isLoggedIn } from '@/utils/auth'
import DashboardPage from '@/views/system/dashboard/index.vue'
import UsersPage from '@/views/system/users/index.vue'
import OrganizationPage from '@/views/system/organization/index.vue'
import RolePage from '@/views/system/role/index.vue'
import ButtonDemoPage from '@/views/system/permission/button-demo/index.vue'
import MenuPage from '@/views/system/menu/index.vue'
import ConfigCenterPage from '@/views/system/config-center/index.vue'
import AuditLogPage from '@/views/system/audit-log/index.vue'
import LoginPage from '@/views/login/index.vue'

const routes: RouteRecordRaw[] = [
  { path: '/login', component: LoginPage, meta: { public: true, title: '登录' } },
  {
    path: '/',
    component: Layout,
    children: [
      { path: '', redirect: '/system/dashboard' },
      { path: '/system/dashboard', component: DashboardPage, meta: { title: '系统首页' } },
      { path: '/system/users', component: UsersPage, meta: { title: '用户管理' } },
      { path: '/system/organization', component: OrganizationPage, meta: { title: '组织管理' } },
      { path: '/system/role', component: RolePage, meta: { title: '角色管理' } },
      { path: '/system/permission/button-demo', component: ButtonDemoPage, meta: { title: '按钮权限示例' } },
      { path: '/system/menu', component: MenuPage, meta: { title: '菜单管理' } },
      { path: '/system/config-center', component: ConfigCenterPage, meta: { title: '配置中心' } },
      { path: '/system/audit-log', component: AuditLogPage, meta: { title: '审计日志' } }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, _from, next) => {
  if (to.meta.public) {
    next()
    return
  }
  if (!isLoggedIn()) {
    next('/login')
    return
  }
  next()
})

export default router
