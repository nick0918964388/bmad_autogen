/**
 * RegisterPage 組件測試
 * 測試註冊頁面的表單驗證、提交流程和使用者互動
 */

import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BrowserRouter } from 'react-router-dom'
import { MantineProvider } from '@mantine/core'
import { notifications } from '@mantine/notifications'
import RegisterPage from './RegisterPage'
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

describe('RegisterPage', () => {
  const mockAuthStore = {
    register: jest.fn(),
    isLoading: false,
    error: null,
    clearError: jest.fn(),
    isAuthenticated: false
  }

  beforeEach(() => {
    jest.clearAllMocks()
    mockUseAuthStore.mockReturnValue(mockAuthStore)
    mockNotifications.show.mockImplementation(() => 'mock-id')
  })

  it('renders registration form correctly', () => {
    render(
      <TestWrapper>
        <RegisterPage />
      </TestWrapper>
    )

    expect(screen.getByText('建立新帳號')).toBeInTheDocument()
    expect(screen.getByLabelText(/姓名/)).toBeInTheDocument()
    expect(screen.getByLabelText(/電子郵件/)).toBeInTheDocument()
    expect(screen.getByLabelText(/密碼/)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /建立帳號/ })).toBeInTheDocument()
  })

  it('shows validation errors for empty fields', async () => {
    const user = userEvent.setup()
    
    render(
      <TestWrapper>
        <RegisterPage />
      </TestWrapper>
    )

    const submitButton = screen.getByRole('button', { name: /建立帳號/ })
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText('姓名為必填')).toBeInTheDocument()
      expect(screen.getByText('電子郵件為必填')).toBeInTheDocument()
      expect(screen.getByText('密碼為必填')).toBeInTheDocument()
    })
  })

  it('validates email format', async () => {
    const user = userEvent.setup()
    
    render(
      <TestWrapper>
        <RegisterPage />
      </TestWrapper>
    )

    const emailInput = screen.getByLabelText(/電子郵件/)
    await user.type(emailInput, 'invalid-email')
    await user.tab() // Trigger blur event

    await waitFor(() => {
      expect(screen.getByText('請輸入有效的電子郵件格式')).toBeInTheDocument()
    })
  })

  it('shows password strength indicator', async () => {
    const user = userEvent.setup()
    
    render(
      <TestWrapper>
        <RegisterPage />
      </TestWrapper>
    )

    const passwordInput = screen.getByLabelText(/密碼/)
    await user.type(passwordInput, 'weak')

    await waitFor(() => {
      expect(screen.getByText('密碼強度')).toBeInTheDocument()
      expect(screen.getByText('弱')).toBeInTheDocument()
    })

    // Test strong password
    await user.clear(passwordInput)
    await user.type(passwordInput, 'StrongPass123!')

    await waitFor(() => {
      expect(screen.getByText('強')).toBeInTheDocument()
    })
  })

  it('validates password strength requirements', async () => {
    const user = userEvent.setup()
    
    render(
      <TestWrapper>
        <RegisterPage />
      </TestWrapper>
    )

    const passwordInput = screen.getByLabelText(/密碼/)
    await user.type(passwordInput, 'weak123')

    await waitFor(() => {
      expect(screen.getByText('建議改善：')).toBeInTheDocument()
      expect(screen.getByText('包含大寫字母')).toBeInTheDocument()
    })
  })

  it('validates minimum name length', async () => {
    const user = userEvent.setup()
    
    render(
      <TestWrapper>
        <RegisterPage />
      </TestWrapper>
    )

    const nameInput = screen.getByLabelText(/姓名/)
    await user.type(nameInput, 'A')
    await user.tab()

    await waitFor(() => {
      expect(screen.getByText('姓名至少需要 2 個字元')).toBeInTheDocument()
    })
  })

  it('submits form with valid data', async () => {
    const user = userEvent.setup()
    mockAuthStore.register.mockResolvedValue(true)
    
    render(
      <TestWrapper>
        <RegisterPage />
      </TestWrapper>
    )

    // Fill form with valid data
    await user.type(screen.getByLabelText(/姓名/), 'John Doe')
    await user.type(screen.getByLabelText(/電子郵件/), 'john@example.com')
    await user.type(screen.getByLabelText(/密碼/), 'StrongPass123!')

    const submitButton = screen.getByRole('button', { name: /建立帳號/ })
    await user.click(submitButton)

    await waitFor(() => {
      expect(mockAuthStore.register).toHaveBeenCalledWith({
        name: 'John Doe',
        email: 'john@example.com',
        password: 'StrongPass123!'
      })
    })
  })

  it('shows loading state during submission', async () => {
    mockUseAuthStore.mockReturnValue({
      ...mockAuthStore,
      isLoading: true
    })
    
    render(
      <TestWrapper>
        <RegisterPage />
      </TestWrapper>
    )

    const submitButton = screen.getByRole('button', { name: /建立帳號/ })
    expect(submitButton).toBeDisabled()
    
    // All form fields should be disabled during loading
    expect(screen.getByLabelText(/姓名/)).toBeDisabled()
    expect(screen.getByLabelText(/電子郵件/)).toBeDisabled()
    expect(screen.getByLabelText(/密碼/)).toBeDisabled()
  })

  it('displays error message when registration fails', () => {
    const errorMessage = '註冊失敗：電子郵件已被使用'
    mockUseAuthStore.mockReturnValue({
      ...mockAuthStore,
      error: errorMessage
    })
    
    render(
      <TestWrapper>
        <RegisterPage />
      </TestWrapper>
    )

    expect(screen.getByText('註冊失敗')).toBeInTheDocument()
    expect(screen.getByText(errorMessage)).toBeInTheDocument()
  })

  it('clears error when close button is clicked', async () => {
    const user = userEvent.setup()
    mockUseAuthStore.mockReturnValue({
      ...mockAuthStore,
      error: '註冊失敗'
    })
    
    render(
      <TestWrapper>
        <RegisterPage />
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
        <RegisterPage />
      </TestWrapper>
    )

    expect(mockNavigate).toHaveBeenCalledWith('/chat', { replace: true })
  })

  it('shows success notification and navigates on successful registration', async () => {
    const user = userEvent.setup()
    mockAuthStore.register.mockResolvedValue(true)
    
    render(
      <TestWrapper>
        <RegisterPage />
      </TestWrapper>
    )

    // Fill and submit form
    await user.type(screen.getByLabelText(/姓名/), 'John Doe')
    await user.type(screen.getByLabelText(/電子郵件/), 'john@example.com')
    await user.type(screen.getByLabelText(/密碼/), 'StrongPass123!')
    
    const submitButton = screen.getByRole('button', { name: /建立帳號/ })
    await user.click(submitButton)

    await waitFor(() => {
      expect(mockNotifications.show).toHaveBeenCalledWith({
        title: '註冊成功！',
        message: '歡迎加入智能助理平台',
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
        <RegisterPage />
      </TestWrapper>
    )

    // Submit empty form to trigger validation errors
    const submitButton = screen.getByRole('button', { name: /建立帳號/ })
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

  it('has link to login page', () => {
    render(
      <TestWrapper>
        <RegisterPage />
      </TestWrapper>
    )

    const loginLink = screen.getByRole('link', { name: /立即登入/ })
    expect(loginLink).toBeInTheDocument()
    expect(loginLink).toHaveAttribute('href', '/login')
  })

  it('shows terms and privacy notice', () => {
    render(
      <TestWrapper>
        <RegisterPage />
      </TestWrapper>
    )

    expect(screen.getByText(/註冊即表示您同意我們的服務條款與隱私權政策/)).toBeInTheDocument()
  })
})