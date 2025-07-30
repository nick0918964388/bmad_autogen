/**
 * API 服務層 - 統一前端與後端 API 通訊
 * 根據編碼標準，所有 API 呼叫必須透過服務層進行
 * 擴展支援身份驗證功能，包含JWT token管理和自動錯誤處理
 */

import { 
  HealthCheckResponse, 
  RegisterRequest, 
  LoginRequest, 
  AuthResponse, 
  ApiError,
  AuthUser,
  KnowledgeBase 
} from '@smart-assistant/shared-types'
import { notifications } from '@mantine/notifications'

class ApiService {
  private baseUrl: string
  private readonly TOKEN_KEY = 'auth_token'
  private readonly USER_KEY = 'auth_user'

  constructor() {
    // 根據編碼標準，透過配置物件存取環境變數
    // 在測試環境中使用 process.env，在瀏覽器環境中使用 import.meta.env
    let apiUrl = '/api'
    
    try {
      // 嘗試使用 import.meta.env (瀏覽器環境)
      apiUrl = import.meta.env.VITE_BACKEND_API_URL || '/api'
    } catch {
      // 如果失敗，使用 process.env (測試環境)
      apiUrl = process.env.VITE_BACKEND_API_URL || '/api'
    }
    
    this.baseUrl = apiUrl
  }

  /**
   * Token 管理方法
   */
  private getToken(): string | null {
    try {
      return localStorage.getItem(this.TOKEN_KEY)
    } catch (error) {
      console.warn('無法從 localStorage 獲取 token:', error)
      return null
    }
  }

  private setToken(token: string): void {
    try {
      localStorage.setItem(this.TOKEN_KEY, token)
    } catch (error) {
      console.error('無法儲存 token 到 localStorage:', error)
    }
  }

  private removeToken(): void {
    try {
      localStorage.removeItem(this.TOKEN_KEY)
      localStorage.removeItem(this.USER_KEY)
    } catch (error) {
      console.error('無法清除 localStorage 中的認證資料:', error)
    }
  }

  private setUser(user: AuthUser): void {
    try {
      localStorage.setItem(this.USER_KEY, JSON.stringify(user))
    } catch (error) {
      console.error('無法儲存用戶資料到 localStorage:', error)
    }
  }

  /**
   * 檢查 token 是否過期
   */
  private isTokenExpired(token: string): boolean {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      const exp = payload.exp * 1000 // 轉換為毫秒
      return Date.now() >= exp
    } catch (error) {
      console.warn('無法解析 token:', error)
      return true // 如果無法解析，視為過期
    }
  }

  /**
   * 統一錯誤處理機制
   */
  private handleApiError(error: any, endpoint: string): never {
    console.error(`API request failed for ${endpoint}:`, error)
    
    // 處理網路錯誤
    if (!navigator.onLine) {
      notifications.show({
        title: '網路連線錯誤',
        message: '請檢查您的網路連線',
        color: 'red',
        position: 'top-right',
      })
      throw new Error('網路連線失敗')
    }

    // 處理認證錯誤
    if (error.status === 401) {
      this.handleTokenExpired()
      notifications.show({
        title: '認證失敗',
        message: '請重新登入',
        color: 'red',
        position: 'top-right',
      })
      throw new Error('認證失敗，請重新登入')
    }

    // 處理伺服器錯誤
    if (error.status >= 500) {
      notifications.show({
        title: '伺服器錯誤',
        message: '伺服器暫時無法處理請求，請稍後再試',
        color: 'red',
        position: 'top-right',
      })
      throw new Error('伺服器錯誤')
    }

    // 處理其他HTTP錯誤
    notifications.show({
      title: '請求失敗',
      message: error.message || '未知錯誤',
      color: 'red',
      position: 'top-right',
    })
    
    throw error
  }

  /**
   * 處理 token 過期
   */
  private handleTokenExpired(): void {
    this.removeToken()
    // 觸發登出事件，讓其他元件知道用戶已登出
    window.dispatchEvent(new CustomEvent('auth:logout'))
  }

  /**
   * 統一的 HTTP 請求方法 - 支援自動 JWT token 附加
   */
  private async request<T>(
    endpoint: string,
    options: RequestInit = {},
    requiresAuth: boolean = false
  ): Promise<T> {
    const url = endpoint.startsWith('/') ? `${this.baseUrl}${endpoint}` : endpoint
    
    // 準備標頭
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>),
    }

    // 如果需要認證，添加 Authorization 標頭
    if (requiresAuth) {
      const token = this.getToken()
      
      if (!token) {
        this.handleApiError({ status: 401, message: '無有效的認證 token' }, endpoint)
      }

      // 檢查 token 是否過期
      if (token && this.isTokenExpired(token)) {
        this.handleTokenExpired()
        this.handleApiError({ status: 401, message: 'Token 已過期' }, endpoint)
      }

      if (token) {
        headers.Authorization = `Bearer ${token}`
      }
    }
    
    try {
      const response = await fetch(url, {
        headers,
        ...options,
      })

      // 處理不同的 HTTP 狀態碼
      if (!response.ok) {
        let errorMessage = `HTTP error! status: ${response.status}`
        
        try {
          // 嘗試解析後端錯誤回應
          const errorData: ApiError = await response.json()
          errorMessage = errorData.error?.message || errorMessage
        } catch {
          // 如果無法解析JSON，使用預設錯誤訊息
        }

        const error = new Error(errorMessage) as any
        error.status = response.status
        throw error
      }

      return response.json()
    } catch (error) {
      this.handleApiError(error, endpoint)
    }
  }

  /**
   * 健康檢查 API
   */
  async checkHealth(): Promise<HealthCheckResponse> {
    // 健康檢查端點不在 /api 路由下，需要使用完整 URL
    const healthUrl = this.baseUrl.replace('/api', '/health')
    return this.request<HealthCheckResponse>(healthUrl)
  }

  /**
   * 基本根路由檢查
   */
  async getBasicInfo(): Promise<{ message: string; version: string; docs: string }> {
    // 直接呼叫根路由，不使用 /api 前綴
    return this.request<{ message: string; version: string; docs: string }>('/')
  }

  // ========== 身份驗證 API 方法 ==========

  /**
   * 用戶註冊 API
   */
  async registerUser(userData: RegisterRequest): Promise<AuthResponse> {
    try {
      const response = await this.request<AuthResponse>(
        '/auth/register',
        {
          method: 'POST',
          body: JSON.stringify(userData),
        }
      )

      // 註冊成功後自動儲存 token 和用戶資料
      if (response.access_token) {
        this.setToken(response.access_token)
        this.setUser(response.user)
        
        // 顯示成功通知
        notifications.show({
          title: '註冊成功',
          message: `歡迎 ${response.user.name}！`,
          color: 'green',
          position: 'top-right',
        })

        // 觸發登入事件
        window.dispatchEvent(new CustomEvent('auth:login', { 
          detail: { user: response.user } 
        }))
      }

      return response
    } catch (error) {
      // 錯誤已在 request 方法中處理並顯示通知
      throw error
    }
  }

  /**
   * 用戶登入 API
   */
  async loginUser(credentials: LoginRequest): Promise<AuthResponse> {
    try {
      const response = await this.request<AuthResponse>(
        '/auth/login',
        {
          method: 'POST',
          body: JSON.stringify(credentials),
        }
      )

      // 登入成功後自動儲存 token 和用戶資料
      if (response.access_token) {
        this.setToken(response.access_token)
        this.setUser(response.user)
        
        // 顯示成功通知
        notifications.show({
          title: '登入成功',
          message: `歡迎回來，${response.user.name}！`,
          color: 'green',
          position: 'top-right',
        })

        // 觸發登入事件
        window.dispatchEvent(new CustomEvent('auth:login', { 
          detail: { user: response.user } 
        }))
      }

      return response
    } catch (error) {
      // 錯誤已在 request 方法中處理並顯示通知
      throw error
    }
  }

  /**
   * 用戶登出 API
   */
  async logoutUser(): Promise<void> {
    try {
      // 呼叫後端登出 API（如果存在）
      await this.request<void>(
        '/auth/logout',
        {
          method: 'POST',
        },
        true // 需要認證
      )
    } catch (error) {
      // 即使後端API失敗，也執行前端登出邏輯
      console.warn('後端登出 API 呼叫失敗，執行前端登出:', error)
    } finally {
      // 清除前端儲存的認證資料
      this.removeToken()
      
      // 顯示登出通知
      notifications.show({
        title: '已登出',
        message: '您已成功登出',
        color: 'blue',
        position: 'top-right',
      })

      // 觸發登出事件
      window.dispatchEvent(new CustomEvent('auth:logout'))
    }
  }

  /**
   * 獲取當前用戶資料
   */
  async getCurrentUser(): Promise<AuthUser> {
    return this.request<AuthUser>('/auth/me', {}, true)
  }

  /**
   * 刷新 token
   */
  async refreshToken(): Promise<AuthResponse> {
    const response = await this.request<AuthResponse>(
      '/auth/refresh',
      {
        method: 'POST',
      },
      true
    )

    if (response.access_token) {
      this.setToken(response.access_token)
      this.setUser(response.user)
    }

    return response
  }

  // ========== 公用認證狀態方法 ==========

  /**
   * 檢查是否已登入
   */
  isAuthenticated(): boolean {
    const token = this.getToken()
    if (!token) return false
    return !this.isTokenExpired(token)
  }

  /**
   * 獲取儲存的用戶資料
   */
  getStoredUser(): AuthUser | null {
    try {
      const userData = localStorage.getItem(this.USER_KEY)
      return userData ? JSON.parse(userData) : null
    } catch (error) {
      console.error('無法獲取用戶資料:', error)
      return null
    }
  }

  /**
   * 手動清除認證狀態（用於強制登出）
   */
  clearAuthState(): void {
    this.removeToken()
    window.dispatchEvent(new CustomEvent('auth:logout'))
  }

  // ========== 知識庫管理 API 方法 ==========

  /**
   * 創建新知識庫
   */
  async createKnowledgeBase(data: { name: string; path: string }): Promise<KnowledgeBase> {
    try {
      const response = await this.request<KnowledgeBase>(
        '/knowledge-base',
        {
          method: 'POST',
          body: JSON.stringify(data),
        },
        true // 需要認證
      )

      notifications.show({
        title: '知識庫創建成功',
        message: `「${data.name}」已開始處理`,
        color: 'green',
        position: 'top-right',
      })

      return response
    } catch (error) {
      // 錯誤已在 request 方法中處理並顯示通知
      throw error
    }
  }

  /**
   * 獲取知識庫列表
   */
  async getKnowledgeBases(): Promise<KnowledgeBase[]> {
    return this.request<KnowledgeBase[]>('/knowledge-base', {}, true)
  }

  /**
   * 獲取特定知識庫狀態
   */
  async getKnowledgeBaseStatus(id: string): Promise<Partial<KnowledgeBase>> {
    return this.request<Partial<KnowledgeBase>>(`/knowledge-base/${id}/status`, {}, true)
  }

  /**
   * 刪除知識庫
   */
  async deleteKnowledgeBase(id: string): Promise<void> {
    try {
      await this.request<void>(
        `/knowledge-base/${id}`,
        {
          method: 'DELETE',
        },
        true
      )

      notifications.show({
        title: '知識庫已刪除',
        message: '知識庫及其相關資料已成功刪除',
        color: 'blue',
        position: 'top-right',
      })
    } catch (error) {
      throw error
    }
  }
}

// 導出單例實例
export const apiService = new ApiService()
export default apiService