# 贡献指南

感谢你对AIMCP项目的兴趣！以下是参与贡献的指南。

## 开发环境设置

1. **克隆仓库**
   ```bash
   git clone https://github.com/yourusername/aimcp.git
   cd aimcp
   ```

2. **创建虚拟环境**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或
   venv\Scripts\activate     # Windows
   ```

3. **安装开发依赖**
   ```bash
   make install-dev
   # 或
   pip install -e ".[dev]"
   pip install build twine
   ```

## 开发流程

### 代码规范

- 使用 `black` 进行代码格式化
- 使用 `isort` 进行导入排序
- 使用 `flake8` 进行代码检查
- 使用 `mypy` 进行类型检查

运行所有检查：
```bash
make format    # 格式化代码
make lint      # 代码检查
make type-check # 类型检查
```

### 测试

- 编写测试用例在 `tests/` 目录下
- 运行测试：`make test` 或 `pytest`
- 确保所有测试通过

### 提交规范

使用清晰的提交信息：
```
feat: 添加新功能
fix: 修复bug
docs: 更新文档
style: 代码格式调整
refactor: 重构代码
test: 添加测试
chore: 其他改动
```

## 发布到PyPI

### 准备工作

1. **注册PyPI账号**
   - 到 [PyPI](https://pypi.org) 注册账号
   - 生成API token

2. **配置认证**
   ```bash
   # 创建 ~/.pypirc 文件
   [pypi]
   username = __token__
   password = pypi-your-api-token-here
   ```

### 发布步骤

#### 方法1: 使用Makefile（推荐）

```bash
# 1. 更新版本号
# 编辑 mcp/__init__.py 和 pyproject.toml 中的版本号

# 2. 运行发布检查
make release

# 3. 发布到PyPI
make upload
```

#### 方法2: 手动发布

```bash
# 1. 清理旧文件
make clean

# 2. 格式化和检查代码
make format
make lint
make type-check

# 3. 运行测试
make test

# 4. 构建包
make build

# 5. 检查包
twine check dist/*

# 6. 上传到测试PyPI（可选）
make upload-test

# 7. 上传到正式PyPI
make upload
```

### 版本管理

采用[语义化版本](https://semver.org/lang/zh-CN/)：
- `MAJOR.MINOR.PATCH`
- 主版本号：不兼容的API修改
- 次版本号：向下兼容的功能性新增
- 修订号：向下兼容的问题修正

### GitHub Actions自动发布

项目配置了GitHub Actions，当创建release时会自动发布到PyPI：

1. **设置PyPI token**
   - 在GitHub仓库设置中添加secret：`PYPI_API_TOKEN`

2. **创建Release**
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```
   
   然后在GitHub上创建Release，GitHub Actions会自动运行测试并发布到PyPI。

## 目录结构

```
aimcp/
├── mcp/                    # 主包
│   ├── __init__.py
│   ├── aimcp.py           # 主要类
│   └── _prompt.py         # AI提示词
├── tests/                 # 测试文件
├── .github/workflows/     # GitHub Actions
├── pyproject.toml        # 包配置
├── README.md            # 项目说明
├── LICENSE              # 许可证
├── Makefile            # 构建脚本
└── example.py          # 使用示例
```

## 问题报告

如果发现问题，请在GitHub Issues中报告：
1. 描述问题的详细信息
2. 提供复现步骤
3. 包含错误信息和环境信息

## 功能请求

欢迎提交功能请求：
1. 在Issues中描述需求
2. 说明使用场景
3. 如果可能，提供实现思路

## Pull Request

1. Fork仓库
2. 创建功能分支：`git checkout -b feature/amazing-feature`
3. 提交改动：`git commit -m 'Add amazing feature'`
4. 推送分支：`git push origin feature/amazing-feature`
5. 创建Pull Request

## 许可证

通过贡献代码，你同意你的贡献将在MIT许可证下授权。 