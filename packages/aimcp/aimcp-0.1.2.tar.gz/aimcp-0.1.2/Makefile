.PHONY: help install install-dev test format lint type-check clean build upload-test upload release

help:
	@echo "AIMCP开发工具"
	@echo ""
	@echo "可用命令:"
	@echo "  install        安装包"
	@echo "  install-dev    安装开发依赖"
	@echo "  test          运行测试"
	@echo "  format        格式化代码"
	@echo "  lint          代码检查"
	@echo "  type-check    类型检查"
	@echo "  clean         清理构建文件"
	@echo "  build         构建包"
	@echo "  upload-test   上传到测试PyPI"
	@echo "  upload        上传到PyPI"
	@echo "  release       完整发布流程"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"
	pip install build twine

test:
	pytest

format:
	black mcp/
	isort mcp/

lint:
	flake8 mcp/

type-check:
	mypy mcp/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

upload-test: build
	python -m twine upload --repository testpypi dist/*

upload: build
	python -m twine upload dist/*

release: clean format lint type-check build
	@echo "准备发布到PyPI..."
	@echo "请确认版本号正确，然后运行: make upload" 