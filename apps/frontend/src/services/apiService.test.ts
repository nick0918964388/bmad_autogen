/**
 * API 服務層測試
 * 確保服務層正確處理API通訊和錯誤情況
 */

import { apiService } from './apiService'

// Mock fetch globally
global.fetch = jest.fn()

// Mock Mantine notifications
jest.mock('@mantine/notifications', () => ({
  notifications: {
    show: jest.fn(),
  },
}))

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
}
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
})

// Mock navigator.onLine
Object.defineProperty(navigator, 'onLine', {
  writable: true,
  value: true,
})

// Mock window.dispatchEvent
Object.defineProperty(window, 'dispatchEvent', {
  value: jest.fn(),
})

describe('ApiService', () => {
  const mockFetch = fetch as jest.MockedFunction<typeof fetch>

  beforeEach(() => {
    mockFetch.mockClear()
    localStorageMock.getItem.mockClear()
    localStorageMock.setItem.mockClear()
    localStorageMock.removeItem.mockClear()
    // Reset navigator.onLine to true
    Object.defineProperty(navigator, 'onLine', { value: true })
  })

  describe('checkHealth', () => {
    it('should return health status on successful response', async () => {
      const mockHealthData = {
        status: 'healthy' as const,
        timestamp: '2025-07-30T10:00:00Z',
        services: {
          database: 'not_configured' as const,
          ollama: 'not_configured' as const,
          vectorDb: 'not_configured' as const
        }
      }

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockHealthData,
      } as Response)

      const result = await apiService.checkHealth()

      expect(mockFetch).toHaveBeenCalledWith(
        '/api/health',
        expect.objectContaining({
          headers: expect.objectContaining({
            'Content-Type': 'application/json'
          })
        })
      )
      expect(result).toEqual(mockHealthData)
    })

    it('should throw error on failed response', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
      } as Response)

      await expect(apiService.checkHealth()).rejects.toThrow('HTTP error! status: 500')
    })

    it('should throw error on network failure', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'))

      await expect(apiService.checkHealth()).rejects.toThrow('Network error')
    })
  })

  describe('getBasicInfo', () => {
    it('should return basic API info', async () => {
      const mockBasicInfo = {
        message: '智能助理應用程式 API',
        version: '1.0.0',
        docs: '/api/docs'
      }

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockBasicInfo,
      } as Response)

      const result = await apiService.getBasicInfo()

      expect(mockFetch).toHaveBeenCalledWith(
        '/',
        expect.objectContaining({
          headers: expect.objectContaining({
            'Content-Type': 'application/json'
          })
        })
      )
      expect(result).toEqual(mockBasicInfo)
    })
  })

  describe('Authentication Methods', () => {
    describe('registerUser', () => {
      it('should register user successfully', async () => {
        const mockRegisterData = {
          email: 'test@example.com',
          password: 'password123',
          name: 'Test User'
        }

        const mockAuthResponse = {
          access_token: 'mock-token',
          token_type: 'Bearer',
          user: {
            id: '1',
            email: 'test@example.com',
            name: 'Test User'
          }
        }

        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: async () => mockAuthResponse,
        } as Response)

        const result = await apiService.registerUser(mockRegisterData)

        expect(mockFetch).toHaveBeenCalledWith(
          '/api/auth/register',
          expect.objectContaining({
            method: 'POST',
            headers: expect.objectContaining({
              'Content-Type': 'application/json'
            }),
            body: JSON.stringify(mockRegisterData)
          })
        )
        expect(result).toEqual(mockAuthResponse)
        expect(localStorageMock.setItem).toHaveBeenCalledWith('auth_token', 'mock-token')
        expect(localStorageMock.setItem).toHaveBeenCalledWith('auth_user', JSON.stringify(mockAuthResponse.user))
      })
    })

    describe('loginUser', () => {
      it('should login user successfully', async () => {
        const mockLoginData = {
          email: 'test@example.com',
          password: 'password123'
        }

        const mockAuthResponse = {
          access_token: 'mock-token',
          token_type: 'Bearer',
          user: {
            id: '1',
            email: 'test@example.com',
            name: 'Test User'
          }
        }

        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: async () => mockAuthResponse,
        } as Response)

        const result = await apiService.loginUser(mockLoginData)

        expect(mockFetch).toHaveBeenCalledWith(
          '/api/auth/login',
          expect.objectContaining({
            method: 'POST',
            headers: expect.objectContaining({
              'Content-Type': 'application/json'
            }),
            body: JSON.stringify(mockLoginData)
          })
        )
        expect(result).toEqual(mockAuthResponse)
        expect(localStorageMock.setItem).toHaveBeenCalledWith('auth_token', 'mock-token')
      })
    })

    describe('isAuthenticated', () => {
      it('should return false when no token exists', () => {
        localStorageMock.getItem.mockReturnValue(null)
        expect(apiService.isAuthenticated()).toBe(false)
      })

      it('should return true when valid token exists', () => {
        // Mock a valid JWT token (not expired)
        const futureTime = Math.floor(Date.now() / 1000) + 3600 // 1 hour from now
        const mockToken = `header.${btoa(JSON.stringify({ exp: futureTime }))}.signature`
        
        localStorageMock.getItem.mockReturnValue(mockToken)
        expect(apiService.isAuthenticated()).toBe(true)
      })

      it('should return false when token is expired', () => {
        // Mock an expired JWT token
        const pastTime = Math.floor(Date.now() / 1000) - 3600 // 1 hour ago
        const mockToken = `header.${btoa(JSON.stringify({ exp: pastTime }))}.signature`
        
        localStorageMock.getItem.mockReturnValue(mockToken)
        expect(apiService.isAuthenticated()).toBe(false)
      })
    })

    describe('logoutUser', () => {
      it('should logout user and clear storage', async () => {
        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: async () => ({}),
        } as Response)

        localStorageMock.getItem.mockReturnValue('mock-token')

        await apiService.logoutUser()

        expect(localStorageMock.removeItem).toHaveBeenCalledWith('auth_token')
        expect(localStorageMock.removeItem).toHaveBeenCalledWith('auth_user')
      })
    })
  })
})