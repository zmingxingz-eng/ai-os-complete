import { defineStore } from 'pinia'

export const usePermissionStore = defineStore('permission', {
  state: () => ({
    menus: [] as any[],
    permissions: [] as string[],
    dataScopes: [] as any[],
    dynamicRoutesReady: false
  }),
  actions: {
    setMenus(menus: any[]) {
      this.menus = (menus || []).filter((item: any) => item && item.visible !== false)
    },
    setPermissions(permissionList: any[]) {
      this.permissions = (permissionList || []).map((item: any) =>
        typeof item === 'string' ? item : item.code || `${item.app_label}.${item.codename}`
      )
    },
    setDataScopes(scopes: any[]) {
      this.dataScopes = scopes
    },
    setDynamicRoutesReady(flag: boolean) {
      this.dynamicRoutesReady = flag
    }
  }
})
