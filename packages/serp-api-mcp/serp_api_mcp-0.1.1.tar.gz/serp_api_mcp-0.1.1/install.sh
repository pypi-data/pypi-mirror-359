#!/bin/bash
# Install script for SERP API MCP Server

echo "Installing SERP API MCP Server..."

# Install in editable mode
pip install -e .

echo "Installation complete!"
echo ""
echo "You can now use 'serp-api-mcp' command from anywhere."
echo ""
echo "For Claude Desktop, use this configuration:"
echo '{'
echo '  "mcpServers": {'
echo '    "serp-api": {'
echo '      "command": "serp-api-mcp",'
echo '      "env": {'
echo '        "SERPAPI_API_KEY": "your_api_key_here"'
echo '      }'
echo '    }'
echo '  }'
echo '}'