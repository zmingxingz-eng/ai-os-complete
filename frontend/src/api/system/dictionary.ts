import request from '@/api/request'

export const fetchDictionaryList = () => request.get('/system/dictionary/')
