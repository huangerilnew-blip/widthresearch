import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient


load_dotenv(Path(__file__).parent / ".env")


async def run_required_tools() -> None:
    tavily_key = os.getenv("TAVILY_API_KEY")
    exa_key = os.getenv("EXA_API_KEY")

    if not tavily_key or not exa_key:
        raise ValueError("Missing TAVILY_API_KEY or EXA_API_KEY in environment")

    client = MultiServerMCPClient({
        "paper-search": {
            "command": "python",
            "args": ["-m", "core.mcp.search_tool_mcp.mcp_server"],
            "cwd": str(Path(__file__).parent),
            "env": {
                "TAVILY_API_KEY": tavily_key,
                "EXA_API_KEY": exa_key
            },
            "transport": "stdio"
        }
    })

    tools = await client.get_tools()
    tool_map = {tool.name: tool for tool in tools}

    required_tools = ["wikipedia_search", "exa_context_search", "tavily_search"]
    query = "langchain short-term memory best practices"

    for tool_name in required_tools:
        tool = tool_map.get(tool_name)
        if not tool:
            print(f"{tool_name}: tool not found")
            continue

        print(f"\n== {tool_name} ==")
        try:
            result = await tool.ainvoke({"query": query})
            print(f"result type: {type(result)}")
            if isinstance(result, str):
                print(f"result preview: {result[:300]}")
            elif isinstance(result, list):
                print(f"result list size: {len(result)}")
                if result:
                    first = result[0]
                    print(f"first item type: {type(first)}")
                    if isinstance(first, dict):
                        print(f"first keys: {list(first.keys())}")
            elif isinstance(result, dict):
                print(f"result keys: {list(result.keys())}")
        except Exception as exc:
            print(f"{tool_name} failed: {exc}")


if __name__ == "__main__":
    asyncio.run(run_required_tools())
