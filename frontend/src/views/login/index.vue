<template>
  <div class="login-page">
    <el-card shadow="never" class="login-card app-card">
      <div class="login-card__title">AI OS Admin</div>
      <div class="login-card__subtitle">使用系统账号登录后台管理平台</div>
      <el-form :model="form" label-position="top">
        <el-form-item label="账号">
          <el-input v-model="form.username" placeholder="请输入账号" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" show-password placeholder="请输入密码" />
        </el-form-item>
        <el-form-item class="login-card__actions">
          <el-button type="primary" :loading="loading" @click="handleLogin">登录系统</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { loginApi, fetchMyMenus, fetchMyPermissions, fetchMyDataScopes } from '@/api/auth'
import { usePermissionStore } from '@/store/permission'
import { setRefreshToken, setToken } from '@/utils/token'
import { registerDynamicRoutes } from '@/router/dynamic'

const router = useRouter()
const permissionStore = usePermissionStore()
const loading = ref(false)
const form = reactive({
  username: 'admin',
  password: 'Admin123456'
})

const handleLogin = async () => {
  loading.value = true
  try {
    const loginResult = await loginApi(form)
    if (loginResult?.access) setToken(loginResult.access)
    if (loginResult?.refresh) setRefreshToken(loginResult.refresh)

    const [menus, permissions, dataScopes] = await Promise.all([
      fetchMyMenus().catch(() => []),
      fetchMyPermissions().catch(() => []),
      fetchMyDataScopes().catch(() => [])
    ])

    permissionStore.setMenus(menus || [])
    permissionStore.setPermissions(permissions || [])
    permissionStore.setDataScopes(dataScopes || [])
    registerDynamicRoutes(router, menus || [])
    permissionStore.setDynamicRoutesReady(true)
    router.push('/system/dashboard')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: #e9ecef;
}

.login-card {
  width: 420px;
}

.login-card__title {
  font-size: 24px;
  font-weight: 600;
  text-align: center;
}

.login-card__subtitle {
  margin: 8px 0 24px;
  text-align: center;
  color: var(--el-text-color-secondary);
}

.login-card__actions :deep(.el-form-item__content) {
  justify-content: center;
}

.login-card__actions .el-button {
  width: 100%;
}
</style>
