#!/usr/bin/env python3
"""
查看 Context7 工具的详细参数信息
"""

import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.mcp.context7_grep import Context7GrepMCPClient


async def inspect_tools():
    """查看工具的详细参数"""
    print("=" * 70)
    print("Context7 工具详细信息")
    print("=" * 70)

    client = Context7GrepMCPClient(context7_need=True, grep_need=False)
    tools = await client.get_tools()

    for tool in tools:
        print(f"\n{'='*70}")
        print(f"工具名称: {tool.name}")
        print(f"{'='*70}")
        print(f"\n描述:\n{tool.description}")

        # 获取参数 schema
        if hasattr(tool, 'args_schema') and tool.args_schema:
            import json

            # 如果是 dict，直接打印
            if isinstance(tool.args_schema, dict):
                print(f"\n参数 Schema:")
                print(json.dumps(tool.args_schema, indent=2, ensure_ascii=False))
            # 如果是对象，获取 JSON Schema
            elif hasattr(tool.args_schema, 'model_json_schema'):
                schema = tool.args_schema.model_json_schema()
                print(f"\n参数 JSON Schema:")
                print(json.dumps(schema, indent=2, ensure_ascii=False))

    await client.close()


if __name__ == "__main__":
    asyncio.run(inspect_tools())
