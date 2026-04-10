import type { App, DirectiveBinding } from 'vue'
import { usePermissionStore } from '@/store/permission'

function hasPermission(code: string) {
  const store = usePermissionStore()
  return store.permissions.includes(code)
}

const permissionDirective = {
  mounted(el: HTMLElement, binding: DirectiveBinding<string>) {
    const code = binding.value
    if (code && !hasPermission(code)) {
      el.parentNode && el.parentNode.removeChild(el)
    }
  }
}

export function setupPermissionDirective(app: App) {
  app.directive('permission', permissionDirective)
}
