import request from '@/api/request'

export const fetchOrganizationList = (params?: any) => request.get('/system/organization/', { params })
export const createOrganization = (data: any) => request.post('/system/organization/', data)
export const updateOrganization = (id: number, data: any) => request.put(`/system/organization/${id}/`, data)
export const deleteOrganization = (id: number) => request.delete(`/system/organization/${id}/`)
