# Epic Details

### Epic 1: 專案基礎與核心 Chatbot 介面

[cite_start]**Epic Goal**: 建立智能助理應用程式的基礎框架，包括前後端分離的 Docker Compose 部署設定，完成核心 Chatbot 的 UI 介面，並實現使用者本地帳號的註冊與登入功能 [cite: 470][cite_start]。此 Epic 將為整個應用程式的後續開發奠定穩固的基礎 [cite: 470]。

#### Story 1.1: 專案初始化與 Docker Compose 環境建置

**As a** 開發者,
**I want** 能夠透過 Docker Compose 啟動前後端應用程式的開發環境,
[cite_start]**so that** 我可以快速開始專案開發並確保環境一致性 [cite: 476]。

##### Acceptance Criteria

1.  [cite_start]AC1: 專案根目錄下存在一個 `docker-compose.yml` 檔案，能夠同時啟動前端和後端服務 [cite: 477]。
2.  [cite_start]AC2: 前端服務 (React + Mantine) 能夠在 Docker 容器中成功啟動並顯示初始頁面 [cite: 477]。
3.  [cite_start]AC3: 後端服務 (FastAPI) 能夠在 Docker 容器中成功啟動並暴露 API 接口 [cite: 477]。
4.  [cite_start]AC4: 前後端服務之間能夠透過 Docker 網路進行通訊 [cite: 477]。
5.  [cite_start]AC5: 專案包含必要的 `Dockerfile` 和依賴設定文件 (如 `package.json`, `requirements.txt`)，用於建構前後端映像 [cite: 477]。

#### Story 1.2: 基礎 Chatbot UI 介面開發

**As a** 使用者,
**I want** 能夠看到一個類似 Gemini 風格的基礎 Chatbot 介面,
[cite_start]**so that** 我可以直觀地開始與智能助理互動 [cite: 476]。

##### Acceptance Criteria

1.  [cite_start]AC1: 介面包含一個主對話區，用於顯示智能助理和使用者的對話內容 [cite: 478]。
2.  [cite_start]AC2: 介面包含一個歷史聊天區，位於側邊或左側，用於顯示過去的對話列表 [cite: 478]。
3.  [cite_start]AC3: 初始狀態下，對話區中央顯示一個輸入框，引導使用者輸入 [cite: 478]。
4.  [cite_start]AC4: 當使用者在輸入框中輸入文字後，輸入框能夠自動置底 [cite: 478]。
5.  [cite_start]AC5: 介面風格簡潔、現代，符合類似 Gemini 的視覺設計原則 [cite: 478]。
6.  [cite_start]AC6: 前端介面使用 React 18 和 Mantine 7 開發 [cite: 478]。

#### Story 1.3: 使用者本地帳號註冊與登入功能

**As a** 使用者,
**I want** 能夠註冊一個本地帳號並登入智能助理應用程式,
[cite_start]**so that** 我可以擁有個人化的使用體驗和資料 [cite: 476]。

##### Acceptance Criteria

1.  [cite_start]AC1: 應用程式提供一個註冊介面，使用者可以輸入電子郵件和密碼來創建新帳號 [cite: 478]。
2.  [cite_start]AC2: 應用程式提供一個登入介面，使用者可以使用已註冊的電子郵件和密碼進行登入 [cite: 478]。
3.  [cite_start]AC3: 成功註冊或登入後，使用者能夠進入 Chatbot 主介面 [cite: 478]。
4.  [cite_start]AC4: 後端實作使用者帳號的儲存，並對密碼進行安全加密（例如使用 bcrypt） [cite: 478]。
5.  [cite_start]AC5: 後端登入 API 能夠安全地驗證使用者憑證，並返回身份驗證憑證（例如 JWT） [cite: 478]。
6.  [cite_start]AC6: 註冊和登入介面提供必要的輸入驗證和錯誤訊息提示 [cite: 478]。

### Epic 2: 知識庫管理與智能互動基礎

[cite_start]**Epic Goal**: 實現智能助理的文件知識庫管理功能，允許使用者自訂文件資料夾路徑，並將其內容透過 Ollama Embedding 模型存入向量資料庫，從而使智能助理能夠利用這些知識進行基礎的智能互動 [cite: 532]。

#### Story 2.1: 文件資料夾路徑自訂與文件上傳介面

**As a** 使用者,
**I want** 能夠透過介面指定本地文件資料夾路徑，並觸發文件內容的導入,
[cite_start]**so that** 我可以將我的專有知識整合到智能助理中 [cite: 536]。

##### Acceptance Criteria

1.  [cite_start]AC1: 介面提供一個清晰的 UI 元素（例如輸入框、檔案瀏覽按鈕），允許使用者輸入或選擇本地文件資料夾的路徑 [cite: 538]。
2.  [cite_start]AC2: 介面包含一個「導入」或「開始同步」按鈕，用於觸發文件內容的後端處理 [cite: 538]。
3.  [cite_start]AC3: 介面能顯示文件導入的狀態（例如：正在處理、已完成、錯誤），並提供進度指示 [cite: 538]。
4.  [cite_start]AC4: 後端 API 能夠接收使用者提交的文件資料夾路徑 [cite: 538]。
5.  [cite_start]AC5: 後端能夠安全地存取並讀取指定路徑下的所有檔案和子資料夾中的文件內容 [cite: 538]。

#### Story 2.2: 文件內容 Embedding 與向量資料庫儲存

**As a** 智能助理系統,
**I want** 能夠將使用者指定的文件內容轉換為向量並安全地儲存到向量資料庫中,
[cite_start]**so that** 我可以高效地檢索並利用這些知識進行回應 [cite: 536]。

##### Acceptance Criteria

1.  [cite_start]AC1: 後端服務能夠成功連接到 `http://ollama.webtw.xyz:11434` 的 Ollama 服務 [cite: 538]。
2.  [cite_start]AC2: 後端服務能夠使用 `all-minilm:l6-v2` 模型對讀取到的文件內容執行 Embedding 操作 [cite: 538]。
3.  [cite_start]AC3: 每個文件或其分塊內容都能被正確地轉換為 Embedding 向量 [cite: 538]。
4.  [cite_start]AC4: Embedding 向量能夠成功儲存到選定的向量資料庫中（例如 Faiss 或 ChromaDB） [cite: 538]。
5.  [cite_start]AC5: 向量資料庫能夠為每個儲存的向量保留原始文件來源的連結或識別符 [cite: 538]。
6.  [cite_start]AC6: 向量資料庫在儲存過程中能處理不同文件類型（如 `.txt`, `.md`, `.pdf` 等）的文本提取 [cite: 539]。

#### Story 2.3: 智能助理基礎知識檢索與對話整合

**As a** 使用者,
**I want** 智能助理在對話時能夠檢索並利用我導入的知識庫進行回答,
[cite_start]**so that** 我可以獲得更精準和個人化的資訊 [cite: 536]。

##### Acceptance Criteria

1.  [cite_start]AC1: 當使用者在 Chatbot 介面輸入問題時，後端能夠觸發知識檢索流程 [cite: 538]。
2.  [cite_start]AC2: 知識檢索流程能夠利用向量資料庫，基於使用者查詢進行語義相似性搜索，並檢索相關的文件內容片段 [cite: 538]。
3.  [cite_start]AC3: 檢索到的相關內容能夠作為上下文，傳遞給智能助理 (AutoGen 代理) 進行答案生成 [cite: 538]。
4.  [cite_start]AC4: 智能助理能夠根據檢索到的知識生成自然語言回答，並顯示在 Chatbot 介面中 [cite: 538]。
5.  [cite_start]AC5: 智能助理的回覆中，能夠（或可選地）引用其資訊來源（例如來自哪個文件） [cite: 538]。

### Epic 3: 外部登入與 AutoGen 整合

[cite_start]**Epic Goal**: 擴展智能助理應用程式的使用者登入方式，整合 Google 第三方登入功能，並將 AutoGen 框架與後端服務進行深度整合，實現多代理智能體在對話中的高效協同與功能擴展 [cite: 532]。

#### Story 3.1: 整合 Google 帳號登入

**As a** 使用者,
**I want** 能夠使用我的 Google 帳號快速登入智能助理應用程式,
[cite_start]**so that** 我可以享受更便捷的登入體驗，無需註冊新的本地帳號 [cite: 536]。

##### Acceptance Criteria

1.  [cite_start]AC1: 登入介面提供一個清晰的「使用 Google 登入」按鈕或連結 [cite: 538]。
2.  [cite_start]AC2: 點擊 Google 登入後，使用者會被導向 Google 的授權頁面進行驗證 [cite: 538]。
3.  [cite_start]AC3: 成功授權後，使用者會被安全地導回應用程式，並自動完成登入 [cite: 538]。
4.  [cite_start]AC4: 後端能夠處理 Google OAuth2 或 OpenID Connect 回呼，安全地獲取並驗證使用者資訊 [cite: 538]。
5.  [cite_start]AC5: 後端能夠將 Google 帳號與應用程式的內部使用者系統進行關聯，如果首次登入則自動創建新帳號 [cite: 538]。
6.  [cite_start]AC6: 登入成功後，前端能夠正確處理並儲存使用者會話憑證 [cite: 538]。

#### Story 3.2: AutoGen 框架與後端服務整合

**As a** 智能助理系統,
**I want** 能夠將 AutoGen 框架的核心多代理功能與 FastAPI 後端服務無縫整合,
[cite_start]**so that** 我可以啟用更複雜、更智能的對話流程和任務協作 [cite: 536]。

##### Acceptance Criteria

1.  [cite_start]AC1: 後端 FastAPI 應用程式能夠成功初始化 AutoGen `GroupChatManager` 或其他必要的 AutoGen 協作組件 [cite: 538]。
2.  [cite_start]AC2: 能夠在 FastAPI 中定義和註冊 AutoGen 代理人 (Agents) 的基本角色，例如 `UserProxyAgent`、`AssistantAgent` 等 [cite: 538]。
3.  [cite_start]AC3: FastAPI 能夠暴露一個 API 接口，作為前端與 AutoGen 代理對話的入口 [cite: 538]。
4.  [cite_start]AC4: 前端可以透過此 API 接口向 AutoGen 代理發送使用者訊息，並接收代理的回應 [cite: 538]。
5.  [cite_start]AC5: AutoGen 代理之間能夠在後端成功進行多輪對話和協作，並將最終結果傳遞回前端 [cite: 538]。
6.  [cite_start]AC6: 整合過程遵循 AutoGen 的最佳實踐，確保代理之間的通訊和任務分配邏輯清晰 [cite: 538]。

#### Story 3.3: AutoGen 代理人工具整合（知識檢索）

**As a** 智能助理系統,
**I want** AutoGen 代理人能夠呼叫知識檢索工具，以利用向量資料庫中的資訊回答使用者問題,
[cite_start]**so that** 能夠在對話中提供基於導入知識庫的智能回應 [cite: 536]。

##### Acceptance Criteria

1.  [cite_start]AC1: 在 AutoGen 框架內定義一個可由代理人呼叫的工具函數（例如 `retrieve_knowledge(query)`） [cite: 538]。
2.  [cite_start]AC2: 此工具函數能夠在後端調用向量資料庫的查詢邏輯，基於輸入的 `query` 檢索相關的文件內容片段 [cite: 538]。
3.  [cite_start]AC3: AutoGen 的 `AssistantAgent` 能夠識別使用者問題是否需要知識檢索，並自動呼叫 `retrieve_knowledge` 工具 [cite: 538]。
4.  [cite_start]AC4: 檢索到的內容能夠被 `AssistantAgent` 利用，形成更精準和內容豐富的答案 [cite: 538]。
5.  [cite_start]AC5: 整個工具呼叫和內容生成的流程在後端是穩定和可追溯的 [cite: 538]。
