# External APIs

### Google OAuth2 API

  * **Purpose**: 用於實現使用者透過 Google 帳號登入應用程式的功能，提供便捷的第三方身份驗證。
  * **Documentation**: Google Identity Platform - OAuth 2.0 (實際文件 URL 將在實作時獲取最新版本)
  * **Base URL(s)**:
      * 授權端點: `https://accounts.google.com/o/oauth2/v2/auth`
      * Token 端點: `https://oauth2.googleapis.com/token`
      * 使用者資訊端點: `https://www.googleapis.com/oauth2/v3/userinfo` (或 `https://openidconnect.googleapis.com/v1/userinfo` 依需求選擇)
  * **Authentication**: OAuth 2.0 授權碼流程 (Authorization Code Flow)。應用程式將使用 `client_id` 和 `client_secret` 進行身份驗證，並透過回呼 URL 接收授權碼。
  * **Rate Limits**: Google OAuth2 API 有標準的配額限制，通常在數百萬次請求/天，對於 MVP 階段應足夠。
  * **Key Endpoints Used**:
      * `GET https://accounts.google.com/o/oauth2/v2/auth` - 啟動授權流程。
      * `POST https://oauth2.googleapis.com/token` - 交換授權碼為 Access Token 和 ID Token。
      * `GET https://www.googleapis.com/oauth2/v3/userinfo` - 獲取使用者個人資料。
  * **Integration Notes**:
      * 後端負責處理 OAuth 回呼和 Token 交換，確保 `client_secret` 的安全儲存。
      * 前端負責觸發導向 Google 授權頁面，並處理導回。
      * 需處理可能的網路錯誤和授權失敗情況。
