# Web Scraper Module

## Overview

The Web Scraper module provides tools for web scraping, crawling, and content extraction using the Firecrawl service. These tools are designed to be used by AI agents in the Agents Manager system.

## Features

- **Web Page Scraping**: Scrape individual web pages and extract content in multiple formats (markdown, HTML, links)
- **Search**: Search the web and optionally scrape the top results
- **Site Crawling**: Crawl entire websites with configurable depth and limits
- **Structured Data Extraction**: Extract structured data using prompts or schemas

## Installation

The required dependencies are managed through Poetry. The necessary dependencies should already be included in the project's `pyproject.toml`:

```toml
[dependencies]
firecrawl-py = "^1.0.0"
requests = "^2.31.0"
python-dotenv = "^1.0.0"
```

## Environment Setup

To use these tools, you need to set your Firecrawl API key in the environment:

```bash
export FIRECRAWL_API_KEY="your-api-key-here"
```

Or add it to your `.env` file:

```env
FIRECRAWL_API_KEY=your-api-key-here
```

## Module Structure

```
src/modules/tools/web_scraper/
├── __init__.py
├── client.py
├── firecrawl_tools.py
└── types.py
```

- `types.py`: Data classes for Firecrawl options
- `client.py`: Firecrawl client implementation
- `firecrawl_tools.py`: Agent-oriented tool functions
- `__init__.py`: Package initialization

## Usage

### Importing the Tools

```python
from src.modules.tools.web_scraper import (
    tool_scrape,
    tool_search,
    tool_crawl_site,
    tool_extract
)
```

### Scrape a Single Page

```python
result = tool_scrape("https://example.com")
print(result["markdown"])
```

### Search the Web

```python
# Simple search
result = tool_search("AI news 2024")

# Search with content scraping
result = tool_search("AI news 2024", limit=5, scrape_markdown=True)
```

### Crawl a Website

```python
result = tool_crawl_site("https://docs.example.com", max_pages=100)
```

### Extract Structured Data

```python
# Using a prompt
result = tool_extract(
    inputs=["https://example.com/blog/*"],
    prompt="Extract all blog post titles and their URLs"
)

# Using a schema
schema = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "links": {"type": "array", "items": {"type": "string"}}
    }
}
result = tool_extract(
    inputs=["https://example.com/*"],
    schema=schema
)
```

## API Reference

### tool_scrape(url: str) -> Dict[str, Any]

Scrape a single URL and return markdown, links, and HTML content.

**Parameters:**
- `url` (str): The URL to scrape

**Returns:**
- `Dict[str, Any]`: Scraped data including markdown, links, and HTML

### tool_search(query: str, limit: int = 5, scrape_markdown: bool = False) -> Dict[str, Any]

Search the web and optionally scrape the top results.

**Parameters:**
- `query` (str): Search query
- `limit` (int): Number of results to return (default: 5)
- `scrape_markdown` (bool): Whether to scrape markdown content for each result (default: False)

**Returns:**
- `Dict[str, Any]`: Search results with optional scraped content

### tool_crawl_site(url: str, max_pages: int = 200) -> Dict[str, Any]

Crawl an entire website up to a maximum number of pages.

**Parameters:**
- `url` (str): The website URL to crawl
- `max_pages` (int): Maximum number of pages to crawl (default: 200)

**Returns:**
- `Dict[str, Any]`: Crawled data from all pages

### tool_extract(inputs: List[str], prompt: str | None = None, schema: dict | None = None) -> Dict[str, Any]

Extract structured data using a prompt or schema over a list of URLs or a wildcard domain.

**Parameters:**
- `inputs` (List[str]): List of URLs or wildcard patterns to extract from
- `prompt` (str, optional): Prompt to guide extraction
- `schema` (dict, optional): Schema to structure the extracted data

**Returns:**
- `Dict[str, Any]`: Extracted structured data

## Testing

To run the tests, make sure you have set the `FIRECRAWL_API_KEY` environment variable and run:

```bash
pytest src/tests/web_scraper/
```

Note: Tests will be skipped if the `FIRECRAWL_API_KEY` environment variable is not set.

## Best Practices

1. **Rate Limiting**: Be mindful of the rate limits imposed by the Firecrawl service
2. **Cost Management**: Choose appropriate formats and limits to manage costs
3. **Error Handling**: Always handle potential exceptions when using these tools
4. **Caching**: Take advantage of Firecrawl's caching mechanisms when appropriate
5. **Privacy**: Respect website terms of service and privacy policies

## Troubleshooting

### Common Issues

1. **API Key Not Found**: Ensure the `FIRECRAWL_API_KEY` environment variable is set
2. **Timeout Errors**: For large crawls, consider increasing timeout values
3. **Rate Limiting**: If you encounter rate limiting, implement exponential backoff

### Error Handling

All tools may raise exceptions in case of errors. Handle these appropriately in your agent implementations:

```python
try:
    result = tool_scrape("https://example.com")
except Exception as e:
    print(f"Scraping failed: {e}")
```