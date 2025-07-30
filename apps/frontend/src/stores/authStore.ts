import { create } from 'zustand';
import { AuthUser, LoginRequest, RegisterRequest } from '@smart-assistant/shared-types';
import { apiService } from '../services/apiService';

interface AuthState {
  // 認證狀態
  user: AuthUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  
  // 認證動作
  login: (credentials: LoginRequest) => Promise<boolean>;
  register: (userData: RegisterRequest) => Promise<boolean>;
  logout: () => void;
  clearError: () => void;
  
  // 檢查認證狀態
  checkAuth: () => Promise<void>;
  checkAuthStatus: () => Promise<void>;
  initializeAuth: () => Promise<void>;
  
  // 重置狀態
  reset: () => void;
}

// 從 localStorage 取得持久化的認證資料
const getStoredAuth = (): { user: AuthUser | null; token: string | null } => {
  try {
    const storedUser = localStorage.getItem('auth_user');
    const storedToken = localStorage.getItem('auth_token');
    
    return {
      user: storedUser ? JSON.parse(storedUser) : null,
      token: storedToken
    };
  } catch (error) {
    console.warn('讀取認證資料失敗:', error);
    return { user: null, token: null };
  }
};

// 儲存認證資料到 localStorage
const storeAuth = (user: AuthUser, token: string): void => {
  try {
    localStorage.setItem('auth_user', JSON.stringify(user));
    localStorage.setItem('auth_token', token);
  } catch (error) {
    console.warn('儲存認證資料失敗:', error);
  }
};

// 清除認證資料
const clearStoredAuth = (): void => {
  try {
    localStorage.removeItem('auth_user');
    localStorage.removeItem('auth_token');
  } catch (error) {
    console.warn('清除認證資料失敗:', error);
  }
};

// 初始狀態 - 從 localStorage 恢復
const initialStoredAuth = getStoredAuth();

export const useAuthStore = create<AuthState>((set) => ({
  // 初始狀態
  user: initialStoredAuth.user,
  isAuthenticated: !!initialStoredAuth.user && !!initialStoredAuth.token,
  isLoading: false,
  error: null,

  // 登入動作
  login: async (credentials: LoginRequest): Promise<boolean> => {
    set({ isLoading: true, error: null });
    
    try {
      const response = await apiService.loginUser(credentials);
      
      // 儲存認證資料
      storeAuth(response.user, response.access_token);
      
      set({
        user: response.user,
        isAuthenticated: true,
        isLoading: false,
        error: null
      });
      
      return true;
    } catch (error) {
      const errorMessage = error instanceof Error 
        ? error.message 
        : '登入失敗，請檢查帳號密碼';
      
      set({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: errorMessage
      });
      
      return false;
    }
  },

  // 註冊動作
  register: async (userData: RegisterRequest): Promise<boolean> => {
    set({ isLoading: true, error: null });
    
    try {
      const response = await apiService.registerUser(userData);
      
      // 儲存認證資料
      storeAuth(response.user, response.access_token);
      
      set({
        user: response.user,
        isAuthenticated: true,
        isLoading: false,
        error: null
      });
      
      return true;
    } catch (error) {
      const errorMessage = error instanceof Error 
        ? error.message 
        : '註冊失敗，請稍後重試';
      
      set({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: errorMessage
      });
      
      return false;
    }
  },

  // 登出動作
  logout: () => {
    clearStoredAuth();
    
    set({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null
    });
  },

  // 清除錯誤
  clearError: () => {
    set({ error: null });
  },

  // 檢查認證狀態
  checkAuth: async (): Promise<void> => {
    const storedAuth = getStoredAuth();
    
    if (!storedAuth.user || !storedAuth.token) {
      set({
        user: null,
        isAuthenticated: false,
        isLoading: false
      });
      return;
    }
    
    set({ isLoading: true });
    
    try {
      // 驗證 token 是否有效
      const userInfo = await apiService.getCurrentUser();
      
      set({
        user: userInfo,
        isAuthenticated: true,
        isLoading: false,
        error: null
      });
    } catch (error) {
      console.warn('Token 驗證失敗:', error);
      
      // Token 無效，清除儲存的認證資料
      clearStoredAuth();
      
      set({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: null
      });
    }
  },

  // 檢查認證狀態 (別名)
  checkAuthStatus: async (): Promise<void> => {
    const storedAuth = getStoredAuth();
    
    if (!storedAuth.user || !storedAuth.token) {
      set({
        user: null,
        isAuthenticated: false,
        isLoading: false
      });
      return;
    }
    
    set({ isLoading: true });
    
    try {
      // 驗證 token 是否有效
      const userInfo = await apiService.getCurrentUser();
      
      set({
        user: userInfo,
        isAuthenticated: true,
        isLoading: false,
        error: null
      });
    } catch (error) {
      console.warn('Token 驗證失敗:', error);
      
      // Token 無效，清除儲存的認證資料
      clearStoredAuth();
      
      set({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: null
      });
    }
  },

  // 初始化認證 (應用程式啟動時調用)
  initializeAuth: async (): Promise<void> => {
    const storedAuth = getStoredAuth();
    
    if (!storedAuth.user || !storedAuth.token) {
      set({
        user: null,
        isAuthenticated: false,
        isLoading: false
      });
      return;
    }
    
    set({ 
      user: storedAuth.user,
      isAuthenticated: true,
      isLoading: false
    });
  },

  // 重置狀態
  reset: () => {
    clearStoredAuth();
    
    set({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null
    });
  }
}));