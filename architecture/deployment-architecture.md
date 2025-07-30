# Deployment Architecture

### Deployment Strategy

本節定義了 `智能助理應用程式` 的部署策略，主要基於 Docker Compose 實現本地開發和簡單部署。

  * **Frontend Deployment**
      * **Platform**: Docker Container (via Docker Compose)
      * **Build Command**: `pnpm build` (在 `apps/frontend` 目錄下執行)
      * **Output Directory**: `apps/frontend/dist`
      * **CDN/Edge**: N/A (初期本地部署不使用 CDN)
  * **Backend Deployment**
      * **Platform**: Docker Container (via Docker Compose)
      * **Build Command**: Dockerfile 自動建構
      * **Deployment Method**: Docker Compose `up -d` (用於啟動服務)

### CI/CD Pipeline

初期將使用 **GitHub Actions** 來自動化測試和部署流程，以確保程式碼品質並簡化發布。

```yaml