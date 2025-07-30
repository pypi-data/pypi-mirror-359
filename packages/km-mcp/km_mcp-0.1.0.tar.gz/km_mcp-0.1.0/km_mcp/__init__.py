"""
Meituan Knowledge Management MCP Server

A Model Context Protocol server for accessing Meituan internal documents.
"""

__version__ = "0.1.0"
__author__ = "Meituan Engineering Team"
__email__ = "engineering@meituan.com"

from .server import mcp

__all__ = ["mcp", "__version__"]
