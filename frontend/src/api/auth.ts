import request from '@/api/request'

export const loginApi = (data: { username: string; password: string }) =>
  request.post('/system/auth/login/', data)

export const logoutApi = () => request.post('/system/auth/logout/')

export const fetchMe = () => request.get('/system/auth/me/')

export const fetchMyMenus = () => request.get('/system/auth/my-menus/')

export const fetchMyPermissions = () => request.get('/system/auth/my-permissions/')

export const fetchMyDataScopes = () => request.get('/system/auth/my-data-scopes/')

export const fetchSessionInfo = () => request.get('/system/auth/session-info/')

export const refreshTokenApi = (refresh: string) =>
  request.post('/system/auth/refresh-token/', { refresh })
