import request from '@/api/request'

export const fetchAuditLogList = () => request.get('/system/audit-log/')
