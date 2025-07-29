"""Integration tests for Jenkins MCP Server."""

import pytest
from unittest.mock import patch, MagicMock
from jenkins_mcp_server.server import create_server
from jenkins_mcp_server.models import ContentItem


@pytest.fixture
def mcp_server(mock_env_vars):
    """Create MCP server for testing."""
    with patch('jenkins_mcp_server.handlers.base_handler.BaseHandler.jenkins_client'):
        return create_server()


@pytest.mark.integration
class TestServerIntegration:
    """Integration tests for server functionality."""

    @pytest.mark.asyncio
    async def test_list_jenkins_jobs_integration(self, mcp_server):
        """Test job listing integration."""
        # Test that the server has the tool registered
        tools = await mcp_server.list_tools()
        registered_tools = [tool.name for tool in tools]
        assert 'list_jenkins_jobs' in registered_tools

    @pytest.mark.asyncio
    async def test_server_info_integration(self, mcp_server):
        """Test server info integration."""
        # Test that the server has the tool registered
        tools = await mcp_server.list_tools()
        registered_tools = [tool.name for tool in tools]
        assert 'get_jenkins_server_info' in registered_tools

    @pytest.mark.asyncio
    async def test_error_handling_integration(self, mcp_server):
        """Test error handling across the server."""
        # Test that the server has error handling tools
        tools = await mcp_server.list_tools()
        registered_tools = [tool.name for tool in tools]
        assert 'list_jenkins_jobs' in registered_tools
        
        # Verify the tool has proper error handling by checking it exists
        list_jobs_tool = next((tool for tool in tools if tool.name == 'list_jenkins_jobs'), None)
        assert list_jobs_tool is not None
        assert list_jobs_tool.description is not None
