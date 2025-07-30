/**
 * AuthStore 測試
 * 測試認證狀態管理、登入登出流程和錯誤處理
 */

import { act, renderHook } from '@testing-library/react'
import { useAuthStore } from './authStore'
import { apiService } from '../services/apiService'
import { AuthResponse, LoginRequest, RegisterRequest, AuthUser } from '@smart-assistant/shared-types'

// Mock apiService
jest.mock('../services/apiService')
const mockApiService = apiService as jest.Mocked<typeof apiService>

// Mock localStorage
const mockLocalStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
}

Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage,
})

describe('AuthStore', () => {
  const mockUser: AuthUser = {
    id: 1,
    email: 'test@example.com',
    name: 'Test User'
  }

  const mockAuthResponse: AuthResponse = {
    access_token: 'mock-token',
    token_type: 'Bearer',
    user: mockUser
  }

  beforeEach(() => {
    jest.clearAllMocks()
    mockLocalStorage.getItem.mockReturnValue(null)
    
    // Reset the store to initial state
    const { result } = renderHook(() => useAuthStore())
    act(() => {
      result.current.reset()
    })
  })

  describe('Initial State', () => {
    it('initializes with empty state when no stored data', () => {
      const { result } = renderHook(() => useAuthStore())
      
      expect(result.current.user).toBeNull()
      expect(result.current.isAuthenticated).toBe(false)
      expect(result.current.isLoading).toBe(false)
      expect(result.current.error).toBeNull()
    })

    it('initializes with stored user data', () => {
      mockLocalStorage.getItem.mockImplementation((key) => {
        if (key === 'auth_user') return JSON.stringify(mockUser)
        if (key === 'auth_token') return 'stored-token'
        return null
      })

      const { result } = renderHook(() => useAuthStore())
      
      expect(result.current.user).toEqual(mockUser)
      expect(result.current.isAuthenticated).toBe(true)
    })
  })

  describe('Login', () => {
    it('successfully logs in user', async () => {
      mockApiService.loginUser.mockResolvedValue(mockAuthResponse)
      
      const { result } = renderHook(() => useAuthStore())
      
      const credentials: LoginRequest = {
        email: 'test@example.com',
        password: 'password123'
      }

      let loginResult: boolean
      await act(async () => {
        loginResult = await result.current.login(credentials)
      })

      expect(loginResult!).toBe(true)
      expect(result.current.user).toEqual(mockUser)
      expect(result.current.isAuthenticated).toBe(true)
      expect(result.current.isLoading).toBe(false)
      expect(result.current.error).toBeNull()
      expect(mockLocalStorage.setItem).toHaveBeenCalledWith('auth_user', JSON.stringify(mockUser))
      expect(mockLocalStorage.setItem).toHaveBeenCalledWith('auth_token', 'mock-token')
    })

    it('handles login failure', async () => {
      const errorMessage = '登入失敗'
      mockApiService.loginUser.mockRejectedValue(new Error(errorMessage))
      
      const { result } = renderHook(() => useAuthStore())
      
      const credentials: LoginRequest = {
        email: 'test@example.com',
        password: 'wrong-password'
      }

      let loginResult: boolean
      await act(async () => {
        loginResult = await result.current.login(credentials)
      })

      expect(loginResult!).toBe(false)
      expect(result.current.user).toBeNull()
      expect(result.current.isAuthenticated).toBe(false)
      expect(result.current.isLoading).toBe(false)
      expect(result.current.error).toBe(errorMessage)
    })

    it('sets loading state during login', async () => {
      let resolveLogin: (value: AuthResponse) => void
      mockApiService.loginUser.mockReturnValue(
        new Promise((resolve) => {
          resolveLogin = resolve
        })
      )
      
      const { result } = renderHook(() => useAuthStore())
      
      const credentials: LoginRequest = {
        email: 'test@example.com',
        password: 'password123'
      }

      act(() => {
        result.current.login(credentials)
      })

      expect(result.current.isLoading).toBe(true)

      await act(async () => {
        resolveLogin!(mockAuthResponse)
      })

      expect(result.current.isLoading).toBe(false)
    })
  })

  describe('Register', () => {
    it('successfully registers user', async () => {
      mockApiService.registerUser.mockResolvedValue(mockAuthResponse)
      
      const { result } = renderHook(() => useAuthStore())
      
      const userData: RegisterRequest = {
        name: 'Test User',
        email: 'test@example.com',
        password: 'password123'
      }

      let registerResult: boolean
      await act(async () => {
        registerResult = await result.current.register(userData)
      })

      expect(registerResult!).toBe(true)
      expect(result.current.user).toEqual(mockUser)
      expect(result.current.isAuthenticated).toBe(true)
      expect(result.current.isLoading).toBe(false)
      expect(result.current.error).toBeNull()
      expect(mockLocalStorage.setItem).toHaveBeenCalledWith('auth_user', JSON.stringify(mockUser))
      expect(mockLocalStorage.setItem).toHaveBeenCalledWith('auth_token', 'mock-token')
    })

    it('handles registration failure', async () => {
      const errorMessage = '註冊失敗'
      mockApiService.registerUser.mockRejectedValue(new Error(errorMessage))
      
      const { result } = renderHook(() => useAuthStore())
      
      const userData: RegisterRequest = {
        name: 'Test User',
        email: 'test@example.com',
        password: 'password123'
      }

      let registerResult: boolean
      await act(async () => {
        registerResult = await result.current.register(userData)
      })

      expect(registerResult!).toBe(false)
      expect(result.current.user).toBeNull()
      expect(result.current.isAuthenticated).toBe(false)
      expect(result.current.isLoading).toBe(false)
      expect(result.current.error).toBe(errorMessage)
    })
  })

  describe('Logout', () => {
    it('successfully logs out user', () => {
      const { result } = renderHook(() => useAuthStore())
      
      // First set user as logged in
      act(() => {
        result.current.login({
          email: 'test@example.com',
          password: 'password123'
        })
      })

      act(() => {
        result.current.logout()
      })

      expect(result.current.user).toBeNull()
      expect(result.current.isAuthenticated).toBe(false)
      expect(result.current.isLoading).toBe(false)
      expect(result.current.error).toBeNull()
      expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('auth_user')
      expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('auth_token')
    })
  })

  describe('Check Auth', () => {
    it('validates stored token successfully', async () => {
      mockLocalStorage.getItem.mockImplementation((key) => {
        if (key === 'auth_user') return JSON.stringify(mockUser)
        if (key === 'auth_token') return 'valid-token'
        return null
      })

      mockApiService.getCurrentUser.mockResolvedValue(mockUser)
      
      const { result } = renderHook(() => useAuthStore())

      await act(async () => {
        await result.current.checkAuth()
      })

      expect(result.current.user).toEqual(mockUser)
      expect(result.current.isAuthenticated).toBe(true)
      expect(result.current.error).toBeNull()
    })

    it('clears auth when token is invalid', async () => {
      mockLocalStorage.getItem.mockImplementation((key) => {
        if (key === 'auth_user') return JSON.stringify(mockUser)
        if (key === 'auth_token') return 'invalid-token'
        return null
      })

      mockApiService.getCurrentUser.mockRejectedValue(new Error('Token invalid'))
      
      const { result } = renderHook(() => useAuthStore())

      await act(async () => {
        await result.current.checkAuth()
      })

      expect(result.current.user).toBeNull()
      expect(result.current.isAuthenticated).toBe(false)
      expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('auth_user')
      expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('auth_token')
    })

    it('handles missing stored data gracefully', async () => {
      mockLocalStorage.getItem.mockReturnValue(null)
      
      const { result } = renderHook(() => useAuthStore())

      await act(async () => {
        await result.current.checkAuth()
      })

      expect(result.current.user).toBeNull()
      expect(result.current.isAuthenticated).toBe(false)
      expect(result.current.isLoading).toBe(false)
    })
  })

  describe('Error Handling', () => {
    it('clears error when clearError is called', () => {
      const { result } = renderHook(() => useAuthStore())
      
      // Set an error
      act(() => {
        result.current.login({
          email: 'test@example.com',
          password: 'wrong-password'
        })
      })

      act(() => {
        result.current.clearError()
      })

      expect(result.current.error).toBeNull()
    })

    it('handles non-Error objects in catch blocks', async () => {
      mockApiService.loginUser.mockRejectedValue('String error')
      
      const { result } = renderHook(() => useAuthStore())
      
      const credentials: LoginRequest = {
        email: 'test@example.com',
        password: 'password123'
      }

      await act(async () => {
        await result.current.login(credentials)
      })

      expect(result.current.error).toBe('登入失敗，請檢查帳號密碼')
    })
  })

  describe('Reset', () => {
    it('resets store to initial state', () => {
      const { result } = renderHook(() => useAuthStore())
      
      // Set some state
      act(() => {
        // Simulate logged in state
        mockLocalStorage.setItem('auth_user', JSON.stringify(mockUser))
        mockLocalStorage.setItem('auth_token', 'token')
      })

      act(() => {
        result.current.reset()
      })

      expect(result.current.user).toBeNull()
      expect(result.current.isAuthenticated).toBe(false)
      expect(result.current.isLoading).toBe(false)
      expect(result.current.error).toBeNull()
      expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('auth_user')
      expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('auth_token')
    })
  })

  describe('localStorage Error Handling', () => {
    it('handles localStorage errors gracefully during read', () => {
      mockLocalStorage.getItem.mockImplementation(() => {
        throw new Error('Storage error')
      })

      // Should not throw error
      expect(() => {
        renderHook(() => useAuthStore())
      }).not.toThrow()
    })

    it('handles localStorage errors gracefully during write', async () => {
      mockLocalStorage.setItem.mockImplementation(() => {
        throw new Error('Storage error')
      })
      
      mockApiService.loginUser.mockResolvedValue(mockAuthResponse)
      
      const { result } = renderHook(() => useAuthStore())
      
      const credentials: LoginRequest = {
        email: 'test@example.com',
        password: 'password123'
      }

      // Should not throw error even if localStorage fails
      await act(async () => {
        await expect(result.current.login(credentials)).resolves.toBe(true)
      })
    })
  })
})