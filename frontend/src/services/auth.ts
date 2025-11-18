import api from './api'
import type { TokenResponse, UserCredentials, UserRegistration } from '../types'

export const signup = async (payload: UserRegistration) => {
  const { data } = await api.post<TokenResponse>('/auth/signup', payload)
  return data
}

export const login = async (payload: UserCredentials) => {
  const { data } = await api.post<TokenResponse>('/auth/login', payload)
  return data
}

export const fetchCurrentUser = async () => {
  const { data } = await api.get('/auth/me')
  return data
}

