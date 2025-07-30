"""System handler for Jenkins MCP Server."""

import json
from typing import Dict, List, Any, Optional

from loguru import logger

from jenkins_mcp_server.handlers.base_handler import BaseHandler
from jenkins_mcp_server.models import JenkinsServerInfo, QueueItemInfo, SystemAnalysis


class SystemHandler(BaseHandler):
    """Handler for Jenkins system operations."""
    
    async def get_server_info(self, detailed: bool = False) -> JenkinsServerInfo:
        """Get Jenkins server information.
        
        Args:
            detailed: Whether to fetch detailed system information
            
        Returns:
            JenkinsServerInfo with basic or comprehensive information
        """
        try:
            cache_key = f'server_info_{"detailed" if detailed else "basic"}'
            
            return await self.get_cached_or_fetch(
                cache_key=cache_key,
                fetch_func=lambda: self._fetch_server_info(detailed),
                cache_type='server',
            )
            
        except Exception as e:
            raise self._handle_jenkins_exception(e, 'Get server info')
    
    def _fetch_server_info(self, detailed: bool = False) -> JenkinsServerInfo:
        """Fetch server information from Jenkins API."""
        try:
            # Basic server info
            server_info = self.jenkins_client.get_info()
            
            basic_info = JenkinsServerInfo(
                version=server_info.get('version', 'Unknown'),
                url=self.jenkins_url
            )
            
            if not detailed:
                return basic_info
            
            # Enhanced detailed information
            basic_info.version_details = self._get_version_details(server_info)
            basic_info.system_health = self._get_system_health()
            basic_info.jvm_info = self._get_jvm_info()
            basic_info.node_info = self._get_node_info()
            basic_info.security_config = self._get_security_config()
            basic_info.global_config = self._get_global_config()
            basic_info.plugin_info = self._get_plugin_info()
            basic_info.environment_info = self._get_environment_info()
            basic_info.tools_info = self._get_tools_info()
            
            return basic_info
            
        except Exception as e:
            logger.error(f'Failed to fetch server info: {e}')
            # Return basic info even if detailed fetch fails
            return JenkinsServerInfo(
                version='Unknown',
                url=self.jenkins_url
            )
    
    def _get_version_details(self, server_info: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed version information."""
        try:
            version = server_info.get('version', 'Unknown')
            
            # Determine if LTS version
            is_lts = 'lts' in version.lower() or len(version.split('.')) > 2
            
            return {
                'core_version': version,
                'is_lts': is_lts,
                'hudson_version': server_info.get('hudsonVersion', version),
                'jenkins_session': server_info.get('jenkinsSession'),
                'instance_identity': server_info.get('instanceIdentity'),
                'system_message': server_info.get('systemMessage', ''),
            }
        except Exception as e:
            logger.debug(f'Failed to get version details: {e}')
            return {'error': str(e)}
    
    def _get_system_health(self) -> Dict[str, Any]:
        """Get system health indicators."""
        try:
            # Try to get system metrics if available
            health_data = {}
            
            # Get basic system info
            try:
                system_info_url = f'{self.jenkins_url}/systemInfo/api/json'
                response = self.jenkins_client.jenkins_open(system_info_url)
                if response:
                    system_data = response.json()
                    health_data.update({
                        'system_properties': len(system_data.get('systemProperties', {})),
                        'environment_variables': len(system_data.get('envVars', {})),
                    })
            except Exception:
                pass
            
            # Get load statistics if available
            try:
                load_stats_url = f'{self.jenkins_url}/overallLoad/api/json'
                response = self.jenkins_client.jenkins_open(load_stats_url)
                if response:
                    load_data = response.json()
                    health_data.update({
                        'load_statistics': load_data
                    })
            except Exception:
                pass
            
            return health_data
            
        except Exception as e:
            logger.debug(f'Failed to get system health: {e}')
            return {'error': str(e)}
    
    def _get_jvm_info(self) -> Dict[str, Any]:
        """Get JVM statistics and configuration."""
        try:
            jvm_info = {}
            
            # Try to get JVM metrics
            try:
                system_info_url = f'{self.jenkins_url}/systemInfo/api/json'
                response = self.jenkins_client.jenkins_open(system_info_url)
                if response:
                    system_data = response.json()
                    system_props = system_data.get('systemProperties', {})
                    
                    jvm_info = {
                        'java_version': system_props.get('java.version'),
                        'java_vendor': system_props.get('java.vendor'),
                        'java_home': system_props.get('java.home'),
                        'jvm_name': system_props.get('java.vm.name'),
                        'jvm_version': system_props.get('java.vm.version'),
                        'os_name': system_props.get('os.name'),
                        'os_arch': system_props.get('os.arch'),
                        'os_version': system_props.get('os.version'),
                        'user_timezone': system_props.get('user.timezone'),
                        'file_encoding': system_props.get('file.encoding'),
                    }
            except Exception:
                pass
            
            return jvm_info
            
        except Exception as e:
            logger.debug(f'Failed to get JVM info: {e}')
            return {'error': str(e)}
    
    def _get_node_info(self) -> Dict[str, Any]:
        """Get node details and statistics."""
        try:
            nodes_info = {
                'total_nodes': 0,
                'online_nodes': 0,
                'offline_nodes': 0,
                'total_executors': 0,
                'busy_executors': 0,
                'nodes': []
            }
            
            # Get all nodes using the correct API
            try:
                nodes = self.jenkins_client.get_nodes(depth=1)
                nodes_info['total_nodes'] = len(nodes)
                
                for node in nodes:
                    try:
                        node_name = node['name']
                        # Handle master node name variations
                        if node_name in ['master', 'Built-In Node']:
                            node_name = '(master)'
                        
                        node_info = self.jenkins_client.get_node_info(node_name, depth=1)
                        
                        is_online = not node_info.get('offline', True)
                        if is_online:
                            nodes_info['online_nodes'] += 1
                        else:
                            nodes_info['offline_nodes'] += 1
                        
                        num_executors = node_info.get('numExecutors', 0)
                        nodes_info['total_executors'] += num_executors
                        
                        # Count busy executors
                        executors = node_info.get('executors', [])
                        busy_count = sum(1 for executor in executors if executor.get('currentExecutable'))
                        nodes_info['busy_executors'] += busy_count
                        
                        nodes_info['nodes'].append({
                            'name': node['name'],
                            'online': is_online,
                            'executors': num_executors,
                            'busy_executors': busy_count,
                            'labels': [label.get('name', '') for label in node_info.get('assignedLabels', [])],
                            'description': node_info.get('description', ''),
                            'architecture': node_info.get('architecture'),
                            'monitor_data': node_info.get('monitorData', {})
                        })
                        
                    except Exception as node_error:
                        logger.warning(f'Failed to get info for node {node.get("name", "unknown")}: {node_error}')
                        # Add basic node info even if detailed fetch fails
                        nodes_info['nodes'].append({
                            'name': node.get('name', 'unknown'),
                            'online': not node.get('offline', True),
                            'executors': 0,
                            'busy_executors': 0,
                            'labels': [],
                            'description': '',
                            'error': str(node_error)
                        })
                        continue
            except Exception as nodes_error:
                logger.error(f'Failed to get nodes list: {nodes_error}')
                raise
            
            return nodes_info
            
        except Exception as e:
            logger.error(f'Failed to get node info: {e}')
            return {
                'total_nodes': 0,
                'online_nodes': 0,
                'offline_nodes': 0,
                'total_executors': 0,
                'busy_executors': 0,
                'nodes': [],
                'error': str(e)
            }
    
    def _get_security_config(self) -> Dict[str, Any]:
        """Get security configuration details."""
        try:
            security_info = {}
            
            # Try to get security realm info
            try:
                # This requires admin permissions, so it might fail
                config_url = f'{self.jenkins_url}/configureSecurity/api/json'
                response = self.jenkins_client.jenkins_open(config_url)
                if response:
                    security_info['security_configured'] = True
            except Exception:
                security_info['security_configured'] = False
                security_info['note'] = 'Security configuration requires admin permissions'
            
            return security_info
            
        except Exception as e:
            logger.debug(f'Failed to get security config: {e}')
            return {'error': str(e)}
    
    def _get_global_config(self) -> Dict[str, Any]:
        """Get global configuration settings."""
        try:
            config_info = {}
            
            # Get basic configuration info that's publicly available
            server_info = self.jenkins_client.get_info()
            config_info.update({
                'quiet_period': server_info.get('quietPeriod', 5),
                'scm_checkout_retry_count': server_info.get('scmCheckoutRetryCount', 0),
                'slave_agent_port': server_info.get('slaveAgentPort', -1),
                'use_crumbs': server_info.get('useCrumbs', False),
                'use_security': server_info.get('useSecurity', False),
            })
            
            return config_info
            
        except Exception as e:
            logger.debug(f'Failed to get global config: {e}')
            return {'error': str(e)}
    
    def _get_plugin_info(self) -> Dict[str, Any]:
        """Get plugin inventory and status."""
        try:
            plugins_info = {
                'total_plugins': 0,
                'enabled_plugins': 0,
                'disabled_plugins': 0,
                'plugins_with_updates': 0,
                'plugins': []
            }
            
            # Try to get detailed plugin info first
            try:
                plugins_dict = self.jenkins_client.get_plugins(depth=2)
                # Convert multi_key_dict to list of plugins
                plugins = [plugin for plugin in plugins_dict.values()]
                plugins_info['total_plugins'] = len(plugins)
                
                for plugin in plugins:
                    # Plugin is a dict subclass, use dictionary access
                    is_enabled = plugin.get('enabled', False)
                    has_update = plugin.get('hasUpdate', False)
                    
                    if is_enabled:
                        plugins_info['enabled_plugins'] += 1
                    else:
                        plugins_info['disabled_plugins'] += 1
                    
                    if has_update:
                        plugins_info['plugins_with_updates'] += 1
                    
                    plugins_info['plugins'].append({
                        'short_name': plugin.get('shortName', ''),
                        'long_name': plugin.get('longName', ''),
                        'version': str(plugin.get('version', 'Unknown')),
                        'enabled': is_enabled,
                        'active': plugin.get('active', False),
                        'has_update': has_update,
                        'url': plugin.get('url', ''),
                        'dependencies': plugin.get('dependencies', [])
                    })
            except Exception as detailed_error:
                logger.warning(f'Failed to get detailed plugin info: {detailed_error}')
                # Try fallback to basic plugin info
                try:
                    plugins_info_json = self.jenkins_client.get_plugins_info()
                    plugins_info['total_plugins'] = len(plugins_info_json)
                    plugins_info['enabled_plugins'] = len(plugins_info_json)  # Assume all enabled
                    plugins_info['plugins'] = [
                        {
                            'short_name': p.get('shortName', ''),
                            'version': p.get('version', ''),
                            'enabled': True,  # Assume enabled in basic info
                            'active': True
                        }
                        for p in plugins_info_json
                    ]
                except Exception as basic_error:
                    logger.error(f'Failed to get basic plugin info: {basic_error}')
                    raise
            
            return plugins_info
            
        except Exception as e:
            logger.error(f'Failed to get plugin info: {e}')
            return {
                'total_plugins': 0,
                'enabled_plugins': 0,
                'disabled_plugins': 0,
                'plugins_with_updates': 0,
                'plugins': [],
                'error': str(e)
            }
    
    def _get_environment_info(self) -> Dict[str, Any]:
        """Get system environment variables."""
        try:
            env_info = {}
            
            # Get environment variables if accessible
            try:
                system_info_url = f'{self.jenkins_url}/systemInfo/api/json'
                response = self.jenkins_client.jenkins_open(system_info_url)
                if response:
                    system_data = response.json()
                    env_vars = system_data.get('envVars', {})
                    
                    # Filter sensitive environment variables
                    filtered_env = {}
                    sensitive_keys = ['password', 'token', 'key', 'secret', 'credential']
                    
                    for key, value in env_vars.items():
                        if any(sensitive in key.lower() for sensitive in sensitive_keys):
                            filtered_env[key] = '[FILTERED]'
                        else:
                            filtered_env[key] = value
                    
                    env_info = {
                        'total_variables': len(env_vars),
                        'filtered_variables': len([k for k in env_vars.keys() 
                                                 if any(s in k.lower() for s in sensitive_keys)]),
                        'environment_variables': filtered_env
                    }
            except Exception:
                env_info['error'] = 'Environment variables not accessible'
            
            return env_info
            
        except Exception as e:
            logger.debug(f'Failed to get environment info: {e}')
            return {'error': str(e)}
    
    def _get_tools_info(self) -> Dict[str, Any]:
        """Get installed tools and their configurations."""
        try:
            tools_info = {
                'global_tools': [],
                'tool_installations': {}
            }
            
            # This would require parsing global tool configuration
            # For now, return basic structure
            tools_info['note'] = 'Tool configuration requires admin access to global configuration'
            
            return tools_info
            
        except Exception as e:
            logger.debug(f'Failed to get tools info: {e}')
            return {'error': str(e)}
    
    async def analyze_system(self) -> SystemAnalysis:
        """Perform comprehensive system analysis."""
        try:
            # Get detailed server info first
            server_info = await self.get_server_info(detailed=True)
            
            analysis = SystemAnalysis(
                overall_health='Unknown',
                health_checks=[],
                security_audit={},
                resource_usage={},
                optimization_recommendations=[],
                plugin_analysis={}
            )
            
            # Perform health checks
            analysis.health_checks = self._perform_health_checks(server_info)
            
            # Determine overall health
            failed_checks = [check for check in analysis.health_checks if check.get('status') == 'FAILED']
            warning_checks = [check for check in analysis.health_checks if check.get('status') == 'WARNING']
            
            if failed_checks:
                analysis.overall_health = 'CRITICAL'
            elif warning_checks:
                analysis.overall_health = 'WARNING'
            else:
                analysis.overall_health = 'HEALTHY'
            
            # Security audit
            analysis.security_audit = self._perform_security_audit(server_info)
            
            # Resource usage analysis
            analysis.resource_usage = self._analyze_resource_usage(server_info)
            
            # Plugin analysis
            analysis.plugin_analysis = self._analyze_plugins(server_info)
            
            # Generate optimization recommendations
            analysis.optimization_recommendations = self._generate_optimization_recommendations(
                server_info, analysis
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f'Failed to analyze system: {e}')
            return SystemAnalysis(
                overall_health='ERROR',
                health_checks=[{'name': 'System Analysis', 'status': 'FAILED', 'message': str(e)}]
            )
    
    def _perform_health_checks(self, server_info: JenkinsServerInfo) -> List[Dict[str, Any]]:
        """Perform various health checks."""
        checks = []
        
        # Version check
        if server_info.version_details:
            version = server_info.version_details.get('core_version', '')
            if version and version != 'Unknown':
                checks.append({
                    'name': 'Jenkins Version',
                    'status': 'PASSED',
                    'message': f'Jenkins version {version} detected',
                    'details': server_info.version_details
                })
            else:
                checks.append({
                    'name': 'Jenkins Version',
                    'status': 'WARNING',
                    'message': 'Could not determine Jenkins version'
                })
        
        # Node health check
        if server_info.node_info:
            total_nodes = server_info.node_info.get('total_nodes', 0)
            online_nodes = server_info.node_info.get('online_nodes', 0)
            
            if total_nodes > 0:
                online_percentage = (online_nodes / total_nodes) * 100
                if online_percentage >= 90:
                    status = 'PASSED'
                elif online_percentage >= 70:
                    status = 'WARNING'
                else:
                    status = 'FAILED'
                
                checks.append({
                    'name': 'Node Availability',
                    'status': status,
                    'message': f'{online_nodes}/{total_nodes} nodes online ({online_percentage:.1f}%)',
                    'details': server_info.node_info
                })
        
        # Plugin health check
        if server_info.plugin_info:
            total_plugins = server_info.plugin_info.get('total_plugins', 0)
            plugins_with_updates = server_info.plugin_info.get('plugins_with_updates', 0)
            
            if total_plugins > 0:
                update_percentage = (plugins_with_updates / total_plugins) * 100
                if update_percentage == 0:
                    status = 'PASSED'
                elif update_percentage <= 20:
                    status = 'WARNING'
                else:
                    status = 'FAILED'
                
                checks.append({
                    'name': 'Plugin Updates',
                    'status': status,
                    'message': f'{plugins_with_updates}/{total_plugins} plugins have updates ({update_percentage:.1f}%)',
                    'details': {'plugins_needing_updates': plugins_with_updates}
                })
        
        return checks
    
    def _perform_security_audit(self, server_info: JenkinsServerInfo) -> Dict[str, Any]:
        """Perform security audit."""
        audit = {
            'security_enabled': False,
            'recommendations': [],
            'findings': []
        }
        
        if server_info.security_config:
            security_configured = server_info.security_config.get('security_configured', False)
            audit['security_enabled'] = security_configured
            
            if not security_configured:
                audit['findings'].append({
                    'severity': 'HIGH',
                    'finding': 'Security not configured',
                    'recommendation': 'Enable security and configure authentication'
                })
        
        # Check for security-related plugins
        if server_info.plugin_info:
            security_plugins = []
            for plugin in server_info.plugin_info.get('plugins', []):
                plugin_name = plugin.get('short_name', '').lower()
                if any(sec_term in plugin_name for sec_term in ['security', 'auth', 'ldap', 'saml']):
                    security_plugins.append(plugin['short_name'])
            
            audit['security_plugins'] = security_plugins
            
            if not security_plugins:
                audit['recommendations'].append(
                    'Consider installing security-related plugins for enhanced authentication'
                )
        
        return audit
    
    def _analyze_resource_usage(self, server_info: JenkinsServerInfo) -> Dict[str, Any]:
        """Analyze resource usage."""
        usage = {
            'executor_utilization': 0,
            'node_distribution': {},
            'recommendations': []
        }
        
        if server_info.node_info:
            total_executors = server_info.node_info.get('total_executors', 0)
            busy_executors = server_info.node_info.get('busy_executors', 0)
            
            if total_executors > 0:
                utilization = (busy_executors / total_executors) * 100
                usage['executor_utilization'] = utilization
                
                if utilization > 80:
                    usage['recommendations'].append(
                        'High executor utilization detected. Consider adding more nodes or executors.'
                    )
                elif utilization < 20:
                    usage['recommendations'].append(
                        'Low executor utilization. Consider reducing the number of executors to save resources.'
                    )
        
        return usage
    
    def _analyze_plugins(self, server_info: JenkinsServerInfo) -> Dict[str, Any]:
        """Analyze plugin ecosystem."""
        analysis = {
            'plugin_health': 'Unknown',
            'outdated_plugins': [],
            'recommendations': []
        }
        
        if server_info.plugin_info:
            total_plugins = server_info.plugin_info.get('total_plugins', 0)
            plugins_with_updates = server_info.plugin_info.get('plugins_with_updates', 0)
            
            if total_plugins > 0:
                update_ratio = plugins_with_updates / total_plugins
                
                if update_ratio <= 0.1:
                    analysis['plugin_health'] = 'GOOD'
                elif update_ratio <= 0.3:
                    analysis['plugin_health'] = 'FAIR'
                else:
                    analysis['plugin_health'] = 'POOR'
                
                # Get outdated plugins
                for plugin in server_info.plugin_info.get('plugins', []):
                    if plugin.get('has_update'):
                        analysis['outdated_plugins'].append({
                            'name': plugin.get('short_name'),
                            'current_version': plugin.get('version'),
                            'enabled': plugin.get('enabled')
                        })
                
                if plugins_with_updates > 0:
                    analysis['recommendations'].append(
                        f'Update {plugins_with_updates} outdated plugins to improve security and functionality'
                    )
        
        return analysis
    
    def _generate_optimization_recommendations(
        self, 
        server_info: JenkinsServerInfo, 
        analysis: SystemAnalysis
    ) -> List[str]:
        """Generate system optimization recommendations."""
        recommendations = []
        
        # Based on health checks
        failed_checks = [check for check in analysis.health_checks if check.get('status') == 'FAILED']
        if failed_checks:
            recommendations.append('Address failed health checks to improve system stability')
        
        # Based on resource usage
        if analysis.resource_usage.get('executor_utilization', 0) > 80:
            recommendations.append('Consider scaling out with additional Jenkins nodes')
        
        # Based on plugin analysis
        if analysis.plugin_analysis.get('plugin_health') == 'POOR':
            recommendations.append('Update outdated plugins to improve security and performance')
        
        # Based on security audit
        if not analysis.security_audit.get('security_enabled'):
            recommendations.append('Enable Jenkins security to protect your CI/CD environment')
        
        # General recommendations
        if server_info.version_details and not server_info.version_details.get('is_lts'):
            recommendations.append('Consider using Jenkins LTS version for better stability')
        
        return recommendations
    

    
    async def get_queue_info(self) -> List[QueueItemInfo]:
        """Get Jenkins build queue information."""
        try:
            cache_key = 'queue_info'
            
            return await self.get_cached_or_fetch(
                cache_key=cache_key,
                fetch_func=self._fetch_queue_info,
                cache_type='general',
            )
            
        except Exception as e:
            raise self._handle_jenkins_exception(e, 'Get queue info')
    
    def _fetch_queue_info(self) -> List[QueueItemInfo]:
        """Fetch queue information from Jenkins API."""
        try:
            queue_info = self.jenkins_client.get_queue_info()
            
            queue_items = []
            for item in queue_info:
                queue_item = QueueItemInfo(
                    id=item.get('id', 0),
                    task_name=item.get('task', {}).get('name', 'Unknown'),
                    url=item.get('url'),
                    why=item.get('why'),
                    blocked=item.get('blocked', False),
                    buildable=item.get('buildable', True),
                    stuck=item.get('stuck', False),
                    in_quiet_period=item.get('inQueueSince', 0) > 0,
                    pending=item.get('pending', False),
                    params=item.get('params'),
                    buildable_start_milliseconds=item.get('buildableStartMilliseconds'),
                    waiting_start_milliseconds=item.get('waitingStartMilliseconds'),
                )
                queue_items.append(queue_item)
            
            return queue_items
            
        except Exception as e:
            logger.error(f'Failed to fetch queue info: {e}')
            raise
    async def get_system_info(self) -> 'SystemInfo':
        """Get comprehensive system information.
        
        Returns:
            SystemInfo with detailed system information
        """
        try:
            from jenkins_mcp_server.models import SystemInfo
            
            # Get basic server info first
            server_info = await self.get_server_info(detailed=True)
            
            # Extract system information from various sources
            jvm_info = server_info.jvm_info or {}
            environment_info = server_info.environment_info or {}
            
            return SystemInfo(
                jenkins_version=server_info.version,
                java_version=jvm_info.get('java_version', 'Unknown'),
                java_vendor=jvm_info.get('java_vendor', 'Unknown'),
                java_vm_name=jvm_info.get('java_vm_name', 'Unknown'),
                java_vm_version=jvm_info.get('java_vm_version', 'Unknown'),
                os_name=jvm_info.get('os_name', 'Unknown'),
                os_version=jvm_info.get('os_version', 'Unknown'),
                os_arch=jvm_info.get('os_arch', 'Unknown'),
                system_properties=jvm_info.get('system_properties', {}),
                environment_variables=environment_info.get('filtered_env_vars', {}),
                memory_info=jvm_info.get('memory_info', {}),
                disk_usage=jvm_info.get('disk_usage', {}),
                uptime=jvm_info.get('uptime'),
                load_statistics=jvm_info.get('load_statistics', {})
            )
            
        except Exception as e:
            logger.error(f'Failed to get system info: {e}')
            raise self._handle_jenkins_exception(e, 'Get system info')
