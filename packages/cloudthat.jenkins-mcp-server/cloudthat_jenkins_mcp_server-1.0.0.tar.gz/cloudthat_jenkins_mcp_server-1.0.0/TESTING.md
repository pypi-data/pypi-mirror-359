# Testing Guide - Jenkins MCP Server

![Tests](https://img.shields.io/badge/tests-passing-brightgreen)
![Coverage](https://img.shields.io/badge/coverage-90%25-brightgreen)
![Test Strategy](https://img.shields.io/badge/strategy-comprehensive-blue)
![CloudThat](https://img.shields.io/badge/CloudThat-OSS-orange.svg)

This document provides comprehensive guidance for testing the Jenkins MCP Server, a CloudThat project developed by Saurabh Kumar Jain (skj@cloudthat.com).

**Project Owner:** CloudThat Technologies Pvt. Ltd.  
**Author:** Saurabh Kumar Jain (skj@cloudthat.com) - CSA - Projects Head, DevOps and Kubernetes  
**Repository:** https://gitlab.cloudthat.com/cloudthat-oss/jenkins_mcp.git

## 📋 Table of Contents

- [Test Strategy](#test-strategy)
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Test Categories](#test-categories)
- [Coverage Requirements](#coverage-requirements)
- [Writing Tests](#writing-tests)
- [Continuous Integration](#continuous-integration)
- [Troubleshooting](#troubleshooting)

## 🎯 Test Strategy

### **Testing Philosophy**

Our testing approach follows the **Test Pyramid** principle, ensuring comprehensive coverage while maintaining fast feedback loops:

```
    /\
   /  \     E2E Tests (Few)
  /____\    Integration Tests (Some)  
 /______\   Unit Tests (Many)
```

- **Unit Tests (70%)**: Fast, isolated tests for individual components
- **Integration Tests (25%)**: Test component interactions and external dependencies
- **End-to-End Tests (5%)**: Full workflow testing with real Jenkins instances

### **Test Objectives**

1. **Functionality Verification**: Ensure all features work as expected
2. **Regression Prevention**: Catch breaking changes early
3. **Edge Case Coverage**: Handle boundary conditions and error scenarios
4. **Performance Validation**: Verify response times and resource usage
5. **Security Testing**: Validate authentication and authorization
6. **CloudThat Quality Standards**: Maintain enterprise-grade reliability

## 📁 Test Structure

```
tests/
├── 📄 conftest.py                    # Pytest configuration and shared fixtures
├── 📁 unit/                          # Unit tests (isolated component testing)
│   ├── 🧪 test_system_handler.py     # System information operations
│   ├── 🧪 test_build_handler.py      # Build management operations
│   ├── 🧪 test_pipeline_handler.py   # Pipeline operations
│   ├── 🧪 test_job_handler.py        # Job management operations
│   ├── 🧪 test_models.py             # Data model validation
│   ├── 🧪 test_utils.py              # Utility function tests
│   └── 🧪 test_validation.py         # Input validation tests
├── 📁 integration/                   # Integration tests (component interaction)
│   ├── 🧪 test_server_integration.py # Full server integration tests
│   ├── 🧪 test_basic_integration.py  # Basic integration scenarios
│   └── 🧪 test_tool_registration.py  # MCP tool registration tests
└── 📄 pytest.ini                    # Pytest configuration file
```

## 🚀 Running Tests

### **Prerequisites**

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Install test dependencies (if not already installed)
pip install -e ".[test]"
```

### **Basic Test Execution**

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_build_handler.py

# Run specific test function
pytest tests/unit/test_build_handler.py::test_trigger_build_success
```

### **Test Categories**

```bash
# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/

# Run tests by marker
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m slow          # Slow tests only
```

### **Coverage Testing**

```bash
# Run tests with coverage
pytest --cov=jenkins_mcp_server

# Generate HTML coverage report
pytest --cov=jenkins_mcp_server --cov-report=html

# Generate coverage report with missing lines
pytest --cov=jenkins_mcp_server --cov-report=term-missing

# Set minimum coverage threshold (CloudThat standard: 90%)
pytest --cov=jenkins_mcp_server --cov-fail-under=90
```

### **Parallel Test Execution**

```bash
# Install pytest-xdist for parallel execution
pip install pytest-xdist

# Run tests in parallel (auto-detect CPU cores)
pytest -n auto

# Run tests with specific number of workers
pytest -n 4
```

### **Advanced Test Options**

```bash
# Run tests with detailed output
pytest -v --tb=short

# Run only failed tests from last run
pytest --lf

# Run tests and stop on first failure
pytest -x

# Run tests with custom markers
pytest -m "not slow"     # Skip slow tests
pytest -m "unit and not integration"  # Complex marker expressions
```

## 🧪 Test Categories

### **Unit Tests**

**Purpose**: Test individual components in isolation

**Characteristics**:
- Fast execution (< 1 second per test)
- No external dependencies
- Use mocks for external services
- High code coverage

**Example**:
```python
@pytest.mark.unit
async def test_validate_job_name_success():
    """Test successful job name validation."""
    valid_name = "my-valid-job-name"
    result = validate_job_name(valid_name)
    assert result == valid_name

@pytest.mark.unit
async def test_validate_job_name_invalid():
    """Test job name validation with invalid input."""
    with pytest.raises(ValidationError):
        validate_job_name("")
```

### **Integration Tests**

**Purpose**: Test component interactions and external dependencies

**Characteristics**:
- Moderate execution time (1-10 seconds per test)
- May use real external services
- Test end-to-end workflows
- Validate data flow between components

**Example**:
```python
@pytest.mark.integration
async def test_jenkins_connection_integration():
    """Test actual Jenkins server connection."""
    handler = SystemHandler()
    server_info = await handler.get_server_info()
    assert server_info.url is not None
    assert server_info.version is not None
```

### **Performance Tests**

**Purpose**: Validate response times and resource usage

**Characteristics**:
- Measure execution time
- Monitor memory usage
- Test under load conditions
- Validate caching effectiveness

**Example**:
```python
@pytest.mark.performance
async def test_job_listing_performance():
    """Test job listing performance meets CloudThat standards."""
    handler = JobHandler()
    
    start_time = time.time()
    jobs = await handler.list_jobs()
    execution_time = time.time() - start_time
    
    assert execution_time < 5.0  # CloudThat performance requirement
    assert len(jobs) > 0
```

## 📊 Coverage Requirements

### **CloudThat Coverage Standards**

- **Overall Coverage**: Minimum 90% (CloudThat enterprise standard)
- **New Code Coverage**: Minimum 95%
- **Critical Paths**: 100% (authentication, build operations)
- **Handler Classes**: Minimum 95%
- **Utility Functions**: Minimum 98%

### **Coverage Exclusions**

```python
# In pyproject.toml
[tool.coverage.run]
omit = [
    "tests/*",
    "jenkins_mcp_server/__main__.py",
    "*/venv/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
]
```

### **Coverage Reporting**

```bash
# Generate coverage report
pytest --cov=jenkins_mcp_server --cov-report=html

# View HTML report
open htmlcov/index.html

# Generate XML report for CI
pytest --cov=jenkins_mcp_server --cov-report=xml
```

## ✍️ Writing Tests

### **CloudThat Test Naming Conventions**

```python
# Test file naming
test_<module_name>.py

# Test function naming
def test_<function_name>_<scenario>():
    """Test <description> - CloudThat standard."""
    pass

# Test class naming
class Test<ClassName>:
    """Test cases for <ClassName> - CloudThat implementation."""
    pass
```

### **Test Structure (AAA Pattern)**

```python
async def test_trigger_build_with_parameters():
    """Test triggering build with parameters - CloudThat Jenkins integration."""
    # Arrange
    handler = BuildHandler()
    job_name = "test-job"
    parameters = {"BRANCH": "main", "DEPLOY": True}
    
    # Act
    result = await handler.trigger_build(job_name, parameters)
    
    # Assert
    assert result.triggered is True
    assert result.queue_item_id is not None
    assert result.parameters == parameters
```

### **Using Fixtures**

```python
@pytest.fixture
async def build_handler():
    """Create a BuildHandler instance for testing CloudThat implementation."""
    return BuildHandler()

@pytest.fixture
def sample_job_data():
    """Provide sample job data for CloudThat testing standards."""
    return {
        "name": "cloudthat-test-job",
        "type": "freestyle",
        "description": "Test job for CloudThat Jenkins MCP Server"
    }

async def test_with_fixtures(build_handler, sample_job_data):
    """Test using CloudThat standard fixtures."""
    result = await build_handler.create_job(**sample_job_data)
    assert result.name == sample_job_data["name"]
```

### **Mocking External Dependencies**

```python
@pytest.mark.unit
@patch('jenkins_mcp_server.handlers.base_handler.jenkins.Jenkins')
async def test_with_mock_jenkins(mock_jenkins_class):
    """Test with mocked Jenkins client - CloudThat testing approach."""
    # Setup mock
    mock_jenkins = mock_jenkins_class.return_value
    mock_jenkins.get_info.return_value = {"version": "2.400.0"}
    
    # Test
    handler = SystemHandler()
    info = await handler.get_server_info()
    
    # Verify
    assert info.version == "2.400.0"
    mock_jenkins.get_info.assert_called_once()
```

### **Parametrized Tests**

```python
@pytest.mark.parametrize("job_name,expected", [
    ("cloudthat-valid-job", "cloudthat-valid-job"),
    ("valid_job", "valid_job"),
    ("ValidJob", "ValidJob"),
])
def test_job_name_validation(job_name, expected):
    """Test job name validation with various inputs - CloudThat standards."""
    result = validate_job_name(job_name)
    assert result == expected

@pytest.mark.parametrize("invalid_name", [
    "",
    None,
    "job with spaces",
    "job@with#special",
])
def test_invalid_job_names(invalid_name):
    """Test job name validation with invalid inputs - CloudThat validation."""
    with pytest.raises(ValidationError):
        validate_job_name(invalid_name)
```

## 🔄 Continuous Integration

### **GitLab CI/CD Pipeline**

```yaml
# .gitlab-ci.yml
stages:
  - test
  - coverage
  - quality

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"

cache:
  paths:
    - .cache/pip/
    - venv/

before_script:
  - python -m venv venv
  - source venv/bin/activate
  - pip install -e ".[test]"

test:
  stage: test
  script:
    - pytest -v
  artifacts:
    reports:
      junit: test-results.xml
    paths:
      - test-results.xml
  coverage: '/TOTAL.*\s+(\d+%)$/'

coverage:
  stage: coverage
  script:
    - pytest --cov=jenkins_mcp_server --cov-report=xml --cov-report=html
    - coverage report --fail-under=90
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
    paths:
      - htmlcov/
  coverage: '/TOTAL.*\s+(\d+%)$/'

quality:
  stage: quality
  script:
    - ruff check .
    - mypy jenkins_mcp_server/
  allow_failure: false
```

### **Pre-commit Hooks**

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: tests
        name: CloudThat Test Suite
        entry: pytest
        language: system
        pass_filenames: false
        always_run: true
      - id: coverage
        name: CloudThat Coverage Check
        entry: pytest --cov=jenkins_mcp_server --cov-fail-under=90
        language: system
        pass_filenames: false
        always_run: true
```

## 🔧 Troubleshooting

### **Common Test Issues**

#### **Import Errors**
```bash
# Error: ModuleNotFoundError
# Solution: Install package in development mode
pip install -e .
```

#### **Async Test Issues**
```bash
# Error: RuntimeError: There is no current event loop
# Solution: Use pytest-asyncio
pip install pytest-asyncio

# Add to pytest.ini
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

#### **Mock Issues**
```bash
# Error: Mock not working as expected
# Solution: Ensure correct import path
@patch('jenkins_mcp_server.handlers.build_handler.jenkins.Jenkins')
```

### **CloudThat Test Environment Setup**

```bash
# Set CloudThat test environment variables
export JENKINS_TEST_URL=http://cloudthat-jenkins:8080
export JENKINS_TEST_USERNAME=cloudthat-test-user
export JENKINS_TEST_TOKEN=cloudthat-test-token

# Or use .env file
echo "JENKINS_TEST_URL=http://cloudthat-jenkins:8080" > .env.test
```

### **Debugging Tests**

```bash
# Run tests with debugging
pytest --pdb

# Run specific test with debugging
pytest tests/unit/test_build_handler.py::test_trigger_build -s --pdb

# Add print statements (use -s flag)
pytest -s tests/unit/test_build_handler.py
```

### **Performance Issues**

```bash
# Profile test execution
pytest --profile

# Run tests with timing
pytest --durations=10

# Skip slow tests during development
pytest -m "not slow"
```

## 📈 Test Metrics

### **CloudThat Quality Metrics**

- **Test Count**: 100+ comprehensive tests
- **Coverage Percentage**: 90%+ (CloudThat enterprise standard)
- **Execution Time**: < 2 minutes for full suite
- **Flaky Tests**: 0% tolerance
- **Test Reliability**: 99.9%+ pass rate

### **Reporting**

```bash
# Generate comprehensive test report
pytest --html=cloudthat-test-report.html --self-contained-html

# Generate JUnit XML for CI
pytest --junitxml=cloudthat-test-results.xml

# Generate coverage badge
coverage-badge -o cloudthat-coverage.svg
```

## 🎯 CloudThat Testing Standards

### **Enterprise Testing Requirements**

1. **Comprehensive Coverage**: 90%+ code coverage maintained
2. **Performance Standards**: All tests complete within defined SLAs
3. **Security Testing**: Authentication and authorization validation
4. **Integration Testing**: Real Jenkins instance testing
5. **Documentation**: All tests properly documented
6. **Maintainability**: Tests are easy to understand and modify
7. **Reliability**: Tests are deterministic and stable

### **Quality Assurance Process**

1. **Pre-commit Testing**: All tests must pass before commit
2. **Merge Request Testing**: Full test suite execution required
3. **Performance Monitoring**: Test execution time tracking
4. **Coverage Monitoring**: Coverage trends analysis
5. **Quality Gates**: Automated quality checks in CI/CD

---

## 🏢 About CloudThat Testing Standards

**CloudThat** maintains enterprise-grade testing standards across all our projects. This Jenkins MCP Server testing framework represents our commitment to quality and reliability in DevOps tooling.

As an **AWS Premier Tier Services Partner**, we apply the same rigorous testing standards used in our client engagements to ensure production-ready software quality.

**Website**: [https://cloudthat.com](https://cloudthat.com)  
**Contact**: info@cloudthat.com  
**Author**: Saurabh Kumar Jain (skj@cloudthat.com)

---

For questions about testing, please refer to our [Contributing Guidelines](CONTRIBUTING.md) or create an issue on our GitLab repository.
