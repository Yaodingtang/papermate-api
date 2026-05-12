# PaperMate Pro - 后端代码

## 项目结构

```
api/
├── app/
│   ├── main.py              # FastAPI 应用入口
│   ├── core/
│   │   ├── config.py        # 配置管理
│   │   ├── database.py      # 数据库连接
│   │   └── security.py      # 安全相关
│   ├── models/
│   │   └── __init__.py      # SQLAlchemy 模型
│   ├── schemas/
│   │   └── __init__.py      # Pydantic 模型
│   ├── api/
│   │   ├── deps.py          # 依赖注入
│   │   └── v1/
│   │       ├── auth.py      # 认证接口
│   │       ├── papers.py    # 论文接口
│   │       ├── annotations.py
│   │       ├── cards.py
│   │       ├── ai.py        # AI 接口
│   │       ├── daily.py     # 每日推送
│   │       ├── stats.py     # 统计
│   │       ├── teams.py
│   │       └── journals.py
│   └── db/
│       └── init.sql         # 数据库初始化
├── data/
│   └── papermate.db         # SQLite 数据库
├── requirements.txt
└── .env
```

## 已实现的接口

### 认证
- POST /api/v1/auth/register
- POST /api/v1/auth/login
- GET /api/v1/auth/me

### 论文管理
- GET /api/v1/papers
- POST /api/v1/papers/upload
- GET /api/v1/papers/{id}
- PATCH /api/v1/papers/{id}
- DELETE /api/v1/papers/{id}
- POST /api/v1/papers/import

### 批注
- GET /api/v1/papers/{id}/annotations
- POST /api/v1/papers/{id}/annotations
- PATCH /api/v1/annotations/{id}
- DELETE /api/v1/annotations/{id}

### 知识卡片
- GET /api/v1/cards
- POST /api/v1/cards
- GET /api/v1/cards/{id}
- DELETE /api/v1/cards/{id}

### AI 功能
- POST /api/v1/ai/chat
- POST /api/v1/ai/review/generate
- GET /api/v1/ai/graph/{paper_id}
- POST /api/v1/ai/writing/polish
- POST /api/v1/ai/writing/citations
- POST /api/v1/ai/writing/check

### 每日推送
- GET /api/v1/daily/recommendations
- PATCH /api/v1/daily/settings
- PATCH /api/v1/daily/interests

### 统计
- GET /api/v1/stats/overview

### 团队
- GET /api/v1/teams
- POST /api/v1/teams
- POST /api/v1/teams/{id}/members
- GET /api/v1/teams/{id}/discussions

### 投稿管理
- GET /api/v1/journals
- POST /api/v1/journals
- PATCH /api/v1/journals/{id}

## 运行方式

```bash
cd api
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8100
```