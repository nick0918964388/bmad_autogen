# High Level Architecture

### Technical Summary

此系統將採用**混合式微服務與單體式架構**，結合 React/Mantine 前端與 FastAPI/AutoGen 後端，並利用 **Docker Compose** 進行容器化部署。核心 Chatbot 與 AutoGen 代理人作為單一服務運作，而文件處理與 Embedding 則可獨立擴展。資料模型將統一管理，並透過 RESTful API 進行前後端通訊。整個架構旨在支援 PRD 的目標，提供高效、可擴展且具備知識檢索能力的智能助理應用程式。

### Platform and Infrastructure Choice

根據 PRD 的需求，此專案將專注於 **Web 響應式應用程式**，並預計使用 **Docker Compose** 進行本地開發和初期部署。

**平台推薦：Docker Compose + 本地部署**

* **優點**：
    * **快速開發與環境一致性**：Docker Compose 能夠快速啟動包含前後端服務的開發環境，確保團隊成員環境一致。
    * **輕量級部署**：對於 MVP 階段，Docker Compose 提供了簡單高效的部署方式，無需複雜的雲端資源配置。
    * **可移植性**：基於 Docker 容器，應用程式可以在任何支援 Docker 的環境中運行。
    * **成本效益**：初期無雲端服務費用，降低開發成本。
* **缺點**：
    * **擴展性限制**：Docker Compose 不適合生產環境的大規模水平擴展。
    * **高可用性限制**：需要額外的工具和策略來實現高可用性。

**選定平台：Docker Compose**

* **關鍵服務**：Docker Daemon, Docker Compose。
* **部署主機與區域**：本地開發環境 (Local Development Environment)。

### Repository Structure

* **結構**：**Monorepo (單一儲存庫)**。
* **Monorepo 工具**：考慮使用 `npm workspaces` 或 `pnpm workspaces` 進行簡單的套件管理，以統一管理前後端專案。若未來專案規模擴大，可升級至 `Nx` 或 `Turborepo`。
* **套件組織策略**：
    * `apps/`: 包含獨立的應用程式，如 `apps/frontend` (React app) 和 `apps/backend` (FastAPI app)。
    * `packages/`: 包含可共享的程式碼，如 `packages/shared-types` (前後端共享的 TypeScript 類型定義)、`packages/ui-components` (共享的 Mantine/React 組件)。

### High Level Architecture Diagram

```mermaid
graph TD
    User -->|HTTP/HTTPS| Frontend[Frontend: React/Mantine]
    Frontend -->|RESTful API| Backend[Backend: FastAPI/AutoGen]
    Backend -->|Local FS Access| DocumentFolder[User Defined Document Folder]
    Backend -->|Ollama API| OllamaService[Ollama Service: all-minilm:l6-v2]
    Backend -->|DB Connection| PostgreSQL[PostgreSQL DB: User Data/Chat History]
    Backend -->|Vector DB Connection| VectorDB[Vector Database: Faiss/ChromaDB]

    subgraph Containerized Deployment (Docker Compose)
        Frontend
        Backend
        OllamaService
        PostgreSQL
        VectorDB
    end

    subgraph AutoGen Multi-Agent System (within Backend)
        Backend --> UserProxyAgent[User Proxy Agent]
        UserProxyAgent --> QueryUnderstandingAgent[Query Understanding Agent]
        QueryUnderstandingAgent --> KnowledgeRetrievalAgent[Knowledge Retrieval Agent]
        KnowledgeRetrievalAgent --> AnswerGenerationAgent[Answer Generation Agent]
        AnswerGenerationAgent --> TaskExecutionAgent(Task Execution Agent - Optional)
        AnswerGenerationAgent --> FeedbackLearningAgent(Feedback & Learning Agent - Optional)
        KnowledgeRetrievalAgent --> VectorDB
    end
````

### Architectural Patterns

  * **全端架構**：
      * **推薦**：**混合式架構 (Hybrid Monolith/Microservices)**。
          * **理由**：核心 Chatbot 和 AutoGen 代理人可作為單一服務啟動，簡化初期開發。文件處理和 Embedding 則可獨立擴展，為未來高併發處理文件預留彈性。
  * **前端模式**：
      * **Component-Based UI (組件化 UI)**：使用 React 組件化開發，提高可重用性和維護性。
      * **State Management (狀態管理)**：採用 Zustand 進行輕量級全局狀態管理。
  * **後端模式**：
      * **Repository Pattern (儲存庫模式)**：抽象化數據存取邏輯，提高可測試性和未來資料庫遷移的靈活性。
      * **推薦**：**基於 FastAPI 的 RESTful API 設計**。
          * **理由**：FastAPI 提供高性能的非同步 API 開發，內建 Pydantic 用於數據驗證，非常適合構建 RESTful 服務。
  * **整合模式**：
      * **推薦**：**直接 RESTful API 通訊**。
          * **理由**：MVP 階段前後端直接透過標準 RESTful API 進行通訊，簡化複雜性，符合快速開發原則。
