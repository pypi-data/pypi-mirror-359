"""Test configuration and fixtures for Jenkins MCP Server tests."""

import asyncio
import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any, List

# Test environment variables
TEST_JENKINS_URL = "http://test-jenkins:8080"
TEST_JENKINS_USERNAME = "test-user"
TEST_JENKINS_TOKEN = "test-token"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    env_vars = {
        'JENKINS_URL': TEST_JENKINS_URL,
        'JENKINS_USERNAME': TEST_JENKINS_USERNAME,
        'JENKINS_TOKEN': TEST_JENKINS_TOKEN,
        'JENKINS_TIMEOUT': '30',
    }
    
    with patch.dict(os.environ, env_vars, clear=False):
        yield env_vars


@pytest.fixture
def mock_jenkins_client():
    """Mock Jenkins client for testing."""
    client = MagicMock()
    
    # Mock basic methods
    client.get_info.return_value = {
        'version': '2.504.1',
        'url': TEST_JENKINS_URL,
        'quietPeriod': 5,
        'scmCheckoutRetryCount': 0,
        'slaveAgentPort': -1,
        'useCrumbs': True,
        'useSecurity': True,
    }
    
    client.get_jobs.return_value = [
        {'name': 'test-job-1', 'url': f'{TEST_JENKINS_URL}/job/test-job-1/', 'color': 'blue'},
        {'name': 'test-job-2', 'url': f'{TEST_JENKINS_URL}/job/test-job-2/', 'color': 'red'},
        {'name': 'test-folder', 'url': f'{TEST_JENKINS_URL}/job/test-folder/', 'color': 'notbuilt'},
    ]
    
    client.get_job_info.return_value = {
        'name': 'test-job-1',
        'url': f'{TEST_JENKINS_URL}/job/test-job-1/',
        'buildable': True,
        'color': 'blue',
        'description': 'Test job description',
        'lastBuild': {'number': 42, 'url': f'{TEST_JENKINS_URL}/job/test-job-1/42/'},
        'builds': [
            {'number': 42, 'url': f'{TEST_JENKINS_URL}/job/test-job-1/42/'},
            {'number': 41, 'url': f'{TEST_JENKINS_URL}/job/test-job-1/41/'},
        ]
    }
    
    client.get_build_info.return_value = {
        'number': 42,
        'url': f'{TEST_JENKINS_URL}/job/test-job-1/42/',
        'result': 'SUCCESS',
        'duration': 120000,  # 2 minutes in milliseconds
        'timestamp': 1640995200000,  # Unix timestamp
        'building': False,
        'description': 'Test build',
    }
    
    client.get_build_console_output.return_value = "Build log output\nBuild completed successfully"
    
    client.get_queue_info.return_value = []
    
    client.get_nodes.return_value = [
        {'name': 'master', 'offline': False},
        {'name': 'agent-1', 'offline': False},
    ]
    
    client.get_node_info.return_value = {
        'displayName': 'master',
        'numExecutors': 4,
        'offline': False,
        'executors': [
            {'currentExecutable': None},
            {'currentExecutable': {'url': f'{TEST_JENKINS_URL}/job/test-job-1/42/'}},
            {'currentExecutable': None},
            {'currentExecutable': None},
        ],
        'assignedLabels': [{'name': 'master'}],
        'description': 'Jenkins master node',
        'monitorData': {}
    }
    
    client.get_plugins.return_value = [
        {
            'shortName': 'git',
            'longName': 'Git plugin',
            'version': '4.8.3',
            'enabled': True,
            'active': True,
            'hasUpdate': False,
            'url': 'https://plugins.jenkins.io/git',
            'dependencies': []
        },
        {
            'shortName': 'pipeline-stage-view',
            'longName': 'Pipeline Stage View Plugin',
            'version': '2.25',
            'enabled': True,
            'active': True,
            'hasUpdate': True,
            'url': 'https://plugins.jenkins.io/pipeline-stage-view',
            'dependencies': []
        }
    ]
    
    # Mock job creation
    client.create_job.return_value = True
    client.reconfig_job.return_value = True
    client.delete_job.return_value = True
    
    # Mock build operations
    client.build_job.return_value = 123  # Queue item ID
    
    return client


@pytest.fixture
def sample_job_data():
    """Sample job data for testing."""
    return {
        'name': 'test-pipeline',
        'url': f'{TEST_JENKINS_URL}/job/test-pipeline/',
        'buildable': True,
        'color': 'blue',
        'description': 'Test pipeline job',
        '_class': 'org.jenkinsci.plugins.workflow.job.WorkflowJob',
        'lastBuild': {
            'number': 10,
            'url': f'{TEST_JENKINS_URL}/job/test-pipeline/10/'
        },
        'builds': [
            {'number': 10, 'url': f'{TEST_JENKINS_URL}/job/test-pipeline/10/'},
            {'number': 9, 'url': f'{TEST_JENKINS_URL}/job/test-pipeline/9/'},
        ]
    }


@pytest.fixture
def sample_build_data():
    """Sample build data for testing."""
    return {
        'number': 10,
        'url': f'{TEST_JENKINS_URL}/job/test-pipeline/10/',
        'result': 'SUCCESS',
        'duration': 300000,  # 5 minutes
        'timestamp': 1640995200000,
        'building': False,
        'description': 'Test build',
        'actions': [],
        'artifacts': [],
        'changeSet': {'items': []},
        'culprits': []
    }


@pytest.fixture
def sample_pipeline_script():
    """Sample pipeline script for testing."""
    return """
pipeline {
    agent any
    
    parameters {
        string(name: 'BRANCH', defaultValue: 'main', description: 'Branch to build')
        booleanParam(name: 'DEPLOY', defaultValue: false, description: 'Deploy after build')
    }
    
    stages {
        stage('Build') {
            steps {
                echo "Building branch: ${params.BRANCH}"
                sh 'make build'
            }
        }
        stage('Test') {
            steps {
                sh 'make test'
                publishTestResults testResultsPattern: 'test-results.xml'
            }
        }
        stage('Deploy') {
            when {
                params.DEPLOY == true
            }
            steps {
                sh 'make deploy'
            }
        }
    }
    
    post {
        always {
            archiveArtifacts artifacts: 'build/**/*', allowEmptyArchive: true
        }
        success {
            echo 'Pipeline succeeded!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}
"""


@pytest.fixture
def sample_scripted_pipeline():
    """Sample scripted pipeline for testing."""
    return """
node {
    try {
        stage('Checkout') {
            checkout scm
        }
        
        stage('Build') {
            sh 'npm install'
            sh 'npm run build'
        }
        
        stage('Test') {
            sh 'npm test'
        }
        
        stage('Deploy') {
            if (env.BRANCH_NAME == 'main') {
                sh 'npm run deploy'
            }
        }
    } catch (Exception e) {
        currentBuild.result = 'FAILURE'
        throw e
    } finally {
        archiveArtifacts artifacts: 'dist/**/*', allowEmptyArchive: true
    }
}
"""


@pytest.fixture
def invalid_pipeline_script():
    """Invalid pipeline script for testing validation."""
    return """
pipeline {
    agent any
    stages {
        stage('Build') {
            echo 'Missing steps block'
        }
    }
    // Missing closing brace
"""


@pytest.fixture
def mock_http_response():
    """Mock HTTP response for testing."""
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {'status': 'ok'}
    response.text = 'Success'
    response.headers = {'Content-Type': 'application/json'}
    return response


@pytest.fixture
def mock_system_info():
    """Mock system information for testing."""
    return {
        'systemProperties': {
            'java.version': '17.0.8',
            'java.vendor': 'Eclipse Adoptium',
            'java.home': '/opt/java/openjdk',
            'java.vm.name': 'OpenJDK 64-Bit Server VM',
            'java.vm.version': '17.0.8+7',
            'os.name': 'Linux',
            'os.arch': 'amd64',
            'os.version': '5.4.0-74-generic',
            'user.timezone': 'UTC',
            'file.encoding': 'UTF-8',
        },
        'envVars': {
            'JAVA_HOME': '/opt/java/openjdk',
            'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin',
            'JENKINS_HOME': '/var/jenkins_home',
            'JENKINS_SECRET': '[FILTERED]',
            'API_TOKEN': '[FILTERED]',
        }
    }


@pytest.fixture
def mock_crumb_response():
    """Mock CSRF crumb response."""
    return {
        'crumb': 'test-crumb-value',
        'crumbRequestField': 'Jenkins-Crumb'
    }


@pytest.fixture
def mock_validation_response():
    """Mock pipeline validation response."""
    return {
        'result': 'success',
        'errors': [],
        'warnings': ['Consider adding error handling']
    }


@pytest.fixture
def mock_build_analytics_data():
    """Mock build analytics data for testing."""
    return [
        {
            'number': 10,
            'result': 'SUCCESS',
            'duration': 300000,
            'timestamp': 1640995200000,
            'url': f'{TEST_JENKINS_URL}/job/test-pipeline/10/',
            'building': False
        },
        {
            'number': 9,
            'result': 'SUCCESS',
            'duration': 280000,
            'timestamp': 1640991600000,
            'url': f'{TEST_JENKINS_URL}/job/test-pipeline/9/',
            'building': False
        },
        {
            'number': 8,
            'result': 'FAILURE',
            'duration': 150000,
            'timestamp': 1640988000000,
            'url': f'{TEST_JENKINS_URL}/job/test-pipeline/8/',
            'building': False
        },
        {
            'number': 7,
            'result': 'SUCCESS',
            'duration': 320000,
            'timestamp': 1640984400000,
            'url': f'{TEST_JENKINS_URL}/job/test-pipeline/7/',
            'building': False
        },
        {
            'number': 6,
            'result': 'ABORTED',
            'duration': 60000,
            'timestamp': 1640980800000,
            'url': f'{TEST_JENKINS_URL}/job/test-pipeline/6/',
            'building': False
        }
    ]


@pytest.fixture
def mock_stage_data():
    """Mock pipeline stage data for testing."""
    return {
        'stages': [
            {
                'name': 'Build',
                'status': 'SUCCESS',
                'durationMillis': 120000,
                'startTimeMillis': 1640995200000
            },
            {
                'name': 'Test',
                'status': 'SUCCESS',
                'durationMillis': 90000,
                'startTimeMillis': 1640995320000
            },
            {
                'name': 'Deploy',
                'status': 'SUCCESS',
                'durationMillis': 60000,
                'startTimeMillis': 1640995410000
            }
        ]
    }


# Test data constants
TEST_JOB_NAMES = ['test-job-1', 'test-job-2', 'test-pipeline', 'test-folder']
TEST_BUILD_NUMBERS = [1, 2, 10, 42, 100]
TEST_FOLDER_PATHS = ['', 'folder1', 'folder1/subfolder', 'team/project/environment']
TEST_PIPELINE_TYPES = ['declarative', 'scripted', 'unknown']
TEST_BUILD_RESULTS = ['SUCCESS', 'FAILURE', 'ABORTED', 'UNSTABLE', 'NOT_BUILT']


@pytest.fixture(params=TEST_JOB_NAMES)
def job_name_param(request):
    """Parametrized job names for testing."""
    return request.param


@pytest.fixture(params=TEST_BUILD_NUMBERS)
def build_number_param(request):
    """Parametrized build numbers for testing."""
    return request.param


@pytest.fixture(params=TEST_FOLDER_PATHS)
def folder_path_param(request):
    """Parametrized folder paths for testing."""
    return request.param


@pytest.fixture(params=TEST_PIPELINE_TYPES)
def pipeline_type_param(request):
    """Parametrized pipeline types for testing."""
    return request.param


@pytest.fixture(params=TEST_BUILD_RESULTS)
def build_result_param(request):
    """Parametrized build results for testing."""
    return request.param


# Async test helpers
@pytest.fixture
def async_mock():
    """Create an AsyncMock for testing async functions."""
    return AsyncMock()


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "edge_case: mark test as an edge case test"
    )
    config.addinivalue_line(
        "markers", "error_handling: mark test as error handling test"
    )


# Test utilities
class TestUtils:
    """Utility functions for testing."""
    
    @staticmethod
    def create_mock_job_data(name: str, job_type: str = 'freestyle', **kwargs) -> Dict[str, Any]:
        """Create mock job data for testing."""
        base_data = {
            'name': name,
            'url': f'{TEST_JENKINS_URL}/job/{name}/',
            'buildable': True,
            'color': 'blue',
            'description': f'Test {job_type} job',
            '_class': f'hudson.model.{job_type.title()}Project',
        }
        base_data.update(kwargs)
        return base_data
    
    @staticmethod
    def create_mock_build_data(job_name: str, build_number: int, **kwargs) -> Dict[str, Any]:
        """Create mock build data for testing."""
        base_data = {
            'number': build_number,
            'url': f'{TEST_JENKINS_URL}/job/{job_name}/{build_number}/',
            'result': 'SUCCESS',
            'duration': 120000,
            'timestamp': 1640995200000,
            'building': False,
        }
        base_data.update(kwargs)
        return base_data
    
    @staticmethod
    def create_error_response(status_code: int, message: str) -> MagicMock:
        """Create mock error response for testing."""
        response = MagicMock()
        response.status_code = status_code
        response.text = message
        response.json.side_effect = ValueError("No JSON object could be decoded")
        return response


@pytest.fixture
def test_utils():
    """Test utilities fixture."""
    return TestUtils
