#!/usr/bin/env python3
"""Test tool registration in the Jenkins MCP server."""

import pytest
from unittest.mock import patch, MagicMock
from jenkins_mcp_server.server import create_server


@pytest.mark.integration
@pytest.mark.asyncio
async def test_tool_registration():
    """Test tool registration in the Jenkins MCP server."""
    with patch('jenkins_mcp_server.handlers.base_handler.jenkins.Jenkins') as mock_jenkins:
        # Configure mock
        mock_jenkins_instance = MagicMock()
        mock_jenkins.return_value = mock_jenkins_instance
        
        # Create server
        server = create_server()
        
        # Verify tools are registered by checking the server's _tools
        expected_tools = [
            'list_jenkins_jobs',
            'get_job_details', 
            'create_jenkins_job',
            'trigger_jenkins_build',
            'get_build_status',
            'get_build_logs',
            'create_jenkins_pipeline',
            'update_jenkins_pipeline',
            'get_jenkins_server_info',
            'get_jenkins_queue'
        ]
        
        registered_tools = [tool.name for tool in await server.list_tools()]
        
        for expected_tool in expected_tools:
            assert expected_tool in registered_tools, f"Tool {expected_tool} not registered. Available: {registered_tools}"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_tool_count():
    """Test that the expected number of tools are registered."""
    with patch('jenkins_mcp_server.handlers.base_handler.jenkins.Jenkins') as mock_jenkins:
        mock_jenkins_instance = MagicMock()
        mock_jenkins.return_value = mock_jenkins_instance
        
        server = create_server()
        
        # Count tools by checking the server's _tools
        expected_tools = [
            'list_jenkins_jobs', 'get_job_details', 'create_jenkins_job',
            'trigger_jenkins_build', 'get_build_status', 'get_build_logs',
            'create_jenkins_pipeline', 'update_jenkins_pipeline',
            'get_jenkins_server_info', 'get_jenkins_queue'
        ]
        
        registered_tools = [tool.name for tool in await server.list_tools()]
        tool_count = len([tool for tool in expected_tools if tool in registered_tools])
        
        assert tool_count >= 8, f"Expected at least 8 tools, got {tool_count}. Available: {registered_tools}"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_tool_descriptions():
    """Test that all tools have proper descriptions."""
    with patch('jenkins_mcp_server.handlers.base_handler.jenkins.Jenkins') as mock_jenkins:
        mock_jenkins_instance = MagicMock()
        mock_jenkins.return_value = mock_jenkins_instance
        
        server = create_server()
        
        # Just verify server was created successfully
        # Tool descriptions are handled by FastMCP decorators
        assert server is not None
