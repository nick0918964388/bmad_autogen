# Testing Strategy

本節定義了 `智能助理應用程式` 的綜合測試策略，旨在確保程式碼品質、功能正確性和系統穩定性。

### Testing Pyramid

測試金字塔將指導測試的組織和分佈，確保覆蓋範圍廣泛且效率最高：

```plaintext
E2E Tests
   /        \
Integration Tests
   /            \
Frontend Unit  Backend Unit
```

### Test Organization

#### Frontend Tests

前端測試將依據組件和頁面進行組織，與程式碼緊密結合：

```plaintext
apps/frontend/
├── src/
│   ├── components/
│   │   ├── Button/
│   │   │   ├── Button.tsx
│   │   │   └── Button.test.tsx # Unit/Component tests
│   │   ├── ChatWindow/
│   │   │   ├── ChatWindow.tsx
│   │   │   └── ChatWindow.test.tsx
│   │   ├── pages/
│   │   │   ├── HomePage/
│   │   │   │   ├── HomePage.tsx
│   │   │   │   └── HomePage.test.tsx # Page-level integration tests
│   │   └── services/
│   │       └── api.test.ts # API client unit tests
├── tests/ # 更廣泛的整合測試或 E2E 設置
│   ├── integration/
│   └── e2e/
```

#### Backend Tests

後端測試將按模組或服務進行組織：

```plaintext
apps/backend/
├── src/
│   ├── api/
│   │   ├── routers/
│   │   │   ├── auth.py
│   │   │   └── auth_test.py # Unit/Integration tests for routers
│   ├── services/
│   │   ├── user_service.py
│   │   └── user_service_test.py # Unit/Integration tests for services
│   ├── agents/
│   │   ├── assistant_agent.py
│   │   │   └── assistant_agent_test.py # Unit tests for agent logic
│   │   └── tools/
│   │       ├── knowledge_retrieval_tool.py
│   │       └── knowledge_retrieval_tool_test.py # Unit tests for tool functions
│   └── models/
│       └── models_test.py # Unit tests for ORM models
├── tests/ # 更高層次的整合測試或端對端設置
│   └── integration/
```

#### E2E Tests

端對端測試將獨立於前後端應用程式存放，專注於模擬真實使用者流程：

```plaintext
e2e/
├── tests/
│   ├── auth.spec.ts # Login/Logout flow
│   ├── chat.spec.ts # Chat interaction flow
│   ├── knowledge_base.spec.ts # Document upload and retrieval flow
├── playwright.config.ts
├── package.json
```

### Test Examples

#### Frontend Component Test

這是一個使用 Jest 和 React Testing Library 的基本 React 組件測試範例：

```typescript
// apps/frontend/src/components/Button/Button.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import Button from './Button';

describe('Button', () => {
  test('renders with correct text', () => {
    render(<Button>Click Me</Button>);
    expect(screen.getByText(/click me/i)).toBeInTheDocument();
  });

  test('calls onClick handler when clicked', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click Me</Button>);
    fireEvent.click(screen.getByText(/click me/i));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});
```

#### Backend API Test

這是一個使用 Pytest 和 httpx 的 FastAPI API 測試範例：

```typescript