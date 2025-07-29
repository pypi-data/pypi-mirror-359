"""Unit tests for validation utilities."""

import pytest
from jenkins_mcp_server.utils.validation import validate_jenkins_url, validate_job_name
from jenkins_mcp_server.exceptions import JenkinsValidationError


@pytest.mark.unit
class TestValidation:
    """Test cases for validation functions."""
    
    def test_validate_jenkins_url_valid(self):
        """Test valid Jenkins URL validation."""
        valid_urls = [
            'http://jenkins:8080',
            'https://jenkins.example.com'
        ]
        
        for url in valid_urls:
            result = validate_jenkins_url(url)
            assert result == url
    
    def test_validate_job_name_valid(self):
        """Test valid job name validation."""
        valid_names = ['test-job', 'my_job_123']
        
        for name in valid_names:
            result = validate_job_name(name)
            assert result == name
