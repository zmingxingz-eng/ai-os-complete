import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', {
  state: () => ({
    title: 'AI OS 2.0'
  })
})
