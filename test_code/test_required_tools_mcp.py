import asyncio
import json
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

    def _extract_payload(value: object) -> dict | None:
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return None
        if isinstance(value, list) and value:
            first = value[0]
            text = getattr(first, "text", None)
            if text:
                return _extract_payload(text)
        if isinstance(value, dict):
            return value
        return None

    required_tools = ["wikipedia_search", "exa_context_search", "tavily_search"]
    download_tools = ["wikipedia_download", "exa_context_download", "tavily_download"]
    query = "langchain short-term memory best practices"
    search_payloads: dict[str, dict] = {}

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
            payload = _extract_payload(result)
            if payload:
                search_payloads[tool_name] = payload
        except Exception as exc:
            print(f"{tool_name} failed: {exc}")

    for tool_name in download_tools:
        tool = tool_map.get(tool_name)
        if not tool:
            print(f"{tool_name}: tool not found")
            continue
        search_tool = tool_name.replace("_download", "_search")
        payload = search_payloads.get(search_tool, {})
        papers = payload.get("papers", []) if isinstance(payload, dict) else []
        if not papers:
            print(f"{tool_name}: no papers available")
            continue
        print(f"\n== {tool_name} ==")
        try:
            result = await tool.ainvoke({"papers": papers})
            print(f"result type: {type(result)}")
            if isinstance(result, list) and result:
                first = result[0]
                print(f"first item type: {type(first)}")
            payload = _extract_payload(result)
            if payload:
                print(f"payload keys: {list(payload.keys())}")
        except Exception as exc:
            print(f"{tool_name} failed: {exc}")


if __name__ == "__main__":
    asyncio.run(run_required_tools())
