import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import type { TokenResponse, UserPublic } from '../types'

type AuthContextValue = {
  user: UserPublic | null
  token: string | null
  loading: boolean
  isAuthenticated: boolean
  login: (payload: TokenResponse) => void
  logout: () => void
}

const LOCAL_STORAGE_KEY = 'userinsight_auth'

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<UserPublic | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const stored = localStorage.getItem(LOCAL_STORAGE_KEY)
    if (stored) {
      const parsed = JSON.parse(stored) as { user: UserPublic; token: string }
      setUser(parsed.user)
      setToken(parsed.token)
      localStorage.setItem('ui_token', parsed.token)
    }
    setLoading(false)
  }, [])

  const login = useCallback((payload: TokenResponse) => {
    setUser(payload.user)
    setToken(payload.access_token)
    localStorage.setItem(
      LOCAL_STORAGE_KEY,
      JSON.stringify({ user: payload.user, token: payload.access_token }),
    )
    localStorage.setItem('ui_token', payload.access_token)
  }, [])

  const logout = useCallback(() => {
    setUser(null)
    setToken(null)
    localStorage.removeItem(LOCAL_STORAGE_KEY)
    localStorage.removeItem('ui_token')
  }, [])

  const value = useMemo(
    () => ({
      user,
      token,
      loading,
      isAuthenticated: Boolean(user && token),
      login,
      logout,
    }),
    [user, token, loading, login, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

