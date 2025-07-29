from fastmcp import Client
import asyncio
import json
from openai import AsyncOpenAI
import os
from pydantic import BaseModel
from typing import Any, Dict, List, Optional, Union
from ._prompt import TOOL_PROMPT


class Tool(BaseModel):
    name: str
    description: str

class AIMCP:
    def __init__(self, 
                 mcp_config_path: str = "./mcp_config.json", 
                 tools_config_path: str = "./tools_config.json",
                 api_key: Optional[str] = None,
                 base_url: Optional[str] = None,
                 model: str = "gpt-4o-mini",
                 language: str = "中文"
                 ):
        """
        初始化AIMCP客户端
        
        Args:
            mcp_config_path: MCP配置文件路径
            tools_config_path: 工具配置文件路径
            api_key: OpenAI API密钥，如果不提供将从环境变量OPENAI_API_KEY获取
            base_url: API基础URL，如果不提供将从环境变量OPENAI_BASE_URL获取
            model: 使用的AI模型名称
            language: 生成描述的语言
        """
        self.tools_config_path = tools_config_path
        self.mcp_config_path = mcp_config_path
        self.language = language
        self.model = model
        
        # 从环境变量或参数获取API配置
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL")
        
        if not self.api_key:
            raise ValueError("API key is required. Please provide it as parameter or set OPENAI_API_KEY environment variable.")
        
        # 加载MCP配置
        try:
            with open(self.mcp_config_path, "r", encoding="utf-8") as f:
                self.mcp_config = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"MCP config file not found: {self.mcp_config_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in MCP config file: {self.mcp_config_path}")
        
        # 初始化客户端
        self.mcp_client = Client(self.mcp_config)
        
        llm_kwargs = {"api_key": self.api_key}
        if self.base_url:
            llm_kwargs["base_url"] = self.base_url
            
        self.llm_client = AsyncOpenAI(**llm_kwargs)

    async def load_mcp_tools(self):
        """加载MCP工具列表"""
        async with self.mcp_client as client:
            tools = await client.list_tools()
            return [{**vars(tool)} for tool in tools]
    
    async def llm_create_description(self, tool: Dict[str, Any], prompt: str = TOOL_PROMPT):
        """使用AI生成工具描述"""
        tool_str = json.dumps(tool, ensure_ascii=False)
        prompt = prompt.format(tool_name=tool_str, language=self.language)
        
        try:
            response = await self.llm_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            parsed_content = json.loads(content)
            return {
                "name": parsed_content.get("name", tool["name"]),
                "description": parsed_content.get("description", tool["description"])
            }
        except Exception as e:
            print(f"生成描述失败: {e}")
            return {"name": tool["name"], "description": tool["description"]}
        
    async def create_aimcp_tools(self, output_path: Optional[str] = None, ai_create: bool = False):
        """
        创建AIMCP工具配置文件
        
        Args:
            output_path: 输出文件路径，默认使用tools_config_path
            ai_create: 是否使用AI生成工具描述
            
        Returns:
            str: 输出文件路径
        """
        if output_path is None:
            output_path = self.tools_config_path
            
        tools = await self.load_mcp_tools()
        aimcp_tools = []
        
        for tool in tools:
            if ai_create:
                aimcp_item = await self.llm_create_description(tool)
                item = {
                    **tool,
                    "aimcp_name": aimcp_item["name"],
                    "aimcp_description": aimcp_item["description"]
                }
            else:
                item = {
                    **tool,
                    "aimcp_name": tool["name"],
                    "aimcp_description": tool["description"]
                }
            aimcp_tools.append(item)
        
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(aimcp_tools, f, ensure_ascii=False, indent=4)
        
        return output_path
    
    async def call_tool(self, name: str, arguments: Optional[Dict[str, Any]] = None):
        """
        调用指定的工具
        
        Args:
            name: 工具名称
            arguments: 工具参数
            
        Returns:
            工具执行结果
        """
        try:
            with open(self.tools_config_path, "r", encoding="utf-8") as f:
                tools_config = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Tools config file not found: {self.tools_config_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in tools config file: {self.tools_config_path}")
        
        call_tool = None
        for tool in tools_config:
            if tool["name"] == name:
                call_tool = tool
                break
        
        if call_tool is None:
            raise ValueError(f"Tool '{name}' not found in tools config")
        
        async with self.mcp_client as client:
            try:
                result = await client.call_tool(call_tool["name"], arguments)
                return result
            except Exception as e:
                return f"执行工具'{name}'失败，参数：{arguments}，错误信息：{e}"

    def get_available_tools(self):
        """获取可用工具列表"""
        try:
            with open(self.tools_config_path, "r", encoding="utf-8") as f:
                tools_config = json.load(f)
            return [tool for tool in tools_config]
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            return []


if __name__ == "__main__":
    # 示例用法
    t = AIMCP(mcp_config_path="/home/qichen/zh/aimcp/mcp_config.json")
    print(asyncio.run(t.create_aimcp_tools(ai_create=False)))