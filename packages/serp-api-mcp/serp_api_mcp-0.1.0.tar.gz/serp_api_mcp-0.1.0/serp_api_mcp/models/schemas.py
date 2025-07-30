"""
Pydantic models for SERP API MCP Server.

Defines the data structures for search requests and responses.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    """Individual search result from SERPAPI."""
    
    title: str = Field(..., description="Title of the search result")
    link: str = Field(..., description="URL of the search result")
    snippet: str = Field(..., description="Text snippet from the search result")
    date: Optional[str] = Field(None, description="Publication date if available")
    position: int = Field(..., description="Position in search results")
    source: Optional[str] = Field(None, description="Source website name")
    
    class Config:
        extra = "allow"  # Allow additional fields from SERPAPI


class SearchResponse(BaseModel):
    """Response model for search operations."""
    
    success: bool = Field(..., description="Whether the search was successful")
    query: str = Field(..., description="The search query used")
    total_results: Optional[int] = Field(None, description="Total number of results found")
    results: List[SearchResult] = Field(default_factory=list, description="List of search results")
    search_parameters: Dict[str, Any] = Field(..., description="Parameters used for the search")
    error: Optional[str] = Field(None, description="Error message if search failed")
    search_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata from SERPAPI")
    
    class Config:
        extra = "forbid"


class SearchParameters(BaseModel):
    """Parameters for search operations."""
    
    query: str = Field(..., description="Search query")
    num_results: int = Field(10, description="Number of results to return", ge=1, le=100)
    country: str = Field("us", description="Country code for search localization")
    language: str = Field("en", description="Language code for search results")
    location: Optional[str] = Field(None, description="Specific location for localized search")
    safe_search: bool = Field(True, description="Enable safe search filtering")
    start: int = Field(0, description="Starting position for pagination", ge=0)
    
    class Config:
        extra = "forbid"