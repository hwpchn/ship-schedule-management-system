# 🚢 船舶航线管理系统 - 开发工具

.PHONY: help install test lint format clean migrate runserver

# 默认目标
help:
	@echo "🚢 船舶航线管理系统 - 可用命令:"
	@echo ""
	@echo "📦 环境管理:"
	@echo "  install     - 安装依赖包"
	@echo "  install-dev - 安装开发依赖"
	@echo ""
	@echo "🧪 测试相关:"
	@echo "  test        - 运行所有测试"
	@echo "  test-models - 运行模型测试"
	@echo "  test-auth   - 运行认证测试"
	@echo "  test-api    - 运行API测试"
	@echo "  coverage    - 生成覆盖率报告"
	@echo ""
	@echo "🔧 代码质量:"
	@echo "  lint        - 代码质量检查"
	@echo "  format      - 代码格式化"
	@echo "  check       - 运行所有检查"
	@echo ""
	@echo "🗄️ 数据库:"
	@echo "  migrate     - 执行数据库迁移"
	@echo "  makemigrations - 创建迁移文件"
	@echo ""
	@echo "🚀 服务器:"
	@echo "  runserver   - 启动开发服务器"
	@echo "  shell       - 启动Django shell"
	@echo ""
	@echo "🧹 清理:"
	@echo "  clean       - 清理缓存文件"

# 环境管理
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt

# 测试
test:
	python manage.py test --settings=ship_schedule.test_settings

test-models:
	python run_tests.py models

test-auth:
	python run_tests.py auth

test-api:
	python run_tests.py api

coverage:
	python run_tests.py coverage

# 代码质量
lint:
	flake8 .
	mypy .

format:
	black .
	isort .

check: lint test
	@echo "✅ 所有检查通过"

# 数据库
migrate:
	python manage.py migrate

makemigrations:
	python manage.py makemigrations

# 服务器
runserver:
	python manage.py runserver

shell:
	python manage.py shell

# 清理
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
