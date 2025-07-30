"""Jenkins MCP Server implementation.

This module implements the main Jenkins MCP server using FastMCP,
providing comprehensive Jenkins CI/CD integration for AI assistants.

The server provides standardized tools for Jenkins operations including:
- Job management (create, update, delete, list)
- Build operations (trigger, monitor, logs)
- Pipeline management (create, update, deploy)
- System information (server status, queue, nodes)

All operations follow MCP protocol standards and include comprehensive
error handling, caching, and retry logic for production reliability.
"""

import argparse
import os
from typing import Any, Dict, List, Optional

from loguru import logger
from mcp.server.fastmcp import FastMCP

from jenkins_mcp_server.models import ContentItem, McpResponse
from jenkins_mcp_server.utils.cache import initialize_cache_manager
from jenkins_mcp_server.utils.connection_pool import initialize_connection_pool
from jenkins_mcp_server.utils.logging_helper import setup_logging


# Server instructions for AI assistants
SERVER_INSTRUCTIONS = """
# Jenkins MCP Server

This MCP server provides comprehensive tools for managing Jenkins CI/CD pipelines and is the preferred mechanism for Jenkins automation.

## IMPORTANT: Use MCP Tools for Jenkins Operations

DO NOT use Jenkins CLI commands or direct API calls. Always use the MCP tools provided by this server for Jenkins operations.

## Configuration

The server requires the following environment variables:
- JENKINS_URL: Jenkins server URL (required)
- JENKINS_USERNAME: Jenkins username (required)
- JENKINS_TOKEN: Jenkins API token (required)
- JENKINS_TIMEOUT: Request timeout in seconds (optional, default: 30)

## Usage Notes

- All operations are performed using the configured Jenkins credentials
- The server includes intelligent caching to improve performance
- Connection pooling is used for efficient resource utilization
- Comprehensive error handling with detailed error messages
- Automatic retry logic for transient failures

## Common Workflows

### Managing Jobs and Builds
1. List jobs: `list_jenkins_jobs(folder_path='optional/folder/path')`
2. Get job details: `get_job_details(job_name='my-job')`
3. Create job: `create_jenkins_job(job_name='my-job', job_type='freestyle')`
4. Trigger build: `trigger_jenkins_build(job_name='my-job', parameters={'key': 'value'})`
5. Monitor build: `get_build_status(job_name='my-job', build_number=123)`
6. Get build logs: `get_build_logs(job_name='my-job', build_number=123)`
7. Manage builds: `manage_jenkins_builds(operation='abort', job_name='my-job')`

### Pipeline Management
1. Create pipeline: `create_jenkins_pipeline(name='my-pipeline', script='pipeline { ... }')`
2. Update pipeline: `update_jenkins_pipeline(name='my-pipeline', script='pipeline { ... }')`
3. Generate template: `generate_pipeline_template(pipeline_type='declarative', job_name='my-job')`
4. Validate script: `validate_pipeline_script(script='pipeline { ... }')`

### System Administration
1. Get server info: `get_jenkins_server_info(detailed=True)`
2. Monitor queue: `get_jenkins_queue()`
3. System analysis: `analyze_jenkins_system(analysis_type='comprehensive')`

## Best Practices

- Use descriptive job and pipeline names
- Include meaningful descriptions for jobs and pipelines
- Use parameters for flexible pipeline execution
- Monitor build status and logs for troubleshooting
- Organize jobs in folders for better management
- Use appropriate timeouts for long-running operations
- Leverage caching for frequently accessed data

## Error Handling

The server provides detailed error messages and automatic retry logic for:
- Connection timeouts and network issues
- Rate limiting and server overload
- Authentication and authorization problems
- Resource not found errors
- Invalid parameter validation

## Security

- All credentials are handled securely
- API tokens are preferred over passwords
- SSL/TLS verification is enforced by default
- Sensitive data is masked in logs
- Input validation prevents injection attacks
"""

SERVER_DEPENDENCIES = [
    'loguru',
    'mcp',
    'pydantic',
    'httpx',
    'python-jenkins',
    'jenkinsapi',
    'cachetools',
    'tenacity',
    'python-dotenv',
]


def create_server() -> FastMCP:
    """Create and configure the Jenkins MCP server instance.
    
    Returns:
        Configured FastMCP server instance
    """
    # Initialize server with instructions
    server = FastMCP(
        name='jenkins-mcp-server',
        instructions=SERVER_INSTRUCTIONS,
        dependencies=SERVER_DEPENDENCIES,
    )
    
    # Initialize handlers lazily - they will be created when first tool is called
    _handlers = None
    
    def get_handlers():
        nonlocal _handlers
        if _handlers is None:
            from jenkins_mcp_server.handlers.job_handler import JobHandler
            from jenkins_mcp_server.handlers.build_handler import BuildHandler
            from jenkins_mcp_server.handlers.pipeline_handler import PipelineHandler
            from jenkins_mcp_server.handlers.system_handler import SystemHandler
            
            _handlers = {
                'job': JobHandler(),
                'build': BuildHandler(),
                'pipeline': PipelineHandler(),
                'system': SystemHandler(),
            }
        return _handlers
    
    # Register job management tools
    @server.tool()
    async def list_jenkins_jobs(
        folder_path: Optional[str] = None,
        include_disabled: bool = True,
        recursive: bool = False,
    ) -> List[ContentItem]:
        """List Jenkins jobs with optional filtering.
        
        Args:
            folder_path: Optional folder path to list jobs from
            include_disabled: Whether to include disabled jobs
            recursive: Whether to recursively list jobs in subfolders
            
        Returns:
            List of job information
        """
        try:
            handlers = get_handlers()
            jobs = await handlers['job'].list_jobs(
                folder_path=folder_path,
                include_disabled=include_disabled,
                recursive=recursive,
            )
            
            return [ContentItem(
                type='text',
                text=f'Found {len(jobs)} jobs:\n' + '\n'.join([
                    f'- {job.name} ({job.job_type}) - {job.url}'
                    for job in jobs
                ])
            )]
            
        except Exception as e:
            logger.error(f'Failed to list jobs: {e}')
            return [ContentItem(
                type='text',
                text=f'Error listing jobs: {str(e)}'
            )]
    
    @server.tool()
    async def get_job_details(
        job_name: str,
        include_builds: bool = True,
        build_limit: int = 10,
    ) -> List[ContentItem]:
        """Get detailed information about a Jenkins job.
        
        Args:
            job_name: Name of the job
            include_builds: Whether to include recent build information
            build_limit: Maximum number of recent builds to include
            
        Returns:
            Detailed job information
        """
        try:
            handlers = get_handlers()
            job_info = await handlers['job'].get_job_details(
                job_name=job_name,
                include_builds=include_builds,
                build_limit=build_limit,
            )
            
            content = [
                f'Job: {job_info.name}',
                f'Type: {job_info.job_type}',
                f'URL: {job_info.url}',
                f'Buildable: {job_info.buildable}',
                f'Disabled: {job_info.disabled}',
            ]
            
            if job_info.description:
                content.append(f'Description: {job_info.description}')
            
            if job_info.last_build:
                content.append(f'Last Build: #{job_info.last_build.get("number", "N/A")}')
            
            if include_builds and job_info.builds:
                content.append(f'\nRecent Builds ({len(job_info.builds)}):')
                for build in job_info.builds[:build_limit]:
                    content.append(f'  - #{build.get("number", "N/A")}: {build.get("url", "N/A")}')
            
            return [ContentItem(
                type='text',
                text='\n'.join(content)
            )]
            
        except Exception as e:
            logger.error(f'Failed to get job details: {e}')
            return [ContentItem(
                type='text',
                text=f'Error getting job details: {str(e)}'
            )]
    
    @server.tool()
    async def create_jenkins_job(
        job_name: str,
        job_type: str = 'freestyle',
        description: Optional[str] = None,
        folder_path: Optional[str] = None,
        config_xml: Optional[str] = None,
    ) -> List[ContentItem]:
        """Create a new Jenkins job.
        
        Args:
            job_name: Name for the new job
            job_type: Type of job (freestyle, pipeline, folder)
            description: Optional job description
            folder_path: Optional folder path to create job in
            config_xml: Optional custom configuration XML
            
        Returns:
            Job creation result
        """
        try:
            handlers = get_handlers()
            result = await handlers['job'].create_job(
                job_name=job_name,
                job_type=job_type,
                description=description,
                folder_path=folder_path,
                config_xml=config_xml,
            )
            
            return [ContentItem(
                type='text',
                text=f'Successfully created job: {result.name}\nURL: {result.url}'
            )]
            
        except Exception as e:
            logger.error(f'Failed to create job: {e}')
            return [ContentItem(
                type='text',
                text=f'Error creating job: {str(e)}'
            )]
    
    # Register build management tools
    @server.tool()
    async def trigger_jenkins_build(
        job_name: str,
        parameters: Optional[Dict[str, Any]] = None,
        wait_for_start: bool = False,
        timeout: int = 60,
    ) -> List[ContentItem]:
        """Trigger a Jenkins build.
        
        Args:
            job_name: Name of the job to build
            parameters: Optional build parameters
            wait_for_start: Whether to wait for build to start
            timeout: Timeout in seconds for waiting
            
        Returns:
            Build trigger result
        """
        try:
            handlers = get_handlers()
            result = await handlers['build'].trigger_build(
                job_name=job_name,
                parameters=parameters or {},
                wait_for_start=wait_for_start,
                timeout=timeout,
            )
            
            content = [
                f'Build triggered for job: {result.job_name}',
                f'Triggered: {result.triggered}',
                f'Message: {result.message}',
            ]
            
            if result.queue_item_id:
                content.append(f'Queue Item ID: {result.queue_item_id}')
            
            if result.build_number:
                content.append(f'Build Number: {result.build_number}')
                content.append(f'Build URL: {result.build_url}')
            
            return [ContentItem(
                type='text',
                text='\n'.join(content)
            )]
            
        except Exception as e:
            logger.error(f'Failed to trigger build: {e}')
            return [ContentItem(
                type='text',
                text=f'Error triggering build: {str(e)}'
            )]
    
    @server.tool()
    async def get_build_status(
        job_name: str,
        build_number: Optional[int] = None,
    ) -> List[ContentItem]:
        """Get Jenkins build status and information.
        
        Args:
            job_name: Name of the job
            build_number: Build number (latest if not specified)
            
        Returns:
            Build status information
        """
        try:
            handlers = get_handlers()
            build_info = await handlers['build'].get_build_info(
                job_name=job_name,
                build_number=build_number,
            )
            
            content = [
                f'Build #{build_info.number} for {build_info.job_name}',
                f'Status: {build_info.result or "RUNNING" if build_info.building else "UNKNOWN"}',
                f'Building: {build_info.building}',
                f'URL: {build_info.url}',
            ]
            
            if build_info.duration:
                content.append(f'Duration: {build_info.duration / 1000:.1f} seconds')
            
            if build_info.timestamp:
                content.append(f'Started: {build_info.timestamp}')
            
            if build_info.built_on:
                content.append(f'Built on: {build_info.built_on}')
            
            if build_info.description:
                content.append(f'Description: {build_info.description}')
            
            return [ContentItem(
                type='text',
                text='\n'.join(content)
            )]
            
        except Exception as e:
            logger.error(f'Failed to get build status: {e}')
            return [ContentItem(
                type='text',
                text=f'Error getting build status: {str(e)}'
            )]
    
    @server.tool()
    async def get_build_logs(
        job_name: str,
        build_number: Optional[int] = None,
        start_line: int = 0,
        max_lines: int = 1000,
    ) -> List[ContentItem]:
        """Get Jenkins build console logs.
        
        Args:
            job_name: Name of the job
            build_number: Build number (latest if not specified)
            start_line: Starting line number
            max_lines: Maximum number of lines to return
            
        Returns:
            Build console logs
        """
        try:
            handlers = get_handlers()
            logs = await handlers['build'].get_build_logs(
                job_name=job_name,
                build_number=build_number,
                start_line=start_line,
                max_lines=max_lines,
            )
            
            return [ContentItem(
                type='text',
                text=f'Build logs for {job_name} #{build_number or "latest"}:\n\n{logs}'
            )]
            
        except Exception as e:
            logger.error(f'Failed to get build logs: {e}')
            return [ContentItem(
                type='text',
                text=f'Error getting build logs: {str(e)}'
            )]
    
    # Register pipeline management tools
    @server.tool()
    async def create_jenkins_pipeline(
        name: str,
        script: str,
        description: Optional[str] = None,
        folder_path: Optional[str] = None,
        parameters: Optional[List[Dict[str, Any]]] = None,
        shared_libraries: Optional[List[str]] = None,
        pipeline_type: Optional[str] = None,
        validate_script: bool = True,
    ) -> List[ContentItem]:
        """Create a Jenkins pipeline job with enhanced validation and shared library support.
        
        Args:
            name: Pipeline name
            script: Pipeline script (Jenkinsfile content)
            description: Optional pipeline description
            folder_path: Optional folder path
            parameters: Optional pipeline parameters
            shared_libraries: List of shared libraries to include
            pipeline_type: Type of pipeline ('declarative' or 'scripted', auto-detected if not specified)
            validate_script: Whether to validate the pipeline script before creation
            
        Returns:
            Pipeline creation result with enhanced information
        """
        try:
            handlers = get_handlers()
            result = await handlers['pipeline'].create_pipeline(
                name=name,
                script=script,
                description=description,
                folder_path=folder_path,
                parameters=parameters or [],
                shared_libraries=shared_libraries,
                pipeline_type=pipeline_type,
                validate_script=validate_script,
            )
            
            content = [
                f'Pipeline Creation Result:',
                f'Name: {result.pipeline_name}',
                f'Status: {"✅ Created" if result.created else "❌ Failed"}',
                f'Type: {result.pipeline_type}',
                f'URL: {result.job_url}' if result.job_url else '',
                f'Message: {result.message}'
            ]
            
            if result.shared_libraries:
                content.append(f'Shared Libraries: {", ".join(result.shared_libraries)}')
            
            if result.validation_result:
                validation = result.validation_result
                content.append(f'Validation: {"✅ Passed" if validation["valid"] else "❌ Failed"}')
                
                if validation.get('warnings'):
                    content.append(f'Warnings: {len(validation["warnings"])}')
                    for warning in validation['warnings'][:3]:  # Show first 3 warnings
                        content.append(f'  • {warning}')
                
                if validation.get('used_tools'):
                    content.append(f'Tools Used: {", ".join(validation["used_tools"][:5])}')  # Show first 5 tools
            
            return [ContentItem(
                type='text',
                text='\n'.join(content)
            )]
            
        except Exception as e:
            logger.error(f'Failed to create pipeline: {e}')
            
            # Enhanced error reporting
            from jenkins_mcp_server.utils.error_reporting import report_operation_error, format_error_for_user
            error_report = report_operation_error(
                'create_jenkins_pipeline',
                e,
                context={'name': name, 'pipeline_type': pipeline_type, 'has_shared_libraries': bool(shared_libraries)}
            )
            
            return [ContentItem(
                type='text',
                text=format_error_for_user(error_report)
            )]
    
    @server.tool()
    async def generate_pipeline_template(
        pipeline_type: str,
        job_name: str,
        stages: Optional[List[str]] = None,
        shared_libraries: Optional[List[str]] = None,
        parameters: Optional[List[Dict[str, Any]]] = None,
        agent: Optional[str] = None,
    ) -> List[ContentItem]:
        """Generate a Jenkins pipeline template.
        
        Args:
            pipeline_type: Type of pipeline ('declarative' or 'scripted')
            job_name: Name of the job for the template
            stages: List of stage names (default: ['Build', 'Test', 'Deploy'])
            shared_libraries: List of shared libraries to include
            parameters: List of pipeline parameters
            agent: Agent specification (default: 'any')
            
        Returns:
            Generated pipeline template
        """
        try:
            from jenkins_mcp_server.utils.pipeline_utils import generate_pipeline_template
            
            template = generate_pipeline_template(
                pipeline_type=pipeline_type,
                job_name=job_name,
                stages=stages or ['Build', 'Test', 'Deploy'],
                shared_libraries=shared_libraries or [],
                parameters=parameters or [],
                agent=agent or 'any'
            )
            
            return [ContentItem(
                type='text',
                text=f'Generated {pipeline_type} pipeline template for {job_name}:\n\n```groovy\n{template}\n```'
            )]
            
        except Exception as e:
            logger.error(f'Failed to generate pipeline template: {e}')
            return [ContentItem(
                type='text',
                text=f'Error generating pipeline template: {str(e)}'
            )]
    
    @server.tool()
    async def validate_pipeline_script(
        script: str,
        pipeline_type: Optional[str] = None,
    ) -> List[ContentItem]:
        """Validate a Jenkins pipeline script.
        
        Args:
            script: Pipeline script to validate
            pipeline_type: Type of pipeline ('declarative' or 'scripted', auto-detected if not specified)
            
        Returns:
            Validation results
        """
        try:
            from jenkins_mcp_server.utils.pipeline_utils import PipelineValidator, detect_pipeline_type
            
            if not pipeline_type:
                pipeline_type = detect_pipeline_type(script)
            
            validator = PipelineValidator()
            result = validator.validate_pipeline_script(script, pipeline_type)
            
            content = [
                f'Pipeline Script Validation Results:',
                f'Type: {pipeline_type}',
                f'Status: {"✅ Valid" if result["valid"] else "❌ Invalid"}',
            ]
            
            if result['errors']:
                content.append(f'\n❌ Errors ({len(result["errors"])}):')
                for error in result['errors']:
                    content.append(f'  • {error}')
            
            if result['warnings']:
                content.append(f'\n⚠️ Warnings ({len(result["warnings"])}):')
                for warning in result['warnings']:
                    content.append(f'  • {warning}')
            
            if result['used_tools']:
                content.append(f'\n🔧 Tools Used ({len(result["used_tools"])}):')
                content.append(f'  {", ".join(result["used_tools"])}')
            
            if result['used_shared_libraries']:
                content.append(f'\n📚 Shared Libraries ({len(result["used_shared_libraries"])}):')
                content.append(f'  {", ".join(result["used_shared_libraries"])}')
            
            return [ContentItem(
                type='text',
                text='\n'.join(content)
            )]
            
        except Exception as e:
            logger.error(f'Failed to validate pipeline script: {e}')
            return [ContentItem(
                type='text',
                text=f'Error validating pipeline script: {str(e)}'
            )]
    
    @server.tool()
    async def manage_jenkins_builds(
        operation: str,
        job_name: str,
        build_number: Optional[int] = None,
        follow_logs: bool = False,
        max_lines: int = 100
    ) -> List[ContentItem]:
        """Manage Jenkins builds with various operations.
        
        Args:
            operation: Operation to perform ('abort', 'stream_logs', 'analytics')
            job_name: Name of the job
            build_number: Build number (latest if not specified)
            follow_logs: Whether to follow live logs (for stream_logs operation)
            max_lines: Maximum lines to return (for stream_logs operation)
            
        Returns:
            Operation results
        """
        try:
            handlers = get_handlers()
            
            if operation == 'abort':
                result = await handlers['build'].abort_build(job_name, build_number)
                
                return [ContentItem(
                    type='text',
                    text=f'Build Abort Operation:\n'
                         f'Job: {result.job_name}\n'
                         f'Build: #{result.build_number or "latest"}\n'
                         f'Status: {"✅ Success" if result.success else "❌ Failed"}\n'
                         f'Message: {result.message}'
                )]
            
            elif operation == 'stream_logs':
                result = await handlers['build'].stream_build_logs(
                    job_name, build_number, follow_logs, max_lines
                )
                
                if result['success']:
                    log_text = '\n'.join(result['logs'][:50])  # Show first 50 lines
                    content = [
                        f'Build Log Stream:',
                        f'Job: {result["job_name"]}',
                        f'Build: #{result["build_number"]}',
                        f'Status: {"🔄 Building" if result["is_building"] else "✅ Complete"}',
                        f'',
                        f'Recent Logs:',
                        log_text,
                    ]
                    
                    if result['is_building']:
                        content.append(f'\n🔗 Live logs: {result["log_url"]}')
                    
                    return [ContentItem(type='text', text='\n'.join(content))]
                else:
                    return [ContentItem(type='text', text=f'❌ {result["message"]}')]
            
            elif operation == 'analytics':
                analytics = await handlers['build'].get_build_analytics(job_name, 50, True)
                
                content = [
                    f'Build Analytics for {analytics.job_name}:',
                    f'',
                    f'📊 Performance Metrics:',
                    f'  Total Builds: {analytics.total_builds}',
                    f'  Success Rate: {analytics.success_rate:.1f}%',
                    f'  Average Duration: {analytics.average_duration:.1f} seconds',
                    f'',
                ]
                
                if analytics.bottlenecks:
                    content.extend([
                        f'⚠️ Bottlenecks Identified:',
                        *[f'  • {bottleneck}' for bottleneck in analytics.bottlenecks[:3]],
                        f'',
                    ])
                
                if analytics.optimization_suggestions:
                    content.extend([
                        f'💡 Optimization Suggestions:',
                        *[f'  • {suggestion}' for suggestion in analytics.optimization_suggestions[:3]],
                    ])
                
                return [ContentItem(type='text', text='\n'.join(content))]
            
            else:
                return [ContentItem(
                    type='text',
                    text=f'❌ Unknown operation: {operation}. Available: abort, stream_logs, analytics'
                )]
                
        except Exception as e:
            logger.error(f'Failed to manage build: {e}')
            return [ContentItem(
                type='text',
                text=f'Error managing build: {str(e)}'
            )]
    
    @server.tool()
    async def analyze_jenkins_system(
        analysis_type: str = 'comprehensive'
    ) -> List[ContentItem]:
        """Perform comprehensive Jenkins system analysis.
        
        Args:
            analysis_type: Type of analysis ('comprehensive', 'health', 'security', 'performance')
            
        Returns:
            System analysis results with recommendations
        """
        try:
            handlers = get_handlers()
            
            if analysis_type in ['comprehensive', 'health']:
                analysis = await handlers['system'].analyze_system()
                
                content = [
                    f'Jenkins System Analysis:',
                    f'',
                    f'🏥 Overall Health: {analysis.overall_health}',
                    f'',
                ]
                
                # Health checks
                if analysis.health_checks:
                    content.append('📋 Health Check Results:')
                    for check in analysis.health_checks[:5]:  # Show first 5 checks
                        status_icon = {'PASSED': '✅', 'WARNING': '⚠️', 'FAILED': '❌'}.get(check.get('status'), '❓')
                        content.append(f'  {status_icon} {check.get("name")}: {check.get("message")}')
                    content.append('')
                
                # Security audit
                if analysis.security_audit:
                    security = analysis.security_audit
                    content.extend([
                        f'🔒 Security Status:',
                        f'  Security Enabled: {"Yes" if security.get("security_enabled") else "No"}',
                    ])
                    
                    if security.get('findings'):
                        content.append('  Security Findings:')
                        for finding in security['findings'][:3]:
                            content.append(f'    • {finding.get("finding")} ({finding.get("severity")})')
                    content.append('')
                
                # Resource usage
                if analysis.resource_usage:
                    usage = analysis.resource_usage
                    content.extend([
                        f'📈 Resource Usage:',
                        f'  Executor Utilization: {usage.get("executor_utilization", 0):.1f}%',
                    ])
                    content.append('')
                
                # Plugin analysis
                if analysis.plugin_analysis:
                    plugin_health = analysis.plugin_analysis.get('plugin_health', 'Unknown')
                    outdated_count = len(analysis.plugin_analysis.get('outdated_plugins', []))
                    content.extend([
                        f'🔌 Plugin Health: {plugin_health}',
                        f'  Outdated Plugins: {outdated_count}',
                        f'',
                    ])
                
                # Recommendations
                if analysis.optimization_recommendations:
                    content.extend([
                        f'💡 Optimization Recommendations:',
                        *[f'  • {rec}' for rec in analysis.optimization_recommendations[:5]],
                    ])
                
                return [ContentItem(type='text', text='\n'.join(content))]
            
            else:
                return [ContentItem(
                    type='text',
                    text=f'❌ Unknown analysis type: {analysis_type}. Available: comprehensive, health'
                )]
                
        except Exception as e:
            logger.error(f'Failed to analyze system: {e}')
            return [ContentItem(
                type='text',
                text=f'Error analyzing system: {str(e)}'
            )]
    
    @server.tool()
    async def update_jenkins_pipeline(
        name: str,
        script: Optional[str] = None,
        description: Optional[str] = None,
        parameters: Optional[List[Dict[str, Any]]] = None,
        shared_libraries: Optional[List[str]] = None,
        validate_script: bool = True,
    ) -> List[ContentItem]:
        """Update an existing Jenkins pipeline with new configuration.
        
        Args:
            name: Pipeline name to update
            script: New pipeline script (optional - keeps existing if not provided)
            description: New description (optional)
            parameters: New parameters (optional)
            shared_libraries: New shared libraries (optional)
            validate_script: Whether to validate the script before updating
            
        Returns:
            Pipeline update results
        """
        try:
            handlers = get_handlers()
            result = await handlers['pipeline'].update_pipeline(
                name=name,
                script=script,
                description=description,
                parameters=parameters,
                shared_libraries=shared_libraries,
                validate_script=validate_script,
            )
            
            content = [
                f'Pipeline Update Result:',
                f'Name: {result.pipeline_name}',
                f'Status: {"✅ Updated" if result.job_url else "❌ Failed"}',
                f'Type: {result.pipeline_type}',
                f'URL: {result.job_url}' if result.job_url else '',
                f'Message: {result.message}'
            ]
            
            if result.shared_libraries:
                content.append(f'Shared Libraries: {", ".join(result.shared_libraries)}')
            
            if result.validation_result:
                validation = result.validation_result
                content.append(f'Validation: {"✅ Passed" if validation["valid"] else "❌ Failed"}')
                
                if validation.get('warnings'):
                    content.append(f'Warnings: {len(validation["warnings"])}')
                    for warning in validation['warnings'][:2]:
                        content.append(f'  • {warning}')
            
            return [ContentItem(type='text', text='\n'.join(content))]
            
        except Exception as e:
            logger.error(f'Failed to update pipeline: {e}')
            return [ContentItem(
                type='text',
                text=f'Error updating pipeline: {str(e)}'
            )]
    
    # Register system information tools
    @server.tool()
    async def get_jenkins_server_info(detailed: bool = False) -> List[ContentItem]:
        """Get Jenkins server information and status.
        
        Args:
            detailed: Whether to fetch comprehensive system information
            
        Returns:
            Jenkins server information with basic or detailed data
        """
        try:
            handlers = get_handlers()
            server_info = await handlers['system'].get_server_info(detailed=detailed)
            
            content = [
                f'Jenkins Server Information:',
                f'Version: {server_info.version}',
                f'URL: {server_info.url}',
            ]
            
            if detailed and server_info.version_details:
                version_details = server_info.version_details
                content.extend([
                    f'',
                    f'📋 Version Details:',
                    f'  Core Version: {version_details.get("core_version", "Unknown")}',
                    f'  LTS Version: {"Yes" if version_details.get("is_lts") else "No"}',
                ])
            
            if detailed and server_info.node_info:
                node_info = server_info.node_info
                content.extend([
                    f'',
                    f'🖥️ Node Information:',
                    f'  Total Nodes: {node_info.get("total_nodes", 0)}',
                    f'  Online Nodes: {node_info.get("online_nodes", 0)}',
                    f'  Total Executors: {node_info.get("total_executors", 0)}',
                    f'  Busy Executors: {node_info.get("busy_executors", 0)}',
                ])
                
                if node_info.get("total_executors", 0) > 0:
                    utilization = (node_info.get("busy_executors", 0) / node_info.get("total_executors", 1)) * 100
                    content.append(f'  Executor Utilization: {utilization:.1f}%')
            
            if detailed and server_info.plugin_info:
                plugin_info = server_info.plugin_info
                content.extend([
                    f'',
                    f'🔌 Plugin Information:',
                    f'  Total Plugins: {plugin_info.get("total_plugins", 0)}',
                    f'  Enabled Plugins: {plugin_info.get("enabled_plugins", 0)}',
                    f'  Plugins with Updates: {plugin_info.get("plugins_with_updates", 0)}',
                ])
            
            if detailed and server_info.jvm_info and not server_info.jvm_info.get('error'):
                jvm_info = server_info.jvm_info
                content.extend([
                    f'',
                    f'☕ JVM Information:',
                    f'  Java Version: {jvm_info.get("java_version", "Unknown")}',
                    f'  JVM Name: {jvm_info.get("jvm_name", "Unknown")}',
                    f'  OS: {jvm_info.get("os_name", "Unknown")} {jvm_info.get("os_version", "")}',
                ])
            
            return [ContentItem(
                type='text',
                text='\n'.join(content)
            )]
            
        except Exception as e:
            logger.error(f'Failed to get server info: {e}')
            return [ContentItem(
                type='text',
                text=f'Error getting server info: {str(e)}'
            )]
    
    @server.tool()
    async def get_jenkins_queue() -> List[ContentItem]:
        """Get Jenkins build queue information.
        
        Returns:
            Build queue information
        """
        try:
            handlers = get_handlers()
            queue_items = await handlers['system'].get_queue_info()
            
            if not queue_items:
                return [ContentItem(
                    type='text',
                    text='Jenkins build queue is empty'
                )]
            
            content = [f'Jenkins Build Queue ({len(queue_items)} items):']
            
            for item in queue_items:
                content.append(
                    f'- ID: {item.id}, Task: {item.task_name}, '
                    f'Blocked: {item.blocked}, Buildable: {item.buildable}'
                )
                if item.why:
                    content.append(f'  Reason: {item.why}')
            
            return [ContentItem(
                type='text',
                text='\n'.join(content)
            )]
            
        except Exception as e:
            logger.error(f'Failed to get queue info: {e}')
            return [ContentItem(
                type='text',
                text=f'Error getting queue info: {str(e)}'
            )]
    
    return server


# Create the server instance - will be created when imported
app = None

def get_app():
    """Get the FastMCP app instance, creating it if necessary."""
    global app
    if app is None:
        app = create_server()
    return app


def main() -> None:
    """Main entry point for the Jenkins MCP server."""
    parser = argparse.ArgumentParser(description='Jenkins MCP Server')
    parser.add_argument(
        '--jenkins-url',
        help='Jenkins server URL (can also use JENKINS_URL env var)'
    )
    parser.add_argument(
        '--jenkins-username',
        help='Jenkins username (can also use JENKINS_USERNAME env var)'
    )
    parser.add_argument(
        '--jenkins-token',
        help='Jenkins API token (can also use JENKINS_TOKEN env var)'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=30,
        help='Request timeout in seconds (default: 30)'
    )
    parser.add_argument(
        '--log-level',
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Logging level (default: INFO)'
    )
    parser.add_argument(
        '--log-file',
        help='Optional log file path'
    )
    parser.add_argument(
        '--cache-size',
        type=int,
        default=1000,
        help='Cache size (default: 1000)'
    )
    parser.add_argument(
        '--max-connections',
        type=int,
        default=20,
        help='Maximum HTTP connections (default: 20)'
    )
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(
        level=args.log_level,
        log_file=args.log_file,
        include_caller=args.log_level == 'DEBUG',
    )
    
    # Set environment variables from command line args
    if args.jenkins_url:
        os.environ['JENKINS_URL'] = args.jenkins_url
    if args.jenkins_username:
        os.environ['JENKINS_USERNAME'] = args.jenkins_username
    if args.jenkins_token:
        os.environ['JENKINS_TOKEN'] = args.jenkins_token
    
    os.environ['JENKINS_TIMEOUT'] = str(args.timeout)
    
    # Validate required environment variables
    required_vars = ['JENKINS_URL', 'JENKINS_USERNAME', 'JENKINS_TOKEN']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f'Missing required environment variables: {", ".join(missing_vars)}')
        logger.error('Please set the following environment variables or use command line arguments:')
        logger.error('- JENKINS_URL: Jenkins server URL')
        logger.error('- JENKINS_USERNAME: Jenkins username')
        logger.error('- JENKINS_TOKEN: Jenkins API token')
        exit(1)
    
    # Initialize cache and connection pool
    initialize_cache_manager(max_size=args.cache_size)
    initialize_connection_pool(max_connections=args.max_connections)
    
    logger.info('Starting Jenkins MCP Server')
    logger.info(f'Jenkins URL: {os.getenv("JENKINS_URL")}')
    logger.info(f'Username: {os.getenv("JENKINS_USERNAME")}')
    logger.info(f'Timeout: {args.timeout}s')
    logger.info(f'Log Level: {args.log_level}')
    
    # Run the server
    app = get_app()
    app.run()


if __name__ == '__main__':
    main()
