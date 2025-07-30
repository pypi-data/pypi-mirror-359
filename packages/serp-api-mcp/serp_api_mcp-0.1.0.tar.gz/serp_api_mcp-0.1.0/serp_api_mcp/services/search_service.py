"""
Search service for SERP API integration.

Handles communication with SERPAPI and processes search results.
"""

import httpx
from typing import Optional
from serp_api_mcp.config import (
    SERPAPI_KEY,
    SERPAPI_BASE_URL,
    DEFAULT_SEARCH_ENGINE,
    REQUEST_TIMEOUT
)
from serp_api_mcp.models.schemas import SearchResponse, SearchResult, SearchParameters
from serp_api_mcp.utils.logging import logger


async def search_google(
    query: str,
    num_results: int = 10,
    country: str = "us",
    language: str = "en",
    location: Optional[str] = None,
    safe_search: bool = True,
    start: int = 0
) -> SearchResponse:
    """
    Perform a Google search using SERPAPI.
    
    Args:
        query: The search query
        num_results: Number of results to return (max 100)
        country: Country code for localization
        language: Language code for results
        location: Specific location for localized search
        safe_search: Enable safe search filtering
        start: Starting position for pagination
        
    Returns:
        SearchResponse with results or error information
    """
    
    # Build search parameters
    search_params = SearchParameters(
        query=query,
        num_results=num_results,
        country=country,
        language=language,
        location=location,
        safe_search=safe_search,
        start=start
    )
    
    # Prepare SERPAPI request parameters
    params = {
        "api_key": SERPAPI_KEY,
        "engine": DEFAULT_SEARCH_ENGINE,
        "q": query,
        "num": num_results,
        "gl": country,
        "hl": language,
        "start": start,
        "safe": "active" if safe_search else "off",
        "output": "json"
    }
    
    # Add optional location parameter
    if location:
        params["location"] = location
    
    logger.debug(f"Searching Google for: '{query}' with params: {params}")
    
    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            response = await client.get(SERPAPI_BASE_URL, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract organic results
            organic_results = data.get("organic_results", [])
            search_results = []
            
            for idx, result in enumerate(organic_results):
                search_result = SearchResult(
                    title=result.get("title", ""),
                    link=result.get("link", ""),
                    snippet=result.get("snippet", ""),
                    date=result.get("date"),
                    position=idx + 1 + start,
                    source=result.get("source")
                )
                search_results.append(search_result)
            
            # Get search metadata
            search_info = data.get("search_information", {})
            total_results = search_info.get("total_results")
            
            logger.info(f"Search completed: found {len(search_results)} results for '{query}'")
            
            return SearchResponse(
                success=True,
                query=query,
                total_results=total_results,
                results=search_results,
                search_parameters=search_params.model_dump(),
                search_metadata={
                    "search_time": search_info.get("time_taken_displayed"),
                    "total_results_formatted": search_info.get("total_results_formatted"),
                    "query_displayed": search_info.get("query_displayed")
                }
            )
            
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error during search: {e}")
        error_msg = f"SERPAPI request failed with status {e.response.status_code}"
        
        # Check for specific error cases
        if e.response.status_code == 401:
            error_msg = "Invalid SERPAPI key. Please check your API credentials."
        elif e.response.status_code == 429:
            error_msg = "Rate limit exceeded. Please try again later."
            
        return SearchResponse(
            success=False,
            query=query,
            results=[],
            search_parameters=search_params.model_dump(),
            error=error_msg
        )
        
    except httpx.TimeoutException:
        logger.error(f"Timeout during search for query: {query}")
        return SearchResponse(
            success=False,
            query=query,
            results=[],
            search_parameters=search_params.model_dump(),
            error="Search request timed out. Please try again."
        )
        
    except Exception as e:
        logger.error(f"Unexpected error during search: {e}")
        return SearchResponse(
            success=False,
            query=query,
            results=[],
            search_parameters=search_params.model_dump(),
            error=f"An unexpected error occurred: {str(e)}"
        )