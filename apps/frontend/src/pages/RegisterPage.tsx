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
  Group,
  Progress,
  List
} from '@mantine/core'
import { useForm } from '@mantine/form'
import { notifications } from '@mantine/notifications'
import { IconX, IconInfoCircle } from '@tabler/icons-react'
import { useAuthStore } from '../stores/authStore'
import { RegisterRequest } from '@smart-assistant/shared-types'

// 密碼強度驗證
const getPasswordStrength = (password: string): { score: number; feedback: string[] } => {
  const feedback: string[] = []
  let score = 0

  if (password.length >= 8) {
    score += 20
  } else {
    feedback.push('至少 8 個字元')
  }

  if (/[A-Z]/.test(password)) {
    score += 20
  } else {
    feedback.push('包含大寫字母')
  }

  if (/[a-z]/.test(password)) {
    score += 20
  } else {
    feedback.push('包含小寫字母')
  }

  if (/[0-9]/.test(password)) {
    score += 20
  } else {
    feedback.push('包含數字')
  }

  if (/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>?]/.test(password)) {
    score += 20
  } else {
    feedback.push('包含特殊字元')
  }

  return { score, feedback }
}

// 密碼強度顏色
const getPasswordStrengthColor = (score: number): string => {
  if (score < 50) return 'red'
  if (score < 75) return 'yellow'
  return 'green'
}

export default function RegisterPage() {
  const navigate = useNavigate()
  const { register, isLoading, error, clearError, isAuthenticated } = useAuthStore()
  const [passwordStrength, setPasswordStrength] = useState({ score: 0, feedback: [] as string[] })

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

  // Mantine 表單設定
  const form = useForm<RegisterRequest>({
    mode: 'uncontrolled',
    initialValues: {
      name: '',
      email: '',
      password: ''
    },
    validate: {
      name: (value: string) => {
        if (!value.trim()) return '姓名為必填'
        if (value.trim().length < 2) return '姓名至少需要 2 個字元'
        return null
      },
      email: (value: string) => {
        if (!value) return '電子郵件為必填'
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) return '請輸入有效的電子郵件格式'
        return null
      },
      password: (value: string) => {
        if (!value) return '密碼為必填'
        if (value.length < 8) return '密碼至少需要 8 個字元'
        const strength = getPasswordStrength(value)
        if (strength.score < 100) return '密碼必須包含大小寫字母、數字和特殊字元'
        return null
      }
    },
    validateInputOnChange: ['email'],
    validateInputOnBlur: true
  })

  // 處理密碼變更以更新強度指示器
  const handlePasswordChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const password = event.currentTarget.value
    setPasswordStrength(getPasswordStrength(password))
    form.getInputProps('password').onChange?.(event)
  }

  // 處理表單提交
  const handleSubmit = async (values: RegisterRequest) => {
    clearError()
    
    try {
      const success = await register(values)
      
      if (success) {
        notifications.show({
          title: '註冊成功！',
          message: '歡迎加入智能助理平台',
          color: 'green',
          position: 'top-right'
        })
        navigate('/chat', { replace: true })
      }
    } catch (err) {
      // 錯誤訊息已由 authStore 處理
      console.error('註冊失敗:', err)
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

  return (
    <Container size={420} my={40}>
      <Title ta="center" mb="md">
        建立新帳號
      </Title>
      
      <Text c="dimmed" size="sm" ta="center" mb="xl">
        已經有帳號了嗎？{' '}
        <Anchor component={Link} to="/login" size="sm">
          立即登入
        </Anchor>
      </Text>

      <Paper withBorder shadow="md" p={30} mt={30} radius="md">
        <form onSubmit={form.onSubmit(handleSubmit, handleValidationErrors)}>
          <Stack gap="md">
            {/* 錯誤訊息顯示 */}
            {error && (
              <Alert 
                icon={<IconX size="1rem" />} 
                title="註冊失敗" 
                color="red"
                onClose={clearError}
                withCloseButton
              >
                {error}
              </Alert>
            )}

            {/* 姓名欄位 */}
            <TextInput
              required
              label="姓名"
              placeholder="請輸入您的姓名"
              key={form.key('name')}
              {...form.getInputProps('name')}
              disabled={isLoading}
            />

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
              onChange={handlePasswordChange}
              disabled={isLoading}
              visibilityToggleButtonProps={{
                'aria-label': '切換密碼顯示狀態'
              }}
            />

            {/* 密碼強度指示器 */}
            {form.getValues().password && (
              <Stack gap="xs">
                <Group justify="space-between">
                  <Text size="sm" c="dimmed">密碼強度</Text>
                  <Text size="sm" c={getPasswordStrengthColor(passwordStrength.score)}>
                    {passwordStrength.score < 50 ? '弱' : 
                     passwordStrength.score < 75 ? '中等' : '強'}
                  </Text>
                </Group>
                
                <Progress 
                  value={passwordStrength.score} 
                  color={getPasswordStrengthColor(passwordStrength.score)}
                  size="sm"
                />
                
                {passwordStrength.feedback.length > 0 && (
                  <Alert 
                    icon={<IconInfoCircle size="1rem" />} 
                    color="blue"
                    variant="light"
                  >
                    <Text size="sm" mb="xs">建議改善：</Text>
                    <List size="sm" spacing="xs">
                      {passwordStrength.feedback.map((item, index) => (
                        <List.Item key={index}>{item}</List.Item>
                      ))}
                    </List>
                  </Alert>
                )}
              </Stack>
            )}

            {/* 提交按鈕 */}
            <Button 
              type="submit" 
              fullWidth 
              mt="xl"
              loading={isLoading}
              disabled={isLoading}
            >
              建立帳號
            </Button>
          </Stack>
        </form>

        {/* 附加資訊 */}
        <Alert 
          icon={<IconInfoCircle size="1rem" />} 
          color="blue"
          variant="light"
          mt="md"
        >
          <Text size="sm">
            註冊即表示您同意我們的服務條款與隱私權政策。
            您的資料將受到完善保護。
          </Text>
        </Alert>
      </Paper>
    </Container>
  )
}