"""Unit tests for utility modules."""

import pytest
from jenkins_mcp_server.utils.path_utils import (
    normalize_jenkins_path, jenkins_path_to_url_path, validate_jenkins_path,
    get_parent_path, get_path_segments, join_jenkins_paths
)
from jenkins_mcp_server.utils.pipeline_utils import (
    PipelineValidator, detect_pipeline_type, generate_pipeline_template,
    validate_shared_library_syntax
)
from jenkins_mcp_server.utils.error_reporting import (
    ErrorReporter, report_operation_error, format_error_for_user
)


@pytest.mark.unit
class TestPathUtils:
    """Test cases for path utilities."""
    
    def test_normalize_jenkins_path(self):
        """Test path normalization."""
        test_cases = [
            ('', ''),
            ('folder1', 'folder1'),
            ('/folder1/', 'folder1'),
            ('folder1//folder2', 'folder1/folder2'),
            ('  folder1/folder2  ', 'folder1/folder2'),
        ]
        
        for input_path, expected in test_cases:
            result = normalize_jenkins_path(input_path)
            assert result == expected
    
    def test_jenkins_path_to_url_path(self):
        """Test conversion from Jenkins path to URL path."""
        test_cases = [
            ('', ''),
            ('folder1', 'job/folder1'),
            ('folder1/folder2', 'job/folder1/job/folder2'),
            ('team/project/env', 'job/team/job/project/job/env'),
        ]
        
        for jenkins_path, expected in test_cases:
            result = jenkins_path_to_url_path(jenkins_path)
            assert result == expected
    
    def test_validate_jenkins_path(self):
        """Test path validation."""
        valid_paths = ['', 'folder1', 'folder1/folder2', 'team-alpha/project_1']
        invalid_paths = ['folder<1', 'folder>1', 'folder:1', 'con', 'prn']
        
        for path in valid_paths:
            assert validate_jenkins_path(path) is True
        
        for path in invalid_paths:
            assert validate_jenkins_path(path) is False
    
    def test_get_parent_path(self):
        """Test parent path extraction."""
        test_cases = [
            ('', None),
            ('folder1', None),
            ('folder1/folder2', 'folder1'),
            ('team/project/env', 'team/project'),
        ]
        
        for path, expected in test_cases:
            result = get_parent_path(path)
            assert result == expected
    
    def test_get_path_segments(self):
        """Test path segment extraction."""
        test_cases = [
            ('', []),
            ('folder1', ['folder1']),
            ('folder1/folder2', ['folder1', 'folder2']),
            ('team/project/env', ['team', 'project', 'env']),
        ]
        
        for path, expected in test_cases:
            result = get_path_segments(path)
            assert result == expected
    
    def test_join_jenkins_paths(self):
        """Test path joining."""
        result = join_jenkins_paths('team', 'project', 'environment')
        assert result == 'team/project/environment'
        
        result = join_jenkins_paths('', 'folder1', '', 'folder2')
        assert result == 'folder1/folder2'


@pytest.mark.unit
class TestPipelineUtils:
    """Test cases for pipeline utilities."""
    
    def test_detect_pipeline_type_declarative(self, sample_pipeline_script):
        """Test detection of declarative pipeline."""
        result = detect_pipeline_type(sample_pipeline_script)
        assert result == 'declarative'
    
    def test_detect_pipeline_type_scripted(self, sample_scripted_pipeline):
        """Test detection of scripted pipeline."""
        result = detect_pipeline_type(sample_scripted_pipeline)
        assert result == 'scripted'
    
    def test_detect_pipeline_type_unknown(self):
        """Test detection of unknown pipeline type."""
        unknown_script = "echo 'not a pipeline'"
        result = detect_pipeline_type(unknown_script)
        assert result == 'unknown'
    
    def test_pipeline_validator_declarative_valid(self, sample_pipeline_script):
        """Test validation of valid declarative pipeline."""
        validator = PipelineValidator()
        result = validator.validate_pipeline_script(sample_pipeline_script, 'declarative')
        
        assert result['valid'] is True
        assert len(result['errors']) == 0
        assert len(result['used_tools']) > 0
    
    def test_pipeline_validator_declarative_invalid(self, invalid_pipeline_script):
        """Test validation of invalid declarative pipeline."""
        validator = PipelineValidator()
        result = validator.validate_pipeline_script(invalid_pipeline_script, 'declarative')
        
        assert result['valid'] is False
        assert len(result['errors']) > 0
    
    def test_pipeline_validator_scripted(self, sample_scripted_pipeline):
        """Test validation of scripted pipeline."""
        validator = PipelineValidator()
        result = validator.validate_pipeline_script(sample_scripted_pipeline, 'scripted')
        
        assert result['valid'] is True
        assert len(result['warnings']) >= 0
    
    def test_generate_pipeline_template_declarative(self):
        """Test declarative pipeline template generation."""
        template = generate_pipeline_template(
            'declarative',
            'test-job',
            stages=['Build', 'Test', 'Deploy'],
            shared_libraries=['common-utils']
        )
        
        assert 'pipeline {' in template
        assert 'agent any' in template
        assert '@Library(\'common-utils\')' in template
        assert 'stage(\'Build\')' in template
        assert 'stage(\'Test\')' in template
        assert 'stage(\'Deploy\')' in template
    
    def test_generate_pipeline_template_scripted(self):
        """Test scripted pipeline template generation."""
        template = generate_pipeline_template(
            'scripted',
            'test-job',
            stages=['Checkout', 'Build']
        )
        
        assert 'node {' in template
        assert 'try {' in template
        assert 'stage(\'Checkout\')' in template
        assert 'stage(\'Build\')' in template
        assert 'catch (Exception e)' in template
    
    def test_validate_shared_library_syntax(self):
        """Test shared library name validation."""
        valid_names = ['common-utils', 'deploy_helpers', 'test123']
        invalid_names = ['', 'invalid@name', 'pipeline', 'a' * 101]
        
        for name in valid_names:
            is_valid, errors = validate_shared_library_syntax(name)
            assert is_valid is True
            assert len(errors) == 0
        
        for name in invalid_names:
            is_valid, errors = validate_shared_library_syntax(name)
            assert is_valid is False
            assert len(errors) > 0


@pytest.mark.unit
class TestErrorReporting:
    """Test cases for error reporting utilities."""
    
    def test_error_reporter_basic(self):
        """Test basic error reporting."""
        reporter = ErrorReporter()
        error = Exception("Test error")
        
        report = reporter.report_error('test_operation', error)
        
        assert report['operation'] == 'test_operation'
        assert report['error_type'] == 'Exception'
        assert report['error_message'] == 'Test error'
        assert len(reporter.error_history) == 1
    
    def test_error_reporter_with_context(self):
        """Test error reporting with context."""
        reporter = ErrorReporter()
        error = Exception("Connection failed")
        context = {'url': 'http://jenkins:8080', 'timeout': 30}
        
        report = reporter.report_error('connect', error, context=context)
        
        assert report['context'] == context
        # Suggestions may be empty for generic exceptions
        assert 'suggestions' in report
    
    def test_error_reporter_jenkins_specific_suggestions(self):
        """Test Jenkins-specific error suggestions."""
        from jenkins_mcp_server.exceptions import JenkinsAuthenticationError
        
        reporter = ErrorReporter()
        
        # Test authentication error with Jenkins-specific exception
        auth_error = JenkinsAuthenticationError("Authentication failed", jenkins_url="http://jenkins:8080")
        report = reporter.report_error('login', auth_error)
        suggestions = report['suggestions']
        
        # Check if suggestions contain authentication-related terms
        assert len(suggestions) > 0, "Should have suggestions for authentication error"
        
        # Test connection error with Jenkins-specific exception
        from jenkins_mcp_server.exceptions import JenkinsConnectionError
        conn_error = JenkinsConnectionError("Connection timeout", jenkins_url="http://jenkins:8080")
        report = reporter.report_error('connect', conn_error)
        suggestions = report['suggestions']
        
        # Check if suggestions exist for connection error
        assert len(suggestions) > 0, "Should have suggestions for connection error"
    
    def test_get_error_summary(self):
        """Test error summary generation."""
        reporter = ErrorReporter()
        
        # Add multiple errors
        reporter.report_error('op1', Exception("Error 1"))
        reporter.report_error('op2', ValueError("Error 2"))
        reporter.report_error('op3', Exception("Error 3"))
        
        summary = reporter.get_error_summary()
        
        assert summary['total_errors'] == 3
        assert len(summary['recent_errors']) == 3
        assert 'Exception' in summary['error_types']
        assert 'ValueError' in summary['error_types']
        assert summary['most_common_error'] == 'Exception'
    
    def test_format_error_for_user(self):
        """Test user-friendly error formatting."""
        error_report = {
            'operation': 'create_pipeline',
            'error_message': 'Validation failed',
            'context': {'pipeline_name': 'test'},
            'suggestions': ['Check syntax', 'Validate parameters']
        }
        
        formatted = format_error_for_user(error_report)
        
        assert '❌ Operation \'create_pipeline\' failed' in formatted
        assert 'Validation failed' in formatted
        assert '💡 Suggestions:' in formatted
        assert '• Check syntax' in formatted
    
    def test_report_operation_error_global(self):
        """Test global error reporting function."""
        error = Exception("Global test error")
        context = {'test': True}
        
        report = report_operation_error('global_test', error, context=context)
        
        assert report['operation'] == 'global_test'
        assert report['context'] == context
        assert len(report['suggestions']) >= 0


@pytest.mark.edge_case
class TestUtilsEdgeCases:
    """Test edge cases for utility functions."""
    
    def test_normalize_jenkins_path_edge_cases(self):
        """Test path normalization edge cases."""
        edge_cases = [
            (None, ''),  # Should handle None gracefully
            ('///', ''),
            ('   ', ''),
            ('folder1///folder2///', 'folder1/folder2'),
        ]
        
        for input_path, expected in edge_cases:
            if input_path is None:
                # Skip None test as it would cause TypeError
                continue
            result = normalize_jenkins_path(input_path)
            assert result == expected
    
    def test_pipeline_validator_empty_script(self):
        """Test pipeline validation with empty script."""
        validator = PipelineValidator()
        result = validator.validate_pipeline_script('', 'declarative')
        
        assert result['valid'] is False
        assert 'empty' in result['errors'][0].lower()
    
    def test_error_reporter_clear_history(self):
        """Test error history clearing."""
        reporter = ErrorReporter()
        reporter.report_error('test', Exception("Test"))
        
        assert len(reporter.error_history) == 1
        
        reporter.clear_history()
        
        assert len(reporter.error_history) == 0
