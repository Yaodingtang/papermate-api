#!/bin/bash

# PaperMate 项目打包脚本
# 使用方法: ./pack.sh

set -e

echo "📦 打包 PaperMate 项目..."
echo ""

INIT_DIR="/home/hermes/.openclaw/workspace/papermate-init"
OUTPUT_DIR="/home/hermes/.openclaw/workspace/papermate-release"

# 清理输出目录
rm -rf $OUTPUT_DIR
mkdir -p $OUTPUT_DIR

# ========== 打包前端项目 ==========
echo "📦 打包前端项目..."
WEB_DIR=$OUTPUT_DIR/papermate-web
mkdir -p $WEB_DIR

# 复制前端文件
cp -r $INIT_DIR/web/* $WEB_DIR/

# 创建必要的空目录
mkdir -p $WEB_DIR/app/\(auth\)/login
mkdir -p $WEB_DIR/app/\(auth\)/register
mkdir -p $WEB_DIR/app/\(main\)/discover
mkdir -p $WEB_DIR/app/\(main\)/reading
mkdir -p $WEB_DIR/app/\(main\)/cards
mkdir -p $WEB_DIR/app/\(main\)/review
mkdir -p $WEB_DIR/app/\(main\)/experiment
mkdir -p $WEB_DIR/app/\(main\)/submit
mkdir -p $WEB_DIR/app/\(main\)/track
mkdir -p $WEB_DIR/app/\(main\)/team
mkdir -p $WEB_DIR/components/ui
mkdir -p $WEB_DIR/components/layout
mkdir -p $WEB_DIR/components/paper
mkdir -p $WEB_DIR/components/reader
mkdir -p $WEB_DIR/lib
mkdir -p $WEB_DIR/stores
mkdir -p $WEB_DIR/hooks
mkdir -p $WEB_DIR/types
mkdir -p $WEB_DIR/public
mkdir -p $WEB_DIR/styles

# 创建 .gitignore
cat > $WEB_DIR/.gitignore << 'EOF'
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

# 创建 .env.example
cat > $WEB_DIR/.env.example << 'EOF'
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
EOF

echo "✅ 前端项目已打包到: $WEB_DIR"

# ========== 打包后端项目 ==========
echo "📦 打包后端项目..."
API_DIR=$OUTPUT_DIR/papermate-api
mkdir -p $API_DIR

# 复制后端文件
cp -r $INIT_DIR/api/* $API_DIR/

# 创建必要的空目录
mkdir -p $API_DIR/app/api/v1
mkdir -p $API_DIR/app/core
mkdir -p $API_DIR/app/models
mkdir -p $API_DIR/app/schemas
mkdir -p $API_DIR/app/services
mkdir -p $API_DIR/app/tasks
mkdir -p $API_DIR/tests

# 创建 __init__.py 文件
touch $API_DIR/app/__init__.py
touch $API_DIR/app/api/__init__.py
touch $API_DIR/app/api/v1/__init__.py
touch $API_DIR/app/core/__init__.py
touch $API_DIR/app/services/__init__.py
touch $API_DIR/app/tasks/__init__.py

# 创建 .gitignore
cat > $API_DIR/.gitignore << 'EOF'
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

echo "✅ 后端项目已打包到: $API_DIR"

# ========== 创建压缩包 ==========
echo ""
echo "📦 创建压缩包..."
cd $OUTPUT_DIR
tar -czvf papermate-projects.tar.gz papermate-web papermate-api

echo ""
echo "🎉 打包完成！"
echo ""
echo "压缩包位置: $OUTPUT_DIR/papermate-projects.tar.gz"
echo ""
echo "解压后，请手动推送到 GitHub："
echo ""
echo "1. 解压压缩包:"
echo "   tar -xzvf papermate-projects.tar.gz"
echo ""
echo "2. 推送前端项目:"
echo "   cd papermate-web"
echo "   git init"
echo "   git add ."
echo "   git commit -m 'Initial commit'"
echo "   git branch -M main"
echo "   git remote add origin https://github.com/Yaodingtang/papermate-web.git"
echo "   git push -u origin main"
echo ""
echo "3. 推送后端项目:"
echo "   cd papermate-api"
echo "   git init"
echo "   git add ."
echo "   git commit -m 'Initial commit'"
echo "   git branch -M main"
echo "   git remote add origin https://github.com/Yaodingtang/papermate-api.git"
echo "   git push -u origin main"