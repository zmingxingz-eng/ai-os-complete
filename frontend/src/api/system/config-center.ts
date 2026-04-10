import request from '@/api/request'

export const fetchConfigCenterList = () => request.get('/system/config-center/')
export const createConfigCenterItem = (data: any) => request.post('/system/config-center/', data)
export const updateConfigCenterItem = (id: number, data: any) => request.put(`/system/config-center/${id}/`, data)
export const deleteConfigCenterItem = (id: number) => request.delete(`/system/config-center/${id}/`)
