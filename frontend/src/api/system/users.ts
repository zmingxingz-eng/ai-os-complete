import request from '@/api/request'

export const fetchUsersList = (params?: any) => request.get('/system/users/', { params })
export const createUser = (data: any) => request.post('/system/users/', data)
export const updateUser = (id: number, data: any) => request.put(`/system/users/${id}/`, data)
export const deleteUser = (id: number) => request.delete(`/system/users/${id}/`)
