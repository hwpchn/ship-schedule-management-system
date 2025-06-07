#!/bin/bash

# 船舶航线管理系统API测试脚本
echo "==============================================="
echo "🚢 船舶航线管理系统 API 测试脚本"
echo "==============================================="

# 检查Python环境
if [ ! -d ".venv" ]; then
  echo "❌ 未找到虚拟环境 (.venv)，请先设置环境"
  echo "提示: 运行以下命令创建虚拟环境并安装依赖"
  echo "  python -m venv .venv"
  echo "  source .venv/bin/activate  # Linux/Mac"
  echo "  pip install -r requirements.txt"
  exit 1
fi

# 激活虚拟环境
echo "🔄 激活虚拟环境..."
if [[ "$OSTYPE" == "darwin"* ]] || [[ "$OSTYPE" == "linux-gnu"* ]]; then
  source .venv/bin/activate
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
  source .venv/Scripts/activate
else
  echo "⚠️ 未知操作系统，请手动激活虚拟环境后再运行测试"
  exit 1
fi

# 检查服务器是否运行
echo "🔍 检查API服务器是否运行..."
curl -s http://127.0.0.1:8000/api/ > /dev/null
if [ $? -ne 0 ]; then
  echo "⚠️ API服务器未运行，尝试在后台启动..."
  nohup python manage.py runserver > server.log 2>&1 &
  SERVER_PID=$!
  echo "🚀 服务器已在后台启动 (PID: $SERVER_PID)"
  sleep 3  # 等待服务器启动
else
  echo "✅ API服务器已运行"
fi

# 运行测试
echo "🧪 开始API综合测试..."
python tests/api_full_test.py

# 测试完成
echo "==============================================="
echo "🏁 测试脚本执行完成"
echo "如需查看详细日志，请查看 server.log 文件"
echo "==============================================="
