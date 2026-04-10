<template>
  <div class="login-page">
    <div class="login-card">
      <h2>AI OS 2.0 登录</h2>
      <el-form :model="form" label-width="70px">
        <el-form-item label="账号">
          <el-input v-model="form.username" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="handleLogin">登录</el-button>
        </el-form-item>
      </el-form>
    </div>
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
