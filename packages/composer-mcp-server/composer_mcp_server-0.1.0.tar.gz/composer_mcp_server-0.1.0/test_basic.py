"""Basic tests for composer-mcp-server package."""

import pytest


def test_import_composer_mcp_server():
    """Test that the package can be imported."""
    import composer_mcp_server
    assert composer_mcp_server is not None


def test_server_module_exists():
    """Test that the server module exists."""
    from composer_mcp_server import server
    assert server is not None


def test_mcp_available():
    """Test that the MCP server is available."""
    from composer_mcp_server.server import mcp
    assert mcp is not None


def test_package_version():
    """Test that the package has a version."""
    import composer_mcp_server
    # Check if version is available (it should be defined in __init__.py or __version__.py)
    assert hasattr(composer_mcp_server, '__version__') or hasattr(composer_mcp_server, 'version') 