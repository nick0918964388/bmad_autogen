import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MantineProvider } from '@mantine/core'
import { Notifications } from '@mantine/notifications'
import App from './App'
import { apiService } from './services/apiService'

// Mock the API service
jest.mock('./services/apiService')
const mockApiService = apiService as jest.Mocked<typeof apiService>

const renderWithMantine = (component: React.ReactElement) => {
  return render(
    <MantineProvider>
      <Notifications />
      {component}
    </MantineProvider>
  )
}

describe('App', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  test('renders app title', () => {
    mockApiService.checkHealth.mockResolvedValue({
      status: 'healthy',
      timestamp: '2025-07-30T10:00:00Z'
    })
    
    renderWithMantine(<App />)
    expect(screen.getByText(/智能助理應用程式/)).toBeInTheDocument()
  })

  test('shows frontend status as running', () => {
    mockApiService.checkHealth.mockResolvedValue({
      status: 'healthy',
      timestamp: '2025-07-30T10:00:00Z'
    })

    renderWithMantine(<App />)
    expect(screen.getByText(/前端服務:/)).toBeInTheDocument()
    expect(screen.getByText(/✓ 運行中/)).toBeInTheDocument()
  })

  test('renders test connection button', () => {
    mockApiService.checkHealth.mockResolvedValue({
      status: 'healthy',
      timestamp: '2025-07-30T10:00:00Z'
    })

    renderWithMantine(<App />)
    expect(screen.getByText(/重新測試後端連接/)).toBeInTheDocument()
  })

  test('shows connected status when backend health check succeeds', async () => {
    mockApiService.checkHealth.mockResolvedValue({
      status: 'healthy',
      timestamp: '2025-07-30T10:00:00Z'
    })

    renderWithMantine(<App />)

    await waitFor(() => {
      expect(screen.getByText(/✓ 已連接/)).toBeInTheDocument()
    })
  })

  test('shows disconnected status when backend health check fails', async () => {
    mockApiService.checkHealth.mockRejectedValue(new Error('Connection failed'))

    renderWithMantine(<App />)

    await waitFor(() => {
      expect(screen.getByText(/✗ 未連接/)).toBeInTheDocument()
    })
  })

  test('retests connection when button is clicked', async () => {
    mockApiService.checkHealth.mockResolvedValue({
      status: 'healthy',
      timestamp: '2025-07-30T10:00:00Z'
    })

    renderWithMantine(<App />)
    
    const testButton = screen.getByText(/重新測試後端連接/)
    fireEvent.click(testButton)

    await waitFor(() => {
      expect(mockApiService.checkHealth).toHaveBeenCalledTimes(2) // Initial + button click
    })
  })
})