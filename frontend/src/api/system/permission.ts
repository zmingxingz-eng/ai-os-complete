import request from '@/api/request'

export const fetchPermissionList = (params?: any) => request.get('/system/permission/', { params })
export const fetchPermissionContentTypes = () => request.get('/system/permission/content-types/')
export const createPermission = (data: any) => request.post('/system/permission/', data)
export const updatePermission = (id: number, data: any) => request.put(`/system/permission/${id}/`, data)
export const deletePermission = (id: number) => request.delete(`/system/permission/${id}/`)
