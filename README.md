# 智能助理應用程式

基於 AutoGen 的多代理智能體系統，採用前後端分離架構。

## 快速開始

### 前提條件

- Docker 和 Docker Compose
- Node.js 18+ (用於本地開發)
- Python 3.10+ (用於本地開發)

### 使用 Docker Compose 啟動

```bash
# 建構並啟動所有服務
docker-compose up --build -d

# 檢查服務狀態
docker-compose ps

# 查看日誌
docker-compose logs -f
```

### 訪問應用程式

- **前端**: http://localhost:3000
- **後端 API**: http://localhost:8010
- **API 文檔**: http://localhost:8010/api/docs

### 健康檢查

```bash
# 檢查後端健康狀態
curl http://localhost:8010/health

# 檢查詳細 API 健康狀態
curl http://localhost:8010/api/health
```

## 專案結構

```
smart-assistant-app/
├── apps/
│   ├── frontend/        # React + Mantine 前端應用
│   └── backend/         # FastAPI 後端應用  
├── packages/
│   └── shared-types/    # 前後端共享型別定義
├── infrastructure/
│   └── docker-compose.yml
├── docker-compose.yml   # 根目錄便捷版本
└── README.md
```

## 開發命令

```bash
# 啟動開發環境
docker-compose up -d

# 停止服務
docker-compose down

# 重新建構映像
docker-compose up --build

# 查看服務日誌
docker-compose logs [service-name]

# 進入容器
docker-compose exec [service-name] /bin/bash
```

## 技術堆疊

### 前端
- React 18
- Mantine 7 (UI 組件庫)
- TypeScript 5
- Vite (建構工具)
- Zustand (狀態管理)

### 後端
- Python 3.10+
- FastAPI 0.111.0
- Uvicorn (ASGI 伺服器)
- Pydantic (數據驗證)

### 容器化
- Docker Compose 2.x
- 自定義網路支援服務間通訊

## 環境配置

### 前端環境變數
複製 `apps/frontend/.env.example` 到 `.env.local` 並根據需要修改。

### 後端環境變數
複製 `apps/backend/.env.example` 到 `.env` 並根據需要修改。

## 開發注意事項

1. **熱重載**: 兩個服務都支援程式碼變更的即時重載
2. **網路通訊**: 前後端透過自定義 Docker 網路 `smart-assistant-network` 通訊
3. **Volume 掛載**: 源碼目錄已掛載，支援即時開發

## 故障排除

### 端口衝突
如果遇到端口被占用的錯誤，請修改 `docker-compose.yml` 中的端口映射。

### 容器啟動失敗
檢查 Docker 日誌：
```bash
docker-compose logs [service-name]
```

### 網路連接問題
確認服務都在同一個網路中：
```bash
docker network ls
docker network inspect smart-assistant-network
```