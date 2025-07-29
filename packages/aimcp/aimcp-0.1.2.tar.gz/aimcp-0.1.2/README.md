# AIMCP - AI-Enhanced MCP Tool Manager

[![PyPI version](https://badge.fury.io/py/aimcp.svg)](https://badge.fury.io/py/aimcp)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

AIMCP 是一个基于 MCP (Model Context Protocol) 的工具管理器，主要用于统一管理和规范化工具描述。

## 主要功能

- 🤖 使用大语言模型自动生成标准化的工具描述
- 🔧 通过配置文件统一管理多个 MCP Server
- 📝 支持手动编辑工具描述（无需AI生成）
- 🌍 支持多语言工具描述

## 安装

```bash
pip install aimcp
```

## 快速开始

### 基本使用

```python
from aimcp import AIMCP
import asyncio

# 初始化客户端
client = AIMCP(
    mcp_config_path="./mcp_config.json",
    tools_config_path="./tools_config.json",
    api_key="your-api-key",  # 可选，也可通过环境变量设置
    model="gpt-4o-mini",
    language="中文"
)

# 生成工具配置
# ai_create=True：使用AI生成描述
# ai_create=False：使用原始描述，可后续手动修改
res = asyncio.run(client.create_aimcp_tools(ai_create=False))
```

### MCP配置示例

`mcp_config.json`:
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed/files"],
      "env": {}
    }
  }
}
```

## 未来规划

- 工具路由功能
- 错误处理优化
- 更多服务端集成

## 许可证

MIT License 