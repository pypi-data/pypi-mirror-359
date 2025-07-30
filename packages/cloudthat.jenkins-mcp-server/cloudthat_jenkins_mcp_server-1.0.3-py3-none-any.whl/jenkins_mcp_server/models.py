"""Data models for Jenkins MCP Server.

This module defines all Pydantic models used throughout the Jenkins MCP server,
providing type safety and validation for Jenkins resources and operations.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator, ConfigDict


class JobStatus(str, Enum):
    """Jenkins job status enumeration."""
    
    SUCCESS = 'SUCCESS'
    FAILURE = 'FAILURE'
    UNSTABLE = 'UNSTABLE'
    ABORTED = 'ABORTED'
    NOT_BUILT = 'NOT_BUILT'
    RUNNING = 'RUNNING'
    QUEUED = 'QUEUED'
    UNKNOWN = 'UNKNOWN'


class JobType(str, Enum):
    """Jenkins job type enumeration."""
    
    FREESTYLE = 'freestyle'
    PIPELINE = 'pipeline'
    MULTIBRANCH_PIPELINE = 'multibranch_pipeline'
    FOLDER = 'folder'
    ORGANIZATION_FOLDER = 'organization_folder'
    UNKNOWN = 'unknown'


class BuildResult(str, Enum):
    """Jenkins build result enumeration."""
    
    SUCCESS = 'SUCCESS'
    FAILURE = 'FAILURE'
    UNSTABLE = 'UNSTABLE'
    ABORTED = 'ABORTED'
    NOT_BUILT = 'NOT_BUILT'


class QueueItemState(str, Enum):
    """Jenkins queue item state enumeration."""
    
    WAITING = 'waiting'
    BLOCKED = 'blocked'
    BUILDABLE = 'buildable'
    PENDING = 'pending'
    LEFT = 'left'


class JobInfo(BaseModel):
    """Jenkins job information model.
    
    Represents comprehensive information about a Jenkins job,
    including metadata, configuration, and build history.
    """
    
    name: str = Field(description='Job name')
    url: str = Field(description='Job URL')
    full_name: str = Field(description='Full job name including folder path')
    display_name: Optional[str] = Field(None, description='Display name')
    description: Optional[str] = Field(None, description='Job description')
    job_type: JobType = Field(JobType.UNKNOWN, description='Job type')
    buildable: bool = Field(True, description='Whether job can be built')
    color: Optional[str] = Field(None, description='Job status color')
    in_queue: bool = Field(False, description='Whether job is in build queue')
    keep_dependencies: bool = Field(False, description='Whether to keep dependencies')
    next_build_number: int = Field(1, description='Next build number')
    concurrent_build: bool = Field(False, description='Whether concurrent builds allowed')
    disabled: bool = Field(False, description='Whether job is disabled')
    last_build: Optional[Dict[str, Any]] = Field(None, description='Last build information')
    last_completed_build: Optional[Dict[str, Any]] = Field(None, description='Last completed build')
    last_failed_build: Optional[Dict[str, Any]] = Field(None, description='Last failed build')
    last_stable_build: Optional[Dict[str, Any]] = Field(None, description='Last stable build')
    last_successful_build: Optional[Dict[str, Any]] = Field(None, description='Last successful build')
    last_unstable_build: Optional[Dict[str, Any]] = Field(None, description='Last unstable build')
    last_unsuccessful_build: Optional[Dict[str, Any]] = Field(None, description='Last unsuccessful build')
    builds: List[Dict[str, Any]] = Field(default_factory=list, description='Recent builds')
    health_report: List[Dict[str, Any]] = Field(default_factory=list, description='Health reports')
    parameters: List[Dict[str, Any]] = Field(default_factory=list, description='Job parameters')
    scm_info: Optional[Dict[str, Any]] = Field(None, description='SCM information')
    
    model_config = ConfigDict(use_enum_values=True)


class BuildInfo(BaseModel):
    """Jenkins build information model.
    
    Represents comprehensive information about a Jenkins build,
    including status, artifacts, and execution details.
    """
    
    number: int = Field(description='Build number')
    url: str = Field(description='Build URL')
    job_name: str = Field(description='Job name')
    display_name: Optional[str] = Field(None, description='Build display name')
    description: Optional[str] = Field(None, description='Build description')
    result: Optional[BuildResult] = Field(None, description='Build result')
    building: bool = Field(False, description='Whether build is currently running')
    duration: Optional[int] = Field(None, description='Build duration in milliseconds')
    estimated_duration: Optional[int] = Field(None, description='Estimated duration in milliseconds')
    timestamp: Optional[datetime] = Field(None, description='Build start timestamp')
    built_on: Optional[str] = Field(None, description='Node where build was executed')
    change_set: List[Dict[str, Any]] = Field(default_factory=list, description='SCM changes')
    culprits: List[Dict[str, Any]] = Field(default_factory=list, description='Build culprits')
    artifacts: List[Dict[str, Any]] = Field(default_factory=list, description='Build artifacts')
    test_report: Optional[Dict[str, Any]] = Field(None, description='Test results')
    console_output_url: Optional[str] = Field(None, description='Console output URL')
    parameters: List[Dict[str, Any]] = Field(default_factory=list, description='Build parameters')
    causes: List[Dict[str, Any]] = Field(default_factory=list, description='Build causes')
    
    model_config = ConfigDict(use_enum_values=True)


class FolderInfo(BaseModel):
    """Jenkins folder information model.
    
    Represents information about a Jenkins folder,
    including contained jobs and subfolders.
    """
    
    name: str = Field(description='Folder name')
    url: str = Field(description='Folder URL')
    full_name: str = Field(description='Full folder path')
    display_name: Optional[str] = Field(None, description='Display name')
    description: Optional[str] = Field(None, description='Folder description')
    jobs: List[Dict[str, Any]] = Field(default_factory=list, description='Jobs in folder')
    views: List[Dict[str, Any]] = Field(default_factory=list, description='Views in folder')
    health_report: List[Dict[str, Any]] = Field(default_factory=list, description='Health reports')


class MultiBranchPipelineInfo(BaseModel):
    """Multi-branch pipeline information model.
    
    Represents information about a Jenkins multi-branch pipeline,
    including branch details and scan results.
    """
    
    name: str = Field(description='Pipeline name')
    url: str = Field(description='Pipeline URL')
    full_name: str = Field(description='Full pipeline path')
    display_name: Optional[str] = Field(None, description='Display name')
    description: Optional[str] = Field(None, description='Pipeline description')
    branches: List[Dict[str, Any]] = Field(default_factory=list, description='Pipeline branches')
    scan_result: Optional[Dict[str, Any]] = Field(None, description='Last scan result')
    scm_sources: List[Dict[str, Any]] = Field(default_factory=list, description='SCM sources')
    orphaned_items: List[Dict[str, Any]] = Field(default_factory=list, description='Orphaned items')


class BranchInfo(BaseModel):
    """Pipeline branch information model.
    
    Represents information about a specific branch
    in a multi-branch pipeline.
    """
    
    name: str = Field(description='Branch name')
    url: str = Field(description='Branch URL')
    display_name: Optional[str] = Field(None, description='Display name')
    buildable: bool = Field(True, description='Whether branch can be built')
    color: Optional[str] = Field(None, description='Branch status color')
    last_build: Optional[Dict[str, Any]] = Field(None, description='Last build information')
    last_completed_build: Optional[Dict[str, Any]] = Field(None, description='Last completed build')
    last_successful_build: Optional[Dict[str, Any]] = Field(None, description='Last successful build')
    health_report: List[Dict[str, Any]] = Field(default_factory=list, description='Health reports')


class QueueItemInfo(BaseModel):
    """Jenkins queue item information model.
    
    Represents information about an item in the Jenkins build queue.
    """
    
    id: int = Field(description='Queue item ID')
    task_name: str = Field(description='Task name')
    url: Optional[str] = Field(None, description='Queue item URL')
    why: Optional[str] = Field(None, description='Reason for queuing')
    blocked: bool = Field(False, description='Whether item is blocked')
    buildable: bool = Field(True, description='Whether item is buildable')
    stuck: bool = Field(False, description='Whether item is stuck')
    in_quiet_period: bool = Field(False, description='Whether in quiet period')
    pending: bool = Field(False, description='Whether item is pending')
    params: Optional[str] = Field(None, description='Build parameters')
    buildable_start_milliseconds: Optional[int] = Field(None, description='Buildable start time')
    waiting_start_milliseconds: Optional[int] = Field(None, description='Waiting start time')


class NodeInfo(BaseModel):
    """Jenkins node information model.
    
    Represents information about a Jenkins build node/agent.
    """
    
    name: str = Field(description='Node name')
    url: str = Field(description='Node URL')
    display_name: Optional[str] = Field(None, description='Display name')
    description: Optional[str] = Field(None, description='Node description')
    num_executors: int = Field(0, description='Number of executors')
    mode: Optional[str] = Field(None, description='Node mode')
    node_properties: List[Dict[str, Any]] = Field(default_factory=list, description='Node properties')
    offline: bool = Field(False, description='Whether node is offline')
    offline_cause: Optional[str] = Field(None, description='Offline cause')
    offline_cause_reason: Optional[str] = Field(None, description='Offline cause reason')
    temporarily_offline: bool = Field(False, description='Whether temporarily offline')
    idle: bool = Field(True, description='Whether node is idle')
    launch_supported: bool = Field(True, description='Whether launch is supported')
    manual_launch_allowed: bool = Field(True, description='Whether manual launch allowed')
    monitor_data: Dict[str, Any] = Field(default_factory=dict, description='Monitor data')


class PipelineDefinition(BaseModel):
    """Pipeline definition model.
    
    Represents a Jenkins pipeline definition with script and configuration.
    """
    
    name: str = Field(description='Pipeline name')
    pipeline_type: str = Field(default='unknown', description='Pipeline type (declarative/scripted)')
    script: str = Field(description='Pipeline script (Jenkinsfile content)')
    description: Optional[str] = Field(None, description='Pipeline description')
    parameters: List[Dict[str, Any]] = Field(default_factory=list, description='Pipeline parameters')
    triggers: List[Dict[str, Any]] = Field(default_factory=list, description='Pipeline triggers')
    properties: List[Dict[str, Any]] = Field(default_factory=list, description='Pipeline properties')
    scm_config: Optional[Dict[str, Any]] = Field(None, description='SCM configuration')
    folder_path: Optional[str] = Field(None, description='Target folder path')


class BuildTriggerResult(BaseModel):
    """Build trigger result model.
    
    Represents the result of triggering a Jenkins build.
    """
    
    job_name: str = Field(description='Job name')
    queue_item_id: Optional[int] = Field(None, description='Queue item ID')
    queue_item_url: Optional[str] = Field(None, description='Queue item URL')
    build_number: Optional[int] = Field(None, description='Build number if available')
    build_url: Optional[str] = Field(None, description='Build URL if available')
    triggered: bool = Field(description='Whether trigger was successful')
    message: str = Field(description='Result message')
    parameters: Dict[str, Any] = Field(default_factory=dict, description='Build parameters used')


class PipelineDeploymentResult(BaseModel):
    """Pipeline deployment result model.
    
    Represents the result of deploying a pipeline to Jenkins.
    """
    
    pipeline_name: str = Field(description='Pipeline name')
    created: bool = Field(description='Whether pipeline was created (vs updated)')
    job_url: str = Field(description='Job URL')
    config_xml: Optional[str] = Field(None, description='Generated config XML')
    message: str = Field(description='Deployment message')
    warnings: List[str] = Field(default_factory=list, description='Deployment warnings')
    validation_result: Optional[Dict[str, Any]] = Field(None, description='Pipeline validation result')
    shared_libraries: List[str] = Field(default_factory=list, description='Shared libraries used')
    pipeline_type: str = Field(default='unknown', description='Pipeline type (declarative/scripted)')
    
    @property
    def name(self) -> str:
        """Compatibility property for tests that expect 'name' field."""
        return self.pipeline_name


class JenkinsServerInfo(BaseModel):
    """Jenkins server information model.
    
    Represents comprehensive information about the Jenkins server instance.
    """
    
    version: str = Field(description='Jenkins version')
    url: str = Field(description='Jenkins URL')
    # Enhanced fields for comprehensive server info
    version_details: Optional[Dict[str, Any]] = Field(None, description='Detailed version information')
    system_health: Optional[Dict[str, Any]] = Field(None, description='System health indicators')
    jvm_info: Optional[Dict[str, Any]] = Field(None, description='JVM statistics and configuration')
    node_info: Optional[Dict[str, Any]] = Field(None, description='Node details and statistics')
    security_config: Optional[Dict[str, Any]] = Field(None, description='Security configuration')
    global_config: Optional[Dict[str, Any]] = Field(None, description='Global configuration settings')
    plugin_info: Optional[Dict[str, Any]] = Field(None, description='Plugin inventory and status')
    environment_info: Optional[Dict[str, Any]] = Field(None, description='System environment variables')
    tools_info: Optional[Dict[str, Any]] = Field(None, description='Installed tools configuration')


class BuildAnalytics(BaseModel):
    """Build analytics and performance model."""
    
    job_name: str = Field(description='Job name')
    total_builds: int = Field(description='Total number of builds')
    success_rate: float = Field(description='Success rate percentage')
    average_duration: float = Field(description='Average build duration in seconds')
    recent_performance: List[Dict[str, Any]] = Field(default_factory=list, description='Recent build performance')
    bottlenecks: List[str] = Field(default_factory=list, description='Identified bottlenecks')
    optimization_suggestions: List[str] = Field(default_factory=list, description='Optimization suggestions')


class SystemAnalysis(BaseModel):
    """System analysis and health check model."""
    
    overall_health: str = Field(description='Overall system health status')
    health_checks: List[Dict[str, Any]] = Field(default_factory=list, description='Individual health check results')
    security_audit: Dict[str, Any] = Field(default_factory=dict, description='Security audit results')
    resource_usage: Dict[str, Any] = Field(default_factory=dict, description='Resource usage analysis')
    optimization_recommendations: List[str] = Field(default_factory=list, description='System optimization recommendations')
    plugin_analysis: Dict[str, Any] = Field(default_factory=dict, description='Plugin ecosystem analysis')


class BuildOperation(BaseModel):
    """Build operation result model."""
    
    operation: str = Field(description='Operation performed')
    job_name: str = Field(description='Job name')
    build_number: Optional[int] = Field(None, description='Build number')
    success: bool = Field(description='Operation success status')
    message: str = Field(description='Operation result message')
    details: Optional[Dict[str, Any]] = Field(None, description='Additional operation details')
    mode: Optional[str] = Field(None, description='Server mode')
    node_name: Optional[str] = Field(None, description='Master node name')
    node_description: Optional[str] = Field(None, description='Master node description')
    num_executors: int = Field(0, description='Number of executors on master')
    use_crumbs: bool = Field(False, description='Whether CSRF protection is enabled')
    use_security: bool = Field(False, description='Whether security is enabled')
    views: List[Dict[str, Any]] = Field(default_factory=list, description='Available views')
    jobs: List[Dict[str, Any]] = Field(default_factory=list, description='Top-level jobs')
    queue: List[Dict[str, Any]] = Field(default_factory=list, description='Build queue')
    computer: List[Dict[str, Any]] = Field(default_factory=list, description='Computer information')


class PluginInfo(BaseModel):
    """Jenkins plugin information model.
    
    Represents information about an installed Jenkins plugin.
    """
    
    short_name: str = Field(description='Plugin short name')
    long_name: str = Field(description='Plugin long name')
    version: str = Field(description='Plugin version')
    url: Optional[str] = Field(None, description='Plugin URL')
    active: bool = Field(True, description='Whether plugin is active')
    enabled: bool = Field(True, description='Whether plugin is enabled')
    bundled: bool = Field(False, description='Whether plugin is bundled')
    deleted: bool = Field(False, description='Whether plugin is deleted')
    dependencies: List[Dict[str, Any]] = Field(default_factory=list, description='Plugin dependencies')
    optional_dependencies: List[Dict[str, Any]] = Field(default_factory=list, description='Optional dependencies')
    supports_dynamic_load: bool = Field(False, description='Whether supports dynamic loading')
    has_update: bool = Field(False, description='Whether update is available')
    backup_version: Optional[str] = Field(None, description='Backup version')


class SecurityRealmInfo(BaseModel):
    """Jenkins security realm information model.
    
    Represents information about Jenkins security configuration.
    """
    
    class_name: str = Field(description='Security realm class name')
    allows_signup: bool = Field(False, description='Whether signup is allowed')
    security_components: List[str] = Field(default_factory=list, description='Security components')
    login_url: Optional[str] = Field(None, description='Login URL')
    help_url: Optional[str] = Field(None, description='Help URL')


class AuthorizationStrategyInfo(BaseModel):
    """Jenkins authorization strategy information model.
    
    Represents information about Jenkins authorization configuration.
    """
    
    class_name: str = Field(description='Authorization strategy class name')
    root_url: Optional[str] = Field(None, description='Root URL')
    permissions: List[str] = Field(default_factory=list, description='Available permissions')


class SystemInfo(BaseModel):
    """Jenkins system information model.
    
    Represents comprehensive system information about Jenkins.
    """
    
    jenkins_version: str = Field(description='Jenkins version')
    java_version: str = Field(default='Unknown', description='Java version')
    java_vendor: str = Field(default='Unknown', description='Java vendor')
    java_vm_name: str = Field(default='Unknown', description='Java VM name')
    java_vm_version: str = Field(default='Unknown', description='Java VM version')
    os_name: str = Field(default='Unknown', description='Operating system name')
    os_version: str = Field(default='Unknown', description='Operating system version')
    os_arch: str = Field(default='Unknown', description='Operating system architecture')
    system_properties: Dict[str, str] = Field(default_factory=dict, description='System properties')
    environment_variables: Dict[str, str] = Field(default_factory=dict, description='Environment variables')
    memory_info: Dict[str, Any] = Field(default_factory=dict, description='Memory information')
    disk_usage: Dict[str, Any] = Field(default_factory=dict, description='Disk usage information')
    uptime: Optional[int] = Field(None, description='System uptime in milliseconds')
    load_statistics: Dict[str, Any] = Field(default_factory=dict, description='Load statistics')


# Response models for MCP tools
class ContentItem(BaseModel):
    """MCP content item model."""
    
    type: str = Field(description='Content type')
    text: str = Field(description='Content text')


class McpResponse(BaseModel):
    """MCP response model."""
    
    content: List[ContentItem] = Field(description='Response content')
    is_error: bool = Field(False, description='Whether response is an error')
    
    model_config = ConfigDict(
        alias_generator=lambda field_name: field_name.replace('_', ''),
        populate_by_name=True
    )
