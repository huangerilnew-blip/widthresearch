"""
Context7 和 Grep MCP 客户端集成模块

使用 langchain-adapter-mcp 连接 Context7 和 Grep MCP 服务器
提供统一的工具接口

注意：这两个 MCP 服务器使用 streamable_http 传输模式连接到远程服务
"""

import os
from typing import List, Dict, Any
from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient


class Context7GrepMCPClient:
    """Context7 和 Grep MCP 服务器的统一客户端"""

    def __init__(self, context7_need:  bool = True, grep_need: bool = True):
        """
        初始化 MCP 客户端

        Args:
            context7_api_key: Context7 API 密钥（如果需要）
            grep_url: Grep MCP 服务器 URL（可选，如果不提供则只连接 Context7）
        """
        self.context7_api_key=os.getenv("CONTEXT7_API_KEY")
        self.context7_need=context7_need
        self.grep_need= grep_need
        self._client = None
        self._tools = None

    def _get_proxy_env(self) -> Dict[str, str]:
        """
        获取代理相关的环境变量

        Returns:
            包含代理环境变量的字典
        """
        proxy_env_vars = [
            'http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY',
            'all_proxy', 'ALL_PROXY', 'no_proxy', 'NO_PROXY'
        ]
        return {k: v for k, v in os.environ.items() if k in proxy_env_vars}

    async def _get_client_config(self) -> Dict[str, Any]:
        """
        构建服务器配置字典

        使用 streamable_http 传输模式连接到远程 MCP 服务器

        Returns:
            服务器配置字典
        """
        config = {}

        #Context7 配置
        if self.context7_need:
            if self.context7_api_key:
                config["context7"] = {
                    "transport": "streamable_http",
                    "url": "https://mcp.context7.com/mcp",
                    "headers": {
                        "Authorization": self.context7_api_key
                    }
                }
            else:
                raise ValueError("缺少context7_api_key,无法使用context7 mcp")

        if self.grep_need:
            config["grep"] = {
                "transport": "stdio",
                "command": "python",
                "args": ["core/mcp/grep_mcp/server.py"],
                "env": self._get_proxy_env(),
            }
        return config

    async def get_tools(self) -> List[BaseTool]:
        """
        获取所有可用的 MCP 工具

        Returns:
            LangChain BaseTool 对象列表
        """
        if self._tools is not None:
            return self._tools

        if self._client is None:
            config = await self._get_client_config()
            self._client = MultiServerMCPClient(config)

        self._tools = await self._client.get_tools()
        return self._tools

    async def get_context7_tools(self) -> List[BaseTool]:
        """
        获取 Context7 相关的工具

        Returns:
            Context7 工具列表
        """
        if not self.context7_need:
            return []
        
        all_tools = await self.get_tools()
        return [tool for tool in all_tools if tool.name in ["resolve-library-id", "query-docs"]]

    async def get_grep_tools(self) -> List[BaseTool]:
        """
        获取 Grep 相关的工具

        Returns:
            Grep 工具列表
        """
        all_tools = await self.get_tools()
        return [tool for tool in all_tools if "grep" in tool.name.lower()]

    async def close(self):
        self._client = None
        self._tools = None


async def create_context7_grep_tools(
    context7_need: bool = True,
    grep_need: bool = True
) -> List[BaseTool]:
    """
    便捷函数：创建并获取 Context7 和 Grep 工具

    Args:
        context7_need: 是否启用 Context7（默认 True）
        grep_need: 是否启用 Grep（默认 True）

    Returns:
        可用工具列表
    """
    client = Context7GrepMCPClient(
        context7_need=context7_need,
        grep_need=grep_need
    )
    return await client.get_tools()


# 使用示例
async def main():
    """示例：如何使用 Context7GrepMCPClient"""

    # 方式 1: 使用便捷函数
    tools = await create_context7_grep_tools()

    print(f"可用工具数量: {len(tools)}")
    for tool in tools:
        print(f"- {tool.name}: {tool.description}")

    # 方式 2: 使用客户端类（更多控制）
    client = Context7GrepMCPClient()

    # 获取所有工具
    all_tools = await client.get_tools()

    # 获取特定类型的工具
    context7_tools = await client.get_context7_tools()
    grep_tools = await client.get_grep_tools()

    # 使用工具
    if grep_tools:
        grep_tool = grep_tools[0]
        result = await grep_tool.ainvoke({
            "pattern": "def.*function",
            "path": "."
        })
        print("Grep 结果:", result)

    # 关闭连接
    await client.close()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
