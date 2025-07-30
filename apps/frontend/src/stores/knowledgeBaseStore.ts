import { create } from 'zustand';
import { KnowledgeBase } from '@smart-assistant/shared-types';
import { apiService } from '../services/apiService';

interface KnowledgeBaseState {
  // 知識庫列表
  knowledgeBases: KnowledgeBase[];
  
  // 當前導入進度
  currentImport: KnowledgeBase | null;
  
  // 載入狀態
  isLoading: boolean;
  
  // 錯誤狀態
  error: string | null;
  
  // 動作
  createKnowledgeBase: (data: { name: string; path: string }) => Promise<void>;
  getKnowledgeBases: () => Promise<void>;
  refreshKnowledgeBases: () => Promise<void>;
  getKnowledgeBaseStatus: (id: string) => Promise<void>;
  clearError: () => void;
  setLoading: (loading: boolean) => void;
  
  // 輔助方法
  getKnowledgeBaseById: (id: string) => KnowledgeBase | null;
}

// 輪詢間隔（毫秒）
const POLLING_INTERVAL = 3000;
let pollingTimer: NodeJS.Timeout | null = null;

export const useKnowledgeBaseStore = create<KnowledgeBaseState>((set, get) => ({
  // 初始狀態
  knowledgeBases: [],
  currentImport: null,
  isLoading: false,
  error: null,

  // 建立新知識庫
  createKnowledgeBase: async (data: { name: string; path: string }) => {
    try {
      set({ isLoading: true, error: null });

      const newKnowledgeBase = await apiService.createKnowledgeBase(data);
      
      set((state) => ({
        knowledgeBases: [newKnowledgeBase, ...state.knowledgeBases],
        currentImport: newKnowledgeBase,
        isLoading: false
      }));

      // 開始輪詢狀態更新
      storeUtils.startPolling(newKnowledgeBase.id);

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '建立知識庫失敗';
      set({
        error: errorMessage,
        isLoading: false
      });
    }
  },

  // 獲取知識庫列表
  getKnowledgeBases: async () => {
    try {
      set({ isLoading: true, error: null });

      const knowledgeBases = await apiService.getKnowledgeBases();
      
      set({
        knowledgeBases,
        isLoading: false
      });

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '獲取知識庫列表失敗';
      set({
        error: errorMessage,
        isLoading: false
      });
    }
  },

  // 刷新知識庫列表
  refreshKnowledgeBases: async () => {
    await get().getKnowledgeBases();
  },

  // 獲取特定知識庫狀態
  getKnowledgeBaseStatus: async (id: string) => {
    try {
      const status = await apiService.getKnowledgeBaseStatus(id);
      
      set((state) => {
        const updatedKnowledgeBases = state.knowledgeBases.map(kb =>
          kb.id === id ? { ...kb, ...status } : kb
        );

        const updatedCurrentImport = state.currentImport?.id === id 
          ? { ...state.currentImport, ...status }
          : state.currentImport;

        return {
          knowledgeBases: updatedKnowledgeBases,
          currentImport: updatedCurrentImport,
        };
      });

      // 如果狀態已完成或錯誤，停止輪詢
      if (status.status === 'ready' || status.status === 'error') {
        storeUtils.stopPolling();
        
        // 如果是當前導入的項目，清除 currentImport
        if (get().currentImport?.id === id) {
          set({ currentImport: null });
        }
      }

    } catch (error) {
      console.error('獲取知識庫狀態失敗:', error);
    }
  },

  // 清除錯誤
  clearError: () => {
    set({ error: null });
  },

  // 設置載入狀態
  setLoading: (loading: boolean) => {
    set({ isLoading: loading });
  },

  // 根據 ID 獲取知識庫
  getKnowledgeBaseById: (id: string) => {
    const { knowledgeBases } = get();
    return knowledgeBases.find(kb => kb.id === id) || null;
  },

}));

// 在 store 定義外添加輪詢控制方法
const storeUtils = {
  // 開始輪詢狀態更新
  startPolling: (knowledgeBaseId: string) => {
    // 清除現有的輪詢
    storeUtils.stopPolling();

    pollingTimer = setInterval(async () => {
      const store = useKnowledgeBaseStore.getState();
      const knowledgeBase = store.getKnowledgeBaseById(knowledgeBaseId);
      
      // 如果知識庫不存在或已完成，停止輪詢
      if (!knowledgeBase || knowledgeBase.status === 'ready' || knowledgeBase.status === 'error') {
        storeUtils.stopPolling();
        return;
      }

      await store.getKnowledgeBaseStatus(knowledgeBaseId);
    }, POLLING_INTERVAL);
  },

  // 停止輪詢
  stopPolling: () => {
    if (pollingTimer) {
      clearInterval(pollingTimer);
      pollingTimer = null;
    }
  },
};


// 組件卸載時清理輪詢
if (typeof window !== 'undefined') {
  window.addEventListener('beforeunload', () => {
    if (pollingTimer) {
      clearInterval(pollingTimer);
    }
  });
}