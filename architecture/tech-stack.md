# Tech Stack

以下是 `智能助理應用程式` 的最終技術堆棧選型。這份表格將作為所有開發工作的單一真實來源，所有團隊成員必須依據此處定義的確切版本進行開發。

**關鍵決策總結**:

  * **平台**：Docker Compose (用於容器化部署)。
  * **Embedding 服務**：Ollama (`http://ollama.webtw.xyz:11434` )。
  * **Embedding 模型**：`all-minilm:l6-v2`。

| Category | Technology | Version | Purpose | Rationale |
| :------------------ | :--------- | :-------- | :-------- | :-------- |
| Frontend Language | TypeScript | 5.x | 主要前端開發語言 | 強型別、提升程式碼品質與可維護性。 |
| Frontend Framework | React | 18.x | 核心前端框架 | 業界廣泛採用，組件化開發，擁有龐大生態系。 |
| UI Component Library | Mantine | 7.x | UI 組件庫 | 提供豐富、可客製化的組件，加速 UI 開發，與 React 良好整合。 |
| State Management | Zustand | ^4.0.0 | 前端狀態管理 | 輕量級、易於使用、高效的 React 狀態管理庫。 |
| Backend Language | Python | 3.10+ | 主要後端開發語言 | 適用於 AI/ML 相關應用，擁有豐富的函式庫。 |
| Backend Framework | FastAPI | ^0.111.0 | 後端 API 框架 | 高性能、易於學習、內建 Pydantic 資料驗證，與 AutoGen 兼容。 |
| AI Agent Framework | AutoGen | ^0.2.0 | 多代理智能體框架 | 提供多代理協同對話和任務執行能力。 |
| API Style | REST | 1.0 | 前後端 API 風格 | 標準化、廣泛支持，易於理解和實作。 |
| Database | PostgreSQL | 16.x | 關係型資料庫 | 穩定、可靠、功能強大，適用於使用者資料、聊天歷史等結構化數據。 |
| Cache | Redis | 7.x | 緩存系統 | 高性能 Key-Value 存儲，適用於會話管理、API 響應緩存等。 |
| File Storage | 本地文件系統 | N/A | 儲存使用者文件 | 使用者自訂資料夾路徑，由後端直接存取。 |
| Authentication | OAuth2 / JWT | N/A | 身份驗證與授權 | 支援 Google 登入和本地登入，提供安全的 API 訪問。 |
| Frontend Testing | Jest | ^29.0.0 | 前端單元/整合測試 | 廣泛使用的 JavaScript 測試框架，適合 React 組件測試。 |
| Backend Testing | Pytest | ^8.0.0 | 後端單元/整合測試 | Python 測試框架，簡潔高效。 |
| E2E Testing | Playwright | ^1.40.0 | 端對端測試 | 支援多瀏覽器，提供可靠的端對端測試。 |
| Build Tool | Webpack / Vite | N/A | 前端打包工具 | Vite 更快，Webpack 更靈活，根據具體專案結構和需求決定。 |
| Bundler | Docker Compose | 2.x | 多容器應用程式管理工具 | 簡化前後端及相關服務的本地開發與部署。 |
| IaC Tool | N/A | N/A | 基礎設施即程式碼 | 初期 MVP 階段不使用，未來擴展至雲端部署時再考慮。 |
| CI/CD | GitHub Actions | N/A | 持續整合/交付 | 易於整合、自動化測試和部署流程。 |
| Monitoring | Prometheus/Grafana | N/A | 應用程式監控 | 用於監控應用程式的效能指標和系統健康狀況。 |
| Logging | ELK Stack (Elasticsearch, Logstash, Kibana) | N/A | 日誌管理 | 集中式日誌收集、分析和可視化。 |
| CSS Framework | Tailwind CSS | ^3.0.0 | CSS 實用工具框架 | 加速 CSS 開發，提供高度可客製化的響應式設計。 |
| Embedding Service | Ollama | ^0.1.x | 本地 LLM/Embedding 服務 | 運行本地 Embedding 模型，降低成本和數據隱私風險。 |
| Embedding Model | `all-minilm:l6-v2` | N/A | 文件 Embedding 模型 | 輕量級、高效的 Embedding 模型。 |
