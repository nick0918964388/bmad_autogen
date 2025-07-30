import { create } from 'zustand';
import { ChatSession, Message } from '@smart-assistant/shared-types';

interface ChatState {
  // 聊天會話相關狀態
  sessions: ChatSession[];
  activeSessionId: string | null;
  
  // 訊息相關狀態
  messages: Record<string, Message[]>; // sessionId -> messages[]
  isLoading: boolean;
  
  // 會話管理動作
  createSession: (title?: string) => string;
  selectSession: (sessionId: string) => void;
  deleteSession: (sessionId: string) => void;
  updateSessionTitle: (sessionId: string, title: string) => void;
  
  // 訊息管理動作
  addMessage: (sessionId: string, message: Omit<Message, 'id' | 'timestamp'>) => void;
  sendMessage: (content: string) => Promise<void>;
  setLoading: (loading: boolean) => void;
  
  // 輔助方法
  getActiveSession: () => ChatSession | null;
  getActiveMessages: () => Message[];
  clearAllSessions: () => void;
}

// 生成唯一 ID 的輔助函數
const generateId = () => {
  return Date.now().toString(36) + Math.random().toString(36).substr(2);
};

// 生成會話標題的輔助函數
const generateSessionTitle = (firstMessage?: string) => {
  if (firstMessage) {
    return firstMessage.length > 30 
      ? firstMessage.substring(0, 30) + '...' 
      : firstMessage;
  }
  return `新對話 ${new Date().toLocaleString('zh-TW', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })}`;
};

export const useChatStore = create<ChatState>((set, get) => ({
  // 初始狀態
  sessions: [],
  activeSessionId: null,
  messages: {},
  isLoading: false,

  // 會話管理動作
  createSession: (title?: string) => {
    const sessionId = generateId();
    const now = new Date();
    
    const newSession: ChatSession = {
      id: sessionId,
      userId: 'current-user', // TODO: 後續從認證系統獲取
      title: title || generateSessionTitle(),
      createdAt: now,
      updatedAt: now,
    };

    set((state) => ({
      sessions: [newSession, ...state.sessions],
      activeSessionId: sessionId,
      messages: {
        ...state.messages,
        [sessionId]: []
      }
    }));

    return sessionId;
  },

  selectSession: (sessionId: string) => {
    const { sessions } = get();
    const session = sessions.find(s => s.id === sessionId);
    
    if (session) {
      set({ activeSessionId: sessionId });
    }
  },

  deleteSession: (sessionId: string) => {
    set((state) => {
      const newSessions = state.sessions.filter(s => s.id !== sessionId);
      const newMessages = { ...state.messages };
      delete newMessages[sessionId];
      
      // 如果刪除的是當前活動會話，選擇第一個可用會話或設為 null
      let newActiveSessionId = state.activeSessionId;
      if (state.activeSessionId === sessionId) {
        newActiveSessionId = newSessions.length > 0 ? newSessions[0].id : null;
      }

      return {
        sessions: newSessions,
        messages: newMessages,
        activeSessionId: newActiveSessionId
      };
    });
  },

  updateSessionTitle: (sessionId: string, title: string) => {
    set((state) => ({
      sessions: state.sessions.map(session =>
        session.id === sessionId
          ? { ...session, title, updatedAt: new Date() }
          : session
      )
    }));
  },

  // 訊息管理動作
  addMessage: (sessionId: string, messageData: Omit<Message, 'id' | 'timestamp'>) => {
    const messageId = generateId();
    const now = new Date();
    
    const newMessage: Message = {
      ...messageData,
      id: messageId,
      timestamp: now,
    };

    set((state) => {
      const sessionMessages = state.messages[sessionId] || [];
      
      return {
        messages: {
          ...state.messages,
          [sessionId]: [...sessionMessages, newMessage]
        },
        // 更新會話的最後更新時間
        sessions: state.sessions.map(session =>
          session.id === sessionId
            ? { ...session, updatedAt: now }
            : session
        )
      };
    });
  },

  sendMessage: async (content: string) => {
    const { activeSessionId, addMessage, setLoading, createSession } = get();
    
    // 如果沒有活動會話，創建新會話
    let sessionId = activeSessionId;
    if (!sessionId) {
      sessionId = createSession(generateSessionTitle(content));
    }

    // 添加使用者訊息
    addMessage(sessionId, {
      sessionId,
      sender: 'user',
      content,
    });

    // 設置載入狀態
    setLoading(true);

    try {
      // TODO: 後續實現與後端 API 的整合
      // 模擬 API 呼叫延遲
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // 模擬助理回應
      const assistantResponse = `收到您的訊息：「${content}」。這是一個模擬回應，後續將整合實際的 AutoGen 後端。`;
      
      addMessage(sessionId, {
        sessionId,
        sender: 'assistant',
        content: assistantResponse,
      });

    } catch (error) {
      console.error('發送訊息失敗:', error);
      
      // 添加錯誤訊息
      addMessage(sessionId, {
        sessionId,
        sender: 'system',
        content: '抱歉，發送訊息時發生錯誤，請稍後重試。',
      });
    } finally {
      setLoading(false);
    }
  },

  setLoading: (loading: boolean) => {
    set({ isLoading: loading });
  },

  // 輔助方法
  getActiveSession: () => {
    const { sessions, activeSessionId } = get();
    return sessions.find(s => s.id === activeSessionId) || null;
  },

  getActiveMessages: () => {
    const { messages, activeSessionId } = get();
    return activeSessionId ? messages[activeSessionId] || [] : [];
  },

  clearAllSessions: () => {
    set({
      sessions: [],
      activeSessionId: null,
      messages: {},
      isLoading: false
    });
  },
}));