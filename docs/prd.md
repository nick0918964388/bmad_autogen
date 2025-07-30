# 智能助理應用程式產品需求文件 (PRD)

## Goals and Background Context

### Goals

* [cite_start]提升使用者參與度，將每月活躍使用者 (MAU) 在發布後 6 個月內提升 20% [cite: 236]
* [cite_start]確保核心功能的穩定性和效能，將應用程式的平均回應時間保持在 500 毫秒以下 [cite: 236]
* [cite_start]建立強大的開發者社群，在發布後 1 年內，在 GitHub 上獲得 500 個 Star [cite: 236]
* [cite_start]實現有效的文件整合，使每月平均有 100 個資料夾被成功導入向量資料庫 [cite: 236]
* [cite_start]收集正向使用者回饋，將核心功能的使用者滿意度 (CSAT) 保持在 4.0/5.0 以上 [cite: 236]
* [cite_start]使用者能夠成功自訂文件資料夾路徑並導入向量資料庫，成功率達 95% [cite: 236]
* [cite_start]使用者對智能助理的查詢響應滿意度達 85% [cite: 236]
* [cite_start]使用者平均會話時長 (Average Session Duration) 達到 10 分鐘以上 [cite: 236]
* [cite_start]每月至少有 70% 的活躍使用者使用文件導入功能 [cite: 236]
* [cite_start]智能助理提供相關資訊的準確性達到 90% [cite: 236]

### Background Context

[cite_start]本專案旨在建構一個基於 AutoGen 最新版本的多代理智能體應用程式，其核心為一個智能助理，提供高效、可客製化的對話與知識管理功能 [cite: 236][cite_start]。在當前數位化趨勢下，使用者面臨如何有效管理、檢索並利用不斷增長的非結構化文件資料的挑戰 [cite: 236][cite_start]。現有的工具往往缺乏整合多代理協同工作的能力，導致資訊孤島和低效的互動 [cite: 236][cite_start]。市場上缺乏一個可讓使用者輕鬆將本地文件資料夾內容匯入向量資料庫並進行智能互動的客製化解決方案，這使得個人或小型團隊難以充分發揮其專有知識的價值 [cite: 236][cite_start]。此專案將解決這些問題，提供一個直觀且功能強大的解決方案 [cite: 236]。

### Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-07-30 | 1.0 | Initial PRD draft based on Project Brief | John (Product Manager) |
| 2025-07-30 | 1.1 | Added Google/Local Login & Docker Compose deployment | John (Product Manager) |
| 2025-07-30 | 1.2 | Specified Ollama Embedding model and API. | John (Product Manager) |
| 2025-07-30 | 1.3 | Refined UI/UX goals to align with Gemini style chatbot. | John (Product Manager) |

## Requirements

### Functional

1.  [cite_start]FR1: 系統應支援基於 AutoGen 最新版本構建的多代理智能體核心，以實現智能對話與任務協作 [cite: 242]。
2.  [cite_start]FR2: 應用程式應採用前後端分離架構，前端使用 React + Mantine 進行開發 [cite: 242]。
3.  [cite_start]FR3: 應用程式應採用前後端分離架構，後端使用 AutoGen 框架 + FastAPI 負責代理呼叫、API 接口生成與資料處理 [cite: 242]。
4.  [cite_start]FR4: 應用程式應提供基礎的 Chatbot 介面，包括對話區，用於顯示智能助理與使用者的對話內容 [cite: 242]。
5.  [cite_start]FR5: 應用程式應提供基礎的 Chatbot 介面，包括歷史聊天區，用於儲存並顯示歷史對話記錄 [cite: 242]。
6.  [cite_start]FR6: Chatbot 介面應提供一個起始時位於中間、使用者輸入後自動置底的輸入框，供使用者輸入文字 [cite: 242]。
7.  [cite_start]FR7: 應用程式應提供一個介面，允許使用者自訂文件資料夾的路徑 [cite: 242]。
8.  [cite_start]FR8: 後端應能接收使用者指定的文件資料夾路徑，並處理路徑內所有檔案（包括子資料夾中的文件） [cite: 242]。
9.  [cite_start]FR9: 後端應整合 Embedding 模型，將指定路徑中的文件內容轉換為向量 [cite: 242]。
10. [cite_start]FR10: 後端應整合向量資料庫（例如 Faiss 或 ChromaDB），將 Embedding 向量儲存其中 [cite: 242]。
11. [cite_start]FR11: 系統應提供使用者登入功能，支援 Google 帳號登入選項 [cite: 242]。
12. [cite_start]FR12: 系統應提供使用者登入功能，支援本地帳號註冊與登入選項 [cite: 242]。

### Non Functional

1.  [cite_start]NFR1: 應用程式的平均回應時間應保持在 500 毫秒以下，以確保流暢的使用者體驗 [cite: 244]。
2.  [cite_start]NFR2: 前後端通訊應穩定且具備基本的錯誤處理機制 [cite: 244]。
3.  [cite_start]NFR3: 應用程式介面應具備響應式設計，支援不同螢幕尺寸的設備 [cite: 244]。
4.  [cite_start]NFR4: 文件導入功能的文件處理速度應高效，並確保 Embedding 的準確性 [cite: 244]。
5.  [cite_start]NFR5: 應用程式應具備基礎的安全性，包括數據傳輸加密 (HTTPS/SSL) 及輸入驗證 [cite: 244]。
6.  [cite_start]NFR6: 登入功能應提供安全的身份驗證機制，例如使用 JWT 或 OAuth2 協議 [cite: 244]。
7.  [cite_start]NFR7: 登入功能應具備使用者密碼安全儲存機制 [cite: 244]。

## User Interface Design Goals

### Overall UX Vision

* [cite_start]**整體使用者體驗願景**：提供一個直觀、流暢且高效的智能助理應用程式，讓使用者能夠輕鬆管理知識、與多代理進行智慧互動，並透過友善的介面提升工作效率 [cite: 269][cite_start]。其 Chatbot 介面風格應類似 Gemini [cite: 269]。
* **關鍵互動模式**：
    * [cite_start]**對話式互動**：以 Chatbot 介面為核心，模擬自然語言對話，提供即時回饋 [cite: 269]。
    * [cite_start]**文件管理**：提供清晰的介面，方便使用者瀏覽、選擇和匯入本地文件資料夾 [cite: 269]。
    * [cite_start]**知識檢索**：智能助理能夠快速檢索並呈現相關知識，且來源可追溯 [cite: 269]。
* **核心畫面與視圖**：
    * [cite_start]登入/註冊畫面 (新增功能考量) [cite: 269]
    * [cite_start]Chatbot 主介面 (包含對話區、歷史聊天區、輸入框) [cite: 269]
    * [cite_start]文件匯入與路徑設定介面 [cite: 269]
    * [cite_start]資料庫管理/狀態顯示介面 (例如顯示已匯入文件數量、Embedding 進度) [cite: 269]
* [cite_start]**輔助功能**：例如對話清除、歷史紀錄導出、設定介面等 [cite: 269]。

### Accessibility: None|WCAG AA|WCAG AAA|Custom Requirements

* [cite_start]**無**：目前 MVP 階段不優先考慮 WCAG 標準，但會盡量遵循基本的可訪問性原則 [cite: 270]。

### Branding

* [cite_start]**無**：目前 MVP 階段沒有特定的品牌指南或風格要求 [cite: 271][cite_start]。UI 將主要採用 Mantine 套件的預設風格，以確保快速開發和一致性 [cite: 271][cite_start]。未來可根據品牌發展進行客製化 [cite: 271]。

### Target Device and Platforms: Web Responsive|Mobile Only|Desktop Only|Cross-Platform

* [cite_start]**Web Responsive (響應式網頁)**：應用程式將支援在不同裝置（桌面、平板、手機）上提供最佳的瀏覽和互動體驗 [cite: 272]。

## Technical Assumptions

### Repository Structure: Monorepo|Polyrepo|Multi-repo

* [cite_start]**Monorepo (單一儲存庫)**: 將前後端程式碼、共享類型和基礎設施配置統一管理在一個儲存庫中，以提升協同效率 [cite: 255]。

### Service Architecture

* [cite_start]**混合式架構 (Microservices 搭配 Monolith)**: 核心 Chatbot 和 AutoGen 代理可作為單一服務啟動 [cite: 256][cite_start]。文件處理、Embedding 等功能將視為獨立的微服務，以便未來擴展 [cite: 256]。

### Testing Requirements

* [cite_start]**完整測試金字塔 (Full Testing Pyramid)**: 涵蓋單元測試、整合測試和端對端測試，以確保應用程式的品質和穩定性 [cite: 257]。

### Additional Technical Assumptions and Requests

* **Embedding Model**:
    * [cite_start]**服務提供者**: Ollama [cite: 257]
    * [cite_start]**模型名稱**: `all-minilm:l6-v2` [cite: 257]
    * [cite_start]**服務地址**: `http://ollama.webtw.xyz:11434` [cite: 257]
* [cite_start]**使用者登入功能**: 需要整合 Google 帳號登入選項和本地帳號註冊與登入選項 [cite: 257][cite_start]。登入功能應提供安全的身份驗證機制（例如使用 JWT 或 OAuth2 協議），並具備使用者密碼安全儲存機制 [cite: 257]。
* [cite_start]**部署方式**: 將使用 Docker Compose 部署前後端應用程式 [cite: 257]。

## Epic List

* **Epic 1: 專案基礎與核心 Chatbot 介面**
    * [cite_start]**目標**: 建立專案的基本框架（前後端 Docker Compose 部署設定），並完成基礎 Chatbot 的 UI 介面（包含對話區、歷史聊天區和置底輸入框） [cite: 462][cite_start]。同時建立使用者本地登入/註冊功能 [cite: 462]。
* **Epic 2: 知識庫管理與智能互動基礎**
    * [cite_start]**目標**: 實現使用者自訂文件資料夾路徑的功能，並完成後端文件 Embedding（使用 Ollama `all-minilm:l6-v2`）與向量資料庫儲存的基礎邏輯，使智能助理能從中檢索資訊並進行基礎互動 [cite: 469]。
* **Epic 3: 外部登入與 AutoGen 整合**
    * [cite_start]**目標**: 完成 Google 帳號的第三方登入功能，並將 AutoGen 框架與後端服務進行深度整合，實現多代理智能體在對話中的高效協同與功能擴展 [cite: 469]。

## Epic Details

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

## Checklist Results Report

### Category Statuses

| Category | Status | Critical Issues |
| :-------------------------------- | :----- | :------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1. Problem Definition & Context | PASS | 無 |
| 2. MVP Scope Definition | PASS | 新增登入功能已納入，但需確保不影響 MVP 的「最小可行產品」原則，並在時間/資源上可控 |
| 3. User Experience Requirements | PASS | Gemini 風格的 Chatbot 介面要求已納入，有助於 UX 設計指引 |
| 4. Functional Requirements | PASS | 新增的 Google/本地登入功能及 Ollama Embedding 模型使用已明確定義為功能性需求 |
| 5. Non-Functional Requirements | PASS | 安全性相關的非功能性需求（如密碼安全儲存）已納入 |
| 6. Epic & Story Structure | PASS | Epic 劃分邏輯清晰，包含專案基礎、知識庫管理與 AutoGen 整合。Docker Compose 部署的考量已納入 Epic 1 |
| 7. Technical Guidance | PASS | Ollama Embedding 模型、Docker Compose 部署方式等技術假設已明確。 |
| 8. Cross-Functional Requirements | PARTIAL | 數據實體和關係已在專案簡報中初步識別，但需要架構師進一步細化資料模型和資料庫選型。 |
| 9. Clarity & Communication | PASS | PRD 整體清晰，結構良好。 |

### Critical Deficiencies

無

### Recommendations

* **開發前必須修復的項目 (Must-fix before development)**:
    * **資料模型與資料庫選型細化**: Architect 需根據功能需求和您選擇的 Ollama Embedding 模型，在架構文件中詳細定義數據模型和最終的向量資料庫選型 (Faiss 或 ChromaDB)。
    * **AutoGen 代理人詳細設計**: Architect 需在架構文件中，詳細設計各 AutoGen 代理人的角色、職責、工具呼叫方式以及它們之間的對話流程，並考慮使用 `SelectorGroupChat` 進行代理選擇。
* **可提升品質的項目 (Should-fix for quality)**:
    * **錯誤處理策略細化**: 儘管已定義非功能性需求，但在架構文件中應更具體地規劃前後端錯誤處理、日誌記錄和回饋機制。
    * **安全實作細節**：針對登入、資料存取和文件處理，在架構文件中應提供更具體的安全實作指南。
* **可考慮改進的項目 (Consider for improvement)**:
    * 在 PRD 中為每個 Epic 增加一個簡短的「定義完成 (Definition of Done)」檢查點。
* **可延遲到 Post-MVP 的項目 (Post-MVP deferrals)**:
    * 除本地登入和 Google 登入之外的複雜認證機制。
    * 高級的 UI/UX 客製化工具，例如 AutoGen 代理行為的動態配置介面。

### Final Decision

* **READY FOR ARCHITECT**: 產品需求文件 (PRD) 已大致完整，且經過驗證。雖然仍有部分技術細節需要在架構文件中深入定義，但已為 Architect 的工作奠定了堅實的基礎。

## Next Steps

### UX Expert Prompt

此部分為空，因為此 PRD 已經包含了足夠的 UI/UX 設計目標。如果需要進一步的 UI/UX 規範或 AI UI 生成提示，請手動觸發 UX Expert 的相關任務。

### Architect Prompt

此 PRD 為「智能助理應用程式」提供了全面的產品需求。請您仔細審閱此 PRD，特別是：

* **Technical Assumptions** 部分，其中包含了 Ollama Embedding 模型的具體資訊 (`http://ollama.webtw.xyz:11434` 和 `all-minilm:l6-v2` 模型) 以及 Docker Compose 部署的考量。
* **Requirements** 部分中新增的使用者登入功能（Google 和本地登入）。
* **Epic Details** 中，每個故事的驗收標準。

在創建架構文件時，請特別注意以下關鍵點：

1.  **資料模型與資料庫選型細化**: 需要根據功能需求和指定的 Ollama Embedding 模型，詳細定義數據模型和最終的向量資料庫選型 (Faiss 或 ChromaDB)。
2.  **AutoGen 代理人詳細設計**: 參考 PRD 中的需求，以及**之前提供關於 AutoGen 代理人角色設計和對話流程的詳細說明**。請在架構文件中，詳細設計各 AutoGen 代理人的角色、職責、工具呼叫方式以及它們之間的對話流程。**特別是 QA 任務的 Agent 選擇，請考量並利用 AutoGen 技術文檔 `https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/core-concepts` 中提到的 `SelectorGroupChat` 機制。**
3.  **前後端 Docker Compose 部署架構**: 詳細規劃前後端服務的 Docker 化和 Docker Compose 配置，包括網路、卷軸、環境變數等。
4.  **登入功能架構**: 設計 Google OAuth2/OpenID Connect 和本地認證的流程，包括使用者資料儲存、Token 管理和 API 安全。
5.  **錯誤處理與日誌**: 規劃全面的錯誤處理策略和日誌記錄標準。
6.  **安全實作**: 針對登入、資料存取和文件處理，提供具體的安全實作指南。

請基於此 PRD，並結合現有最佳實踐，創建一份詳細的架構文件，作為開發團隊的技術指南。