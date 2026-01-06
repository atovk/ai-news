export interface User {
  id: number
  username: string
  email: string
  avatar_url?: string | null
  bio?: string | null
  is_admin: boolean
  is_active: boolean
  created_at: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: User
}

export interface LoginRequest {
  username?: string // Backend uses OAuth2PasswordRequestForm which expects username, but we pass email in schemas. 
  // Wait, the backend Login schema expects 'email' and 'password'. 
  // app/schemas/auth.py: UserLogin has email, password.
  email: string
  password: string
}

export interface RegisterRequest {
  username: string
  email: string
  password: string
}

export interface UpdateProfileRequest {
  username?: string
  email?: string
  avatar_url?: string
  bio?: string
  password?: string
}
