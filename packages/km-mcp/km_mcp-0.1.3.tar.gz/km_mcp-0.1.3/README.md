# KM-MCP: Meituan Knowledge Management MCP Server

[![PyPI version](https://badge.fury.io/py/km-mcp.svg)](https://badge.fury.io/py/km-mcp)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Model Context Protocol (MCP) server for accessing Meituan internal knowledge management system (学城/WIKI). This package provides seamless integration with AI assistants like Claude, enabling them to search and retrieve content from Meituan's internal documentation.

## 🚀 Features

- **🔍 Document Search**: Search through Meituan's internal knowledge base
- **📖 Content Retrieval**: Fetch and convert documents to Markdown format
- **🖼️ Image Support**: Access images and DrawIO diagrams from documents
- **🔒 Security Aware**: Respects document security levels and access controls
- **⚡ Fast & Reliable**: Built with modern Python tools for optimal performance

## 📦 Installation

### From PyPI (Recommended)

```bash
pip install km-mcp
```

### From Source

```bash
git clone https://github.com/meituan/km-mcp.git
cd km-mcp
pip install -e .
```

## 🔧 Quick Start

### 1. Start the MCP Server

```bash
km-mcp-server
```

### 2. Configure with Claude Desktop

Add the following configuration to your Claude Desktop config file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "km-mcp": {
      "command": "km-mcp-server",
      "env": {
        "MAX_SECRET_LEVEL_THRESHOLD": "2",
        "FILTER_SECRET_LEVEL_IN_SEARCH_RESULT": "1",
        "KM_SEARCH_SPACE_TYPE": "0"
      }
    }
  }
}
```

### 3. Use with Other MCP Clients

```python
from km_mcp import mcp

# The MCP server instance is available for integration
# with other MCP clients and frameworks
```

## 🛠️ Available Tools

### 1. search_km
Search for documents in Meituan's knowledge base.

**Parameters:**
- `keyword` (str): Search keyword
- `limit` (int, optional): Maximum number of results (default: 30)
- `offset` (int, optional): Pagination offset (default: 0)

### 2. get_km_doc
Retrieve a specific document by its ID.

**Parameters:**
- `doc_id` (str): Document ID
- `doc_title` (str, optional): Document title for display
- `doc_link` (str, optional): Document link for reference
- `convert_to_md` (bool, optional): Convert to Markdown (default: True)

### 3. read_file_content
Read image or DrawIO diagram content from documents.

**Parameters:**
- `url` (str): File URL from KM system
- `compression_level` (int, optional): Compression level 0-3 (default: 3)

## ⚙️ Configuration

Configure the server behavior using environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `MAX_SECRET_LEVEL_THRESHOLD` | Maximum security level for documents (0-3) | `2` |
| `FILTER_SECRET_LEVEL_IN_SEARCH_RESULT` | Filter search results by security level | `1` |
| `KM_SEARCH_SPACE_TYPE` | Search space (0=public, 1=private) | `0` |

## 🔐 Authentication

The server uses browser cookies for authentication. Make sure you're logged into the Meituan KM system in your browser before using the server.

## 📋 Requirements

- Python 3.10 or higher
- Access to Meituan internal network
- Valid Meituan SSO authentication

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/meituan/km-mcp/issues)
- **Documentation**: [Project Wiki](https://github.com/meituan/km-mcp/wiki)
- **Internal Support**: Contact the Meituan Engineering Team

## 🔗 Related Projects

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Claude Desktop](https://claude.ai/desktop)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)

---

**Note**: This package is designed for use within Meituan's internal network and requires proper authentication to access internal documents.
