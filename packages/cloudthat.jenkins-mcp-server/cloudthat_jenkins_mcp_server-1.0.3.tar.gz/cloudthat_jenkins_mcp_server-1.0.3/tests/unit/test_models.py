"""Unit tests for Jenkins MCP Server data models.

This module provides comprehensive test coverage for all Pydantic models
used throughout the Jenkins MCP Server. Tests ensure proper validation,
serialization, type safety, and edge case handling.

Test Categories:
- Model validation with required and optional fields
- Enum value validation and serialization
- Edge cases with empty/null values
- JSON serialization and deserialization
- Field constraint validation
- Model inheritance and composition

All tests follow pytest conventions and include descriptive docstrings
for maintainability and debugging purposes.
"""

import pytest
from datetime import datetime
from typing import Dict, Any

from jenkins_mcp_server.models import (
    JobInfo,
    JobType,
    JobStatus,
    BuildInfo,
    BuildResult,
    BuildTriggerResult,
    PipelineDefinition,
    PipelineDeploymentResult,
    JenkinsServerInfo,
    QueueItemInfo,
    QueueItemState,
    SystemInfo,
    BuildAnalytics,
    NodeInfo,
    PluginInfo,
    ContentItem,
    McpResponse,
)


@pytest.mark.unit
class TestJobModels:
    """Test cases for job-related models."""

    def test_job_info_model_minimal(self):
        """Test JobInfo model with minimal required fields."""
        job = JobInfo(
            name='test-job',
            url='http://jenkins/job/test-job/',
            full_name='test-job'
        )
        
        assert job.name == 'test-job'
        assert job.url == 'http://jenkins/job/test-job/'
        assert job.full_name == 'test-job'
        assert job.job_type == JobType.UNKNOWN
        assert job.buildable is True
        assert job.disabled is False

    def test_job_info_model_complete(self):
        """Test JobInfo model with all fields populated."""
        job = JobInfo(
            name='test-job',
            url='http://jenkins/job/test-job/',
            full_name='folder/test-job',
            display_name='Test Job',
            description='A test job for validation',
            job_type=JobType.FREESTYLE,
            buildable=True,
            color='blue',
            in_queue=False,
            keep_dependencies=False,
            next_build_number=5,
            concurrent_build=True,
            disabled=False,
            last_build={'number': 4, 'url': 'http://jenkins/job/test-job/4/'},
            builds=[
                {'number': 4, 'url': 'http://jenkins/job/test-job/4/'},
                {'number': 3, 'url': 'http://jenkins/job/test-job/3/'}
            ],
            parameters=[
                {'name': 'BRANCH', 'type': 'string', 'defaultValue': 'main'}
            ]
        )
        
        assert job.name == 'test-job'
        assert job.full_name == 'folder/test-job'
        assert job.display_name == 'Test Job'
        assert job.description == 'A test job for validation'
        assert job.job_type == JobType.FREESTYLE
        assert job.next_build_number == 5
        assert job.concurrent_build is True
        assert len(job.builds) == 2
        assert len(job.parameters) == 1

    def test_job_info_model_validation_error(self):
        """Test JobInfo model validation errors."""
        # Missing required fields
        with pytest.raises(ValueError):
            JobInfo(name='test-job')  # Missing url and full_name

    def test_job_type_enum_values(self):
        """Test JobType enum values."""
        assert JobType.FREESTYLE == 'freestyle'
        assert JobType.PIPELINE == 'pipeline'
        assert JobType.MULTIBRANCH_PIPELINE == 'multibranch_pipeline'
        assert JobType.FOLDER == 'folder'
        assert JobType.UNKNOWN == 'unknown'

    def test_job_status_enum_values(self):
        """Test JobStatus enum values."""
        assert JobStatus.SUCCESS == 'SUCCESS'
        assert JobStatus.FAILURE == 'FAILURE'
        assert JobStatus.UNSTABLE == 'UNSTABLE'
        assert JobStatus.ABORTED == 'ABORTED'
        assert JobStatus.RUNNING == 'RUNNING'


@pytest.mark.unit
class TestBuildModels:
    """Test cases for build-related models."""

    def test_build_info_model_minimal(self):
        """Test BuildInfo model with minimal required fields."""
        build = BuildInfo(
            number=42,
            url='http://jenkins/job/test-job/42/',
            job_name='test-job'
        )
        
        assert build.number == 42
        assert build.url == 'http://jenkins/job/test-job/42/'
        assert build.job_name == 'test-job'
        assert build.building is False
        assert build.result is None

    def test_build_info_model_complete(self):
        """Test BuildInfo model with all fields populated."""
        build = BuildInfo(
            number=42,
            url='http://jenkins/job/test-job/42/',
            job_name='test-job',
            display_name='#42',
            description='Test build',
            result=BuildResult.SUCCESS,
            building=False,
            duration=120000,  # 2 minutes in milliseconds
            estimated_duration=150000,
            timestamp=datetime.now(),
            built_on='jenkins-agent-1',
            change_set=[
                {'commitId': 'abc123', 'author': 'developer', 'msg': 'Fix bug'}
            ],
            artifacts=[
                {'fileName': 'app.jar', 'relativePath': 'target/app.jar'}
            ],
            parameters=[
                {'name': 'BRANCH', 'value': 'main'}
            ]
        )
        
        assert build.number == 42
        assert build.job_name == 'test-job'
        assert build.result == BuildResult.SUCCESS
        assert build.duration == 120000
        assert build.built_on == 'jenkins-agent-1'
        assert len(build.change_set) == 1
        assert len(build.artifacts) == 1
        assert len(build.parameters) == 1

    def test_build_result_enum_values(self):
        """Test BuildResult enum values."""
        assert BuildResult.SUCCESS == 'SUCCESS'
        assert BuildResult.FAILURE == 'FAILURE'
        assert BuildResult.UNSTABLE == 'UNSTABLE'
        assert BuildResult.ABORTED == 'ABORTED'
        assert BuildResult.NOT_BUILT == 'NOT_BUILT'

    def test_build_trigger_result_model(self):
        """Test BuildTriggerResult model."""
        result = BuildTriggerResult(
            job_name='test-job',
            triggered=True,
            queue_item_id=123,
            queue_item_url='http://jenkins/queue/item/123/',
            build_number=42,
            build_url='http://jenkins/job/test-job/42/',
            message='Build triggered successfully',
            parameters={'BRANCH': 'main'}
        )
        
        assert result.job_name == 'test-job'
        assert result.triggered is True
        assert result.queue_item_id == 123
        assert result.build_number == 42
        assert result.message == 'Build triggered successfully'
        assert result.parameters == {'BRANCH': 'main'}


@pytest.mark.unit
class TestPipelineModels:
    """Test cases for pipeline-related models."""

    def test_pipeline_definition_model(self):
        """Test PipelineDefinition model."""
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
        
        pipeline = PipelineDefinition(
            name='test-pipeline',
            script=pipeline_script,
            description='Test pipeline',
            pipeline_type='declarative',
            parameters=[
                {'name': 'BRANCH', 'type': 'string', 'defaultValue': 'main'}
            ]
        )
        
        assert pipeline.name == 'test-pipeline'
        assert 'pipeline {' in pipeline.script
        assert pipeline.description == 'Test pipeline'
        assert pipeline.pipeline_type == 'declarative'
        assert len(pipeline.parameters) == 1

    def test_pipeline_deployment_result_model(self):
        """Test PipelineDeploymentResult model."""
        result = PipelineDeploymentResult(
            pipeline_name='test-pipeline',
            created=True,
            job_url='http://jenkins/job/test-pipeline/',
            message='Pipeline created successfully',
            config_xml='<xml>...</xml>',
            validation_results={
                'syntax_valid': True,
                'warnings': [],
                'errors': []
            },
            shared_libraries=[],
            pipeline_type='declarative'
        )
        
        assert result.pipeline_name == 'test-pipeline'
        assert result.created is True
        assert result.job_url == 'http://jenkins/job/test-pipeline/'
        assert result.message == 'Pipeline created successfully'
        assert result.pipeline_type == 'declarative'


@pytest.mark.unit
class TestSystemModels:
    """Test cases for system-related models."""

    def test_jenkins_server_info_model(self):
        """Test JenkinsServerInfo model."""
        server_info = JenkinsServerInfo(
            version='2.401.3',
            url='http://jenkins:8080',
            version_details={
                'version': '2.401.3',
                'build_date': '2023-08-15'
            },
            system_health={
                'status': 'healthy',
                'uptime': 86400
            }
        )
        
        assert server_info.version == '2.401.3'
        assert server_info.url == 'http://jenkins:8080'
        assert server_info.version_details['version'] == '2.401.3'
        assert server_info.system_health['status'] == 'healthy'

    def test_queue_item_info_model(self):
        """Test QueueItemInfo model."""
        queue_item = QueueItemInfo(
            id=123,
            task_name='test-job',
            url='http://jenkins/queue/item/123/',
            why='Waiting for next available executor',
            blocked=False,
            buildable=True,
            stuck=False,
            in_quiet_period=False,
            pending=True
        )
        
        assert queue_item.id == 123
        assert queue_item.task_name == 'test-job'
        assert queue_item.why == 'Waiting for next available executor'
        assert queue_item.blocked is False
        assert queue_item.buildable is True

    def test_queue_item_state_enum_values(self):
        """Test QueueItemState enum values."""
        assert QueueItemState.WAITING == 'waiting'
        assert QueueItemState.BLOCKED == 'blocked'
        assert QueueItemState.BUILDABLE == 'buildable'
        assert QueueItemState.PENDING == 'pending'
        assert QueueItemState.LEFT == 'left'

    def test_system_info_model(self):
        """Test SystemInfo model."""
        system_info = SystemInfo(
            jenkins_version='2.401.3',
            java_version='17.0.8',
            java_vendor='Eclipse Adoptium',
            java_vm_name='OpenJDK 64-Bit Server VM',
            java_vm_version='17.0.8+7',
            os_name='Linux',
            os_version='5.4.0-74-generic',
            os_arch='amd64'
        )
        
        assert system_info.jenkins_version == '2.401.3'
        assert system_info.java_version == '17.0.8'
        assert system_info.os_name == 'Linux'


@pytest.mark.unit
class TestUtilityModels:
    """Test cases for utility models."""

    def test_content_item_model(self):
        """Test ContentItem model."""
        content = ContentItem(
            type='text',
            text='Sample content'
        )
        
        assert content.type == 'text'
        assert content.text == 'Sample content'

    def test_mcp_response_model(self):
        """Test McpResponse model."""
        response = McpResponse(
            content=[
                ContentItem(type='text', text='Response content')
            ]
        )
        
        assert len(response.content) == 1
        assert response.content[0].type == 'text'
        assert response.content[0].text == 'Response content'

    def test_node_info_model(self):
        """Test NodeInfo model."""
        node = NodeInfo(
            name='jenkins-agent-1',
            url='http://jenkins:8080/computer/jenkins-agent-1/',  # Add required url field
            description='Jenkins build agent',
            num_executors=4,
            mode='NORMAL',
            idle=True,
            offline=False,
            temporarily_offline=False,
            offline_cause=None,
            launch_supported=True,
            manual_launch_allowed=True
        )
        
        assert node.name == 'jenkins-agent-1'
        assert node.description == 'Jenkins build agent'
        assert node.num_executors == 4
        assert node.idle is True
        assert node.offline is False

    def test_plugin_info_model(self):
        """Test PluginInfo model."""
        plugin = PluginInfo(
            short_name='git',
            long_name='Git Plugin',  # Add required long_name field
            version='4.8.3',
            enabled=True,
            active=True,
            has_update=False,
            url='https://plugins.jenkins.io/git/',
            dependencies=[  # Change to list of dicts as expected by model
                {'name': 'scm-api', 'version': '2.6.4'},
                {'name': 'workflow-scm-step', 'version': '2.13'}
            ]
        )
        
        assert plugin.short_name == 'git'
        assert plugin.long_name == 'Git Plugin'  # Update assertion
        assert plugin.version == '4.8.3'
        assert plugin.enabled is True
        assert len(plugin.dependencies) == 2


@pytest.mark.unit
class TestModelEdgeCases:
    """Test cases for model edge cases and validation."""

    def test_job_info_with_empty_lists(self):
        """Test JobInfo model with empty lists."""
        job = JobInfo(
            name='empty-job',
            url='http://jenkins/job/empty-job/',
            full_name='empty-job',
            builds=[],
            health_report=[],
            parameters=[]
        )
        
        assert len(job.builds) == 0
        assert len(job.health_report) == 0
        assert len(job.parameters) == 0

    def test_build_info_with_none_values(self):
        """Test BuildInfo model with None values."""
        build = BuildInfo(
            number=1,
            url='http://jenkins/job/test/1/',
            job_name='test',
            result=None,
            duration=None,
            timestamp=None,
            built_on=None
        )
        
        assert build.result is None
        assert build.duration is None
        assert build.timestamp is None
        assert build.built_on is None

    def test_model_serialization(self):
        """Test model serialization to dict."""
        job = JobInfo(
            name='test-job',
            url='http://jenkins/job/test-job/',
            full_name='test-job',
            job_type=JobType.FREESTYLE
        )
        
        job_dict = job.model_dump()
        assert isinstance(job_dict, dict)
        assert job_dict['name'] == 'test-job'
        assert job_dict['job_type'] == 'freestyle'  # Enum value

    def test_model_json_serialization(self):
        """Test model JSON serialization."""
        build = BuildInfo(
            number=1,
            url='http://jenkins/job/test/1/',
            job_name='test',
            result=BuildResult.SUCCESS
        )
        
        json_str = build.model_dump_json()
        assert isinstance(json_str, str)
        # Parse JSON and check values instead of string matching
        import json
        data = json.loads(json_str)
        assert data['number'] == 1
        assert data['result'] == 'SUCCESS'
