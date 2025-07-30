
## Serp API MCP Implementation

### Overview
This MCP server integrates with SERPAPI API to provide structured search capabilities. It follows MCP best practices by accepting well-defined parameters rather than natural language, allowing the LLM client to handle the natural language processing.


## 2. Technology Stack
- **Package Management:** Use Poetry for all Python dependency management and uv to accelerate installation and virtual environment creation.
All dependencies must be declared in pyproject.toml.
Use Poetry commands for installing, updating, and managing dependencies.
The uv tool may be used under the hood to speed up installs, but Poetry remains the canonical interface for dependency resolution and packaging.

## Sensitive Data
- Place all sensitive information in a .env file

### Architecture
**Correct MCP Pattern:**
- **LLM Client:** Processes natural language and extracts structured parameters
- **MCP Server:** Handles API integration with structured inputs

### Requirements 
 **MCP Tool: google_search_tool**  Google Search Engine Results API - expose the https://serpapi.com/search-api as a mcp tool  
   - Accepts structured parameters (not natural language)
   - Returns formatted search results with:
    - title
    - snippet
    - link
    - date

## Example Response ##
Here’s your data formatted as clean, readable Markdown, ideal for inclusion in a report, notebook, or README:

⸻

🔍 Search Query

latest AI trends July 2025 artificial intelligence breakthroughs news

⸻

📌 Topics

1. AI Investment Surge for Generative AI
	•	Summary: Gartner forecasts $644 billion in generative AI spending for 2025.
	•	Relevance Score: 0.9

⸻

2. AI in Drug Discovery Revolutionizes R&D
	•	Summary: AI-driven drug discovery transforms medicine and bioinformatics.
	•	Relevance Score: 0.8

⸻

3. Bitdeer AI Wins Innovation Award for MLOps
	•	Summary: Bitdeer recognized for its comprehensive MLOps innovation approach.
	•	Relevance Score: 0.7

⸻

📊 Metadata

Key	Value
Execution Time (s)	8.781
Agent Version	2.0
Model Used	openai:gpt-4o
Requested Results	3
Web Search Enabled	true
Search Engine	Google via SerpAPI
Search Results Analyzed	14
Note	Topics are based on real-time web search results


⸻

Let me know if you want this in a table, embedded in HTML, or converted to a downloadable file.


## Implementation Details

### google_search_tool Parameters
The tool accepts the following structured parameters:
- **query** (required): The search query string
- **num_results** (optional): Number of results to return (1-100, default: 10)
- **country** (optional): Country code for localization (e.g., "us", "uk", "ca", default: "us")
- **language** (optional): Language code for results (e.g., "en", "es", "fr", default: "en")
- **location** (optional): Specific location for localized search (e.g., "New York", "London")
- **safe_search** (optional): Enable safe search filtering (default: True)
- **start** (optional): Starting position for pagination (default: 0)

### Response Structure
```json
{
  "success": true,
  "query": "search query used",
  "total_results": 1234567,
  "results": [
    {
      "title": "Result Title",
      "link": "https://example.com",
      "snippet": "Text snippet from the result...",
      "date": "2 days ago",
      "position": 1,
      "source": "example.com"
    }
  ],
  "search_parameters": {
    "query": "search query used",
    "num_results": 10,
    "country": "us",
    "language": "en",
    "safe_search": true,
    "start": 0
  },
  "search_metadata": {
    "search_time": "0.45 seconds",
    "total_results_formatted": "About 1,230,000 results"
  }
}
```

## Setup Instructions

### 1. Prerequisites
- Python 3.10 or higher
- Poetry (install with `curl -sSL https://install.python-poetry.org | python3 -`)
- SERPAPI API key (get from https://serpapi.com)

### 2. Installation
```bash
# Clone the repository
git clone <repository-url>
cd serp-api-mcp

# Install dependencies with Poetry
poetry install

# Copy environment file and add your API key
cp .env.example .env
# Edit .env and add your SERPAPI_API_KEY
```

### 3. Configuration
Create a `.env` file with:
```env
# Required
SERPAPI_API_KEY=your_serpapi_key_here

# Optional
MCP_PORT=3000              # Port for HTTP mode (default: 3000)
MCP_CONNECTION_TYPE=stdio  # Connection type: stdio or http (default: stdio)
DEBUG=false                # Enable debug logging (default: false)
REQUEST_TIMEOUT=30         # API request timeout in seconds (default: 30)
MAX_RETRIES=3             # Maximum retry attempts (default: 3)
```

### 4. Running the Server

#### Option 1: Direct Python execution
```bash
# Run with default stdio connection
python main.py

# Run with HTTP connection on specific port
python main.py --connection_type http --port 5000
```

#### Option 2: Using Poetry
```bash
# Run with Poetry
poetry run python main.py

# Or install as package and run
poetry install
poetry run serp-api-mcp
```

#### Option 3: As installed package
```bash
# After poetry install
serp-api-mcp

# With options
serp-api-mcp --connection_type http --port 5000
```

### 5. MCP Client Configuration

For Claude Desktop or other MCP clients, add to your configuration:

**For stdio mode:**
```json
{
  "mcpServers": {
    "serp-api": {
      "command": "python",
      "args": ["/path/to/serp-api-mcp/main.py"],
      "env": {
        "SERPAPI_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

**For HTTP mode:**
```json
{
  "mcpServers": {
    "serp-api": {
      "url": "http://localhost:3000",
      "transport": "http"
    }
  }
}
```

## Project Structure 

```
├── serp_api_mcp/
│   ├── __init__.py              # Package initialization
│   ├── config.py                # Environment variables and configuration
│   ├── models/
│   │   ├── __init__.py          # Models package init
│   │   └── schemas.py           # Pydantic models for search
│   ├── services/
│   │   ├── __init__.py          # Services package init
│   │   └── search_service.py    # SERPAPI integration logic
│   ├── utils/
│   │   ├── __init__.py          # Utils package init
│   │   └── logging.py           # Rich logging configuration
│   └── server.py                # MCP server with google_search_tool
├── main.py                      # Entry point script
├── pyproject.toml               # Poetry package configuration
├── .env.example                 # Example environment variables
├── LICENSE                      # MIT License
└── README.md                    # Project documentation

