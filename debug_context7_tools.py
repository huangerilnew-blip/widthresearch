"""
调试 Context7 工具 - 查看实际返回的工具名称
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

import sys
sys.path.insert(0, '.')

from core.mcp.context7_grep import Context7GrepMCPClient


async def debug_context7_tools():
    """调试 Context7 返回的工具"""
    print("=" * 60)
    print("Context7 工具调试")
    print("=" * 60)
    
    if not os.getenv("CONTEXT7_API_KEY"):
        print("❌ 未设置 CONTEXT7_API_KEY")
        return
    
    print(f"\n✓ API Key: {os.getenv('CONTEXT7_API_KEY')[:20]}...")
    
    try:
        print("\n[1] 创建 Context7 客户端...")
        client = Context7GrepMCPClient(context7_need=True, grep_need=False)
        
        print("[2] 获取所有工具...")
        all_tools = await client.get_tools()
        
        print(f"\n✓ 总共获取到 {len(all_tools)} 个工具\n")
        
        print("工具详细信息:")
        print("-" * 60)
        for i, tool in enumerate(all_tools, 1):
            print(f"\n工具 {i}:")
            print(f"  名称: {tool.name}")
            print(f"  描述: {tool.description[:100]}...")
            print(f"  类型: {type(tool).__name__}")
            
            # 检查是否匹配 context7_ 前缀
            if tool.name.startswith("context7_"):
                print(f"  ✓ 匹配 context7_ 前缀")
            else:
                print(f"  ✗ 不匹配 context7_ 前缀")
        
        print("\n" + "-" * 60)
        
        # 使用过滤方法
        print("\n[3] 使用 get_context7_tools() 过滤...")
        context7_tools = await client.get_context7_tools()
        print(f"过滤后的 Context7 工具数: {len(context7_tools)}")
        
        if context7_tools:
            for tool in context7_tools:
                print(f"  - {tool.name}")
        else:
            print("  (无)")
        
        await client.close()
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(debug_context7_tools())
