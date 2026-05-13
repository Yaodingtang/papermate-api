# PaperMate Pro - 更新日志

## 2026-05-13 更新

### 🔒 安全问题修复 (P0)

#### 1. API Key 安全
- **问题**: AI API Key 硬编码在代码中
- **修复**: 
  - API Key 现在从环境变量 `AI_API_KEY` 读取
  - 支持从 `.env` 文件配置
  - 添加 `get_ai_api_key()` 函数统一管理

#### 2. 文件上传安全
- **问题**: 文件上传缺少安全检查
- **修复**:
  - 检查文件扩展名（只允许 .pdf）
  - 检查文件大小（限制 50MB）
  - 检查文件头签名（防止伪造扩展名）
  - 使用 python-magic 检查真实 MIME 类型
  - 防止路径遍历攻击

#### 3. 速率限制
- **问题**: API 无速率限制，可能被滥用
- **修复**:
  - 使用 slowapi 添加速率限制
  - 文件上传: 10次/分钟
  - AI 对话: 30次/分钟
  - 元数据查询: 20次/分钟
  - 摘要生成: 10次/分钟

### 🚀 功能实现 (P0)

#### 1. PDF 解析服务
新增 `app/services/pdf_service.py`，支持：
- 提取 PDF 元数据（标题、作者、页数等）
- 按页提取文本内容
- 提取目录结构
- 提取图片和表格信息
- 自动提取摘要和参考文献
- 生成页面预览图
- 文本搜索功能

#### 2. 论文元数据服务
新增 `app/services/metadata_service.py`，支持：
- 通过 DOI 获取论文信息（Crossref API）
- 搜索学术论文
- 从文本中提取 DOI
- 获取引用链

#### 3. 前端 API 连接
- 创建 `hooks/usePapers.ts` 自定义 Hook
- 书架页面连接真实 API
- 添加加载状态和错误处理

### 🎨 代码优化 (P1)

#### 1. 错误边界
新增 `components/ErrorBoundary.tsx`：
- `ErrorBoundary` - 通用错误边界
- `PageErrorBoundary` - 页面级错误边界
- `CardErrorBoundary` - 卡片级错误边界

#### 2. 骨架屏
新增 `components/Skeleton.tsx`：
- `Skeleton` - 基础骨架屏
- `PaperCardSkeleton` - 论文卡片骨架屏
- `PaperListSkeleton` - 论文列表骨架屏
- `PaperDetailSkeleton` - 论文详情骨架屏
- `StatCardSkeleton` - 统计卡片骨架屏
- `TableSkeleton` - 表格骨架屏

### ✨ 新功能 (P2)

#### 1. 智能摘要
新增 API 端点：
- `POST /api/v1/ai/summary/generate` - 生成摘要（支持简洁/详细/要点三种模式）
- `POST /api/v1/ai/summary/translate` - 翻译摘要
- `POST /api/v1/ai/summary/keypoints` - 提取关键点

#### 2. 引用追踪
新增 API 端点：
- `GET /api/v1/ai/citations/{paper_id}` - 获取引用网络
- `GET /api/v1/ai/citations/trending` - 获取热门被引论文
- `POST /api/v1/ai/citations/compare` - 对比论文引用

### 📦 依赖更新

新增依赖：
- `slowapi==0.1.9` - 速率限制
- `pdfplumber==0.11.0` - PDF 解析
- `python-magic==0.4.27` - 文件类型检测
- `habanero==1.2.6` - Crossref API 客户端

---

## 部署说明

### 环境变量配置

创建 `.env` 文件：

```env
# AI API 配置
AI_API_KEY=your_api_key_here
AI_API_URL=https://spark-api-open.xf-yun.com/v1/chat/completions
AI_MODEL=generalv3.5

# 数据库
DATABASE_URL=sqlite+aiosqlite:///./data/papermate.db

# JWT
JWT_SECRET=your_jwt_secret_here

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost:3001"]
```

### 启动服务

```bash
# 后端
cd papermate-api/api
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8100

# 前端
cd papermate-web
npm install
npm run dev
```

---

## API 文档

访问 http://localhost:8100/docs 查看完整 API 文档。
