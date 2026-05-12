# PaperMate Pro - API 接口设计文档

## 基础信息

- **Base URL**: `/api/v1`
- **认证方式**: Bearer Token (JWT)
- **响应格式**: JSON

---

## 一、认证接口

### 1.1 用户注册
```
POST /auth/register
Request:
{
  "email": "user@example.com",
  "password": "password123",
  "name": "张三"
}
Response:
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "张三"
  }
}
```

### 1.2 用户登录
```
POST /auth/login
Request:
{
  "email": "user@example.com",
  "password": "password123"
}
Response:
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": {...}
}
```

### 1.3 获取当前用户
```
GET /auth/me
Response:
{
  "id": 1,
  "email": "user@example.com",
  "name": "张三",
  "avatar": null,
  "research_interests": ["NLP", "Transformer"],
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

## 二、论文接口

### 2.1 获取论文列表
```
GET /papers?folder_id=1&status=reading&search=transformer&page=1&limit=20
Response:
{
  "items": [
    {
      "id": 1,
      "title": "Attention Is All You Need",
      "authors": ["Vaswani", "Shazeer", "Parmar"],
      "year": 2017,
      "venue": "NeurIPS",
      "abstract": "...",
      "status": "reading",
      "progress": 80,
      "folder_id": 1,
      "tags": ["Transformer", "NLP"],
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 100,
  "page": 1,
  "limit": 20
}
```

### 2.2 上传论文
```
POST /papers/upload
Content-Type: multipart/form-data
Request:
- file: PDF文件
- folder_id: 文件夹ID（可选）
Response:
{
  "id": 1,
  "title": "论文标题",
  "authors": [...],
  "status": "unread",
  "progress": 0
}
```

### 2.3 获取论文详情
```
GET /papers/{id}
Response:
{
  "id": 1,
  "title": "Attention Is All You Need",
  "authors": ["Vaswani", "Shazeer", "Parmar"],
  "year": 2017,
  "venue": "NeurIPS",
  "abstract": "...",
  "doi": "10.1234/...",
  "pdf_url": "/uploads/papers/1.pdf",
  "status": "reading",
  "progress": 80,
  "current_page": 5,
  "total_pages": 15,
  "folder_id": 1,
  "tags": ["Transformer", "NLP"],
  "highlights": [...],
  "annotations": [...],
  "bookmarks": [...],
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-02T00:00:00Z"
}
```

### 2.4 更新论文状态
```
PATCH /papers/{id}
Request:
{
  "status": "completed",
  "progress": 100,
  "current_page": 15,
  "folder_id": 2
}
```

### 2.5 删除论文
```
DELETE /papers/{id}
```

### 2.6 导入文献库
```
POST /papers/import
Request:
{
  "source": "zotero",  // zotero, mendeley, endnote, bibtex
  "file": "export.bib"  // 上传的文件
}
Response:
{
  "imported": 50,
  "skipped": 5,
  "papers": [...]
}
```

---

## 三、文件夹接口

### 3.1 获取文件夹列表
```
GET /folders
Response:
{
  "items": [
    {
      "id": 1,
      "name": "Transformer",
      "paper_count": 12,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### 3.2 创建文件夹
```
POST /folders
Request:
{
  "name": "新文件夹"
}
```

### 3.3 更新/删除文件夹
```
PATCH /folders/{id}
DELETE /folders/{id}
```

---

## 四、批注接口

### 4.1 获取论文批注
```
GET /papers/{paper_id}/annotations
Response:
{
  "items": [
    {
      "id": 1,
      "paper_id": 1,
      "user_id": 1,
      "page": 1,
      "position": {"x": 100, "y": 200, "width": 300, "height": 50},
      "type": "highlight",  // highlight, note, underline
      "color": "#ffeb3b",
      "content": "重要内容",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### 4.2 创建批注
```
POST /papers/{paper_id}/annotations
Request:
{
  "page": 1,
  "position": {"x": 100, "y": 200, "width": 300, "height": 50},
  "type": "highlight",
  "color": "#ffeb3b",
  "content": "重要内容"
}
```

### 4.3 更新/删除批注
```
PATCH /annotations/{id}
DELETE /annotations/{id}
```

---

## 五、知识卡片接口

### 5.1 获取卡片列表
```
GET /cards?type=method&tag=NLP&page=1&limit=20
Response:
{
  "items": [
    {
      "id": 1,
      "title": "Transformer 架构",
      "type": "concept",  // concept, method, formula, data
      "content": "...",
      "paper_id": 1,
      "paper_title": "Attention Is All You Need",
      "tags": ["NLP", "Transformer"],
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 50
}
```

### 5.2 创建卡片
```
POST /cards
Request:
{
  "title": "Multi-Head Attention",
  "type": "method",
  "content": "多头注意力机制...",
  "paper_id": 1,
  "tags": ["NLP", "Attention"]
}
```

---

## 六、AI 接口

### 6.1 论文问答
```
POST /ai/chat
Request:
{
  "paper_id": 1,
  "question": "这篇论文的核心贡献是什么？",
  "conversation_id": "uuid"  // 可选，用于多轮对话
}
Response:
{
  "answer": "这篇论文的核心贡献是...",
  "conversation_id": "uuid",
  "references": [
    {"page": 1, "text": "相关原文..."}
  ]
}
```

### 6.2 生成文献综述
```
POST /ai/review/generate
Request:
{
  "topic": "Transformer架构及其应用",
  "paper_ids": [1, 2, 3],
  "sections": ["background", "methods", "progress", "comparison", "future"]
}
Response:
{
  "review_id": "uuid",
  "status": "generating",  // generating, completed
  "sections": [
    {
      "id": "background",
      "title": "研究背景",
      "content": "...",
      "status": "completed"
    }
  ]
}
```

### 6.3 获取论文关系图谱
```
GET /ai/graph/{paper_id}?depth=2
Response:
{
  "nodes": [
    {
      "id": 1,
      "title": "Attention Is All You Need",
      "type": "core",  // core, derived, precursor
      "year": 2017,
      "citations": 89000
    }
  ],
  "edges": [
    {
      "source": 1,
      "target": 2,
      "type": "cited"  // cited, influenced
    }
  ]
}
```

### 6.4 写作助手 - 润色
```
POST /ai/writing/polish
Request:
{
  "content": "我们提出了一个新的模型...",
  "style": "academic"  // academic, concise, detailed
}
Response:
{
  "polished": "本文提出了一种新型模型...",
  "suggestions": [
    {"original": "新的", "suggested": "新型", "reason": "更学术化"}
  ]
}
```

### 6.5 写作助手 - 引用推荐
```
POST /ai/writing/citations
Request:
{
  "content": "Transformer 模型在 NLP 领域取得了巨大成功...",
  "top_k": 5
}
Response:
{
  "citations": [
    {
      "id": 1,
      "title": "Attention Is All You Need",
      "authors": "Vaswani et al.",
      "year": 2017,
      "relevance": 95,
      "reason": "核心方法引用"
    }
  ]
}
```

### 6.6 写作助手 - 论文检查
```
POST /ai/writing/check
Request:
{
  "content": "论文全文内容..."
}
Response:
{
  "score": 85,
  "issues": [
    {
      "type": "grammar",
      "severity": "error",
      "line": 3,
      "text": "their 应为 there",
      "suggestion": "there"
    }
  ]
}
```

---

## 七、每日推送接口

### 7.1 获取今日推荐
```
GET /daily/recommendations
Response:
{
  "date": "2024-05-12",
  "papers": [
    {
      "id": 1,
      "title": "...",
      "authors": "...",
      "reason": "基于你关注的 NLP 领域",
      "relevance": 95
    }
  ]
}
```

### 7.2 更新推送设置
```
PATCH /daily/settings
Request:
{
  "enabled": true,
  "time": "09:00",
  "channel": "app",  // app, email, wechat
  "count": 5
}
```

### 7.3 更新研究兴趣
```
PATCH /daily/interests
Request:
{
  "interests": ["NLP", "Transformer", "Fine-tuning"]
}
```

---

## 八、统计接口

### 8.1 获取统计数据
```
GET /stats/overview?period=week
Response:
{
  "papers_read": 15,
  "reading_time": 1200,  // 分钟
  "annotations": 45,
  "field_distribution": [
    {"field": "NLP", "count": 10},
    {"field": "CV", "count": 5}
  ],
  "keyword_cloud": [
    {"keyword": "Transformer", "count": 20},
    {"keyword": "Attention", "count": 15}
  ]
}
```

---

## 九、团队接口

### 9.1 获取团队列表
```
GET /teams
Response:
{
  "items": [
    {
      "id": 1,
      "name": "NLP研究组",
      "member_count": 5,
      "paper_count": 50,
      "role": "admin"
    }
  ]
}
```

### 9.2 创建团队
```
POST /teams
Request:
{
  "name": "新团队",
  "description": "团队描述"
}
```

### 9.3 邀请成员
```
POST /teams/{team_id}/members
Request:
{
  "email": "member@example.com",
  "role": "member"  // admin, member
}
```

### 9.4 团队讨论
```
GET /teams/{team_id}/discussions?paper_id=1
POST /teams/{team_id}/discussions
```

---

## 十、投稿管理接口

### 10.1 获取期刊列表
```
GET /journals?status=targeting
Response:
{
  "items": [
    {
      "id": 1,
      "name": "ACL 2024",
      "type": "conference",
      "field": "NLP",
      "deadline": "2024-05-20",
      "status": "targeting",
      "impact_factor": null,
      "acceptance_rate": "23%"
    }
  ]
}
```

### 10.2 添加期刊
```
POST /journals
Request:
{
  "name": "NeurIPS 2024",
  "type": "conference",
  "deadline": "2024-05-22",
  "status": "interested"
}
```

---

## 十一、对比接口

### 11.1 获取对比数据
```
POST /compare
Request:
{
  "paper_ids": [1, 2, 3]
}
Response:
{
  "papers": [...],
  "comparison": {
    "methods": {
      "架构": ["Transformer", "Transformer", "CNN+Transformer"],
      "参数量": ["65M", "340M", "175B"]
    },
    "results": {
      "BLEU": ["28.4", "32.1", "-"]
    }
  }
}
```

---

## 十二、引用导出接口

### 12.1 导出引用
```
GET /papers/{id}/citation?format=bibtex
Response:
{
  "citation": "@article{vaswani2017attention, ...}",
  "format": "bibtex"
}
```

---

## 错误响应格式

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "邮箱格式不正确",
    "details": {...}
  }
}
```

## 通用状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未认证 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 500 | 服务器错误 |