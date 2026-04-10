import { storeToRefs } from 'pinia'
import { usePermissionStore } from '@/store/permission'

export function usePermission() {
  const permissionStore = usePermissionStore()
  const { permissions } = storeToRefs(permissionStore)

  const hasPermission = (code: string) => permissions.value.includes(code)

  return { hasPermission }
}
