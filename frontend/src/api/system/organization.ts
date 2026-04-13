import request from '@/api/request'

export const fetchOrganizationList = (params?: any) => request.get('/system/organization/', { params })
export const createOrganization = (data: any) => request.post('/system/organization/', data)
export const updateOrganization = (id: number, data: any) => request.put(`/system/organization/${id}/`, data)
export const deleteOrganization = (id: number) => request.delete(`/system/organization/${id}/`)

export const fetchPositionList = (params?: any) => request.get('/system/organization/positions/', { params })
export const createPosition = (data: any) => request.post('/system/organization/positions/', data)
export const updatePosition = (id: number, data: any) => request.put(`/system/organization/positions/${id}/`, data)
export const deletePosition = (id: number) => request.delete(`/system/organization/positions/${id}/`)

export const fetchUserOrganizationRelationList = (params?: any) => request.get('/system/organization/user-relations/', { params })
export const createUserOrganizationRelation = (data: any) => request.post('/system/organization/user-relations/', data)
export const updateUserOrganizationRelation = (id: number, data: any) => request.put(`/system/organization/user-relations/${id}/`, data)
export const deleteUserOrganizationRelation = (id: number) => request.delete(`/system/organization/user-relations/${id}/`)
