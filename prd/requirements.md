# Requirements

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
