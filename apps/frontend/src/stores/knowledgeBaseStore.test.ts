import { useKnowledgeBaseStore } from './knowledgeBaseStore';
import { apiService } from '../services/apiService';
import { KnowledgeBase } from '@smart-assistant/shared-types';

// Mock API service
jest.mock('../services/apiService', () => ({
  apiService: {
    createKnowledgeBase: jest.fn(),
    getKnowledgeBases: jest.fn(),
    getKnowledgeBaseStatus: jest.fn(),
  }
}));

// Mock timers for polling functionality
jest.useFakeTimers();

describe('knowledgeBaseStore', () => {
  beforeEach(() => {
    // Reset store state
    const store = useKnowledgeBaseStore.getState();
    store.knowledgeBases = [];
    store.currentImport = null;
    store.isLoading = false;
    store.error = null;
    
    // Clear all mocks
    jest.clearAllMocks();
  });

  afterEach(() => {
    jest.clearAllTimers();
  });

  test('initial state should be correct', () => {
    const state = useKnowledgeBaseStore.getState();
    
    expect(state.knowledgeBases).toEqual([]);
    expect(state.currentImport).toBeNull();
    expect(state.isLoading).toBe(false);
    expect(state.error).toBeNull();
  });

  test('createKnowledgeBase should call API and update state on success', async () => {
    const mockKnowledgeBase: KnowledgeBase = {
      id: 'kb-1',
      userId: 'user-1',
      name: '測試知識庫',
      path: '/test/path',
      status: 'pending',
      documentCount: 0,
      createdAt: new Date(),
      updatedAt: new Date(),
      importedAt: null,
      totalChunks: 0,
      processingStartedAt: null,
      processingCompletedAt: null,
    };

    (apiService.createKnowledgeBase as jest.Mock).mockResolvedValue(mockKnowledgeBase);

    const store = useKnowledgeBaseStore.getState();
    await store.createKnowledgeBase({ name: '測試知識庫', path: '/test/path' });

    expect(apiService.createKnowledgeBase).toHaveBeenCalledWith({
      name: '測試知識庫',
      path: '/test/path'
    });

    const state = useKnowledgeBaseStore.getState();
    expect(state.knowledgeBases).toContain(mockKnowledgeBase);
    expect(state.currentImport).toBe(mockKnowledgeBase);
    expect(state.isLoading).toBe(false);
    expect(state.error).toBeNull();
  });

  test('createKnowledgeBase should handle API errors', async () => {
    const errorMessage = '路徑無效';
    (apiService.createKnowledgeBase as jest.Mock).mockRejectedValue(new Error(errorMessage));

    const store = useKnowledgeBaseStore.getState();
    await store.createKnowledgeBase({ name: '測試知識庫', path: '/invalid/path' });

    const state = useKnowledgeBaseStore.getState();
    expect(state.error).toBe(errorMessage);
    expect(state.isLoading).toBe(false);
    expect(state.knowledgeBases).toEqual([]);
    expect(state.currentImport).toBeNull();
  });

  test('getKnowledgeBases should fetch and update knowledge bases list', async () => {
    const mockKnowledgeBases: KnowledgeBase[] = [
      {
        id: 'kb-1',
        userId: 'user-1',
        name: '知識庫1',
        path: '/path1',
        status: 'ready',
        documentCount: 10,
        createdAt: new Date(),
        updatedAt: new Date(),
        importedAt: new Date(),
        totalChunks: 25,
        processingStartedAt: new Date(),
        processingCompletedAt: new Date(),
      },
      {
        id: 'kb-2',
        userId: 'user-1',
        name: '知識庫2',
        path: '/path2',
        status: 'processing',
        documentCount: 0,
        createdAt: new Date(),
        updatedAt: new Date(),
        importedAt: null,
        totalChunks: 0,
        processingStartedAt: new Date(),
        processingCompletedAt: null,
      },
    ];

    (apiService.getKnowledgeBases as jest.Mock).mockResolvedValue(mockKnowledgeBases);

    const store = useKnowledgeBaseStore.getState();
    await store.getKnowledgeBases();

    expect(apiService.getKnowledgeBases).toHaveBeenCalled();

    const state = useKnowledgeBaseStore.getState();
    expect(state.knowledgeBases).toEqual(mockKnowledgeBases);
    expect(state.isLoading).toBe(false);
    expect(state.error).toBeNull();
  });

  test('getKnowledgeBases should handle API errors', async () => {
    const errorMessage = '獲取知識庫列表失敗';
    (apiService.getKnowledgeBases as jest.Mock).mockRejectedValue(new Error(errorMessage));

    const store = useKnowledgeBaseStore.getState();
    await store.getKnowledgeBases();

    const state = useKnowledgeBaseStore.getState();
    expect(state.error).toBe(errorMessage);
    expect(state.isLoading).toBe(false);
  });

  test('refreshKnowledgeBases should call getKnowledgeBases', async () => {
    const store = useKnowledgeBaseStore.getState();
    const getKnowledgeBasesSpy = jest.spyOn(store, 'getKnowledgeBases');

    await store.refreshKnowledgeBases();

    expect(getKnowledgeBasesSpy).toHaveBeenCalled();
  });

  test('getKnowledgeBaseStatus should update specific knowledge base status', async () => {
    const initialKnowledgeBase: KnowledgeBase = {
      id: 'kb-1',
      userId: 'user-1',
      name: '測試知識庫',
      path: '/test/path',
      status: 'processing',
      documentCount: 0,
      createdAt: new Date(),
      updatedAt: new Date(),
      importedAt: null,
      totalChunks: 0,
      processingStartedAt: new Date(),
      processingCompletedAt: null,
    };

    // Set initial state
    useKnowledgeBaseStore.setState({
      knowledgeBases: [initialKnowledgeBase],
      currentImport: initialKnowledgeBase,
    });

    const statusUpdate = {
      status: 'ready' as const,
      documentCount: 15,
      totalChunks: 45,
    };

    (apiService.getKnowledgeBaseStatus as jest.Mock).mockResolvedValue(statusUpdate);

    const store = useKnowledgeBaseStore.getState();
    await store.getKnowledgeBaseStatus('kb-1');

    expect(apiService.getKnowledgeBaseStatus).toHaveBeenCalledWith('kb-1');

    const state = useKnowledgeBaseStore.getState();
    const updatedKb = state.knowledgeBases.find(kb => kb.id === 'kb-1');
    expect(updatedKb?.status).toBe('ready');
    expect(updatedKb?.documentCount).toBe(15);
    expect(updatedKb?.totalChunks).toBe(45);

    // Should clear currentImport when status is ready
    expect(state.currentImport).toBeNull();
  });

  test('getKnowledgeBaseStatus should clear currentImport when status is error', async () => {
    const initialKnowledgeBase: KnowledgeBase = {
      id: 'kb-1',
      userId: 'user-1',
      name: '測試知識庫',
      path: '/test/path',
      status: 'processing',
      documentCount: 0,
      createdAt: new Date(),
      updatedAt: new Date(),
      importedAt: null,
      totalChunks: 0,
      processingStartedAt: new Date(),
      processingCompletedAt: null,
    };

    useKnowledgeBaseStore.setState({
      knowledgeBases: [initialKnowledgeBase],
      currentImport: initialKnowledgeBase,
    });

    const statusUpdate = {
      status: 'error' as const,
      errorDetails: '處理失敗',
    };

    (apiService.getKnowledgeBaseStatus as jest.Mock).mockResolvedValue(statusUpdate);

    const store = useKnowledgeBaseStore.getState();
    await store.getKnowledgeBaseStatus('kb-1');

    const state = useKnowledgeBaseStore.getState();
    expect(state.currentImport).toBeNull();
  });

  test('clearError should reset error state', () => {
    useKnowledgeBaseStore.setState({ error: '測試錯誤' });

    const store = useKnowledgeBaseStore.getState();
    store.clearError();

    const state = useKnowledgeBaseStore.getState();
    expect(state.error).toBeNull();
  });

  test('setLoading should update loading state', () => {
    const store = useKnowledgeBaseStore.getState();
    
    store.setLoading(true);
    expect(useKnowledgeBaseStore.getState().isLoading).toBe(true);
    
    store.setLoading(false);
    expect(useKnowledgeBaseStore.getState().isLoading).toBe(false);
  });

  test('getKnowledgeBaseById should return correct knowledge base', () => {
    const knowledgeBase: KnowledgeBase = {
      id: 'kb-1',
      userId: 'user-1',
      name: '測試知識庫',
      path: '/test/path',
      status: 'ready',
      documentCount: 10,
      createdAt: new Date(),
      updatedAt: new Date(),
      importedAt: new Date(),
      totalChunks: 25,
      processingStartedAt: new Date(),
      processingCompletedAt: new Date(),
    };

    useKnowledgeBaseStore.setState({ knowledgeBases: [knowledgeBase] });

    const store = useKnowledgeBaseStore.getState();
    const result = store.getKnowledgeBaseById('kb-1');

    expect(result).toBe(knowledgeBase);
  });

  test('getKnowledgeBaseById should return null for non-existent ID', () => {
    const store = useKnowledgeBaseStore.getState();
    const result = store.getKnowledgeBaseById('non-existent');

    expect(result).toBeNull();
  });

  test('should handle multiple knowledge bases in list', async () => {
    const kb1: KnowledgeBase = {
      id: 'kb-1',
      userId: 'user-1',
      name: '知識庫1',
      path: '/path1',
      status: 'ready',
      documentCount: 10,
      createdAt: new Date(),
      updatedAt: new Date(),
      importedAt: new Date(),
      totalChunks: 25,
      processingStartedAt: new Date(),
      processingCompletedAt: new Date(),
    };

    const kb2: KnowledgeBase = {
      id: 'kb-2',
      userId: 'user-1',
      name: '知識庫2',
      path: '/path2',
      status: 'processing',
      documentCount: 0,
      createdAt: new Date(),
      updatedAt: new Date(),
      importedAt: null,
      totalChunks: 0,
      processingStartedAt: new Date(),
      processingCompletedAt: null,
    };

    (apiService.createKnowledgeBase as jest.Mock).mockResolvedValue(kb2);

    // Add first knowledge base
    useKnowledgeBaseStore.setState({ knowledgeBases: [kb1] });

    // Create second knowledge base
    const store = useKnowledgeBaseStore.getState();
    await store.createKnowledgeBase({ name: '知識庫2', path: '/path2' });

    const state = useKnowledgeBaseStore.getState();
    expect(state.knowledgeBases).toHaveLength(2);
    expect(state.knowledgeBases).toContain(kb1);
    expect(state.knowledgeBases).toContain(kb2);
    expect(state.currentImport).toBe(kb2);
  });

  test('should handle concurrent API calls gracefully', async () => {
    const mockKnowledgeBases: KnowledgeBase[] = [
      {
        id: 'kb-1',
        userId: 'user-1',
        name: '知識庫1',
        path: '/path1',
        status: 'ready',
        documentCount: 10,
        createdAt: new Date(),
        updatedAt: new Date(),
        importedAt: new Date(),
        totalChunks: 25,
        processingStartedAt: new Date(),
        processingCompletedAt: new Date(),
      },
    ];

    (apiService.getKnowledgeBases as jest.Mock).mockResolvedValue(mockKnowledgeBases);

    const store = useKnowledgeBaseStore.getState();
    
    // Start multiple concurrent calls
    const promises = [
      store.getKnowledgeBases(),
      store.getKnowledgeBases(),
      store.getKnowledgeBases(),
    ];

    await Promise.all(promises);

    // Should have been called multiple times
    expect(apiService.getKnowledgeBases).toHaveBeenCalledTimes(3);
    
    const state = useKnowledgeBaseStore.getState();
    expect(state.knowledgeBases).toEqual(mockKnowledgeBases);
  });
});