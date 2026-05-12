#!/bin/bash

# PaperMate 项目初始化脚本
# 使用方法: ./init.sh

set -e

echo "🚀 PaperMate 项目初始化"
echo "========================"

# 配置
GITHUB_USER="Yaodingtang"
WEB_REPO="git@github.com:${GITHUB_USER}/papermate-web.git"
API_REPO="git@github.com:${GITHUB_USER}/papermate-api.git"
INIT_DIR="/home/hermes/.openclaw/workspace/papermate-init"

# ========== 前端项目 ==========
echo ""
echo "📦 初始化前端项目..."
echo ""

# 创建临时目录
WEB_DIR=$(mktemp -d)
cd $WEB_DIR

# 初始化 Git
git init
git config user.email "papermate@example.com"
git config user.name "PaperMate"

# 复制前端文件
cp -r $INIT_DIR/web/* .

# 创建必要的空目录
mkdir -p app/\(auth\)/login
mkdir -p app/\(auth\)/register
mkdir -p app/\(main\)/discover
mkdir -p app/\(main\)/reading
mkdir -p app/\(main\)/cards
mkdir -p app/\(main\)/review
mkdir -p app/\(main\)/experiment
mkdir -p app/\(main\)/submit
mkdir -p app/\(main\)/track
mkdir -p app/\(main\)/team
mkdir -p components/ui
mkdir -p components/layout
mkdir -p components/paper
mkdir -p components/reader
mkdir -p lib
mkdir -p stores
mkdir -p hooks
mkdir -p types
mkdir -p public
mkdir -p styles

# 创建 .gitignore
cat > .gitignore << 'EOF'
# Dependencies
node_modules
.pnp
.pnp.js

# Testing
coverage

# Next.js
.next/
out/

# Production
build

# Misc
.DS_Store
*.pem

# Debug
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Local env files
.env*.local

# Vercel
.vercel

# TypeScript
*.tsbuildinfo
next-env.d.ts
EOF

# 提交
git add .
git commit -m "Initial commit: Next.js project setup

- Next.js 14 with App Router
- shadcn/ui + Tailwind CSS
- Basic layout with sidebar
- API client setup
- Auth store setup
"

# 推送到 GitHub
git branch -M main
git remote add origin $WEB_REPO
git push -u origin main --force

echo "✅ 前端项目已推送到: $WEB_REPO"

# ========== 后端项目 ==========
echo ""
echo "📦 初始化后端项目..."
echo ""

# 创建临时目录
API_DIR=$(mktemp -d)
cd $API_DIR

# 初始化 Git
git init
git config user.email "papermate@example.com"
git config user.name "PaperMate"

# 复制后端文件
cp -r $INIT_DIR/api/* .

# 创建必要的空目录
mkdir -p app/api/v1
mkdir -p app/core
mkdir -p app/models
mkdir -p app/schemas
mkdir -p app/services
mkdir -p app/tasks
mkdir -p tests

# 创建 __init__.py 文件
touch app/__init__.py
touch app/api/__init__.py
touch app/api/v1/__init__.py
touch app/core/__init__.py
touch app/services/__init__.py
touch app/tasks/__init__.py

# 创建 .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
ENV/
env/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Testing
.pytest_cache/
.coverage
htmlcov/

# Environment
.env
.env.local

# Logs
*.log
logs/

# Database
*.db
*.sqlite3
EOF

# 提交
git add .
git commit -m "Initial commit: FastAPI project setup

- FastAPI with async support
- SQLAlchemy 2.0 models
- JWT authentication
- API endpoints: auth, users, papers, annotations, cards, ai
- Docker configuration
"

# 推送到 GitHub
git branch -M main
git remote add origin $API_REPO
git push -u origin main --force

echo "✅ 后端项目已推送到: $API_REPO"

# ========== 完成 ==========
echo ""
echo "🎉 初始化完成！"
echo ""
echo "=========================================="
echo "📦 前端项目: https://github.com/${GITHUB_USER}/papermate-web"
echo "📦 后端项目: https://github.com/${GITHUB_USER}/papermate-api"
echo "=========================================="
echo ""
echo "下一步操作："
echo ""
echo "1. 克隆前端项目:"
echo "   git clone $WEB_REPO"
echo "   cd papermate-web"
echo "   npm install"
echo "   npm run dev"
echo ""
echo "2. 克隆后端项目:"
echo "   git clone $API_REPO"
echo "   cd papermate-api"
echo "   python -m venv venv"
echo "   source venv/bin/activate"
echo "   pip install -r requirements.txt"
echo "   uvicorn app.main:app --reload"
echo ""
echo "3. 配置环境变量:"
echo "   复制 .env.example 为 .env 并填写配置"
echo ""