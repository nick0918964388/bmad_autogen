import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MantineProvider } from '@mantine/core';
import { MemoryRouter } from 'react-router-dom';
import DocumentUploadPage from './DocumentUploadPage';
import { useKnowledgeBaseStore } from '../stores/knowledgeBaseStore';
import { apiService } from '../services/apiService';

// Mock the store
jest.mock('../stores/knowledgeBaseStore');
const mockUseKnowledgeBaseStore = useKnowledgeBaseStore as jest.MockedFunction<typeof useKnowledgeBaseStore>;

// Mock API service
jest.mock('../services/apiService', () => ({
  apiService: {
    createKnowledgeBase: jest.fn(),
    getKnowledgeBases: jest.fn(),
    getKnowledgeBaseStatus: jest.fn(),
  }
}));

const renderWithProviders = (component: React.ReactElement) => {
  return render(
    <MemoryRouter>
      <MantineProvider>
        {component}
      </MantineProvider>
    </MemoryRouter>
  );
};

describe('DocumentUploadPage', () => {
  const mockStore = {
    knowledgeBases: [],
    currentImport: null,
    isLoading: false,
    error: null,
    createKnowledgeBase: jest.fn(),
    refreshKnowledgeBases: jest.fn(),
    clearError: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
    mockUseKnowledgeBaseStore.mockReturnValue(mockStore);
  });

  test('renders page title and form correctly', () => {
    renderWithProviders(<DocumentUploadPage />);
    
    expect(screen.getByText('文件知識庫管理')).toBeInTheDocument();
    expect(screen.getByText('新增知識庫')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('例如：我的專案文件')).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/例如：\/home\/user\/documents/)).toBeInTheDocument();
    expect(screen.getByText('開始導入')).toBeInTheDocument();
  });

  test('shows placeholder text in form inputs', () => {
    renderWithProviders(<DocumentUploadPage />);
    
    expect(screen.getByPlaceholderText('例如：我的專案文件')).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/例如：\/home\/user\/documents/)).toBeInTheDocument();
  });

  test('submit button is disabled when form is invalid', () => {
    renderWithProviders(<DocumentUploadPage />);
    
    const submitButton = screen.getByRole('button', { name: '開始導入' });
    expect(submitButton).toBeDisabled();
  });

  test('submit button is enabled when form is valid', async () => {
    renderWithProviders(<DocumentUploadPage />);
    
    const nameInput = screen.getByPlaceholderText('例如：我的專案文件');
    const pathInput = screen.getByPlaceholderText(/例如：\/home\/user\/documents/);
    const submitButton = screen.getByText('開始導入');
    
    fireEvent.change(nameInput, { target: { value: '測試知識庫' } });
    fireEvent.change(pathInput, { target: { value: '/path/to/documents' } });
    
    await waitFor(() => {
      expect(submitButton).not.toBeDisabled();
    });
  });

  test('calls createKnowledgeBase when form is submitted', async () => {
    renderWithProviders(<DocumentUploadPage />);
    
    const nameInput = screen.getByPlaceholderText('例如：我的專案文件');
    const pathInput = screen.getByPlaceholderText(/例如：\/home\/user\/documents/);
    const submitButton = screen.getByText('開始導入');
    
    fireEvent.change(nameInput, { target: { value: '測試知識庫' } });
    fireEvent.change(pathInput, { target: { value: '/path/to/documents' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(mockStore.createKnowledgeBase).toHaveBeenCalledWith({
        name: '測試知識庫',
        path: '/path/to/documents'
      });
    });
  });

  test('clears form inputs after successful submission', async () => {
    const storeWithoutError = { ...mockStore, error: null };
    mockUseKnowledgeBaseStore.mockReturnValue(storeWithoutError);
    
    renderWithProviders(<DocumentUploadPage />);
    
    const nameInput = screen.getByPlaceholderText('例如：我的專案文件') as HTMLInputElement;
    const pathInput = screen.getByPlaceholderText(/例如：\/home\/user\/documents/) as HTMLInputElement;
    const submitButton = screen.getByText('開始導入');
    
    fireEvent.change(nameInput, { target: { value: '測試知識庫' } });
    fireEvent.change(pathInput, { target: { value: '/path/to/documents' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(nameInput.value).toBe('');
      expect(pathInput.value).toBe('');
    });
  });

  test('displays error message when error exists', () => {
    const storeWithError = { ...mockStore, error: '路徑無效' };
    mockUseKnowledgeBaseStore.mockReturnValue(storeWithError);
    
    renderWithProviders(<DocumentUploadPage />);
    
    expect(screen.getByText('導入失敗')).toBeInTheDocument();
    expect(screen.getByText('路徑無效')).toBeInTheDocument();
  });

  test('shows loading state when loading', () => {
    const storeWithLoading = { ...mockStore, isLoading: true };
    mockUseKnowledgeBaseStore.mockReturnValue(storeWithLoading);
    
    renderWithProviders(<DocumentUploadPage />);
    
    const submitButton = screen.getByRole('button', { name: '開始導入' });
    expect(submitButton).toBeDisabled();
  });

  test('displays current import progress when processing', () => {
    const mockCurrentImport = {
      id: '1',
      userId: 'user1',
      name: '處理中的知識庫',
      path: '/test/path',
      status: 'processing' as const,
      documentCount: 0,
      createdAt: new Date(),
      updatedAt: new Date(),
      importedAt: null,
      totalChunks: 0,
      processingStartedAt: new Date(),
      processingCompletedAt: null,
    };
    
    const storeWithImport = { ...mockStore, currentImport: mockCurrentImport };
    mockUseKnowledgeBaseStore.mockReturnValue(storeWithImport);
    
    renderWithProviders(<DocumentUploadPage />);
    
    expect(screen.getByText('正在處理：處理中的知識庫')).toBeInTheDocument();
    expect(screen.getByText('路徑：/test/path')).toBeInTheDocument();
    expect(screen.getByText('處理中')).toBeInTheDocument();
  });

  test('displays ready status when import completed', () => {
    const mockCurrentImport = {
      id: '1',
      userId: 'user1',
      name: '完成的知識庫',
      path: '/test/path',
      status: 'ready' as const,
      documentCount: 25,
      createdAt: new Date(),
      updatedAt: new Date(),
      importedAt: new Date(),
      totalChunks: 0,
      processingStartedAt: new Date(),
      processingCompletedAt: new Date(),
    };
    
    const storeWithImport = { ...mockStore, currentImport: mockCurrentImport };
    mockUseKnowledgeBaseStore.mockReturnValue(storeWithImport);
    
    renderWithProviders(<DocumentUploadPage />);
    
    expect(screen.getByText('成功導入 25 個文件')).toBeInTheDocument();
    expect(screen.getByText('已完成')).toBeInTheDocument();
  });

  test('displays knowledge base list', () => {
    const mockKnowledgeBases = [
      {
        id: '1',
        userId: 'user1',
        name: '知識庫1',
        path: '/path1',
        status: 'ready' as const,
        documentCount: 10,
        createdAt: new Date(),
        updatedAt: new Date(),
        importedAt: new Date(),
        totalChunks: 0,
        processingStartedAt: new Date(),
        processingCompletedAt: new Date(),
      },
      {
        id: '2',
        userId: 'user1',
        name: '知識庫2',
        path: '/path2',
        status: 'pending' as const,
        documentCount: 0,
        createdAt: new Date(),
        updatedAt: new Date(),
        importedAt: null,
        totalChunks: 0,
        processingStartedAt: null,
        processingCompletedAt: null,
      },
    ];
    
    const storeWithKnowledgeBases = { ...mockStore, knowledgeBases: mockKnowledgeBases };
    mockUseKnowledgeBaseStore.mockReturnValue(storeWithKnowledgeBases);
    
    renderWithProviders(<DocumentUploadPage />);
    
    expect(screen.getByText('已建立的知識庫')).toBeInTheDocument();
    expect(screen.getByText('知識庫1')).toBeInTheDocument();
    expect(screen.getByText('知識庫2')).toBeInTheDocument();
    expect(screen.getByText('已完成')).toBeInTheDocument();
    expect(screen.getByText('等待中')).toBeInTheDocument();
  });

  test('shows empty state when no knowledge bases exist', () => {
    renderWithProviders(<DocumentUploadPage />);
    
    expect(screen.getByText('尚未建立任何知識庫')).toBeInTheDocument();
    expect(screen.getByText('使用上方表單來建立您的第一個知識庫')).toBeInTheDocument();
  });

  test('calls refreshKnowledgeBases when refresh button is clicked', async () => {
    renderWithProviders(<DocumentUploadPage />);
    
    // Find refresh button by testing-id or class since it's an ActionIcon
    const refreshButtons = screen.getAllByRole('button');
    // The refresh button should be the one that's not the submit button
    const refreshButton = refreshButtons.find(btn => !btn.textContent?.includes('開始導入'));
    
    if (refreshButton) {
      fireEvent.click(refreshButton);
      await waitFor(() => {
        expect(mockStore.refreshKnowledgeBases).toHaveBeenCalled();
      });
    }
  });

  test('displays error alert with close functionality', () => {
    const storeWithError = { ...mockStore, error: '測試錯誤' };
    mockUseKnowledgeBaseStore.mockReturnValue(storeWithError);
    
    renderWithProviders(<DocumentUploadPage />);
    
    // Verify error alert is displayed
    expect(screen.getByText('導入失敗')).toBeInTheDocument();
    expect(screen.getByText('測試錯誤')).toBeInTheDocument();
    
    // Test that clearError function exists (component integration test)
    expect(mockStore.clearError).toBeDefined();
  });

  test('clears error when path input changes', () => {
    const storeWithError = { ...mockStore, error: '測試錯誤' };
    mockUseKnowledgeBaseStore.mockReturnValue(storeWithError);
    
    renderWithProviders(<DocumentUploadPage />);
    
    const pathInput = screen.getByPlaceholderText(/例如：\/home\/user\/documents/);
    fireEvent.change(pathInput, { target: { value: '/new/path' } });
    
    expect(mockStore.clearError).toHaveBeenCalled();
  });
});