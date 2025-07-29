"""
AIMCP库的基本测试
"""

import pytest
import json
import tempfile
import os
from unittest.mock import AsyncMock, Mock, patch
from aimcp import AIMCP


class TestAIMCP:
    def test_init_with_api_key(self):
        """测试使用API key初始化"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"mcpServers": {}}, f)
            mcp_config_path = f.name
        
        try:
            client = AIMCP(
                mcp_config_path=mcp_config_path,
                api_key="test-key"
            )
            assert client.api_key == "test-key"
            assert client.model == "gpt-4o-mini"
            assert client.language == "中文"
        finally:
            os.unlink(mcp_config_path)
    
    def test_init_with_env_var(self):
        """测试使用环境变量初始化"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"mcpServers": {}}, f)
            mcp_config_path = f.name
        
        try:
            with patch.dict(os.environ, {'OPENAI_API_KEY': 'env-key'}):
                client = AIMCP(mcp_config_path=mcp_config_path)
                assert client.api_key == "env-key"
        finally:
            os.unlink(mcp_config_path)
    
    def test_init_without_api_key(self):
        """测试没有API key时的错误处理"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"mcpServers": {}}, f)
            mcp_config_path = f.name
        
        try:
            with patch.dict(os.environ, {}, clear=True):
                with pytest.raises(ValueError, match="API key is required"):
                    AIMCP(mcp_config_path=mcp_config_path)
        finally:
            os.unlink(mcp_config_path)
    
    def test_init_missing_config_file(self):
        """测试配置文件不存在时的错误处理"""
        with pytest.raises(FileNotFoundError):
            AIMCP(
                mcp_config_path="nonexistent.json",
                api_key="test-key"
            )
    
    def test_get_available_tools_no_config(self):
        """测试没有工具配置文件时返回空列表"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"mcpServers": {}}, f)
            mcp_config_path = f.name
        
        try:
            client = AIMCP(
                mcp_config_path=mcp_config_path,
                tools_config_path="nonexistent.json",
                api_key="test-key"
            )
            tools = client.get_available_tools()
            assert tools == []
        finally:
            os.unlink(mcp_config_path)
    
    def test_get_available_tools_with_config(self):
        """测试有工具配置文件时返回工具列表"""
        tools_data = [
            {
                "name": "test_tool",
                "aimcp_name": "测试工具",
                "aimcp_description": "这是一个测试工具"
            }
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as mcp_f:
            json.dump({"mcpServers": {}}, mcp_f)
            mcp_config_path = mcp_f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tools_f:
            json.dump(tools_data, tools_f)
            tools_config_path = tools_f.name
        
        try:
            client = AIMCP(
                mcp_config_path=mcp_config_path,
                tools_config_path=tools_config_path,
                api_key="test-key"
            )
            tools = client.get_available_tools()
            assert len(tools) == 1
            assert tools[0]["name"] == "测试工具"
            assert tools[0]["description"] == "这是一个测试工具"
        finally:
            os.unlink(mcp_config_path)
            os.unlink(tools_config_path)


if __name__ == "__main__":
    pytest.main([__file__]) 