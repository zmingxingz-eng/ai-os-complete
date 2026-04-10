import request from '@/api/request'

export const fetchMenuList = (params?: any) => request.get('/system/menu/', { params })
export const createMenu = (data: any) => request.post('/system/menu/', data)
export const updateMenu = (id: number, data: any) => request.put(`/system/menu/${id}/`, data)
export const deleteMenu = (id: number) => request.delete(`/system/menu/${id}/`)
