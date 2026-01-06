import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiClient } from '@/utils/api'
import type { 
  User, 
  LoginRequest, 
  RegisterRequest, 
  AuthResponse,
  UpdateProfileRequest 
} from '@/types/auth'

const TOKEN_KEY = 'access_token'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem(TOKEN_KEY))
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.is_admin || false)

  // Actions
  const login = async (credentials: LoginRequest) => {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.post<AuthResponse>('/auth/login', credentials)
      token.value = response.access_token
      user.value = response.user
      localStorage.setItem(TOKEN_KEY, response.access_token)
      return true
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Login failed'
      // If the backend returns "Incorrect email or password", show that.
      // If it's a validation error 422, it might be an array.
      if (typeof err.response?.data?.detail === 'object') {
          error.value = JSON.stringify(err.response?.data?.detail)
      }
      return false
    } finally {
      loading.value = false
    }
  }

  const register = async (data: RegisterRequest) => {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.post<AuthResponse>('/auth/register', data)
      token.value = response.access_token
      user.value = response.user
      localStorage.setItem(TOKEN_KEY, response.access_token)
      return true
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Registration failed'
      return false
    } finally {
      loading.value = false
    }
  }

  const fetchCurrentUser = async () => {
    if (!token.value) return
    
    loading.value = true
    try {
      // The endpoint is /auth/me for profile
      user.value = await apiClient.get<User>('/auth/me')
    } catch (err) {
      // If 401, clear token
      logout()
    } finally {
      loading.value = false
    }
  }

  const updateProfile = async (data: UpdateProfileRequest) => {
    loading.value = true
    try {
      user.value = await apiClient.put<User>('/auth/me', data)
      return true
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Update failed'
      return false
    } finally {
      loading.value = false
    }
  }

  const logout = () => {
    // Optionally call backend /auth/logout if implemented
    // await apiClient.post('/auth/logout') 
    token.value = null
    user.value = null
    localStorage.removeItem(TOKEN_KEY)
  }

  return {
    user,
    token,
    loading,
    error,
    isAuthenticated,
    isAdmin,
    login,
    register,
    fetchCurrentUser,
    updateProfile,
    logout
  }
})
