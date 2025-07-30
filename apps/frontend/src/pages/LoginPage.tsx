import { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import {
  Container,
  Paper,
  Title,
  Text,
  TextInput,
  PasswordInput,
  Button,
  Stack,
  Alert,
  Anchor,
  Checkbox,
  Divider,
  Group
} from '@mantine/core'
import { useForm } from '@mantine/form'
import { notifications } from '@mantine/notifications'
import { IconX, IconLogin, IconInfoCircle } from '@tabler/icons-react'
import { useAuthStore } from '../stores/authStore'
import { LoginRequest } from '@smart-assistant/shared-types'

export default function LoginPage() {
  const navigate = useNavigate()
  const { login, isLoading, error, clearError, isAuthenticated } = useAuthStore()
  const [rememberMe, setRememberMe] = useState(false)

  // 如果已登入，重導向到聊天頁面
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/chat', { replace: true })
    }
  }, [isAuthenticated, navigate])

  // 清除錯誤訊息當組件掛載時
  useEffect(() => {
    clearError()
  }, [clearError])

  // 從 localStorage 載入記住的帳號資訊
  useEffect(() => {
    const rememberedEmail = localStorage.getItem('remembered_email')
    const rememberedState = localStorage.getItem('remember_me') === 'true'
    
    if (rememberedEmail && rememberedState) {
      form.setFieldValue('email', rememberedEmail)
      setRememberMe(true)
    }
  }, [])

  // Mantine 表單設定
  const form = useForm<LoginRequest>({
    mode: 'uncontrolled',
    initialValues: {
      email: '',
      password: ''
    },
    validate: {
      email: (value) => {
        if (!value) return '電子郵件為必填'
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) return '請輸入有效的電子郵件格式'
        return null
      },
      password: (value) => {
        if (!value) return '密碼為必填'
        if (value.length < 6) return '密碼至少需要 6 個字元'
        return null
      }
    },
    validateInputOnChange: ['email'],
    validateInputOnBlur: true
  })

  // 處理表單提交
  const handleSubmit = async (values: LoginRequest) => {
    clearError()
    
    try {
      // 處理記住帳號功能
      if (rememberMe) {
        localStorage.setItem('remembered_email', values.email)
        localStorage.setItem('remember_me', 'true')
      } else {
        localStorage.removeItem('remembered_email')
        localStorage.removeItem('remember_me')
      }

      const success = await login(values)
      
      if (success) {
        notifications.show({
          title: '登入成功！',
          message: '歡迎回到智能助理平台',
          color: 'green',
          position: 'top-right'
        })
        navigate('/chat', { replace: true })
      }
    } catch (err) {
      // 錯誤訊息已由 authStore 處理
      console.error('登入失敗:', err)
    }
  }

  // 處理表單驗證錯誤
  const handleValidationErrors = (validationErrors: typeof form.errors) => {
    notifications.show({
      title: '表單驗證失敗',
      message: '請檢查並修正表單中的錯誤',
      color: 'red',
      position: 'top-right'
    })
    console.error('表單驗證錯誤:', validationErrors)
  }

  // 處理忘記密碼（目前為示範功能）
  const handleForgotPassword = () => {
    notifications.show({
      title: '功能開發中',
      message: '密碼重設功能正在開發中，請聯繫管理員協助',
      color: 'blue',
      position: 'top-right'
    })
  }

  // 處理測試帳號登入（開發環境使用）
  const handleTestLogin = () => {
    form.setValues({
      email: 'test@example.com',
      password: 'test123456'
    })
    notifications.show({
      title: '測試帳號已填入',
      message: '您可以使用此測試帳號進行登入',
      color: 'blue',
      position: 'top-right'
    })
  }

  return (
    <Container size={420} my={40}>
      <Title ta="center" mb="md">
        歡迎回來
      </Title>
      
      <Text c="dimmed" size="sm" ta="center" mb="xl">
        還沒有帳號嗎？{' '}
        <Anchor component={Link} to="/register" size="sm">
          立即註冊
        </Anchor>
      </Text>

      <Paper withBorder shadow="md" p={30} mt={30} radius="md">
        <form onSubmit={form.onSubmit(handleSubmit, handleValidationErrors)}>
          <Stack gap="md">
            {/* 錯誤訊息顯示 */}
            {error && (
              <Alert 
                icon={<IconX size="1rem" />} 
                title="登入失敗" 
                color="red"
                onClose={clearError}
                withCloseButton
              >
                {error}
              </Alert>
            )}

            {/* 電子郵件欄位 */}
            <TextInput
              required
              label="電子郵件"
              placeholder="your@email.com"
              type="email"
              key={form.key('email')}
              {...form.getInputProps('email')}
              disabled={isLoading}
            />

            {/* 密碼欄位 */}
            <PasswordInput
              required
              label="密碼"
              placeholder="請輸入密碼"
              key={form.key('password')}
              {...form.getInputProps('password')}
              disabled={isLoading}
              visibilityToggleButtonProps={{
                'aria-label': '切換密碼顯示狀態'
              }}
            />

            {/* 記住我與忘記密碼 */}
            <Group justify="space-between" mt="xs">
              <Checkbox
                label="記住我"
                checked={rememberMe}
                onChange={(event) => setRememberMe(event.currentTarget.checked)}
                disabled={isLoading}
              />
              <Anchor 
                size="sm" 
                onClick={handleForgotPassword}
                style={{ cursor: 'pointer' }}
              >
                忘記密碼？
              </Anchor>
            </Group>

            {/* 登入按鈕 */}
            <Button 
              type="submit" 
              fullWidth 
              mt="xl"
              loading={isLoading}
              disabled={isLoading}
              leftSection={<IconLogin size="1rem" />}
            >
              登入
            </Button>

            {/* 開發環境測試功能 */}
            {import.meta.env.DEV && (
              <>
                <Divider label="開發測試" labelPosition="center" />
                <Button 
                  variant="light" 
                  color="blue"
                  fullWidth
                  onClick={handleTestLogin}
                  disabled={isLoading}
                >
                  填入測試帳號
                </Button>
              </>
            )}
          </Stack>
        </form>

        {/* 安全提示 */}
        <Alert 
          icon={<IconInfoCircle size="1rem" />} 
          color="blue"
          variant="light"
          mt="md"
        >
          <Text size="sm">
            為了您的帳號安全，請不要在公共電腦上選擇「記住我」選項。
            如果您忘記密碼，請聯繫系統管理員協助重設。
          </Text>
        </Alert>
      </Paper>
    </Container>
  )
}