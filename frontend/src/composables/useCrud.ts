import { ref } from 'vue'

const normalizeListPayload = <T>(payload: any) => {
  if (Array.isArray(payload)) {
    return { list: payload as T[], count: payload.length, page: 1, pageSize: payload.length || 10 }
  }
  if (payload && Array.isArray(payload.results)) {
    return {
      list: payload.results as T[],
      count: Number(payload.count || 0),
      page: Number(payload.page || 1),
      pageSize: Number(payload.page_size || 10),
    }
  }
  return { list: [] as T[], count: 0, page: 1, pageSize: 10 }
}

export function useCrud<T>(loader: (params?: any) => Promise<any>) {
  const loading = ref(false)
  const list = ref<T[]>([])
  const total = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(10)

  const fetchList = async (params?: any) => {
    loading.value = true
    try {
      const payload = await loader({
        page: currentPage.value,
        page_size: pageSize.value,
        ...(params || {}),
      })
      const normalized = normalizeListPayload<T>(payload)
      list.value = normalized.list
      total.value = normalized.count
      currentPage.value = normalized.page
      pageSize.value = normalized.pageSize
    } finally {
      loading.value = false
    }
  }

  const handleCurrentChange = (page: number) => {
    currentPage.value = page
    fetchList()
  }

  const handleSizeChange = (size: number) => {
    pageSize.value = size
    currentPage.value = 1
    fetchList()
  }

  return { loading, list, total, currentPage, pageSize, fetchList, handleCurrentChange, handleSizeChange }
}
