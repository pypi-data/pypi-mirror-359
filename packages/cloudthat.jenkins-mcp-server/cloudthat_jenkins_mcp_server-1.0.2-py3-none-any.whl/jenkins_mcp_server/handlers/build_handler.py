"""Build handler for Jenkins MCP Server."""

import time
from typing import Any, Dict, List, Optional, Union

from loguru import logger

from jenkins_mcp_server.handlers.base_handler import BaseHandler
from jenkins_mcp_server.models import BuildInfo, BuildResult, BuildTriggerResult
from jenkins_mcp_server.utils.validation import validate_job_name, validate_build_number, validate_build_parameters


class BuildHandler(BaseHandler):
    """Handler for Jenkins build operations."""
    
    async def trigger_build(
        self,
        job_name: str,
        parameters: Optional[Dict[str, Any]] = None,
        wait_for_start: bool = False,
        timeout: int = 60,
    ) -> BuildTriggerResult:
        """Trigger a Jenkins build."""
        try:
            job_name = validate_job_name(job_name)
            parameters = validate_build_parameters(parameters or {})
            
            # Trigger the build with CSRF protection
            if parameters:
                queue_item_id = await self._trigger_build_with_params(job_name, parameters)
            else:
                queue_item_id = await self._trigger_build_simple(job_name)
            
            # Check if build was triggered successfully
            triggered = queue_item_id is not None
            
            result = BuildTriggerResult(
                job_name=job_name,
                queue_item_id=queue_item_id,
                triggered=triggered,
                message=f'Build {"triggered successfully" if triggered else "failed to trigger"} for job {job_name}',
                parameters=parameters,
            )
            
            # Wait for build to start if requested
            if wait_for_start and queue_item_id:
                build_number = await self._wait_for_build_start(job_name, queue_item_id, timeout)
                if build_number:
                    result.build_number = build_number
                    result.build_url = f'{self.jenkins_url}/job/{job_name}/{build_number}/'
            
            return result
            
        except Exception as e:
            logger.error(f'Failed to trigger build: {e}')
            return BuildTriggerResult(
                job_name=job_name or 'unknown',  # Provide default for None
                triggered=False,
                message=f'Failed to trigger build: {str(e)}',
            )
    async def get_build_analytics(
        self,
        job_name: str,
        build_count: int = 50,
        include_stages: bool = True
    ) -> 'BuildAnalytics':
        """Get build performance analytics for a job.
        
        Args:
            job_name: Name of the job
            build_count: Number of recent builds to analyze
            include_stages: Whether to include stage-level analytics
            
        Returns:
            BuildAnalytics with performance data and recommendations
        """
        try:
            from jenkins_mcp_server.models import BuildAnalytics
            
            job_name = validate_job_name(job_name)
            
            # Get recent builds directly since _get_recent_builds is async
            builds = await self._get_recent_builds(job_name, build_count)
            
            if not builds:
                return BuildAnalytics(
                    job_name=job_name,
                    total_builds=0,
                    success_rate=0.0,
                    average_duration=0.0,
                    recent_performance=[],
                    bottlenecks=['No build data available'],
                    optimization_suggestions=['Run some builds to generate analytics']
                )
            
            # Calculate analytics
            total_builds = len(builds)
            successful_builds = [b for b in builds if b.get('result') == 'SUCCESS']
            success_rate = (len(successful_builds) / total_builds) * 100
            
            # Calculate average duration
            durations = [b.get('duration', 0) for b in builds if b.get('duration')]
            average_duration = sum(durations) / len(durations) if durations else 0
            
            # Analyze recent performance
            recent_performance = []
            for build in builds[:10]:  # Last 10 builds
                performance_data = {
                    'build_number': build.get('number'),
                    'result': build.get('result'),
                    'duration': build.get('duration', 0),
                    'timestamp': build.get('timestamp'),
                    'stages': []
                }
                
                if include_stages:
                    performance_data['stages'] = await self._get_build_stages(job_name, build.get('number'))
                
                recent_performance.append(performance_data)
            
            # Identify bottlenecks
            bottlenecks = self._identify_bottlenecks(builds, recent_performance)
            
            # Generate optimization suggestions
            optimization_suggestions = self._generate_build_optimizations(
                builds, success_rate, average_duration, bottlenecks
            )
            
            return BuildAnalytics(
                job_name=job_name,
                total_builds=total_builds,
                success_rate=success_rate,
                average_duration=average_duration / 1000,  # Convert to seconds
                recent_performance=recent_performance,
                bottlenecks=bottlenecks,
                optimization_suggestions=optimization_suggestions
            )
            
        except Exception as e:
            logger.error(f'Failed to get build analytics: {e}')
            return BuildAnalytics(
                job_name=job_name,
                total_builds=0,
                success_rate=0.0,
                average_duration=0.0,
                bottlenecks=[f'Error getting analytics: {str(e)}'],
                optimization_suggestions=['Fix analytics collection issues']
            )
    
    async def _get_recent_builds(self, job_name: str, count: int) -> List[Dict[str, Any]]:
        """Get recent builds for a job."""
        try:
            # Use the correct Jenkins API to get job info with builds
            job_info = await self.execute_with_retry(
                f'get_job_info_{job_name}',
                self.jenkins_client.get_job_info,
                job_name,
                depth=1,  # Get build details
                fetch_all_builds=False
            )
            
            builds = job_info.get('builds', [])[:count]
            
            build_data = []
            for build in builds:
                try:
                    # Get detailed build information for each build
                    build_info = await self.execute_with_retry(
                        f'get_build_info_{job_name}_{build["number"]}',
                        self.jenkins_client.get_build_info,
                        job_name,
                        build['number']
                    )
                    
                    build_data.append({
                        'number': build_info.get('number'),
                        'result': build_info.get('result'),
                        'duration': build_info.get('duration', 0),
                        'timestamp': build_info.get('timestamp'),
                        'url': build_info.get('url'),
                        'building': build_info.get('building', False),
                        'description': build_info.get('description', ''),
                        'built_on': build_info.get('builtOn', ''),
                        'change_set': build_info.get('changeSet', {}).get('items', [])
                    })
                    
                except Exception as build_error:
                    logger.warning(f'Failed to get build info for {job_name}#{build.get("number")}: {build_error}')
                    # Add basic build info even if detailed fetch fails
                    build_data.append({
                        'number': build.get('number'),
                        'result': 'UNKNOWN',
                        'duration': 0,
                        'timestamp': 0,
                        'url': build.get('url', ''),
                        'building': False
                    })
            
            return build_data
            
        except Exception as e:
            logger.error(f'Failed to get recent builds for {job_name}: {e}')
            return []
    
    async def _get_build_stages(self, job_name: str, build_number: int) -> List[Dict[str, Any]]:
        """Get stage information for a build."""
        try:
            # Try to get pipeline stages if it's a pipeline job
            stages_url = f'{self.jenkins_url}/job/{job_name}/{build_number}/wfapi/describe'
            
            try:
                response = await self._make_api_request('GET', stages_url)
                if response and 'stages' in response:
                    stages = []
                    for stage in response['stages']:
                        stages.append({
                            'name': stage.get('name'),
                            'status': stage.get('status'),
                            'duration': stage.get('durationMillis', 0),
                            'start_time': stage.get('startTimeMillis'),
                        })
                    return stages
            except Exception:
                pass
            
            # Fallback: return empty stages list
            return []
            
        except Exception as e:
            logger.debug(f'Failed to get build stages: {e}')
            return []
    
    def _identify_bottlenecks(
        self, 
        builds: List[Dict[str, Any]], 
        recent_performance: Optional[List[Dict[str, Any]]] = None
    ) -> List[str]:
        """Identify performance bottlenecks.
        
        Args:
            builds: List of build data
            recent_performance: Optional recent performance data (for backward compatibility)
        """
        bottlenecks = []
        
        if not builds:
            return bottlenecks
        
        # Use recent_performance if provided, otherwise default to empty list
        if recent_performance is None:
            recent_performance = []
        
        # Check for consistently long builds
        durations = [b.get('duration', 0) for b in builds if b.get('duration')]
        if durations:
            avg_duration = sum(durations) / len(durations)
            long_builds = [d for d in durations if d > avg_duration * 1.5]
            
            if len(long_builds) > len(durations) * 0.3:  # More than 30% are long
                bottlenecks.append('Consistently long build times detected')
        
        # Check for high failure rate
        failed_builds = [b for b in builds if b.get('result') in ['FAILURE', 'ABORTED']]
        if len(failed_builds) > len(builds) * 0.2:  # More than 20% failures
            bottlenecks.append('High build failure rate detected')
        
        # Check for stage-level bottlenecks
        stage_durations = {}
        for perf in recent_performance:
            for stage in perf.get('stages', []):
                stage_name = stage.get('name')
                duration = stage.get('duration', 0)
                if stage_name:
                    if stage_name not in stage_durations:
                        stage_durations[stage_name] = []
                    stage_durations[stage_name].append(duration)
        
        # Find slowest stages
        for stage_name, durations in stage_durations.items():
            if durations:
                avg_duration = sum(durations) / len(durations)
                if avg_duration > 300000:  # More than 5 minutes
                    bottlenecks.append(f'Slow stage detected: {stage_name}')
        
        return bottlenecks
    
    def _generate_build_optimizations(
        self,
        analytics_data: Union[List[Dict[str, Any]], Dict[str, Any]],
        success_rate: Optional[float] = None,
        average_duration: Optional[float] = None,
        bottlenecks: Optional[List[str]] = None
    ) -> List[str]:
        """Generate optimization suggestions.
        
        Args:
            analytics_data: Build analytics data (can be list of builds or analytics dict)
            success_rate: Optional success rate (for backward compatibility)
            average_duration: Optional average duration (for backward compatibility)
            bottlenecks: Optional bottlenecks list (for backward compatibility)
        """
        suggestions = []
        
        # Handle different input formats for backward compatibility
        if isinstance(analytics_data, dict):
            # New format: analytics_data is a dict with computed values
            success_rate = analytics_data.get('success_rate', success_rate or 100)
            average_duration = analytics_data.get('avg_duration', average_duration or 0)
            bottlenecks = analytics_data.get('bottlenecks', bottlenecks or [])
        elif isinstance(analytics_data, list):
            # Old format: analytics_data is list of builds, compute values
            builds = analytics_data
            if builds:
                successful_builds = [b for b in builds if b.get('result') == 'SUCCESS']
                success_rate = (len(successful_builds) / len(builds)) * 100 if builds else 100
                
                durations = [b.get('duration', 0) for b in builds if b.get('duration')]
                average_duration = sum(durations) / len(durations) if durations else 0
                
                bottlenecks = bottlenecks or []
        
        # Success rate optimizations
        if success_rate and success_rate < 80:
            suggestions.append('Improve build stability - success rate is below 80%')
            suggestions.append('Review recent failures and fix common issues')
        
        # Duration optimizations
        if average_duration and average_duration > 1800000:  # More than 30 minutes
            suggestions.append('Consider parallelizing build steps to reduce duration')
            suggestions.append('Review build dependencies and optimize caching')
        
        # Bottleneck-specific suggestions
        for bottleneck in (bottlenecks or []):
            if 'long build times' in bottleneck:
                suggestions.append('Implement build caching to reduce compilation time')
                suggestions.append('Consider using faster build agents')
            elif 'failure rate' in bottleneck:
                suggestions.append('Implement better error handling and retry logic')
                suggestions.append('Add more comprehensive testing in earlier stages')
            elif 'Slow stage' in bottleneck:
                suggestions.append(f'Optimize the slow stage mentioned in bottlenecks')
        
        # General suggestions
        if not suggestions:
            suggestions.append('Build performance looks good - consider monitoring trends')
        
        return suggestions
    
    async def abort_build(
        self,
        job_name: str,
        build_number: Optional[int] = None
    ) -> 'BuildOperation':
        """Abort a running build.
        
        Args:
            job_name: Name of the job
            build_number: Build number to abort (latest if not specified)
            
        Returns:
            BuildOperation result
        """
        try:
            from jenkins_mcp_server.models import BuildOperation
            
            job_name = validate_job_name(job_name)
            
            # Get build number if not specified
            if build_number is None:
                job_info = await self.execute_with_retry(
                    f'get_job_{job_name}',
                    self.jenkins_client.get_job_info,
                    job_name
                )
                build_number = job_info.get('lastBuild', {}).get('number')
                
                if not build_number:
                    return BuildOperation(
                        operation='abort_build',
                        job_name=job_name,
                        success=False,
                        message='No builds found to abort'
                    )
            
            # Check if build is running
            build_info = await self.execute_with_retry(
                f'get_build_{job_name}_{build_number}',
                self.jenkins_client.get_build_info,
                job_name,
                build_number
            )
            
            if not build_info.get('building', False):
                return BuildOperation(
                    operation='abort_build',
                    job_name=job_name,
                    build_number=build_number,
                    success=False,
                    message=f'Build #{build_number} is not running'
                )
            
            # Abort the build
            await self.execute_with_retry(
                f'abort_build_{job_name}_{build_number}',
                self._abort_build_request,
                job_name,
                build_number
            )
            
            return BuildOperation(
                operation='abort_build',
                job_name=job_name,
                build_number=build_number,
                success=True,
                message=f'Build #{build_number} abort request sent successfully'
            )
            
        except Exception as e:
            logger.error(f'Failed to abort build: {e}')
            return BuildOperation(
                operation='abort_build',
                job_name=job_name,
                build_number=build_number,
                success=False,
                message=f'Failed to abort build: {str(e)}'
            )
    
    async def _abort_build_request(self, job_name: str, build_number: int):
        """Send abort request to Jenkins."""
        abort_url = f'{self.jenkins_url}/job/{job_name}/{build_number}/stop'
        await self._make_request('POST', abort_url)
    
    async def stream_build_logs(
        self,
        job_name: str,
        build_number: Optional[int] = None,
        follow: bool = True,
        max_lines: int = 100
    ) -> Dict[str, Any]:
        """Stream build logs with real-time updates.
        
        Args:
            job_name: Name of the job
            build_number: Build number (latest if not specified)
            follow: Whether to follow live logs
            max_lines: Maximum lines to return
            
        Returns:
            Log streaming information
        """
        try:
            job_name = validate_job_name(job_name)
            
            # Get build number if not specified
            if build_number is None:
                job_info = await self.execute_with_retry(
                    f'get_job_{job_name}',
                    self.jenkins_client.get_job_info,
                    job_name
                )
                build_number = job_info.get('lastBuild', {}).get('number')
                
                if not build_number:
                    return {
                        'success': False,
                        'message': 'No builds found',
                        'logs': []
                    }
            
            # Get current logs
            logs = await self.get_build_logs(job_name, build_number, max_lines=max_lines)
            
            # Check if build is still running
            build_info = await self.execute_with_retry(
                f'get_build_{job_name}_{build_number}',
                self.jenkins_client.get_build_info,
                job_name,
                build_number
            )
            
            is_building = build_info.get('building', False)
            
            return {
                'success': True,
                'job_name': job_name,
                'build_number': build_number,
                'is_building': is_building,
                'logs': logs.split('\n') if isinstance(logs, str) else logs,
                'streaming_available': is_building and follow,
                'log_url': f'{self.jenkins_url}/job/{job_name}/{build_number}/console'
            }
            
        except Exception as e:
            logger.error(f'Failed to stream build logs: {e}')
            return {
                'success': False,
                'message': f'Failed to stream logs: {str(e)}',
                'logs': []
            }
    
    async def _trigger_build_simple(self, job_name: str) -> Optional[int]:
        """Trigger a simple build without parameters.
        
        Args:
            job_name: Name of the job to build
            
        Returns:
            Optional[int]: Queue item ID if successful, None otherwise
        """
        try:
            # Use Jenkins client's build_job method which returns queue item ID
            queue_item_id = await self.execute_with_retry(
                f'trigger_build_{job_name}',
                self.jenkins_client.build_job,
                job_name,
            )
            
            return queue_item_id
            
        except Exception as e:
            logger.error(f'Failed to trigger simple build: {e}')
            return None
    
    async def _trigger_build_with_params(self, job_name: str, parameters: Dict[str, Any]) -> Optional[int]:
        """Trigger a build with parameters.
        
        Args:
            job_name: Name of the job to build
            parameters: Build parameters as key-value pairs
            
        Returns:
            Optional[int]: Queue item ID if successful, None otherwise
        """
        try:
            # Use Jenkins client's build_job method which returns queue item ID
            queue_item_id = await self.execute_with_retry(
                f'trigger_build_{job_name}',
                self.jenkins_client.build_job,
                job_name,
                parameters,
            )
            
            return queue_item_id
            
        except Exception as e:
            logger.error(f'Failed to trigger parameterized build: {e}')
            return None
    
    async def get_build_info(
        self,
        job_name: str,
        build_number: Optional[int] = None,
    ) -> BuildInfo:
        """Get Jenkins build information."""
        try:
            job_name = validate_job_name(job_name)
            
            if build_number is not None:
                build_number = validate_build_number(build_number)
                cache_key = f'build_info:{job_name}:{build_number}'
            else:
                cache_key = f'build_info:{job_name}:latest'
            
            return await self.get_cached_or_fetch(
                cache_key=cache_key,
                fetch_func=self._fetch_build_info,
                cache_type='build',
                job_name=job_name,
                build_number=build_number,
            )
            
        except Exception as e:
            raise self._handle_jenkins_exception(e, f'Get build info for {job_name}')
    
    def _fetch_build_info(self, job_name: str, build_number: Optional[int] = None) -> BuildInfo:
        """Fetch build information from Jenkins API."""
        try:
            if build_number is None:
                # Get latest build
                job_info = self.jenkins_client.get_job_info(job_name)
                if not job_info.get('lastBuild'):
                    raise Exception(f'No builds found for job {job_name}')
                build_number = job_info['lastBuild']['number']
            
            build_info = self.jenkins_client.get_build_info(job_name, build_number)
            
            return BuildInfo(
                number=build_info['number'],
                url=build_info['url'],
                job_name=job_name,
                display_name=build_info.get('displayName'),
                description=build_info.get('description'),
                result=BuildResult(build_info['result']) if build_info.get('result') else None,
                building=build_info.get('building', False),
                duration=build_info.get('duration'),
                estimated_duration=build_info.get('estimatedDuration'),
                timestamp=build_info.get('timestamp'),
                built_on=build_info.get('builtOn'),
                change_set=build_info.get('changeSet', {}).get('items', []),
                culprits=build_info.get('culprits', []),
                artifacts=build_info.get('artifacts', []),
            )
            
        except Exception as e:
            logger.error(f'Failed to fetch build info: {e}')
            raise
    
    async def get_build_logs(
        self,
        job_name: str,
        build_number: Optional[int] = None,
        start_line: int = 0,
        max_lines: int = 1000,
    ) -> str:
        """Get Jenkins build console logs."""
        try:
            job_name = validate_job_name(job_name)
            
            if build_number is not None:
                build_number = validate_build_number(build_number)
            else:
                # Get latest build number
                job_info = self.jenkins_client.get_job_info(job_name)
                if not job_info.get('lastBuild'):
                    raise Exception(f'No builds found for job {job_name}')
                build_number = job_info['lastBuild']['number']
            
            # Get console output
            console_output = await self.execute_with_retry(
                f'get_build_logs_{job_name}_{build_number}',
                self.jenkins_client.get_build_console_output,
                job_name,
                build_number,
            )
            
            # Apply line filtering
            lines = console_output.split('\n')
            if start_line > 0:
                lines = lines[start_line:]
            if max_lines > 0:
                lines = lines[:max_lines]
            
            return '\n'.join(lines)
            
        except Exception as e:
            raise self._handle_jenkins_exception(e, f'Get build logs for {job_name}')
    
    async def _wait_for_build_start(self, job_name: str, queue_item_id: int, timeout: int) -> Optional[int]:
        """Wait for build to start and return build number."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                queue_item = self.jenkins_client.get_queue_item(queue_item_id)
                
                if queue_item.get('executable'):
                    return queue_item['executable']['number']
                
                if queue_item.get('cancelled'):
                    logger.warning(f'Build was cancelled for job {job_name}')
                    return None
                
                # Wait before checking again
                time.sleep(2)
                
            except Exception as e:
                logger.warning(f'Error checking queue item {queue_item_id}: {e}')
                time.sleep(2)
        
        logger.warning(f'Timeout waiting for build to start for job {job_name}')
        return None
