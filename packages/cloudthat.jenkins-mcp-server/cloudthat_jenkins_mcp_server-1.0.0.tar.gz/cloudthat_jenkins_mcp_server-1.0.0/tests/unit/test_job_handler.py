"""Unit tests for JobHandler.

This module contains comprehensive tests for the JobHandler class,
ensuring proper functionality of all job-related operations.
"""

import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from jenkins_mcp_server.handlers.job_handler import JobHandler
from jenkins_mcp_server.models import JobInfo
from jenkins_mcp_server.exceptions import JenkinsValidationError, JenkinsOperationError


@pytest.mark.unit
class TestJobHandler:
    """Test cases for JobHandler."""

    @pytest.fixture
    def job_handler(self):
        """Create JobHandler instance for testing."""
        with patch.dict('os.environ', {
            'JENKINS_URL': 'http://test-jenkins:8080',
            'JENKINS_USERNAME': 'test-user',
            'JENKINS_TOKEN': 'test-token'
        }):
            return JobHandler()

    @patch('jenkins_mcp_server.handlers.base_handler.jenkins.Jenkins')
    @pytest.mark.asyncio
    async def test_list_jobs_simple(self, mock_jenkins_class, job_handler):
        """Test listing jobs without folder path."""
        # Setup mock
        mock_jenkins_client = MagicMock()
        mock_jenkins_class.return_value = mock_jenkins_client
        mock_jenkins_client.get_whoami.return_value = {'fullName': 'test-user'}
        
        # Mock the internal _fetch_jobs method
        expected_jobs = [
            JobInfo(name='job1', url='http://test-jenkins:8080/job/job1/', full_name='job1'),
            JobInfo(name='job2', url='http://test-jenkins:8080/job/job2/', full_name='job2')
        ]
        
        with patch.object(job_handler, '_fetch_jobs', return_value=expected_jobs):
            # Test
            result = await job_handler.list_jobs()
            
            # Verify
            assert len(result) == 2
            assert all(isinstance(job, JobInfo) for job in result)
            assert result[0].name == 'job1'
            assert result[1].name == 'job2'

    @patch('jenkins_mcp_server.handlers.base_handler.jenkins.Jenkins')
    @pytest.mark.asyncio
    async def test_get_job_details(self, mock_jenkins_class, job_handler):
        """Test getting job details."""
        # Setup mock
        mock_jenkins_client = MagicMock()
        mock_jenkins_class.return_value = mock_jenkins_client
        mock_jenkins_client.get_whoami.return_value = {'fullName': 'test-user'}
        
        # Mock the internal method
        expected_job = JobInfo(
            name='test-job',
            url='http://test-jenkins:8080/job/test-job/',
            full_name='test-job',
            description='Test job description'
        )
        
        with patch.object(job_handler, '_fetch_job_details', return_value=expected_job):
            # Test
            result = await job_handler.get_job_details('test-job')
            
            # Verify
            assert isinstance(result, JobInfo)
            assert result.name == 'test-job'
            assert result.description == 'Test job description'

    @patch('jenkins_mcp_server.handlers.base_handler.jenkins.Jenkins')
    @pytest.mark.asyncio
    async def test_create_job_freestyle(self, mock_jenkins_class, job_handler):
        """Test creating a freestyle job."""
        # Setup mock
        mock_jenkins_client = MagicMock()
        mock_jenkins_class.return_value = mock_jenkins_client
        mock_jenkins_client.get_whoami.return_value = {'fullName': 'test-user'}
        mock_jenkins_client.create_job.return_value = True
        
        # Mock get_job_details to return created job
        expected_job = JobInfo(
            name='new-freestyle-job',
            url='http://test-jenkins:8080/job/new-freestyle-job/',
            full_name='new-freestyle-job',
            description='New freestyle job'
        )
        
        with patch.object(job_handler, 'get_job_details', return_value=expected_job):
            # Test
            result = await job_handler.create_job(
                job_name='new-freestyle-job',
                job_type='freestyle',
                description='New freestyle job'
            )
            
            # Verify
            assert isinstance(result, JobInfo)
            assert result.name == 'new-freestyle-job'

    @pytest.mark.asyncio
    async def test_list_jobs_validation_error_handled(self, job_handler):
        """Test list jobs with invalid folder path - should be handled gracefully."""
        # Test with invalid folder path - should raise JenkinsOperationError, not ValidationError
        with pytest.raises(JenkinsOperationError):
            await job_handler.list_jobs(folder_path='invalid/path/../')

    @pytest.mark.asyncio
    async def test_get_job_details_validation_error_handled(self, job_handler):
        """Test get job details with validation error - should be handled gracefully."""
        # Test with empty job name - should raise JenkinsOperationError, not ValidationError
        with pytest.raises(JenkinsOperationError):
            await job_handler.get_job_details('')

    @pytest.mark.asyncio
    async def test_create_job_validation_error_handled(self, job_handler):
        """Test create job with validation error - should be handled gracefully."""
        # Test with empty job name - should raise JenkinsOperationError, not ValidationError
        with pytest.raises(JenkinsOperationError):
            await job_handler.create_job('')
