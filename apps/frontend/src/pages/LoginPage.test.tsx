/**
 * LoginPage 組件測試
 * 測試登入頁面的表單驗證、提交流程和使用者互動
 */

import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BrowserRouter } from 'react-router-dom'
import { MantineProvider } from '@mantine/core'
import { notifications } from '@mantine/notifications'
import LoginPage from './LoginPage'
import { useAuthStore } from '../stores/authStore'

// Mock dependencies
jest.mock('../stores/authStore')
jest.mock('@mantine/notifications')

const mockUseAuthStore = useAuthStore as jest.MockedFunction<typeof useAuthStore>
const mockNotifications = notifications as jest.Mocked<typeof notifications>

// Test wrapper component
const TestWrapper = ({ children }: { children: React.ReactNode }) => (
  <BrowserRouter>
    <MantineProvider>
      {children}
    </MantineProvider>
  </BrowserRouter>
)

// Mock navigate function
const mockNavigate = jest.fn()
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}))

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

describe('LoginPage', () => {
  const mockAuthStore = {
    login: jest.fn(),
    isLoading: false,
    error: null,
    clearError: jest.fn(),
    isAuthenticated: false
  }

  beforeEach(() => {
    jest.clearAllMocks()
    mockUseAuthStore.mockReturnValue(mockAuthStore)
    mockNotifications.show.mockImplementation(() => 'mock-id')
    mockLocalStorage.getItem.mockReturnValue(null)
  })

  it('renders login form correctly', () => {
    render(
      <TestWrapper>
        <LoginPage />
      </TestWrapper>
    )

    expect(screen.getByText('歡迎回來')).toBeInTheDocument()
    expect(screen.getByLabelText(/電子郵件/)).toBeInTheDocument()
    expect(screen.getByLabelText(/密碼/)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /登入/ })).toBeInTheDocument()
    expect(screen.getByLabelText(/記住我/)).toBeInTheDocument()
  })

  it('shows validation errors for empty fields', async () => {
    const user = userEvent.setup()
    
    render(
      <TestWrapper>
        <LoginPage />
      </TestWrapper>
    )

    const submitButton = screen.getByRole('button', { name: /登入/ })
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText('電子郵件為必填')).toBeInTheDocument()
      expect(screen.getByText('密碼為必填')).toBeInTheDocument()
    })
  })

  it('validates email format', async () => {
    const user = userEvent.setup()
    
    render(
      <TestWrapper>
        <LoginPage />
      </TestWrapper>
    )

    const emailInput = screen.getByLabelText(/電子郵件/)
    await user.type(emailInput, 'invalid-email')
    await user.tab() // Trigger blur event

    await waitFor(() => {
      expect(screen.getByText('請輸入有效的電子郵件格式')).toBeInTheDocument()
    })
  })

  it('validates minimum password length', async () => {
    const user = userEvent.setup()
    
    render(
      <TestWrapper>
        <LoginPage />
      </TestWrapper>
    )

    const passwordInput = screen.getByLabelText(/密碼/)
    await user.type(passwordInput, '123')
    await user.tab()

    await waitFor(() => {
      expect(screen.getByText('密碼至少需要 6 個字元')).toBeInTheDocument()
    })
  })

  it('submits form with valid data', async () => {
    const user = userEvent.setup()
    mockAuthStore.login.mockResolvedValue(true)
    
    render(
      <TestWrapper>
        <LoginPage />
      </TestWrapper>
    )

    // Fill form with valid data
    await user.type(screen.getByLabelText(/電子郵件/), 'john@example.com')
    await user.type(screen.getByLabelText(/密碼/), 'password123')

    const submitButton = screen.getByRole('button', { name: /登入/ })
    await user.click(submitButton)

    await waitFor(() => {
      expect(mockAuthStore.login).toHaveBeenCalledWith({
        email: 'john@example.com',
        password: 'password123'
      })
    })
  })

  it('handles remember me functionality', async () => {
    const user = userEvent.setup()
    mockAuthStore.login.mockResolvedValue(true)
    
    render(
      <TestWrapper>
        <LoginPage />
      </TestWrapper>
    )

    // Fill form and check remember me
    await user.type(screen.getByLabelText(/電子郵件/), 'john@example.com')
    await user.type(screen.getByLabelText(/密碼/), 'password123')
    await user.click(screen.getByLabelText(/記住我/))

    const submitButton = screen.getByRole('button', { name: /登入/ })
    await user.click(submitButton)

    await waitFor(() => {
      expect(mockLocalStorage.setItem).toHaveBeenCalledWith('remembered_email', 'john@example.com')
      expect(mockLocalStorage.setItem).toHaveBeenCalledWith('remember_me', 'true')
    })
  })

  it('clears remember me data when unchecked', async () => {
    const user = userEvent.setup()
    mockAuthStore.login.mockResolvedValue(true)
    
    render(
      <TestWrapper>
        <LoginPage />
      </TestWrapper>
    )

    // Fill form but don't check remember me
    await user.type(screen.getByLabelText(/電子郵件/), 'john@example.com')
    await user.type(screen.getByLabelText(/密碼/), 'password123')

    const submitButton = screen.getByRole('button', { name: /登入/ })
    await user.click(submitButton)

    await waitFor(() => {
      expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('remembered_email')
      expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('remember_me')
    })
  })

  it('loads remembered email on mount', () => {
    mockLocalStorage.getItem.mockImplementation((key) => {
      if (key === 'remembered_email') return 'remembered@example.com'
      if (key === 'remember_me') return 'true'
      return null
    })
    
    render(
      <TestWrapper>
        <LoginPage />
      </TestWrapper>
    )

    const emailInput = screen.getByLabelText(/電子郵件/) as HTMLInputElement
    const rememberCheckbox = screen.getByLabelText(/記住我/) as HTMLInputElement
    
    expect(emailInput.value).toBe('remembered@example.com')
    expect(rememberCheckbox.checked).toBe(true)
  })

  it('shows loading state during submission', async () => {
    mockUseAuthStore.mockReturnValue({
      ...mockAuthStore,
      isLoading: true
    })
    
    render(
      <TestWrapper>
        <LoginPage />
      </TestWrapper>
    )

    const submitButton = screen.getByRole('button', { name: /登入/ })
    expect(submitButton).toBeDisabled()
    
    // All form fields should be disabled during loading
    expect(screen.getByLabelText(/電子郵件/)).toBeDisabled()
    expect(screen.getByLabelText(/密碼/)).toBeDisabled()
    expect(screen.getByLabelText(/記住我/)).toBeDisabled()
  })

  it('displays error message when login fails', () => {
    const errorMessage = '登入失敗：帳號或密碼錯誤'
    mockUseAuthStore.mockReturnValue({
      ...mockAuthStore,
      error: errorMessage
    })
    
    render(
      <TestWrapper>
        <LoginPage />
      </TestWrapper>
    )

    expect(screen.getByText('登入失敗')).toBeInTheDocument()
    expect(screen.getByText(errorMessage)).toBeInTheDocument()
  })

  it('clears error when close button is clicked', async () => {
    const user = userEvent.setup()
    mockUseAuthStore.mockReturnValue({
      ...mockAuthStore,
      error: '登入失敗'
    })
    
    render(
      <TestWrapper>
        <LoginPage />
      </TestWrapper>
    )

    const closeButton = screen.getByRole('button', { name: /close/i })
    await user.click(closeButton)

    expect(mockAuthStore.clearError).toHaveBeenCalled()
  })

  it('navigates to chat page when already authenticated', () => {
    mockUseAuthStore.mockReturnValue({
      ...mockAuthStore,
      isAuthenticated: true
    })
    
    render(
      <TestWrapper>
        <LoginPage />
      </TestWrapper>
    )

    expect(mockNavigate).toHaveBeenCalledWith('/chat', { replace: true })
  })

  it('shows success notification and navigates on successful login', async () => {
    const user = userEvent.setup()
    mockAuthStore.login.mockResolvedValue(true)
    
    render(
      <TestWrapper>
        <LoginPage />
      </TestWrapper>
    )

    // Fill and submit form
    await user.type(screen.getByLabelText(/電子郵件/), 'john@example.com')
    await user.type(screen.getByLabelText(/密碼/), 'password123')
    
    const submitButton = screen.getByRole('button', { name: /登入/ })
    await user.click(submitButton)

    await waitFor(() => {
      expect(mockNotifications.show).toHaveBeenCalledWith({
        title: '登入成功！',
        message: '歡迎回到智能助理平台',
        color: 'green',
        position: 'top-right'
      })
      expect(mockNavigate).toHaveBeenCalledWith('/chat', { replace: true })
    })
  })

  it('shows validation error notification when form has errors', async () => {
    const user = userEvent.setup()
    
    render(
      <TestWrapper>
        <LoginPage />
      </TestWrapper>
    )

    // Submit empty form to trigger validation errors
    const submitButton = screen.getByRole('button', { name: /登入/ })
    await user.click(submitButton)

    await waitFor(() => {
      expect(mockNotifications.show).toHaveBeenCalledWith({
        title: '表單驗證失敗',
        message: '請檢查並修正表單中的錯誤',
        color: 'red',
        position: 'top-right'
      })
    })
  })

  it('handles forgot password click', async () => {
    const user = userEvent.setup()
    
    render(
      <TestWrapper>
        <LoginPage />
      </TestWrapper>
    )

    const forgotPasswordLink = screen.getByText(/忘記密碼？/)
    await user.click(forgotPasswordLink)

    expect(mockNotifications.show).toHaveBeenCalledWith({
      title: '功能開發中',
      message: '密碼重設功能正在開發中，請聯繫管理員協助',
      color: 'blue',
      position: 'top-right'
    })
  })

  it('has link to register page', () => {
    render(
      <TestWrapper>
        <LoginPage />
      </TestWrapper>
    )

    const registerLink = screen.getByRole('link', { name: /立即註冊/ })
    expect(registerLink).toBeInTheDocument()
    expect(registerLink).toHaveAttribute('href', '/register')
  })

  it('shows security notice', () => {
    render(
      <TestWrapper>
        <LoginPage />
      </TestWrapper>
    )

    expect(screen.getByText(/為了您的帳號安全，請不要在公共電腦上選擇「記住我」選項/)).toBeInTheDocument()
  })

  // Test development environment features
  describe('Development Environment', () => {
    beforeEach(() => {
      // Mock development environment
      Object.defineProperty(globalThis, 'import', {
        value: {
          meta: {
            env: { DEV: true }
          }
        },
        configurable: true
      })
    })

    it('shows test login button in development mode', () => {
      render(
        <TestWrapper>
          <LoginPage />
        </TestWrapper>
      )

      expect(screen.getByText('填入測試帳號')).toBeInTheDocument()
    })

    it('fills test credentials when test button is clicked', async () => {
      const user = userEvent.setup()
      
      render(
        <TestWrapper>
          <LoginPage />
        </TestWrapper>
      )

      const testButton = screen.getByText('填入測試帳號')
      await user.click(testButton)

      const emailInput = screen.getByLabelText(/電子郵件/) as HTMLInputElement
      const passwordInput = screen.getByLabelText(/密碼/) as HTMLInputElement

      expect(emailInput.value).toBe('test@example.com')
      expect(passwordInput.value).toBe('test123456')

      expect(mockNotifications.show).toHaveBeenCalledWith({
        title: '測試帳號已填入',
        message: '您可以使用此測試帳號進行登入',
        color: 'blue',
        position: 'top-right'
      })
    })
  })
})