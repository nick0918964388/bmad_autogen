# Technical Assumptions

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
