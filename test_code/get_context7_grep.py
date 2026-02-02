"""
Context7 and Grep MCP tool output sampler.

This script calls Context7 (resolve-library-id, query-docs) and Grep (grep_query)
tools, then prints the raw JSON outputs to help confirm exact response formats.
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from langchain_core.tools import BaseTool

_ = load_dotenv()
sys.path.insert(0, str(Path(__file__).parent))

from core.mcp.context7_grep import Context7GrepMCPClient


def _try_parse_json(value: Any) -> Any:
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    return value


def _print_output(title: str, value: Any) -> None:
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)
    parsed = _try_parse_json(value)
    if isinstance(parsed, (dict, list)):
        print(json.dumps(parsed, ensure_ascii=False, indent=2))
    else:
        print(parsed)


def _extract_library_id(value: Any) -> Optional[str]:
    parsed = _try_parse_json(value)
    if isinstance(parsed, dict):
        for key in ("library_id", "libraryId", "id"):
            if key in parsed:
                return str(parsed[key])
    if isinstance(parsed, list):
        for item in parsed:
            if isinstance(item, dict):
                for key in ("library_id", "libraryId", "id"):
                    if key in item:
                        return str(item[key])
    return None


def _build_resolve_args(tool: BaseTool) -> Dict[str, str]:
    args: Dict[str, str] = {}
    schema = getattr(tool, "args", {})
    if isinstance(schema, dict):
        if "libraryName" in schema:
            args["libraryName"] = "langchain"
            args["query"] = "langchain"
        else:
            if "library_name" in schema:
                args["library_name"] = "langchain"
            elif "library" in schema:
                args["library"] = "langchain"
            elif "query" in schema:
                args["query"] = "langchain"
            elif "name" in schema:
                args["name"] = "langchain"
    if not args:
        args = {"libraryName": "langchain", "query": "langchain"}
    return args


def _build_query_docs_args(tool: BaseTool, library_id: str) -> Dict[str, str]:
    args: Dict[str, str] = {}
    schema = getattr(tool, "args", {})
    if isinstance(schema, dict):
        if "library_id" in schema:
            args["library_id"] = str(library_id)
        elif "libraryId" in schema:
            args["libraryId"] = str(library_id)
        if "query" in schema:
            args["query"] = "quickstart"
        elif "question" in schema:
            args["question"] = "quickstart"
    if not args:
        args = {"library_id": str(library_id), "query": "quickstart"}
    return args


def _build_grep_args(tool: BaseTool) -> Dict[str, str]:
    args: Dict[str, str] = {}
    schema = getattr(tool, "args", {})
    if isinstance(schema, dict):
        if "query" in schema:
            args["query"] = "async def"
        elif "pattern" in schema:
            args["pattern"] = "async def"
    if not args:
        args = {"query": "async def"}
    return args


async def main():
    has_context7_key = bool(os.getenv("CONTEXT7_API_KEY"))
    client = Context7GrepMCPClient(context7_need=has_context7_key, grep_need=True)

    try:
        tools = await client.get_tools()
        tool_map = {tool.name: tool for tool in tools}

        grep_tool = tool_map.get("grep_query")
        resolve_tool = tool_map.get("resolve-library-id")
        query_tool = tool_map.get("query-docs")

        if grep_tool:
            _print_output("Grep tool args", getattr(grep_tool, "args", {}))
            grep_result = await grep_tool.ainvoke(_build_grep_args(grep_tool))
            _print_output("Grep tool output", grep_result)
        else:
            print("\nNo grep_query tool found.")

        if not has_context7_key:
            print("\nCONTEXT7_API_KEY not set; skipping Context7 tool calls.")
            return

        if resolve_tool:
            _print_output("Context7 resolve-library-id args", getattr(resolve_tool, "args", {}))
            resolve_result = await resolve_tool.ainvoke(_build_resolve_args(resolve_tool))
            _print_output("Context7 resolve-library-id output", resolve_result)
        else:
            print("\nNo resolve-library-id tool found.")
            resolve_result = None

        library_id = _extract_library_id(resolve_result) if resolve_result is not None else None
        if query_tool and library_id:
            _print_output("Context7 query-docs args", getattr(query_tool, "args", {}))
            query_result = await query_tool.ainvoke(_build_query_docs_args(query_tool, library_id))
            _print_output("Context7 query-docs output", query_result)
        elif query_tool:
            print("\nquery-docs tool available but library_id was not resolved.")
        else:
            print("\nNo query-docs tool found.")
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
