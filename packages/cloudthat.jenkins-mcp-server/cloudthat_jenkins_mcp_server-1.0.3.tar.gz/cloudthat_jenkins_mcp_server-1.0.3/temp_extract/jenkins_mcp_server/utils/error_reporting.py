"""Enhanced error handling and reporting utilities."""

import traceback
from typing import Dict, List, Optional, Any
from loguru import logger
from jenkins_mcp_server.exceptions import JenkinsError


class ErrorReporter:
    """Enhanced error reporting for Jenkins operations."""
    
    def __init__(self):
        """Initialize error reporter."""
        self.error_history: List[Dict[str, Any]] = []
    
    def report_error(
        self,
        operation: str,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        suggestions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Report an error with enhanced context and suggestions.
        
        Args:
            operation: Name of the operation that failed
            error: The exception that occurred
            context: Additional context information
            suggestions: List of suggested solutions
            
        Returns:
            Error report dictionary
        """
        error_report = {
            'operation': operation,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context or {},
            'suggestions': suggestions or [],
            'traceback': traceback.format_exc() if logger.level('DEBUG').no <= logger._core.min_level else None
        }
        
        # Add specific suggestions based on error type
        if isinstance(error, JenkinsError):
            error_report['suggestions'].extend(self._get_jenkins_error_suggestions(error))
        
        # Store in history
        self.error_history.append(error_report)
        
        # Log the error
        logger.error(f"Operation '{operation}' failed: {error}")
        if context:
            logger.debug(f"Error context: {context}")
        
        return error_report
    
    def _get_jenkins_error_suggestions(self, error: JenkinsError) -> List[str]:
        """Get suggestions for Jenkins-specific errors.
        
        Args:
            error: Jenkins error
            
        Returns:
            List of suggestions
        """
        suggestions = []
        error_msg = str(error).lower()
        
        if 'authentication' in error_msg or 'unauthorized' in error_msg:
            suggestions.extend([
                "Check that your Jenkins username and API token are correct",
                "Verify that the API token has not expired",
                "Ensure the user has sufficient permissions for this operation",
                "Try regenerating the API token in Jenkins user settings"
            ])
        
        elif 'connection' in error_msg or 'timeout' in error_msg:
            suggestions.extend([
                "Check that Jenkins server is running and accessible",
                "Verify the Jenkins URL is correct",
                "Check network connectivity to Jenkins server",
                "Consider increasing the timeout value"
            ])
        
        elif 'not found' in error_msg or '404' in error_msg:
            suggestions.extend([
                "Verify that the job/folder exists in Jenkins",
                "Check the job/folder path for typos",
                "Ensure you have permission to access the resource",
                "Try listing available jobs to verify the correct name"
            ])
        
        elif 'csrf' in error_msg or 'crumb' in error_msg:
            suggestions.extend([
                "CSRF protection is enabled - this should be handled automatically",
                "Check if Jenkins CSRF settings have changed",
                "Try the operation again as CSRF tokens may have expired"
            ])
        
        elif 'permission' in error_msg or 'forbidden' in error_msg:
            suggestions.extend([
                "Check that your user has the required permissions",
                "Verify job-level permissions if accessing specific jobs",
                "Contact Jenkins administrator to review user permissions",
                "Check if the operation requires additional privileges"
            ])
        
        elif 'syntax' in error_msg or 'invalid' in error_msg:
            suggestions.extend([
                "Check the pipeline script syntax",
                "Validate parameter names and values",
                "Ensure all required fields are provided",
                "Review Jenkins documentation for correct format"
            ])
        
        return suggestions
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of recent errors.
        
        Returns:
            Error summary dictionary
        """
        if not self.error_history:
            return {'total_errors': 0, 'recent_errors': []}
        
        # Get last 10 errors
        recent_errors = self.error_history[-10:]
        
        # Count error types
        error_types = {}
        for error in self.error_history:
            error_type = error['error_type']
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        return {
            'total_errors': len(self.error_history),
            'recent_errors': recent_errors,
            'error_types': error_types,
            'most_common_error': max(error_types.items(), key=lambda x: x[1])[0] if error_types else None
        }
    
    def clear_history(self):
        """Clear error history."""
        self.error_history.clear()


# Global error reporter instance
error_reporter = ErrorReporter()


def report_operation_error(
    operation: str,
    error: Exception,
    context: Optional[Dict[str, Any]] = None,
    suggestions: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Report an operation error using the global error reporter.
    
    Args:
        operation: Name of the operation that failed
        error: The exception that occurred
        context: Additional context information
        suggestions: List of suggested solutions
        
    Returns:
        Error report dictionary
    """
    return error_reporter.report_error(operation, error, context, suggestions)


def format_error_for_user(error_report: Dict[str, Any]) -> str:
    """Format error report for user-friendly display.
    
    Args:
        error_report: Error report dictionary
        
    Returns:
        Formatted error message
    """
    lines = [
        f"❌ Operation '{error_report['operation']}' failed",
        f"Error: {error_report['error_message']}"
    ]
    
    if error_report.get('context'):
        lines.append(f"Context: {error_report['context']}")
    
    if error_report.get('suggestions'):
        lines.append("\n💡 Suggestions:")
        for suggestion in error_report['suggestions']:
            lines.append(f"  • {suggestion}")
    
    return '\n'.join(lines)


def get_troubleshooting_info(operation: str, error: Exception) -> Dict[str, Any]:
    """Get comprehensive troubleshooting information for an error.
    
    Args:
        operation: Name of the operation that failed
        error: The exception that occurred
        
    Returns:
        Troubleshooting information dictionary
    """
    troubleshooting = {
        'operation': operation,
        'error_type': type(error).__name__,
        'error_message': str(error),
        'common_causes': [],
        'diagnostic_steps': [],
        'related_documentation': []
    }
    
    error_msg = str(error).lower()
    
    # Add common causes and diagnostic steps based on error type
    if 'authentication' in error_msg:
        troubleshooting['common_causes'] = [
            "Invalid or expired API token",
            "Incorrect username",
            "User account disabled or locked"
        ]
        troubleshooting['diagnostic_steps'] = [
            "Test credentials with: curl -u username:token http://jenkins-url/api/json",
            "Check user account status in Jenkins user management",
            "Regenerate API token and try again"
        ]
    
    elif 'connection' in error_msg:
        troubleshooting['common_causes'] = [
            "Jenkins server is down or unreachable",
            "Network connectivity issues",
            "Firewall blocking connection",
            "Incorrect Jenkins URL"
        ]
        troubleshooting['diagnostic_steps'] = [
            "Test connectivity with: curl -I http://jenkins-url",
            "Check Jenkins server logs for errors",
            "Verify network configuration and firewall rules"
        ]
    
    elif 'not found' in error_msg:
        troubleshooting['common_causes'] = [
            "Job or folder does not exist",
            "Incorrect job/folder name or path",
            "Insufficient permissions to access resource"
        ]
        troubleshooting['diagnostic_steps'] = [
            "List available jobs to verify names",
            "Check job/folder path for typos",
            "Verify user permissions for the resource"
        ]
    
    return troubleshooting
