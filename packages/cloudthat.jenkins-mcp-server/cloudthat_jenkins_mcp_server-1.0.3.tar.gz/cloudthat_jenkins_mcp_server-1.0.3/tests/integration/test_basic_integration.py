"""Basic integration tests for Jenkins MCP Server."""

import pytest
from unittest.mock import patch
from jenkins_mcp_server.server import create_server


@pytest.mark.integration
class TestBasicIntegration:
    """Basic integration tests."""
    
    @pytest.mark.asyncio
    async def test_server_creation(self, mock_env_vars):
        """Test server creation."""
        with patch('jenkins_mcp_server.handlers.base_handler.BaseHandler.jenkins_client'):
            server = create_server()
            assert server is not None
            assert server.name == 'jenkins-mcp-server'
    
    @pytest.mark.asyncio
    async def test_tools_available(self, mock_env_vars):
        """Test that all expected tools are available."""
        with patch('jenkins_mcp_server.handlers.base_handler.BaseHandler.jenkins_client'):
            server = create_server()
            
            # FastMCP list_tools() returns a list of tools
            expected_tools = [
                'list_jenkins_jobs',
                'get_jenkins_server_info',
                'create_jenkins_pipeline'
            ]
            
            # Check if tools are registered in the server's tools
            tools = await server.list_tools()
            registered_tools = [tool.name for tool in tools]
            
            for tool in expected_tools:
                assert tool in registered_tools, f"Tool {tool} not found in registered tools: {registered_tools}"
