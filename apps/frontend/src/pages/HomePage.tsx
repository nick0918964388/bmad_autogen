import { Container, Title, Text, Stack, Button, Group, Paper, Avatar } from '@mantine/core'
import { notifications } from '@mantine/notifications'
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { apiService } from '../services/apiService'
import { useAuthStore } from '../stores/authStore'

export default function HomePage() {
  const [backendStatus, setBackendStatus] = useState<'loading' | 'connected' | 'disconnected'>('loading')
  const navigate = useNavigate()
  const { user, isAuthenticated, logout } = useAuthStore()

  // 測試後端連接 - 使用服務層
  const testBackendConnection = async () => {
    try {
      const healthResponse = await apiService.checkHealth()
      if (healthResponse.status === 'healthy') {
        setBackendStatus('connected')
        notifications.show({
          title: '後端連接成功',
          message: '智能助理後端服務運行正常',
          color: 'green'
        })
      } else {
        setBackendStatus('disconnected')
        notifications.show({
          title: '後端服務異常',
          message: '後端服務狀態不健康',
          color: 'red'
        })
      }
    } catch (error) {
      console.error('Backend connection failed:', error)
      setBackendStatus('disconnected')
      notifications.show({
        title: '後端連接失敗',
        message: '無法連接到後端服務',
        color: 'red'
      })
    }
  }

  const handleStartChat = () => {
    if (!isAuthenticated) {
      navigate('/login')
    } else {
      navigate('/chat')
    }
  }

  const handleDocuments = () => {
    if (!isAuthenticated) {
      navigate('/login')
    } else {
      navigate('/documents')
    }
  }

  const handleLogin = () => {
    navigate('/login')
  }

  const handleRegister = () => {
    navigate('/register')
  }

  const handleLogout = async () => {
    try {
      await logout()
      notifications.show({
        title: '登出成功',
        message: '您已成功登出',
        color: 'blue'
      })
    } catch (error) {
      console.error('Logout failed:', error)
    }
  }

  useEffect(() => {
    // 初始連接測試
    testBackendConnection()
  }, [])

  return (
    <Container size="md" py="xl">
      <Stack align="center" gap="xl">
        {/* 使用者狀態顯示 */}
        {isAuthenticated && user && (
          <Paper p="md" radius="md" withBorder style={{ alignSelf: 'stretch' }}>
            <Group justify="space-between">
              <Group>
                <Avatar name={user.name} color="blue" radius="xl" />
                <div>
                  <Text size="sm" fw={500}>歡迎回來，{user.name}</Text>
                  <Text size="xs" c="dimmed">{user.email}</Text>
                </div>
              </Group>
              <Button variant="light" size="xs" onClick={handleLogout}>
                登出
              </Button>
            </Group>
          </Paper>
        )}

        <Title order={1} ta="center">
          🤖 智能助理應用程式
        </Title>
        
        <Text size="lg" ta="center" c="dimmed">
          基於 AutoGen 的多代理智能體系統
        </Text>

        <Stack align="center" gap="md">
          <Text size="md" fw={500}>
            環境狀態檢查
          </Text>
          
          <Group>
            <Text size="sm">
              前端服務: <Text span c="green" fw={500}>✓ 運行中</Text>
            </Text>
            <Text size="sm">
              後端服務: 
              <Text 
                span 
                c={backendStatus === 'connected' ? 'green' : backendStatus === 'disconnected' ? 'red' : 'yellow'} 
                fw={500}
              >
                {backendStatus === 'connected' ? '✓ 已連接' : 
                 backendStatus === 'disconnected' ? '✗ 未連接' : '⏳ 檢查中...'}
              </Text>
            </Text>
          </Group>

          <Group>
            <Button 
              onClick={testBackendConnection}
              loading={backendStatus === 'loading'}
              variant="outline"
            >
              重新測試後端連接
            </Button>
            
            {isAuthenticated ? (
              <Group>
                <Button 
                  onClick={handleStartChat}
                  variant="filled"
                  size="md"
                >
                  開始聊天
                </Button>
                <Button 
                  onClick={handleDocuments}
                  variant="outline"
                  size="md"
                >
                  管理文件
                </Button>
              </Group>
            ) : (
              <Group>
                <Button 
                  onClick={handleLogin}
                  variant="outline"
                  size="md"
                >
                  登入
                </Button>
                <Button 
                  onClick={handleRegister}
                  variant="filled"
                  size="md"
                >
                  註冊
                </Button>
              </Group>
            )}
          </Group>
        </Stack>

        <Text size="sm" ta="center" c="dimmed">
          這是智能助理應用程式的初始頁面。<br />
          Docker Compose 環境已成功建置完成！
        </Text>
      </Stack>
    </Container>
  )
}