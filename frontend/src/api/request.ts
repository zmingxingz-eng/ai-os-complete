import axios from 'axios'
import { clearAuthTokens, getRefreshToken, getToken, setToken } from '@/utils/token'

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 10000,
  withCredentials: false
})

let refreshing = false
let queue: Array<(token: string) => void> = []

const flushQueue = (token: string) => {
  queue.forEach((cb) => cb(token))
  queue = []
}

const refreshInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 10000
})

request.interceptors.request.use((config) => {
  const token = getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

request.interceptors.response.use(
  (response) => {
    const payload = response.data
    if (payload && typeof payload === 'object' && 'code' in payload) {
      return payload.data
    }
    return payload
  },
  async (error) => {
    const originalRequest = error.config
    if (error.response?.status === 401 && !originalRequest?._retry) {
      const refresh = getRefreshToken()
      if (!refresh) {
        clearAuthTokens()
        return Promise.reject(error)
      }

      if (refreshing) {
        return new Promise((resolve) => {
          queue.push((token: string) => {
            originalRequest.headers.Authorization = `Bearer ${token}`
            resolve(request(originalRequest))
          })
        })
      }

      originalRequest._retry = true
      refreshing = true
      try {
        const response = await refreshInstance.post('/system/auth/refresh-token/', { refresh })
        const access = response.data?.data?.access || response.data?.access
        if (access) {
          setToken(access)
          originalRequest.headers.Authorization = `Bearer ${access}`
          flushQueue(access)
          return request(originalRequest)
        }
      } catch (refreshError) {
        clearAuthTokens()
        return Promise.reject(refreshError)
      } finally {
        refreshing = false
      }
    }
    return Promise.reject(error)
  }
)

export default request
