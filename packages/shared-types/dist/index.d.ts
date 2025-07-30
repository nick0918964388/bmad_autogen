export interface User {
    id: number;
    email: string;
    passwordHash?: string;
    googleId?: string;
    name: string;
    createdAt: Date;
    updatedAt: Date;
}
export interface ChatSession {
    id: string;
    userId: string;
    title: string;
    createdAt: Date;
    updatedAt: Date;
}
export interface Message {
    id: string;
    sessionId: string;
    sender: 'user' | 'assistant' | 'system';
    content: string;
    timestamp: Date;
    toolCalls?: any[];
    toolOutputs?: any[];
}
export interface KnowledgeBase {
    id: string;
    userId: string;
    name: string;
    path: string;
    status: 'pending' | 'processing' | 'ready' | 'error';
    importedAt: Date;
    documentCount: number;
    errorDetails?: string;
}
export interface DocumentChunk {
    id: string;
    knowledgeBaseId: string;
    documentPath: string;
    chunkIndex: number;
    content: string;
    embedding: number[];
    createdAt: Date;
}
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
export interface ApiError {
    error: {
        code: string;
        message: string;
        details?: Record<string, any>;
        timestamp: string;
        requestId: string;
    };
}
export interface HealthCheckResponse {
    status: 'healthy' | 'unhealthy';
    timestamp: string;
    services?: {
        database?: 'connected' | 'disconnected';
        ollama?: 'connected' | 'disconnected';
        vectorDb?: 'connected' | 'disconnected';
    };
}
