"""
Logging configuration for SERP API MCP Server.

Sets up logging with rich formatting for better debugging.
"""

import logging
from rich.logging import RichHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[
        RichHandler(
            rich_tracebacks=True,
            show_time=True,
            show_path=False
        )
    ]
)

# Create logger instance
logger = logging.getLogger("serp_api_mcp")

# Set log level based on environment
import os
if os.getenv("DEBUG", "").lower() in ("true", "1", "yes"):
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)