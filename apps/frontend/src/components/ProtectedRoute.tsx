import { ReactNode, useEffect } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { LoadingOverlay } from '@mantine/core'

interface ProtectedRouteProps {
  children: ReactNode
  redirectTo?: string
}

export function ProtectedRoute({ 
  children, 
  redirectTo = '/login' 
}: ProtectedRouteProps) {
  const { user, isAuthenticated, checkAuthStatus, isLoading } = useAuthStore()
  const location = useLocation()

  useEffect(() => {
    // 檢查認證狀態
    checkAuthStatus()
  }, [checkAuthStatus])

  // 載入中顯示載入畫面
  if (isLoading) {
    return <LoadingOverlay visible />
  }

  // 如果未認證，導向登入頁面並保存原始路徑
  if (!isAuthenticated || !user) {
    return (
      <Navigate 
        to={redirectTo} 
        state={{ from: location.pathname }} 
        replace 
      />
    )
  }

  // 已認證，渲染子組件
  return <>{children}</>
}

export default ProtectedRoute