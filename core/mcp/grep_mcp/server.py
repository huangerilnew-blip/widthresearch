import asyncio
import json
from typing import Any, Optional, List, Dict, Annotated
from urllib.parse import urlencode, quote_plus
import aiohttp
from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from mcp.server.sse import SseServerTransport
from starlette.requests import Request
from starlette.routing import Mount, Route
from mcp.server import Server
import uvicorn
import re
from pydantic import Field

# Initialize FastMCP server for grep.app functionality
mcp = FastMCP("grep-mcp")


# Custom exception classes for grep.app operations
class GrepAPIError(Exception):
    """Generic error for grep.app API operations."""
    pass


class GrepAPITimeoutError(GrepAPIError):
    """Raised when grep.app API request times out."""
    pass


class GrepAPIRateLimitError(GrepAPIError):
    """Raised when grep.app API rate limit is exceeded."""
    pass


def _extract_text_from_html(html_snippet: str) -> str:
    """Extract clean text from HTML snippet by removing tags."""
    # Simple HTML tag removal using regex
    clean_text = re.sub(r'<[^>]+>', '', html_snippet)
    # Replace HTML entities
    clean_text = clean_text.replace('&quot;', '"').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    return clean_text.strip()


def _extract_line_numbers(html_snippet: str) -> List[int]:
    """Extract line numbers from HTML snippet."""
    line_numbers = []
    # Extract line numbers from data-line attributes
    line_matches = re.findall(r'data-line="(\d+)"', html_snippet)
    for match in line_matches:
        line_numbers.append(int(match))
    return line_numbers


def _get_language_from_extension(extension: str) -> str:
    """Map file extension to programming language for syntax highlighting."""
    extension_map = {
        'py': 'python',
        'js': 'javascript',
        'ts': 'typescript',
        'jsx': 'javascript',
        'tsx': 'typescript',
        'java': 'java',
        'c': 'c',
        'cpp': 'cpp',
        'cc': 'cpp',
        'cxx': 'cpp',
        'h': 'c',
        'hpp': 'cpp',
        'cs': 'csharp',
        'php': 'php',
        'rb': 'ruby',
        'go': 'go',
        'rs': 'rust',
        'swift': 'swift',
        'kt': 'kotlin',
        'scala': 'scala',
        'sh': 'bash',
        'bash': 'bash',
        'zsh': 'bash',
        'fish': 'bash',
        'ps1': 'powershell',
        'sql': 'sql',
        'html': 'html',
        'htm': 'html',
        'xml': 'xml',
        'css': 'css',
        'scss': 'scss',
        'sass': 'sass',
        'less': 'less',
        'json': 'json',
        'yaml': 'yaml',
        'yml': 'yaml',
        'toml': 'toml',
        'ini': 'ini',
        'cfg': 'ini',
        'conf': 'ini',
        'md': 'markdown',
        'markdown': 'markdown',
        'tex': 'latex',
        'r': 'r',
        'R': 'r',
        'matlab': 'matlab',
        'm': 'matlab',
        'pl': 'perl',
        'lua': 'lua',
        'vim': 'vim',
        'dockerfile': 'dockerfile',
        'makefile': 'makefile',
        'make': 'makefile'
    }
    return extension_map.get(extension.lower(), 'text')


def _format_code_snippet(snippet: str, language: str) -> str:
    """Format code snippet with syntax highlighting markers and proper structure."""
    if not snippet.strip():
        return ""
    
    # Limit snippet length to prevent overwhelming output
    max_length = 400
    if len(snippet) > max_length:
        snippet = snippet[:max_length] + "..."
    
    # Split into lines and add line structure
    lines = snippet.split('\n')
    formatted_lines = []
    
    for i, line in enumerate(lines):
        # Remove excessive whitespace but preserve indentation
        cleaned_line = line.rstrip()
        if cleaned_line:  # Only add non-empty lines
            formatted_lines.append(cleaned_line)
        
        # Limit number of lines to prevent overwhelming output
        if len(formatted_lines) >= 8:
            if i < len(lines) - 1:
                formatted_lines.append("... (truncated)")
            break
    
    # Join lines and add language marker for syntax highlighting
    formatted_snippet = '\n'.join(formatted_lines)
    
    # Add language marker for better formatting
    if language and language != 'text':
        return f"```{language}\n{formatted_snippet}\n```"
    else:
        return formatted_snippet


@mcp.tool()
async def grep_query(
    query: str, 
    language: Optional[str] = None,
    repo: Optional[str] = None,
    path: Optional[str] = None
) -> str:
    """Search GitHub code using grep.app API.
    
    This tool enables AI assistants to search through GitHub repositories for specific
    code patterns using grep.app's powerful search index. It returns formatted results
    with repository information, file paths, and code snippets.
    
    Args:
        query: The search query string to find in GitHub repositories
        language: Optional programming language filter (e.g., "Python", "JavaScript")
        repo: Optional repository filter in format "owner/repo" (e.g., "fastapi/fastapi")
        path: Optional path filter to search within specific directories (e.g., "src/")
        
    Returns:
        JSON-formatted string with search results including repository names, file paths, 
        line numbers, and code snippets (limited to 10 results)
        
    Raises:
        GrepAPIError: If search operation fails
    """
    
    # Parameter validation
    if not query or not isinstance(query, str):
        return "❌ Error: 'query' parameter is required and must be a non-empty string"
    
    if len(query.strip()) == 0:
        return "❌ Error: 'query' cannot be empty or only whitespace"
    
    if len(query) > 1000:
        return "❌ Error: 'query' is too long (max 1000 characters). Please use a shorter query."
    
    # Validate optional parameters
    if language is not None:
        if not isinstance(language, str) or len(language.strip()) == 0:
            return "❌ Error: 'language' parameter must be a non-empty string when provided"
        if len(language) > 50:
            return "❌ Error: 'language' parameter is too long (max 50 characters)"
    
    if repo is not None:
        if not isinstance(repo, str) or len(repo.strip()) == 0:
            return "❌ Error: 'repo' parameter must be a non-empty string when provided"
        if "/" not in repo or repo.count("/") != 1:
            return "❌ Error: 'repo' parameter must be in format 'owner/repository' (e.g., 'fastapi/fastapi')"
        if len(repo) > 100:
            return "❌ Error: 'repo' parameter is too long (max 100 characters)"
    
    if path is not None:
        if not isinstance(path, str) or len(path.strip()) == 0:
            return "❌ Error: 'path' parameter must be a non-empty string when provided"
        if len(path) > 200:
            return "❌ Error: 'path' parameter is too long (max 200 characters)"
    
    # Clean query for URL
    clean_query = query.strip()
    
    # Build query parameters
    params = {"q": clean_query}
    
    # Add optional filters following grep.app API format
    if language is not None:
        params["f.lang"] = language.strip()
    
    if repo is not None:
        params["f.repo"] = repo.strip()
    
    if path is not None:
        params["f.path"] = path.strip()
    
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
            url = "https://grep.app/api/search"
            
            async with session.get(url, params=params) as response:
                if response.status == 429:
                    raise GrepAPIRateLimitError("Rate limit exceeded. Please wait before making another request.")
                
                if response.status == 404:
                    return json.dumps({
                        "query": clean_query,
                        "summary": {
                            "total_results": 0,
                            "message": "No results found for this query"
                        },
                        "results": []
                    }, indent=2)
                
                if response.status != 200:
                    raise GrepAPIError(f"API request failed with status {response.status}")
                
                data = await response.json()
                
                # Parse response and format results
                formatted_results = _format_grep_response(data, clean_query)
                return json.dumps(formatted_results, indent=2)
                
    except asyncio.TimeoutError:
        raise GrepAPITimeoutError("Request to grep.app API timed out")
    except aiohttp.ClientError as e:
        raise GrepAPIError(f"Network error while contacting grep.app API: {e}")
    except GrepAPIRateLimitError:
        return "❌ Error: Rate limit exceeded. Please wait before making another request."
    except GrepAPITimeoutError:
        return "❌ Error: Request timed out. The grep.app API may be experiencing issues."
    except GrepAPIError as e:
        return f"❌ Error: {e}"
    except Exception as e:
        return f"❌ Error: Unexpected error occurred: {e}"


def _format_grep_response(data: Dict[str, Any], query: str) -> Dict[str, Any]:
    """Format grep.app API response into a clean, readable structure."""
    
    # Extract summary information
    facets = data.get("facets", {})
    total_count = facets.get("count", 0)
    
    # Extract language statistics
    languages = []
    lang_buckets = facets.get("lang", {}).get("buckets", [])
    for bucket in lang_buckets[:5]:  # Top 5 languages
        languages.append({
            "language": bucket.get("val", "Unknown"),
            "count": bucket.get("count", 0)
        })
    
    # Extract repository statistics
    repositories = []
    repo_buckets = facets.get("repo", {}).get("buckets", [])
    for bucket in repo_buckets[:5]:  # Top 5 repositories
        repositories.append({
            "repository": bucket.get("val", "Unknown"),
            "count": bucket.get("count", 0)
        })
    
    # Extract and format search results, grouped by repository
    hits = data.get("hits", {}).get("hits", [])
    repo_groups = {}
    
    # Apply result limit (hardcoded to 10 results)
    result_limit = 10
    
    for hit in hits[:result_limit]:
        # 处理不同的数据结构 - 字段可能是字符串或字典
        repo_data = hit.get("repo", "Unknown")
        repo = repo_data.get("raw", "Unknown") if isinstance(repo_data, dict) else repo_data
        
        path_data = hit.get("path", "Unknown")
        path = path_data.get("raw", "Unknown") if isinstance(path_data, dict) else path_data
        
        branch_data = hit.get("branch", "main")
        branch = branch_data.get("raw", "main") if isinstance(branch_data, dict) else branch_data
        
        total_matches_data = hit.get("total_matches", "0")
        total_matches = total_matches_data.get("raw", "0") if isinstance(total_matches_data, dict) else str(total_matches_data)
        
        # Extract content snippet
        content = hit.get("content", {})
        html_snippet = content.get("snippet", "")
        
        # Clean the HTML and extract useful information
        clean_snippet = _extract_text_from_html(html_snippet)
        line_numbers = _extract_line_numbers(html_snippet)
        
        # Determine file extension for syntax highlighting
        file_extension = path.split('.')[-1].lower() if '.' in path else 'txt'
        language_hint = _get_language_from_extension(file_extension)
        
        # Format code snippet with syntax highlighting markers
        formatted_snippet = _format_code_snippet(clean_snippet, language_hint)
        
        result = {
            "file_path": path,
            "branch": branch,
            "total_matches": int(total_matches) if total_matches.isdigit() else 0,
            "line_numbers": line_numbers,
            "language": language_hint,
            "code_snippet": formatted_snippet
        }
        
        # Group by repository
        if repo not in repo_groups:
            repo_groups[repo] = []
        repo_groups[repo].append(result)
    
    # Convert grouped results to list format
    results_by_repo = []
    for repo_name, repo_results in repo_groups.items():
        results_by_repo.append({
            "repository": repo_name,
            "matches_count": sum(r["total_matches"] for r in repo_results),
            "files": repo_results
        })
    
    # Sort repositories by number of matches (descending)
    results_by_repo.sort(key=lambda x: x["matches_count"], reverse=True)
    
    # Build final response
    formatted_response = {
        "query": query,
        "summary": {
            "total_results": total_count,
            "results_shown": sum(len(group["files"]) for group in results_by_repo),
            "repositories_found": len(results_by_repo),
            "top_languages": languages,
            "top_repositories": repositories
        },
        "results_by_repository": results_by_repo
    }
    
    return formatted_response


def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """Create a Starlette application that can serve the provided MCP server with SSE.
    
    Sets up a Starlette web application with routes for SSE (Server-Sent Events)
    communication with the MCP server.
    
    Args:
        mcp_server: The MCP server instance to connect
        debug: Whether to enable debug mode for the Starlette app
        
    Returns:
        A configured Starlette application
    """
    # Create an SSE transport with a base path for messages
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> None:
        """Handler for SSE connections.
        
        Establishes an SSE connection and connects it to the MCP server.
        
        Args:
            request: The incoming HTTP request
        """
        # Connect the SSE transport to the request
        async with sse.connect_sse(
                request.scope,
                request.receive,
                request._send,  # noqa: SLF001
        ) as (read_stream, write_stream):
            # Run the MCP server with the SSE streams
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options(),
            )

    # Create and return the Starlette application with routes
    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),  # Endpoint for SSE connections
            Mount("/messages/", app=sse.handle_post_message),  # Endpoint for posting messages
        ],
    )


def main():
    """Main entry point for the Grep MCP server.
    
    This function serves as the primary entry point when the server is launched
    via uvx or direct Python execution. It handles argument parsing and server startup.
    """
    # Get the underlying MCP server from the FastMCP instance
    mcp_server = mcp._mcp_server  # noqa: WPS437
    
    import argparse
    
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description='Run Grep MCP server with configurable transport')
    # Allow choosing between stdio and SSE transport modes
    parser.add_argument('--transport', choices=['stdio', 'sse'], default='stdio', 
                        help='Transport mode (stdio or sse)')
    # Host configuration for SSE mode
    parser.add_argument('--host', default='0.0.0.0', 
                        help='Host to bind to (for SSE mode)')
    # Port configuration for SSE mode
    parser.add_argument('--port', type=int, default=8080, 
                        help='Port to listen on (for SSE mode)')
    args = parser.parse_args()

    # Launch the server with the selected transport mode
    if args.transport == 'stdio':
        # Run with stdio transport (default)
        # This mode communicates through standard input/output
        mcp.run(transport='stdio')
    else:
        # Run with SSE transport (web-based)
        # Create a Starlette app to serve the MCP server
        starlette_app = create_starlette_app(mcp_server, debug=True)
        # Start the web server with the configured host and port
        uvicorn.run(starlette_app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()