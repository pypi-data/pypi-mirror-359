"""
SERP API MCP Server

This module sets up an MCP-compliant server for Google search using SERPAPI.
It provides structured search capabilities with well-defined parameters.
"""

import argparse
from typing import Optional
try:
    # Try the import that mcp dev expects
    from mcp.server.fastmcp import FastMCP
except ImportError:
    # Fall back to the standalone fastmcp package
    from fastmcp import FastMCP
from serp_api_mcp.utils.logging import logger
from serp_api_mcp.config import DEFAULT_PORT, DEFAULT_CONNECTION_TYPE
from serp_api_mcp.services.search_service import search_google as search_google_service

# Create global FastMCP instance for mcp dev compatibility
mcp = FastMCP("SERP API MCP Server")


@mcp.tool()
async def google_search_tool(
    query: str,
    num_results: Optional[int] = 10,
    country: Optional[str] = "us",
    language: Optional[str] = "en",
    location: Optional[str] = None,
    safe_search: Optional[bool] = True,
    start: Optional[int] = 0
) -> dict:
    """
    Search Google using structured parameters via SERPAPI.
    
    This tool allows you to perform Google searches with specific, structured criteria.
    The LLM should extract relevant information from user queries and map them
    to these parameters.
    
    Args:
        query: The search query (e.g., "latest AI trends", "Python tutorials")
        num_results: Number of results to return (1-100, default: 10)
        country: Country code for localization (e.g., "us", "uk", "ca", default: "us")
        language: Language code for results (e.g., "en", "es", "fr", default: "en")
        location: Specific location for localized search (e.g., "New York", "London")
        safe_search: Enable safe search filtering (default: True)
        start: Starting position for pagination (default: 0)
        
    Returns:
        Dictionary containing search results with the following structure:
        - success: Boolean indicating if the search was successful
        - query: The search query used
        - total_results: Total number of results found (if available)
        - results: List of search results with:
            - title: Result title
            - link: URL of the result
            - snippet: Text snippet
            - date: Publication date (if available)
            - position: Position in search results
            - source: Source website name
        - search_parameters: Echo of the search parameters used
        - search_metadata: Additional metadata from SERPAPI
        - error: Error message if the search failed
    """
    logger.debug(f"Searching Google for: '{query}' with {num_results} results")
    
    try:
        result = await search_google_service(
            query=query,
            num_results=num_results,
            country=country,
            language=language,
            location=location,
            safe_search=safe_search,
            start=start
        )
        
        response = {
                "success": result.success,
                "query": result.query,
                "total_results": result.total_results,
                "results": [r.model_dump() for r in result.results],
                "search_parameters": result.search_parameters,
        }
        
        if result.search_metadata:
            response["search_metadata"] = result.search_metadata
            
        if result.error:
            response["error"] = result.error
            
        logger.info(f"Search completed: {len(result.results)} results for '{query}'")
        return response
        
    except Exception as e:
        logger.error(f"Error in google_search_tool: {e}")
        return {
                "success": False,
                "query": query,
                "total_results": 0,
                "results": [],
                "search_parameters": {
                    "query": query,
                    "num_results": num_results,
                    "country": country,
                    "language": language,
                    "location": location,
                    "safe_search": safe_search,
                    "start": start
                },
                "error": str(e)
        }


@mcp.tool()
def server_status() -> dict:
    """
    Check if the SERP API MCP server is running.
    
    Returns:
        Dictionary with server status information
    """
    return {
        "status": "online",
        "message": "SERP API MCP server is active and ready to search Google using structured parameters.",
        "version": "0.1.0",
        "api_configured": bool(mcp)  # Simple check
    }


logger.debug("All MCP tools registered.")


def main():
    """
    Main entry point for running the MCP server.
    """
    parser = argparse.ArgumentParser(description="SERP API MCP Server - Structured Google Search")
    parser.add_argument("--connection_type", type=str, default=DEFAULT_CONNECTION_TYPE,
                        choices=["http", "stdio"], help="Connection type (http or stdio)")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT,
                        help=f"Port to run the server on (default: {DEFAULT_PORT})")
    args = parser.parse_args()
    
    server_type = "sse" if args.connection_type == "http" else "stdio"
    
    logger.info(f"🚀 Starting {mcp.name} with {args.connection_type} connection")
    if args.connection_type == "http":
        logger.info(f"Server running on port {args.port}")
    
    mcp.run(server_type)


if __name__ == "__main__":
    main()