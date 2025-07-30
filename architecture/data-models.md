# Data Models

本節定義了 `智能助理應用程式` 的核心數據模型/實體，這些模型將在前端和後端之間共享。它們基於 PRD 的需求，並包含了關鍵屬性和關係。

### User (使用者)

  * **Purpose**: 儲存應用程式中使用者的基本資訊，包括本地註冊使用者和透過第三方登入的使用者。
  * **Key Attributes**:
      * `id`: `string` - 唯一使用者識別符。
      * `email`: `string` - 使用者的電子郵件地址（唯一）。
      * `passwordHash`: `string` - 加密過的使用者密碼（僅限本地登入）。
      * `googleId`: `string` - Google 帳號的唯一識別符（僅限 Google 登入）。
      * `name`: `string` - 使用者的名稱。
      * `createdAt`: `Date` - 帳號創建時間。
      * `updatedAt`: `Date` - 帳號最後更新時間。

#### TypeScript Interface

```typescript
interface User {
  id: string;
  email: string;
  passwordHash?: string; // Optional for Google login
  googleId?: string;     // Optional for local login
  name: string;
  createdAt: Date;
  updatedAt: Date;
}
```

#### Relationships

  * 與 `ChatSession` (一對多): 一個使用者可以有多個聊天會話。
  * 與 `KnowledgeBase` (一對多): 一個使用者可以有多個知識庫。

### ChatSession (聊天會話)

  * **Purpose**: 儲存使用者與智能助理之間的單次對話會話記錄。
  * **Key Attributes**:
      * `id`: `string` - 唯一會話識別符。
      * `userId`: `string` - 關聯的使用者 ID。
      * `title`: `string` - 會話標題（可自動生成或使用者編輯）。
      * `createdAt`: `Date` - 會話創建時間。
      * `updatedAt`: `Date` - 會話最後更新時間。

#### TypeScript Interface

```typescript
interface ChatSession {
  id: string;
  userId: string;
  title: string;
  createdAt: Date;
  updatedAt: Date;
}
```

#### Relationships

  * 與 `User` (多對一): 多個聊天會話屬於一個使用者。
  * 與 `Message` (一對多): 一個聊天會話可以有多條訊息。

### Message (訊息)

  * **Purpose**: 儲存單條聊天訊息的內容和發送者。
  * **Key Attributes**:
      * `id`: `string` - 唯一訊息識別符。
      * `sessionId`: `string` - 關聯的聊天會話 ID。
      * `sender`: `'user' | 'assistant' | 'system'` - 訊息發送者。
      * `content`: `string` - 訊息內容。
      * `timestamp`: `Date` - 訊息發送時間。
      * `toolCalls`: `any[]` - AutoGen 代理人呼叫工具的記錄 (如果適用)。
      * `toolOutputs`: `any[]` - AutoGen 工具執行輸出的記錄 (如果適用)。

#### TypeScript Interface

```typescript
interface Message {
  id: string;
  sessionId: string;
  sender: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  toolCalls?: any[];   // Optional, for AutoGen tool calls
  toolOutputs?: any[]; // Optional, for AutoGen tool outputs
}
```

#### Relationships

  * 與 `ChatSession` (多對一): 多條訊息屬於一個聊天會話。

### KnowledgeBase (知識庫)

  * **Purpose**: 代表使用者定義的一個文件資料夾，其內容被導入到向量資料庫中。
  * **Key Attributes**:
      * `id`: `string` - 唯一知識庫識別符。
      * `userId`: `string` - 關聯的使用者 ID。
      * `name`: `string` - 知識庫名稱（例如資料夾名稱）。
      * `path`: `string` - 使用者指定的本地文件資料夾路徑。
      * `status`: `'pending' | 'processing' | 'ready' | 'error'` - 導入狀態。
      * `importedAt`: `Date` - 最後導入時間。
      * `documentCount`: `number` - 已導入的文件數量。
      * `errorDetails`: `string` - 導入錯誤的詳細資訊。

#### TypeScript Interface

```typescript
interface KnowledgeBase {
  id: string;
  userId: string;
  name: string;
  path: string;
  status: 'pending' | 'processing' | 'ready' | 'error';
  importedAt: Date;
  documentCount: number;
  errorDetails?: string; // Optional, for error status
}
```

#### Relationships

  * 與 `User` (多對一): 多個知識庫屬於一個使用者。
  * 與 `DocumentChunk` (一對多): 一個知識庫包含多個文件分塊。

### DocumentChunk (文件分塊)

  * **Purpose**: 儲存從原始文件提取並分塊後的內容，以及其對應的 Embedding 向量。這是向量資料庫中的主要數據單元。
  * **Key Attributes**:
      * `id`: `string` - 唯一分塊識別符。
      * `knowledgeBaseId`: `string` - 關聯的知識庫 ID。
      * `documentPath`: `string` - 原始文件在本地的完整路徑。
      * `chunkIndex`: `number` - 該分塊在原始文件中的順序。
      * `content`: `string` - 分塊的文本內容。
      * `embedding`: `number[]` - Ollama `all-minilm:l6-v2` 模型生成的 Embedding 向量。
      * `createdAt`: `Date` - 分塊創建（Embedding 完成）時間。

#### TypeScript Interface

```typescript
interface DocumentChunk {
  id: string;
  knowledgeBaseId: string;
  documentPath: string;
  chunkIndex: number;
  content: string;
  embedding: number[]; // Array of numbers
  createdAt: Date;
}
```

#### Relationships

  * 與 `KnowledgeBase` (多對一): 多個文件分塊屬於一個知識庫。
