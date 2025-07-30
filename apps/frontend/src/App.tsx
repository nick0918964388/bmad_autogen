import { useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { MantineProvider } from '@mantine/core'
import { Notifications } from '@mantine/notifications'
import HomePage from './pages/HomePage'
import ChatPage from './pages/ChatPage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import DocumentUploadPage from './pages/DocumentUploadPage'
import ProtectedRoute from './components/ProtectedRoute'
import { useAuthStore } from './stores/authStore'
import '@mantine/core/styles.css'
import '@mantine/notifications/styles.css'

function App() {
  const { initializeAuth } = useAuthStore()

  useEffect(() => {
    // 應用程式啟動時初始化認證狀態
    initializeAuth()
  }, [initializeAuth])

  return (
    <MantineProvider>
      <Notifications />
      <Router>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route 
            path="/chat" 
            element={
              <ProtectedRoute>
                <ChatPage />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/documents" 
            element={
              <ProtectedRoute>
                <DocumentUploadPage />
              </ProtectedRoute>
            } 
          />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </MantineProvider>
  )
}

export default App