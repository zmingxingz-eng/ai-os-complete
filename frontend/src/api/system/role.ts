import request from '@/api/request'

export const fetchRoleList = (params?: any) => request.get('/system/role/', { params })
export const createRole = (data: any) => request.post('/system/role/', data)
export const updateRole = (id: number, data: any) => request.put(`/system/role/${id}/`, data)
export const deleteRole = (id: number) => request.delete(`/system/role/${id}/`)
