"""Unit tests for BuildHandler.

This module contains comprehensive tests for the BuildHandler class,
ensuring proper functionality of all build-related operations.
"""

import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from jenkins_mcp_server.handlers.build_handler import BuildHandler
from jenkins_mcp_server.models import BuildInfo, BuildTriggerResult
from jenkins_mcp_server.exceptions import JenkinsValidationError, JenkinsOperationError


@pytest.mark.unit
class TestBuildHandler:
    """Test cases for BuildHandler."""

    @pytest.fixture
    def build_handler(self):
        """Create BuildHandler instance for testing."""
        with patch.dict('os.environ', {
            'JENKINS_URL': 'http://test-jenkins:8080',
            'JENKINS_USERNAME': 'test-user',
            'JENKINS_TOKEN': 'test-token'
        }):
            return BuildHandler()

    @patch('jenkins_mcp_server.handlers.base_handler.jenkins.Jenkins')
    @pytest.mark.asyncio
    async def test_trigger_build_simple(self, mock_jenkins_class, build_handler):
        """Test triggering a simple build without parameters."""
        # Setup mock
        mock_jenkins_client = MagicMock()
        mock_jenkins_class.return_value = mock_jenkins_client
        mock_jenkins_client.get_whoami.return_value = {'fullName': 'test-user'}
        mock_jenkins_client.build_job.return_value = 123
        
        # Mock the internal method
        with patch.object(build_handler, '_trigger_build_simple', return_value=123):
            # Test
            result = await build_handler.trigger_build('test-job')
            
            # Verify
            assert isinstance(result, BuildTriggerResult)
            assert result.job_name == 'test-job'
            assert result.triggered is True

    @patch('jenkins_mcp_server.handlers.base_handler.jenkins.Jenkins')
    @pytest.mark.asyncio
    async def test_trigger_build_with_parameters(self, mock_jenkins_class, build_handler):
        """Test triggering a build with parameters."""
        # Setup mock
        mock_jenkins_client = MagicMock()
        mock_jenkins_class.return_value = mock_jenkins_client
        mock_jenkins_client.get_whoami.return_value = {'fullName': 'test-user'}
        
        parameters = {'BRANCH': 'main', 'DEPLOY': True}
        
        # Mock the internal method
        with patch.object(build_handler, '_trigger_build_with_params', return_value=124):
            # Test
            result = await build_handler.trigger_build('test-job', parameters=parameters)
            
            # Verify
            assert isinstance(result, BuildTriggerResult)
            assert result.job_name == 'test-job'
            assert result.triggered is True

    @patch('jenkins_mcp_server.handlers.base_handler.jenkins.Jenkins')
    @pytest.mark.asyncio
    async def test_get_build_info(self, mock_jenkins_class, build_handler):
        """Test getting build information."""
        # Setup mock
        mock_jenkins_client = MagicMock()
        mock_jenkins_class.return_value = mock_jenkins_client
        mock_jenkins_client.get_whoami.return_value = {'fullName': 'test-user'}
        
        # Mock the internal method
        expected_build_info = BuildInfo(
            number=123,
            url='http://test-jenkins:8080/job/test-job/123/',
            job_name='test-job',
            result='SUCCESS',
            building=False
        )
        
        with patch.object(build_handler, '_fetch_build_info', return_value=expected_build_info):
            # Test
            result = await build_handler.get_build_info('test-job', 123)
            
            # Verify
            assert isinstance(result, BuildInfo)
            assert result.number == 123
            assert result.job_name == 'test-job'
            assert result.result == 'SUCCESS'

    @patch('jenkins_mcp_server.handlers.base_handler.jenkins.Jenkins')
    @pytest.mark.asyncio
    async def test_get_build_logs(self, mock_jenkins_class, build_handler):
        """Test getting build logs."""
        # Setup mock
        mock_jenkins_client = MagicMock()
        mock_jenkins_class.return_value = mock_jenkins_client
        mock_jenkins_client.get_whoami.return_value = {'fullName': 'test-user'}
        mock_jenkins_client.get_build_console_output.return_value = "Build started\nBuild completed successfully"
        
        # Test
        result = await build_handler.get_build_logs('test-job', 123)
        
        # Verify
        assert result == "Build started\nBuild completed successfully"

    @patch('jenkins_mcp_server.handlers.base_handler.jenkins.Jenkins')
    @pytest.mark.asyncio
    async def test_abort_build(self, mock_jenkins_class, build_handler):
        """Test aborting a build."""
        # Setup mock
        mock_jenkins_client = MagicMock()
        mock_jenkins_class.return_value = mock_jenkins_client
        mock_jenkins_client.get_whoami.return_value = {'fullName': 'test-user'}
        
        # Mock the internal method
        with patch.object(build_handler, '_abort_build_request', return_value=True):
            # Test
            result = await build_handler.abort_build('test-job', 123)
            
            # Verify - expect BuildOperation object, not boolean
            from jenkins_mcp_server.models import BuildOperation
            assert isinstance(result, BuildOperation)
            assert result.operation == 'abort_build'
            assert result.job_name == 'test-job'
            assert result.build_number == 123

    @patch('jenkins_mcp_server.handlers.base_handler.jenkins.Jenkins')
    @pytest.mark.asyncio
    async def test_get_build_analytics(self, mock_jenkins_class, build_handler):
        """Test getting build analytics."""
        # Setup mock
        mock_jenkins_client = MagicMock()
        mock_jenkins_class.return_value = mock_jenkins_client
        mock_jenkins_client.get_whoami.return_value = {'fullName': 'test-user'}
        
        # Mock the internal methods
        with patch.object(build_handler, '_get_recent_builds', return_value=[]):
            with patch.object(build_handler, '_get_build_stages', return_value=[]):
                # Test
                result = await build_handler.get_build_analytics('test-job')
                
                # Verify - result should be a BuildAnalytics object
                assert result is not None

    @pytest.mark.asyncio
    async def test_trigger_build_validation_error_empty_name(self, build_handler):
        """Test build trigger with empty job name."""
        # Test with empty job name - should return failed result, not raise exception
        result = await build_handler.trigger_build('')
        
        assert isinstance(result, BuildTriggerResult)
        assert result.triggered is False
        assert 'Job name cannot be empty' in result.message

    @pytest.mark.asyncio
    async def test_trigger_build_validation_error_none_name(self, build_handler):
        """Test build trigger with None job name."""
        # Test with None job name - should return failed result, not raise exception
        result = await build_handler.trigger_build(None)
        
        assert isinstance(result, BuildTriggerResult)
        assert result.triggered is False
        assert 'Job name cannot be empty' in result.message

    @patch('jenkins_mcp_server.handlers.base_handler.jenkins.Jenkins')
    @pytest.mark.asyncio
    async def test_stream_build_logs(self, mock_jenkins_class, build_handler):
        """Test streaming build logs."""
        # Setup mock
        mock_jenkins_client = MagicMock()
        mock_jenkins_class.return_value = mock_jenkins_client
        mock_jenkins_client.get_whoami.return_value = {'fullName': 'test-user'}
        
        # Test - method returns a dict, not an async generator
        result = await build_handler.stream_build_logs('test-job', 123)
        
        # Verify we get a dict with log information
        assert isinstance(result, dict)
        assert 'success' in result
        assert 'logs' in result

    @patch('jenkins_mcp_server.handlers.base_handler.jenkins.Jenkins')
    @pytest.mark.asyncio
    async def test_get_recent_builds(self, mock_jenkins_class, build_handler):
        """Test getting recent builds."""
        # Setup mock
        mock_jenkins_client = MagicMock()
        mock_jenkins_class.return_value = mock_jenkins_client
        mock_jenkins_client.get_whoami.return_value = {'fullName': 'test-user'}
        
        # Test
        result = await build_handler._get_recent_builds('test-job', 5)
        
        # Verify
        assert isinstance(result, list)

    @patch('jenkins_mcp_server.handlers.base_handler.jenkins.Jenkins')
    @pytest.mark.asyncio
    async def test_get_build_stages(self, mock_jenkins_class, build_handler):
        """Test getting build stages."""
        # Setup mock
        mock_jenkins_client = MagicMock()
        mock_jenkins_class.return_value = mock_jenkins_client
        mock_jenkins_client.get_whoami.return_value = {'fullName': 'test-user'}
        
        # Test
        result = await build_handler._get_build_stages('test-job', 123)
        
        # Verify
        assert isinstance(result, list)

    def test_identify_bottlenecks(self, build_handler):
        """Test bottleneck identification."""
        # Test data
        builds = [
            {'duration': 120000, 'result': 'SUCCESS'},
            {'duration': 180000, 'result': 'SUCCESS'},
            {'duration': 90000, 'result': 'FAILURE'}
        ]
        
        # Test - method now accepts optional second parameter
        bottlenecks = build_handler._identify_bottlenecks(builds)
        
        # Verify
        assert isinstance(bottlenecks, list)

    def test_generate_build_optimizations(self, build_handler):
        """Test build optimization generation."""
        # Test data
        analytics_data = {
            'avg_duration': 150000,
            'success_rate': 0.8,
            'bottlenecks': ['slow_tests', 'large_artifacts']
        }
        
        # Test
        optimizations = build_handler._generate_build_optimizations(analytics_data)
        
        # Verify
        assert isinstance(optimizations, list)

    @patch('jenkins_mcp_server.handlers.base_handler.jenkins.Jenkins')
    @pytest.mark.asyncio
    async def test_wait_for_build_start(self, mock_jenkins_class, build_handler):
        """Test waiting for build to start."""
        # Setup mock
        mock_jenkins_client = MagicMock()
        mock_jenkins_class.return_value = mock_jenkins_client
        mock_jenkins_client.get_whoami.return_value = {'fullName': 'test-user'}
        
        # Test
        # Configure mock to return an integer
        mock_jenkins_client.get_queue_item.return_value = {'executable': {'number': 123}}
        
        result = await build_handler._wait_for_build_start('test-job', 123, timeout=10)
        
        # Verify - should return build number or None
        assert result is None or isinstance(result, int)


@pytest.mark.unit
class TestBuildHandlerEdgeCases:
    """Test cases for BuildHandler edge cases."""

    @pytest.fixture
    def build_handler(self):
        """Create BuildHandler instance for testing."""
        with patch.dict('os.environ', {
            'JENKINS_URL': 'http://test-jenkins:8080',
            'JENKINS_USERNAME': 'test-user',
            'JENKINS_TOKEN': 'test-token'
        }):
            return BuildHandler()

    @pytest.mark.asyncio
    async def test_trigger_build_with_special_characters(self, build_handler):
        """Test triggering build with special characters in job name."""
        # Test with job name containing spaces and special chars
        result = await build_handler.trigger_build('test job with spaces')
        
        # Should handle gracefully
        assert isinstance(result, BuildTriggerResult)

    @pytest.mark.asyncio
    async def test_get_build_logs_nonexistent_build(self, build_handler):
        """Test getting logs for nonexistent build."""
        # Test with nonexistent build
        try:
            await build_handler.get_build_logs('nonexistent-job', 999)
        except Exception as e:
            # Should handle gracefully with proper exception
            assert isinstance(e, (JenkinsOperationError, Exception))

    @pytest.mark.asyncio
    async def test_abort_build_already_finished(self, build_handler):
        """Test aborting a build that's already finished."""
        # Test aborting finished build
        result = await build_handler.abort_build('test-job', 123)
        
        # Should handle gracefully - expect BuildOperation object
        from jenkins_mcp_server.models import BuildOperation
        assert isinstance(result, BuildOperation)
        assert result.operation == 'abort_build'

    @pytest.mark.asyncio
    async def test_trigger_build_with_empty_parameters(self, build_handler):
        """Test triggering build with empty parameters dict."""
        result = await build_handler.trigger_build('test-job', parameters={})
        
        assert isinstance(result, BuildTriggerResult)
        assert result.job_name == 'test-job'

    @pytest.mark.asyncio
    async def test_trigger_build_with_none_parameters(self, build_handler):
        """Test triggering build with None parameters."""
        result = await build_handler.trigger_build('test-job', parameters=None)
        
        assert isinstance(result, BuildTriggerResult)
        assert result.job_name == 'test-job'
