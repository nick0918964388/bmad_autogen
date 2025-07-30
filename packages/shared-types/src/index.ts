// 智能助理應用程式共享型別定義
// 基於架構文件中定義的數據模型

// 使用者相關型別
export interface User {
  id: number;
  email: string;
  passwordHash?: string; // Optional for Google login
  googleId?: string;     // Optional for local login
  name: string;
  createdAt: Date;
  updatedAt: Date;
}

// 聊天會話型別
export interface ChatSession {
  id: string;
  userId: string;
  title: string;
  createdAt: Date;
  updatedAt: Date;
}

// 訊息型別
export interface Message {
  id: string;
  sessionId: string;
  sender: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  toolCalls?: any[];   // Optional, for AutoGen tool calls
  toolOutputs?: any[]; // Optional, for AutoGen tool outputs
}

// 知識庫型別
export interface KnowledgeBase {
  id: string;
  userId: string;
  name: string;
  path: string;
  status: 'pending' | 'processing' | 'ready' | 'error';
  documentCount: number;
  errorDetails?: string; // Optional, for error status
  createdAt: Date;
  updatedAt: Date;
  importedAt: Date | null;
  totalChunks: number;
  processingStartedAt: Date | null;
  processingCompletedAt: Date | null;
}

// 文件分塊型別
export interface DocumentChunk {
  id: string;
  knowledgeBaseId: string;
  documentPath: string;
  chunkIndex: number;
  content: string;
  embedding: number[]; // Array of numbers
  createdAt: Date;
}

// 身份驗證相關型別
export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: {
    id: number;
    email: string;
    name: string;
  };
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  name: string;
}

export interface AuthUser {
  id: number;
  email: string;
  name: string;
}

// API 錯誤回應型別
export interface ApiError {
  error: {
    code: string;       // 內部錯誤碼
    message: string;    // 使用者友善的錯誤訊息
    details?: Record<string, any>; // 額外詳細資訊
    timestamp: string;  // 錯誤發生時間 (ISO 8601 格式)
    requestId: string;  // 請求 ID (用於日誌追蹤)
  };
}

// 健康檢查回應型別
export interface HealthCheckResponse {
  status: 'healthy' | 'unhealthy';
  timestamp: string;
  services?: {
    database?: 'connected' | 'disconnected';
    ollama?: 'connected' | 'disconnected';
    vectorDb?: 'connected' | 'disconnected';
  };
}