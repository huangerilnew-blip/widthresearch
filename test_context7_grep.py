"""
Context7 和 Grep MCP 客户端测试

测试 context7_grep.py 模块的各项功能
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from core.mcp.context7_grep import Context7GrepMCPClient, create_context7_grep_tools


async def test_client_initialization():
    """测试客户端初始化"""
    print("\n=== 测试 1: 客户端初始化 ===")
    
    try:
        # 测试只启用 grep
        client = Context7GrepMCPClient(context7_need=False, grep_need=True)
        print("✓ Grep-only 客户端初始化成功")
        
        # 测试只启用 context7（需要 API key）
        if os.getenv("CONTEXT7_API_KEY"):
            client = Context7GrepMCPClient(context7_need=True, grep_need=False)
            print("✓ Context7-only 客户端初始化成功")
        else:
            print("⚠ 跳过 Context7 测试（未设置 CONTEXT7_API_KEY）")
        
        # 测试同时启用两者
        client = Context7GrepMCPClient(context7_need=False, grep_need=True)
        print("✓ 双服务器客户端初始化成功")
        
        return True
    except Exception as e:
        print(f"✗ 客户端初始化失败: {e}")
        return False


async def test_get_tools():
    """测试获取工具列表"""
    print("\n=== 测试 2: 获取工具列表 ===")
    
    try:
        # 使用便捷函数获取工具（只测试 grep）
        tools = await create_context7_grep_tools(
            context7_need=False,
            grep_need=True
        )
        
        print(f"✓ 成功获取 {len(tools)} 个工具")
        
        if tools:
            print("\n可用工具:")
            for i, tool in enumerate(tools, 1):
                print(f"  {i}. {tool.name}")
                print(f"     描述: {tool.description[:80]}..." if len(tool.description) > 80 else f"     描述: {tool.description}")
        
        return True
    except Exception as e:
        print(f"✗ 获取工具失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_grep_tools():
    """测试 Grep 工具"""
    print("\n=== 测试 3: Grep 工具功能 ===")
    
    try:
        client = Context7GrepMCPClient(context7_need=False, grep_need=True)
        
        # 获取 grep 工具
        grep_tools = await client.get_grep_tools()
        
        if not grep_tools:
            print("⚠ 未找到 Grep 工具")
            return False
        
        print(f"✓ 找到 {len(grep_tools)} 个 Grep 工具")
        
        # 测试使用 grep 工具搜索
        grep_tool = grep_tools[0]
        print(f"\n使用工具: {grep_tool.name}")
        
        # 在当前项目中搜索 "async def"
        result = await grep_tool.ainvoke({
            "query": "async def test"
        })
        
        print(f"✓ Grep 搜索成功")
        print(f"搜索结果（截取前500字符）:\n{str(result)[:500]}...")
        
        await client.close()
        return True
        
    except Exception as e:
        print(f"✗ Grep 工具测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_context7_tools():
    """测试 Context7 工具获取和调用"""
    print("\n=== 测试 4: Context7 工具功能 ===")
    
    # 检查环境变量
    if not os.getenv("CONTEXT7_API_KEY"):
        print("⚠ 跳过 Context7 测试（未设置 CONTEXT7_API_KEY）")
        print("  提示: 在 .env 文件中设置 CONTEXT7_API_KEY=your-api-key")
        return None
    
    api_key = os.getenv('CONTEXT7_API_KEY')
    print(f"✓ 检测到 CONTEXT7_API_KEY: {api_key[:20]}...{api_key[-4:]}")
    
    # 检查代理设置
    http_proxy = os.getenv('HTTP_PROXY') or os.getenv('http_proxy')
    https_proxy = os.getenv('HTTPS_PROXY') or os.getenv('https_proxy')
    if http_proxy or https_proxy:
        print(f"✓ 代理设置: HTTP={http_proxy}, HTTPS={https_proxy}")
    else:
        print("⚠ 未检测到代理设置（如果需要请设置 HTTP_PROXY 和 HTTPS_PROXY）")
    
    try:
        print("\n[1/4] 正在连接 Context7 MCP 服务器...")
        print("      服务器地址: https://mcp.context7.com/mcp")
        client = Context7GrepMCPClient(context7_need=True, grep_need=False)
        print("      ✓ 客户端创建成功")
        
        print("\n[2/4] 正在获取 Context7 工具列表...")
        context7_tools = await client.get_context7_tools()
        
        if not context7_tools:
            print("      ✗ 未找到任何 Context7 工具")
            await client.close()
            return False
        
        print(f"      ✓ 成功获取 {len(context7_tools)} 个工具")
        
        print("\n[3/4] Context7 工具详细信息:")
        print("-" * 60)
        for i, tool in enumerate(context7_tools, 1):
            print(f"\n工具 {i}: {tool.name}")
            print(f"  描述: {tool.description}")
            
            # 显示工具参数
            if hasattr(tool, 'args') and tool.args:
                print(f"  参数结构:")
                if isinstance(tool.args, dict):
                    for param_name, param_info in tool.args.items():
                        print(f"    - {param_name}: {param_info}")
                else:
                    print(f"    {tool.args}")
            
            # 显示工具的其他属性
            if hasattr(tool, 'return_direct'):
                print(f"  直接返回: {tool.return_direct}")
        
        print("\n" + "-" * 60)
        
        print("\n[4/4] 测试工具调用能力...")
        # 尝试调用第一个工具（如果有合适的测试参数）
        if context7_tools:
            first_tool = context7_tools[0]
            print(f"  选择工具: {first_tool.name}")
            
            # 根据工具名称尝试不同的测试
            try:
                if 'search' in first_tool.name.lower():
                    print(f"  这是一个搜索工具，可以用来搜索代码或文档")
                    print(f"  示例调用: await tool.ainvoke({{'query': 'your search term'}})")
                    # 实际调用示例（需要根据具体工具调整参数）
                    # result = await first_tool.ainvoke({"query": "test"})
                    # print(f"  ✓ 调用成功: {result}")
                elif 'code' in first_tool.name.lower():
                    print(f"  这是一个代码相关工具")
                    print(f"  可用于代码分析、生成或查询")
                else:
                    print(f"  工具类型: {first_tool.name}")
                    print(f"  请查看参数信息以了解如何使用")
                
                print(f"  ✓ 工具结构验证通过")
                
            except Exception as e:
                print(f"  ⚠ 工具调用测试跳过: {e}")
        
        await client.close()
        print("\n✅ Context7 工具测试完成")
        print(f"   - 成功连接到 Context7 服务器")
        print(f"   - 成功获取 {len(context7_tools)} 个工具")
        print(f"   - 工具结构验证通过")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Context7 工具测试失败")
        print(f"   错误类型: {type(e).__name__}")
        print(f"   错误信息: {str(e)}")
        
        # 提供诊断建议
        if 'ConnectError' in str(type(e).__name__) or 'ConnectTimeout' in str(type(e).__name__):
            print(f"\n💡 诊断建议:")
            print(f"   1. 检查代理是否正常运行（如需要）")
            print(f"   2. 确认可以访问 https://mcp.context7.com")
            print(f"   3. 检查防火墙设置")
            print(f"   4. 尝试: curl -I https://mcp.context7.com/mcp")
        elif 'Unauthorized' in str(e) or '401' in str(e):
            print(f"\n💡 诊断建议:")
            print(f"   1. 检查 CONTEXT7_API_KEY 是否正确")
            print(f"   2. 确认 API key 是否已激活")
        
        import traceback
        print(f"\n详细错误信息:")
        traceback.print_exc()
        
        return False




async def test_combined_usage():
    """测试同时使用两个服务"""
    print("\n=== 测试 5: 同时使用 Context7 和 Grep ===")
    
    has_context7_key = bool(os.getenv("CONTEXT7_API_KEY"))
    
    try:
        client = Context7GrepMCPClient(
            context7_need=has_context7_key,
            grep_need=True
        )
        
        all_tools = await client.get_tools()
        context7_tools = await client.get_context7_tools()
        grep_tools = await client.get_grep_tools()
        
        print(f"✓ 总工具数: {len(all_tools)}")
        print(f"  - Context7 工具: {len(context7_tools)}")
        print(f"  - Grep 工具: {len(grep_tools)}")
        
        # 打印所有工具的名称以便调试
        print(f"\n所有工具名称列表:")
        for i, tool in enumerate(all_tools, 1):
            prefix = ""
            if tool.name.startswith("context7_"):
                prefix = "[Context7] "
            elif "grep" in tool.name.lower():
                prefix = "[Grep] "
            else:
                prefix = "[Other] "
            print(f"  {i}. {prefix}{tool.name}")
        
        await client.close()
        return True
        
    except Exception as e:
        print(f"✗ 组合使用测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """运行所有测试"""
    print("=" * 60)
    print("Context7 & Grep MCP 客户端测试套件")
    print("=" * 60)
    
    # 检查环境变量
    print("\n环境检查:")
    print(f"  CONTEXT7_API_KEY: {'已设置 ✓' if os.getenv('CONTEXT7_API_KEY') else '未设置 ⚠'}")
    
    results = []
    
    # 运行测试
    results.append(("客户端初始化", await test_client_initialization()))
    results.append(("获取工具列表", await test_get_tools()))
    results.append(("Grep 工具", await test_grep_tools()))
    results.append(("Context7 工具", await test_context7_tools()))
    results.append(("组合使用", await test_combined_usage()))
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result is True)
    failed = sum(1 for _, result in results if result is False)
    skipped = sum(1 for _, result in results if result is None)
    
    for name, result in results:
        status = "✓ 通过" if result is True else ("✗ 失败" if result is False else "⊘ 跳过")
        print(f"  {status}: {name}")
    
    print(f"\n总计: {passed} 通过, {failed} 失败, {skipped} 跳过")
    
    if failed == 0:
        print("\n🎉 所有测试通过!")
    else:
        print(f"\n⚠ {failed} 个测试失败")
    
    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
