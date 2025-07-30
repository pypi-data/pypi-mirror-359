"""
Configuration module for SERP API MCP Server.

Loads environment variables and provides configuration settings.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
SERPAPI_KEY = os.getenv("SERPAPI_API_KEY") or os.getenv("SERPAPI_KEY")
if not SERPAPI_KEY:
    raise ValueError("SERPAPI_API_KEY or SERPAPI_KEY environment variable is required")

# Server Configuration
DEFAULT_PORT = int(os.getenv("MCP_PORT", "3000"))
DEFAULT_CONNECTION_TYPE = os.getenv("MCP_CONNECTION_TYPE", "stdio")

# SERPAPI Configuration
SERPAPI_BASE_URL = "https://serpapi.com/search"
DEFAULT_SEARCH_ENGINE = "google"
DEFAULT_NUM_RESULTS = 10
DEFAULT_COUNTRY = "us"
DEFAULT_LANGUAGE = "en"

# Request Configuration
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))