# Source Tree

本節描述了 `智能助理應用程式` 的專案資料夾結構，反映了 Monorepo 的組織方式，並為前後端服務、共享代碼和基礎設施配置提供了清晰的劃分。

```plaintext
smart-assistant-app/
├── .github/                    # CI/CD workflows (e.g., GitHub Actions)
│   └── workflows/
│       ├── ci.yaml
│       └── deploy.yaml
├── apps/                       # Application packages
│   ├── frontend/               # Frontend application (React/Mantine)
│   │   ├── public/             # Static assets
│   │   ├── src/
│   │   │   ├── assets/         # Images, icons, fonts
│   │   │   ├── components/     # Reusable UI components
│   │   │   ├── hooks/          # Custom React hooks
│   │   │   ├── pages/          # Page-level components/routes
│   │   │   ├── services/       # API client services
│   │   │   ├── stores/         # Zustand state management stores
│   │   │   ├── styles/         # Global styles, Mantine theme overrides
│   │   │   └── utils/          # Frontend specific utilities
│   │   ├── tests/              # Frontend tests (Jest, React Testing Library)
│   │   ├── .env.example        # Frontend environment variables
│   │   └── package.json
│   └── backend/                # Backend application (FastAPI/AutoGen)
│       ├── src/
│       │   ├── api/            # FastAPI routers/controllers
│       │   ├── core/           # Core application logic, config
│       │   ├── agents/         # AutoGen agents definitions
│       │   ├── services/       # Business logic services (e.g., UserService, ChatService)
│       │   ├── models/         # Database models (SQLAlchemy)
│   │   │   ├── schemas/        # Pydantic schemas for request/response validation
│   │   │   ├── tools/          # AutoGen callable tools (e.g., knowledge retrieval)
│   │   │   └── database.py     # Database connection and session management
│       ├── tests/              # Backend tests (Pytest)
│       ├── .env.example        # Backend environment variables
│       └── requirements.txt
├── packages/                   # Shared packages
│   ├── shared-types/           # Shared TypeScript interfaces and types
│   │   ├── src/
│   │   │   └── index.ts
│   │   └── package.json
│   ├── ui-components/          # Optional: Shared UI components library
│   │   ├── src/
│   │   └── package.json
│   └── config/                 # Shared configuration files (e.g., ESLint, Prettier, TypeScript)
│       ├── eslint-config/
│       ├── prettier-config/
│       └── tsconfig-bases/
├── infrastructure/             # Infrastructure definitions (e.g., Docker Compose)
│   └── docker-compose.yml      # Docker Compose configuration for dev/prod
├── scripts/                    # Monorepo management scripts (optional, e.g., for `npm workspaces`)
├── docs/                       # Documentation
│   ├── prd.md
│   ├── fullstack-architecture.md
│   └── (other docs like project-brief.md)
├── .env.example                # Root level example environment variables
├── package.json                # Root package.json for monorepo workspaces
└── README.md
└── .gitignore
```
