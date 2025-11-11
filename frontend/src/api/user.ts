// src/api/user.ts
import api from './service'

export interface LoginPayload {
  username: string
  password: string
}

export interface RegisterPayload {
  username: string
  password: string
}

export interface UserResponse {
  id: string  // Snowflake ID as string for JavaScript safety
  username: string
  created_at: number
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: UserResponse
}

export interface ForgotPasswordPayload {
  username: string
}

export interface ResetPasswordPayload {
  token: string
  new_password: string
}

export interface MessageResponse {
  message: string
}

export interface VerifyEmailPayload {
  token: string
}

export const userApi = {
  /**
   * Login with username and password
   */
  login: async (payload: LoginPayload): Promise<LoginResponse> => {
    const response = await api.post<LoginResponse>('/user/login', payload)
    return response.data
  },

  /**
   * Register a new user account
   */
  register: async (payload: RegisterPayload): Promise<MessageResponse> => {
    console.log(payload);
    const response = await api.post<MessageResponse>('/user/register', payload)
    console.log(response);
    return response.data
  },

  /**
   * Get current user information
   */
  getCurrentUser: async (): Promise<UserResponse> => {
    const response = await api.get<UserResponse>('/user/')
    return response.data
  },

  /**
   * Request a password reset token
   */
  forgotPassword: async (payload: ForgotPasswordPayload): Promise<MessageResponse> => {
    const response = await api.post<MessageResponse>('/user/forgot-password', payload)
    return response.data
  },

  /**
   * Reset password using a valid reset token
   */
  resetPassword: async (payload: ResetPasswordPayload): Promise<MessageResponse> => {
    const response = await api.post<MessageResponse>('/user/reset-password', payload)
    return response.data
  },

  /**
   * Verify email using verification token
   */
  verifyEmail: async (payload: VerifyEmailPayload): Promise<MessageResponse> => {
    const response = await api.post<MessageResponse>('/user/verify-email', payload)
    return response.data
  },
}
