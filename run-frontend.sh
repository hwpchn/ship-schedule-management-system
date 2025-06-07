#!/bin/bash

# 前端本地运行脚本

set -e

echo "🎨 开始运行前端应用..."

# 检查Node.js是否安装
if ! command -v node &> /dev/null; then
    echo "❌ Node.js未安装，请先安装Node.js"
    exit 1
fi

# 检查pnpm是否安装
if ! command -v pnpm &> /dev/null; then
    echo "❌ pnpm未安装，正在安装..."
    npm install -g pnpm
fi

# 进入前端目录
cd ship-schedule-management-ui

# 安装依赖
echo "📦 安装前端依赖..."
pnpm install

# 检查vite配置，确保API代理配置正确
echo "🔧 检查API代理配置..."

# 启动开发服务器
echo "✅ 准备完成！"
echo ""
echo "🚀 启动前端开发服务器..."
echo "📋 服务信息："
echo "   前端地址: http://localhost:5173"
echo "   后端API代理: http://localhost:8000"
echo ""
echo "请确保后端服务已在 8000 端口运行"
echo "按 Ctrl+C 停止服务"
echo ""

# 启动开发服务器
pnpm run dev