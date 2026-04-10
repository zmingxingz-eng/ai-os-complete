const ACCESS_TOKEN_KEY = 'AI_OS_ACCESS_TOKEN'
const REFRESH_TOKEN_KEY = 'AI_OS_REFRESH_TOKEN'

export const getToken = () => localStorage.getItem(ACCESS_TOKEN_KEY) || ''
export const setToken = (token: string) => localStorage.setItem(ACCESS_TOKEN_KEY, token)
export const removeToken = () => localStorage.removeItem(ACCESS_TOKEN_KEY)

export const getRefreshToken = () => localStorage.getItem(REFRESH_TOKEN_KEY) || ''
export const setRefreshToken = (token: string) => localStorage.setItem(REFRESH_TOKEN_KEY, token)
export const removeRefreshToken = () => localStorage.removeItem(REFRESH_TOKEN_KEY)

export const clearAuthTokens = () => {
  removeToken()
  removeRefreshToken()
}
