# PaperMate Pro - 数据库设计文档

## 数据库选型

- **主数据库**: SQLite（开发）/ PostgreSQL（生产）
- **缓存**: Redis（可选，用于 AI 对话缓存）

---

## 一、用户相关表

### 1.1 users（用户表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PRIMARY KEY | 用户ID |
| email | VARCHAR(255) | UNIQUE, NOT NULL | 邮箱 |
| password_hash | VARCHAR(255) | NOT NULL | 密码哈希 |
| name | VARCHAR(100) | NOT NULL | 用户名 |
| avatar | VARCHAR(500) | NULL | 头像URL |
| research_interests | JSON | NULL | 研究兴趣列表 |
| theme | VARCHAR(20) | DEFAULT 'light' | 主题偏好 |
| daily_push_enabled | BOOLEAN | DEFAULT TRUE | 每日推送开关 |
| push_time | VARCHAR(5) | DEFAULT '09:00' | 推送时间 |
| push_channel | VARCHAR(20) | DEFAULT 'app' | 推送渠道 |
| is_active | BOOLEAN | DEFAULT TRUE | 账户是否激活 |
| created_at | DATETIME | DEFAULT NOW | 创建时间 |
| updated_at | DATETIME | DEFAULT NOW | 更新时间 |

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    avatar VARCHAR(500),
    research_interests JSON,
    theme VARCHAR(20) DEFAULT 'light',
    daily_push_enabled BOOLEAN DEFAULT TRUE,
    push_time VARCHAR(5) DEFAULT '09:00',
    push_channel VARCHAR(20) DEFAULT 'app',
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 二、论文相关表

### 2.1 papers（论文表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PRIMARY KEY | 论文ID |
| user_id | INTEGER | FOREIGN KEY | 所属用户 |
| folder_id | INTEGER | FOREIGN KEY | 所属文件夹 |
| title | VARCHAR(500) | NOT NULL | 标题 |
| authors | JSON | NOT NULL | 作者列表 |
| year | INTEGER | NULL | 发表年份 |
| venue | VARCHAR(200) | NULL | 发表 venue |
| abstract | TEXT | NULL | 摘要 |
| doi | VARCHAR(100) | NULL | DOI |
| arxiv_id | VARCHAR(50) | NULL | arXiv ID |
| pdf_url | VARCHAR(500) | NULL | PDF存储路径 |
| status | VARCHAR(20) | DEFAULT 'unread' | 阅读状态 |
| progress | INTEGER | DEFAULT 0 | 阅读进度(%) |
| current_page | INTEGER | DEFAULT 1 | 当前页码 |
| total_pages | INTEGER | NULL | 总页数 |
| last_read_at | DATETIME | NULL | 最后阅读时间 |
| created_at | DATETIME | DEFAULT NOW | 创建时间 |
| updated_at | DATETIME | DEFAULT NOW | 更新时间 |

```sql
CREATE TABLE papers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    folder_id INTEGER,
    title VARCHAR(500) NOT NULL,
    authors JSON NOT NULL,
    year INTEGER,
    venue VARCHAR(200),
    abstract TEXT,
    doi VARCHAR(100),
    arxiv_id VARCHAR(50),
    pdf_url VARCHAR(500),
    status VARCHAR(20) DEFAULT 'unread',
    progress INTEGER DEFAULT 0,
    current_page INTEGER DEFAULT 1,
    total_pages INTEGER,
    last_read_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (folder_id) REFERENCES folders(id)
);
```

### 2.2 folders（文件夹表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PRIMARY KEY | 文件夹ID |
| user_id | INTEGER | FOREIGN KEY | 所属用户 |
| name | VARCHAR(100) | NOT NULL | 文件夹名 |
| parent_id | INTEGER | FOREIGN KEY | 父文件夹 |
| created_at | DATETIME | DEFAULT NOW | 创建时间 |

```sql
CREATE TABLE folders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    parent_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (parent_id) REFERENCES folders(id)
);
```

### 2.3 paper_tags（论文标签关联表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PRIMARY KEY | ID |
| paper_id | INTEGER | FOREIGN KEY | 论文ID |
| tag_id | INTEGER | FOREIGN KEY | 标签ID |

```sql
CREATE TABLE paper_tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paper_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    FOREIGN KEY (paper_id) REFERENCES papers(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE,
    UNIQUE(paper_id, tag_id)
);
```

### 2.4 tags（标签表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PRIMARY KEY | 标签ID |
| user_id | INTEGER | FOREIGN KEY | 所属用户 |
| name | VARCHAR(50) | NOT NULL | 标签名 |
| color | VARCHAR(10) | NULL | 标签颜色 |

```sql
CREATE TABLE tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name VARCHAR(50) NOT NULL,
    color VARCHAR(10),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

## 三、批注相关表

### 3.1 annotations（批注表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PRIMARY KEY | 批注ID |
| paper_id | INTEGER | FOREIGN KEY | 论文ID |
| user_id | INTEGER | FOREIGN KEY | 用户ID |
| page | INTEGER | NOT NULL | 页码 |
| position | JSON | NOT NULL | 位置信息 |
| type | VARCHAR(20) | NOT NULL | 类型(highlight/note/underline) |
| color | VARCHAR(10) | NULL | 颜色 |
| content | TEXT | NULL | 内容 |
| created_at | DATETIME | DEFAULT NOW | 创建时间 |
| updated_at | DATETIME | DEFAULT NOW | 更新时间 |

```sql
CREATE TABLE annotations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paper_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    page INTEGER NOT NULL,
    position JSON NOT NULL,
    type VARCHAR(20) NOT NULL,
    color VARCHAR(10),
    content TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (paper_id) REFERENCES papers(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### 3.2 bookmarks（书签表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PRIMARY KEY | 书签ID |
| paper_id | INTEGER | FOREIGN KEY | 论文ID |
| user_id | INTEGER | FOREIGN KEY | 用户ID |
| page | INTEGER | NOT NULL | 页码 |
| title | VARCHAR(200) | NULL | 书签标题 |
| created_at | DATETIME | DEFAULT NOW | 创建时间 |

```sql
CREATE TABLE bookmarks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paper_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    page INTEGER NOT NULL,
    title VARCHAR(200),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (paper_id) REFERENCES papers(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

## 四、知识卡片表

### 4.1 cards（知识卡片表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PRIMARY KEY | 卡片ID |
| user_id | INTEGER | FOREIGN KEY | 所属用户 |
| paper_id | INTEGER | FOREIGN KEY | 来源论文 |
| title | VARCHAR(200) | NOT NULL | 标题 |
| type | VARCHAR(20) | NOT NULL | 类型(concept/method/formula/data) |
| content | TEXT | NOT NULL | 内容 |
| created_at | DATETIME | DEFAULT NOW | 创建时间 |
| updated_at | DATETIME | DEFAULT NOW | 更新时间 |

```sql
CREATE TABLE cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    paper_id INTEGER,
    title VARCHAR(200) NOT NULL,
    type VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (paper_id) REFERENCES papers(id)
);
```

### 4.2 card_tags（卡片标签关联表）

```sql
CREATE TABLE card_tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    card_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    FOREIGN KEY (card_id) REFERENCES cards(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE,
    UNIQUE(card_id, tag_id)
);
```

---

## 五、AI 相关表

### 5.1 ai_conversations（AI对话表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PRIMARY KEY | 对话ID |
| user_id | INTEGER | FOREIGN KEY | 用户ID |
| paper_id | INTEGER | FOREIGN KEY | 论文ID |
| title | VARCHAR(200) | NULL | 对话标题 |
| created_at | DATETIME | DEFAULT NOW | 创建时间 |

```sql
CREATE TABLE ai_conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    paper_id INTEGER NOT NULL,
    title VARCHAR(200),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (paper_id) REFERENCES papers(id)
);
```

### 5.2 ai_messages（AI消息表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PRIMARY KEY | 消息ID |
| conversation_id | INTEGER | FOREIGN KEY | 对话ID |
| role | VARCHAR(20) | NOT NULL | 角色(user/assistant) |
| content | TEXT | NOT NULL | 内容 |
| created_at | DATETIME | DEFAULT NOW | 创建时间 |

```sql
CREATE TABLE ai_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES ai_conversations(id) ON DELETE CASCADE
);
```

### 5.3 reviews（文献综述表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PRIMARY KEY | 综述ID |
| user_id | INTEGER | FOREIGN KEY | 用户ID |
| topic | VARCHAR(200) | NOT NULL | 研究主题 |
| paper_ids | JSON | NOT NULL | 参考论文ID列表 |
| status | VARCHAR(20) | DEFAULT 'draft' | 状态 |
| content | JSON | NULL | 各章节内容 |
| created_at | DATETIME | DEFAULT NOW | 创建时间 |
| updated_at | DATETIME | DEFAULT NOW | 更新时间 |

```sql
CREATE TABLE reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    topic VARCHAR(200) NOT NULL,
    paper_ids JSON NOT NULL,
    status VARCHAR(20) DEFAULT 'draft',
    content JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

## 六、团队相关表

### 6.1 teams（团队表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PRIMARY KEY | 团队ID |
| name | VARCHAR(100) | NOT NULL | 团队名 |
| description | TEXT | NULL | 描述 |
| owner_id | INTEGER | FOREIGN KEY | 创建者 |
| created_at | DATETIME | DEFAULT NOW | 创建时间 |

```sql
CREATE TABLE teams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    owner_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES users(id)
);
```

### 6.2 team_members（团队成员表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PRIMARY KEY | ID |
| team_id | INTEGER | FOREIGN KEY | 团队ID |
| user_id | INTEGER | FOREIGN KEY | 用户ID |
| role | VARCHAR(20) | DEFAULT 'member' | 角色(admin/member) |
| joined_at | DATETIME | DEFAULT NOW | 加入时间 |

```sql
CREATE TABLE team_members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    role VARCHAR(20) DEFAULT 'member',
    joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(team_id, user_id)
);
```

### 6.3 team_papers（团队共享论文表）

```sql
CREATE TABLE team_papers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id INTEGER NOT NULL,
    paper_id INTEGER NOT NULL,
    shared_by INTEGER NOT NULL,
    shared_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE,
    FOREIGN KEY (paper_id) REFERENCES papers(id),
    FOREIGN KEY (shared_by) REFERENCES users(id)
);
```

### 6.4 discussions（讨论表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PRIMARY KEY | 讨论ID |
| team_id | INTEGER | FOREIGN KEY | 团队ID |
| paper_id | INTEGER | FOREIGN KEY | 论文ID |
| user_id | INTEGER | FOREIGN KEY | 发起人 |
| title | VARCHAR(200) | NOT NULL | 标题 |
| content | TEXT | NOT NULL | 内容 |
| is_pinned | BOOLEAN | DEFAULT FALSE | 是否置顶 |
| created_at | DATETIME | DEFAULT NOW | 创建时间 |

```sql
CREATE TABLE discussions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id INTEGER NOT NULL,
    paper_id INTEGER,
    user_id INTEGER NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    is_pinned BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (team_id) REFERENCES teams(id),
    FOREIGN KEY (paper_id) REFERENCES papers(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### 6.5 discussion_replies（讨论回复表）

```sql
CREATE TABLE discussion_replies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    discussion_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (discussion_id) REFERENCES discussions(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

## 七、投稿管理表

### 7.1 journals（期刊收藏表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PRIMARY KEY | ID |
| user_id | INTEGER | FOREIGN KEY | 用户ID |
| name | VARCHAR(200) | NOT NULL | 期刊名 |
| type | VARCHAR(20) | NOT NULL | 类型(journal/conference) |
| field | VARCHAR(100) | NULL | 研究领域 |
| impact_factor | DECIMAL(5,2) | NULL | 影响因子 |
| deadline | DATE | NULL | 截稿日期 |
| status | VARCHAR(20) | DEFAULT 'interested' | 状态 |
| acceptance_rate | VARCHAR(10) | NULL | 录用率 |
| review_time | VARCHAR(50) | NULL | 审稿周期 |
| notes | TEXT | NULL | 备注 |
| created_at | DATETIME | DEFAULT NOW | 创建时间 |

```sql
CREATE TABLE journals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name VARCHAR(200) NOT NULL,
    type VARCHAR(20) NOT NULL,
    field VARCHAR(100),
    impact_factor DECIMAL(5,2),
    deadline DATE,
    status VARCHAR(20) DEFAULT 'interested',
    acceptance_rate VARCHAR(10),
    review_time VARCHAR(50),
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

## 八、统计相关表

### 8.1 reading_stats（阅读统计表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PRIMARY KEY | ID |
| user_id | INTEGER | FOREIGN KEY | 用户ID |
| date | DATE | NOT NULL | 日期 |
| papers_read | INTEGER | DEFAULT 0 | 阅读论文数 |
| reading_time | INTEGER | DEFAULT 0 | 阅读时长(分钟) |
| annotations | INTEGER | DEFAULT 0 | 批注数 |
| cards_created | INTEGER | DEFAULT 0 | 创建卡片数 |

```sql
CREATE TABLE reading_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date DATE NOT NULL,
    papers_read INTEGER DEFAULT 0,
    reading_time INTEGER DEFAULT 0,
    annotations INTEGER DEFAULT 0,
    cards_created INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(user_id, date)
);
```

---

## 九、索引设计

```sql
-- 论文表索引
CREATE INDEX idx_papers_user_id ON papers(user_id);
CREATE INDEX idx_papers_folder_id ON papers(folder_id);
CREATE INDEX idx_papers_status ON papers(status);
CREATE INDEX idx_papers_created_at ON papers(created_at);

-- 批注表索引
CREATE INDEX idx_annotations_paper_id ON annotations(paper_id);
CREATE INDEX idx_annotations_user_id ON annotations(user_id);

-- 卡片表索引
CREATE INDEX idx_cards_user_id ON cards(user_id);
CREATE INDEX idx_cards_paper_id ON cards(paper_id);
CREATE INDEX idx_cards_type ON cards(type);

-- AI对话索引
CREATE INDEX idx_ai_conversations_user_id ON ai_conversations(user_id);
CREATE INDEX idx_ai_conversations_paper_id ON ai_conversations(paper_id);

-- 团队成员索引
CREATE INDEX idx_team_members_team_id ON team_members(team_id);
CREATE INDEX idx_team_members_user_id ON team_members(user_id);

-- 阅读统计索引
CREATE INDEX idx_reading_stats_user_id ON reading_stats(user_id);
CREATE INDEX idx_reading_stats_date ON reading_stats(date);
```

---

## 十、ER 图

```
users ──┬── papers ──┬── annotations
        │            ├── bookmarks
        │            ├── paper_tags ── tags
        │            └── ai_conversations ── ai_messages
        │
        ├── folders
        ├── cards ── card_tags ── tags
        ├── reviews
        ├── journals
        ├── reading_stats
        │
        └── team_members ── teams ──┬── team_papers
                                   └── discussions ── discussion_replies
```

---

## 十一、数据迁移脚本

初始化数据库的 SQL 脚本位于 `api/app/db/init.sql`。