/**
 * 環境變數配置模組
 * 統一處理不同環境下的變數取得
 */

// 檢查是否在測試環境
const isTestEnvironment = typeof process !== 'undefined' && process.env.NODE_ENV === 'test'

/**
 * 獲取環境變數的統一方法
 */
export const getEnvVar = (key: string, defaultValue?: string): string => {
  if (isTestEnvironment) {
    // 在測試環境中使用 process.env
    return process.env[key] || defaultValue || ''
  } else {
    // 在瀏覽器環境中使用 import.meta.env
    return (import.meta.env as any)?.[key] || defaultValue || ''
  }
}

// 導出常用的環境變數
export const ENV = {
  BACKEND_API_URL: getEnvVar('VITE_BACKEND_API_URL', '/api'),
  NODE_ENV: getEnvVar('NODE_ENV', 'development'),
  MODE: getEnvVar('MODE', 'development'),
} as const