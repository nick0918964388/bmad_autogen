# Coding Standards

本節定義了 `智能助理應用程式` 的程式碼規範和約定。這些標準對所有開發人員來說都是**強制性**的，旨在確保程式碼品質、可讀性和一致性，特別是對於 AI 代理人未來進行程式碼生成和修改時的理解能力。我們將聚焦於關鍵規則，避免過於瑣碎的細節。

### Critical Fullstack Rules

  * **型別共享 (Type Sharing)**: 所有前後端共享的 TypeScript 介面和型別，必須定義在 `packages/shared-types` 中，並從該處導入使用。
  * **API 呼叫 (API Calls)**: 前端**絕不**能直接發送 HTTP 請求。所有與後端 API 的通訊必須透過專門的服務層 (Service Layer) 進行，以確保統一的錯誤處理、身份驗證和數據轉換。
  * **環境變數 (Environment Variables)**: 只能透過定義好的配置物件或服務來存取環境變數，**絕不**能在程式碼中直接使用 `process.env` 或類似的全局變數，以確保配置的一致性和安全性。
  * **錯誤處理 (Error Handling)**: 所有 API 路由和重要的業務邏輯，必須使用標準化的錯誤處理機制，確保錯誤訊息的一致性，並避免將敏感資訊暴露在錯誤響應中。
  * **狀態更新 (State Updates)**: 在前端，**絕不**能直接修改狀態。必須使用相應的狀態管理模式（例如 Zustand 的 Setter 函數或 Reducer 模式）來更新狀態，以確保狀態的可追溯性和響應性。

### Naming Conventions

| Element | Frontend | Backend | Example |
| :---------------- | :--------------- | :---------------- | :--------------------------- |
| Components | PascalCase | - | `UserProfile.tsx` |
| Hooks | camelCase with 'use' | - | `useAuth.ts` |
| API Routes | - | kebab-case | `/api/user-profile` |
| Database Tables | - | snake\_case | `user_profiles` |
| API Schemas (Pydantic) | - | PascalCase | `UserSchema`, `MessageSchema` |
| Service Files | camelCase | snake\_case | `userService.ts`, `user_service.py` |
| AutoGen Agents | PascalCase + Agent | PascalCase + Agent | `UserProxyAgent`, `KnowledgeRetrievalAgent` |
| AutoGen Tools | snake\_case | snake\_case | `retrieve_knowledge`, `execute_task` |
