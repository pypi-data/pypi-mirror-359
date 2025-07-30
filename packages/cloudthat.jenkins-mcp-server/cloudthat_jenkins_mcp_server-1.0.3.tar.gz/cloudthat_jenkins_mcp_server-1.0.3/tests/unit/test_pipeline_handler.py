"""Unit tests for PipelineHandler."""

import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from jenkins_mcp_server.handlers.pipeline_handler import PipelineHandler
from jenkins_mcp_server.models import PipelineDefinition, PipelineDeploymentResult
from jenkins_mcp_server.exceptions import JenkinsValidationError


@pytest.mark.unit
class TestPipelineHandler:
    """Test cases for PipelineHandler."""

    @pytest.fixture
    def pipeline_handler(self):
        """Create PipelineHandler instance for testing."""
        with patch.dict('os.environ', {
            'JENKINS_URL': 'http://test-jenkins:8080',
            'JENKINS_USERNAME': 'test-user',
            'JENKINS_TOKEN': 'test-token'
        }):
            return PipelineHandler()

    @patch('jenkins_mcp_server.handlers.base_handler.jenkins.Jenkins')
    @pytest.mark.asyncio
    async def test_create_pipeline(self, mock_jenkins_class, pipeline_handler):
        """Test creating a pipeline."""
        # Setup mock
        mock_jenkins_client = MagicMock()
        mock_jenkins_class.return_value = mock_jenkins_client
        mock_jenkins_client.get_whoami.return_value = {'fullName': 'test-user'}
        mock_jenkins_client.create_job.return_value = True
        
        pipeline_script = """
        pipeline {
            agent any
            stages {
                stage('Build') {
                    steps {
                        echo 'Building...'
                    }
                }
            }
        }
        """
        
        # Test
        result = await pipeline_handler.create_pipeline(
            name='test-pipeline',
            script=pipeline_script,
            description='Test pipeline'
        )
        
        # Verify
        assert isinstance(result, PipelineDeploymentResult)
        assert result.name == 'test-pipeline'  # Using property accessor
        assert result.pipeline_name == 'test-pipeline'  # Actual field name
        assert result.created is True  # Correct field name
        mock_jenkins_client.create_job.assert_called_once()

    @patch('jenkins_mcp_server.handlers.base_handler.jenkins.Jenkins')
    @pytest.mark.asyncio
    async def test_update_pipeline(self, mock_jenkins_class, pipeline_handler):
        """Test updating a pipeline."""
        # Setup mock
        mock_jenkins_client = MagicMock()
        mock_jenkins_class.return_value = mock_jenkins_client
        mock_jenkins_client.get_whoami.return_value = {'fullName': 'test-user'}
        mock_jenkins_client.reconfig_job.return_value = True
        
        pipeline_script = """
        pipeline {
            agent any
            stages {
                stage('Build') {
                    steps {
                        echo 'Building updated...'
                    }
                }
            }
        }
        """
        
        # Test
        result = await pipeline_handler.update_pipeline(
            name='test-pipeline',
            script=pipeline_script
        )
        
        # Verify
        assert isinstance(result, PipelineDeploymentResult)
        assert result.name == 'test-pipeline'  # Using property accessor
        assert result.pipeline_name == 'test-pipeline'  # Actual field name
        assert result.created is False  # Update operation, not create
        mock_jenkins_client.reconfig_job.assert_called_once()

    @patch('jenkins_mcp_server.handlers.base_handler.jenkins.Jenkins')
    @pytest.mark.asyncio
    async def test_create_pipeline_validation_error(self, mock_jenkins_class, pipeline_handler):
        """Test create pipeline with validation error."""
        # Test with empty name - handler returns error result, doesn't raise exception
        result = await pipeline_handler.create_pipeline('', 'script')
        assert isinstance(result, PipelineDeploymentResult)
        assert result.created is False
        assert 'Job name cannot be empty' in result.message

        # Test with empty script - handler returns error result, doesn't raise exception
        result = await pipeline_handler.create_pipeline('test-pipeline', '')
        assert isinstance(result, PipelineDeploymentResult)
        assert result.created is False

    @patch('jenkins_mcp_server.handlers.base_handler.jenkins.Jenkins')
    @pytest.mark.asyncio
    async def test_update_pipeline_validation_error(self, mock_jenkins_class, pipeline_handler):
        """Test update pipeline with validation error."""
        # Test with empty name - handler returns error result, doesn't raise exception
        result = await pipeline_handler.update_pipeline('', 'script')
        assert isinstance(result, PipelineDeploymentResult)
        assert result.created is False
        assert 'Job name cannot be empty' in result.message

    @patch('jenkins_mcp_server.handlers.base_handler.jenkins.Jenkins')
    @pytest.mark.asyncio
    async def test_get_pipeline_definition(self, mock_jenkins_class, pipeline_handler):
        """Test getting pipeline definition."""
        # Setup mock
        mock_jenkins_client = MagicMock()
        mock_jenkins_class.return_value = mock_jenkins_client
        mock_jenkins_client.get_whoami.return_value = {'fullName': 'test-user'}
        mock_jenkins_client.get_job_info.return_value = {
            'description': 'Test pipeline description',  # Return string instead of mock
            'property': [],
            'fullName': 'test-pipeline'
        }
        mock_jenkins_client.get_job_config.return_value = """
        <flow-definition>
            <script>
                pipeline {
                    agent any
                    stages {
                        stage('Build') {
                            steps {
                                echo 'Building...'
                            }
                        }
                    }
                }
            </script>
        </flow-definition>
        """
        
        # Test
        result = await pipeline_handler.get_pipeline_definition('test-pipeline')
        
        # Verify
        assert isinstance(result, PipelineDefinition)
        assert result.name == 'test-pipeline'
        assert 'pipeline {' in result.script
        mock_jenkins_client.get_job_config.assert_called_once_with('test-pipeline')
