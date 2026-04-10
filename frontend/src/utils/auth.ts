import { getToken } from './token'
export const isLoggedIn = () => Boolean(getToken())
