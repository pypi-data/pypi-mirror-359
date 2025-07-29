# Contributing to Jenkins MCP Server

![Contributors Welcome](https://img.shields.io/badge/contributors-welcome-brightgreen.svg)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)
![Code Style](https://img.shields.io/badge/code%20style-ruff-000000.svg)
![CloudThat](https://img.shields.io/badge/CloudThat-OSS-orange.svg)

Thank you for your interest in contributing to the Jenkins MCP Server! This project is developed and maintained by **CloudThat Technologies Pvt. Ltd.** as part of our innovation initiative. This document provides comprehensive guidelines for contributors to ensure productive collaboration.

**Project Owner:** CloudThat Technologies Pvt. Ltd.  
**Author:** Saurabh Kumar Jain (skj@cloudthat.com) - CSA - Projects Head, DevOps and Kubernetes  
**Repository:** https://gitlab.cloudthat.com/cloudthat-oss/jenkins_mcp.git

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Standards](#code-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Issue Guidelines](#issue-guidelines)
- [Intellectual Property](#intellectual-property)

## 🤝 Code of Conduct

By participating in this CloudThat project, you agree to abide by our Code of Conduct:

- **Be Respectful**: Treat all community members with respect and kindness
- **Be Constructive**: Provide helpful feedback and suggestions
- **Be Inclusive**: Welcome newcomers and help them get started
- **Be Professional**: Maintain a professional tone in all communications
- **Be Patient**: Remember that everyone has different experience levels
- **Respect Intellectual Property**: Acknowledge CloudThat's ownership and licensing terms

## 🚀 Getting Started

### **Prerequisites**

- **Python**: 3.10 or higher
- **Git**: Latest version
- **GitLab Account**: For accessing CloudThat's GitLab repository
- **Jenkins Instance**: For testing (optional but recommended)
- **IDE**: VS Code, PyCharm, or similar with Python support

### **Development Setup**

1. **Fork and Clone the Repository**
   ```bash
   # Fork the repository on GitLab first, then:
   git clone https://gitlab.cloudthat.com/your-username/jenkins_mcp.git
   cd jenkins_mcp
   
   # Add upstream remote
   git remote add upstream https://gitlab.cloudthat.com/cloudthat-oss/jenkins_mcp.git
   ```

2. **Create a Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Development Dependencies**
   ```bash
   # Install the package in development mode with all dependencies
   pip install -e ".[dev,test]"
   
   # Install pre-commit hooks
   pre-commit install
   ```

4. **Verify Installation**
   ```bash
   # Run tests to ensure everything is working
   pytest
   
   # Check code style
   ruff check .
   
   # Run type checking
   mypy jenkins_mcp_server/
   ```

5. **Set Up Test Environment** (Optional)
   ```bash
   # Create .env file for testing
   cp .env.example .env
   
   # Edit .env with your Jenkins test instance details
   JENKINS_URL=http://your-test-jenkins:8080
   JENKINS_USERNAME=test-user
   JENKINS_TOKEN=your-test-token
   ```

## 🔄 Development Workflow

### **Branch Naming Conventions**

Use descriptive branch names following this pattern:

```
<type>/<short-description>

Types:
- feature/    # New features
- fix/        # Bug fixes
- docs/       # Documentation updates
- refactor/   # Code refactoring
- test/       # Test improvements
- chore/      # Maintenance tasks
```

**Examples:**
- `feature/add-pipeline-validation`
- `fix/build-trigger-timeout`
- `docs/update-installation-guide`
- `refactor/improve-error-handling`

### **Commit Message Format**

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(handlers): add pipeline validation support

Add server-side Jenkinsfile validation before pipeline creation
to catch syntax errors early and provide better user feedback.

Closes #123
```

```
fix(build): resolve parameterized build triggering issue

The build_job method was not properly handling parameter
serialization for complex parameter types.

Fixes #456
```

## 📏 Code Standards

### **Python Code Style**

We use **Ruff** for code formatting and linting:

```bash
# Format code
ruff format .

# Check for linting issues
ruff check .

# Fix auto-fixable issues
ruff check --fix .
```

### **Code Quality Requirements**

1. **Type Hints**: All functions must have proper type hints
   ```python
   def create_job(self, job_name: str, job_type: str) -> JobResult:
       """Create a new Jenkins job."""
       pass
   ```

2. **Docstrings**: All public functions must have docstrings
   ```python
   def trigger_build(self, job_name: str, parameters: Optional[Dict[str, Any]] = None) -> BuildResult:
       """Trigger a Jenkins build.
       
       Args:
           job_name: Name of the job to trigger
           parameters: Optional build parameters
           
       Returns:
           BuildResult: Result of the build trigger operation
           
       Raises:
           JenkinsError: If the build fails to trigger
       """
       pass
   ```

3. **Error Handling**: Proper exception handling with specific error types
   ```python
   try:
       result = await self.jenkins_client.build_job(job_name)
   except jenkins.JenkinsException as e:
       raise JenkinsConnectionError(f"Failed to trigger build: {e}")
   ```

4. **Logging**: Use structured logging with appropriate levels
   ```python
   logger.info(f"Triggering build for job: {job_name}")
   logger.debug(f"Build parameters: {parameters}")
   ```

### **Import Organization**

Organize imports in this order:
1. Standard library imports
2. Third-party imports
3. Local application imports

```python
# Standard library
import asyncio
from typing import Dict, List, Optional

# Third-party
import httpx
from pydantic import BaseModel

# Local
from jenkins_mcp_server.exceptions import JenkinsError
from jenkins_mcp_server.models import BuildResult
```

## 🧪 Testing Guidelines

### **Test Structure**

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test end-to-end functionality
- **Mock Tests**: Use mocks for external dependencies

### **Writing Tests**

1. **Test File Naming**: `test_<module_name>.py`
2. **Test Function Naming**: `test_<functionality>_<scenario>`
3. **Test Organization**: Group related tests in classes

```python
class TestBuildHandler:
    """Test cases for BuildHandler."""
    
    async def test_trigger_build_success(self):
        """Test successful build triggering."""
        # Arrange
        handler = BuildHandler()
        
        # Act
        result = await handler.trigger_build("test-job")
        
        # Assert
        assert result.triggered is True
        assert result.queue_item_id is not None
    
    async def test_trigger_build_with_invalid_job_name(self):
        """Test build triggering with invalid job name."""
        handler = BuildHandler()
        
        with pytest.raises(ValidationError):
            await handler.trigger_build("")
```

### **Running Tests**

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=jenkins_mcp_server --cov-report=html

# Run specific test file
pytest tests/unit/test_build_handler.py

# Run with verbose output
pytest -v

# Run tests in parallel
pytest -n auto
```

### **Test Coverage Requirements**

- **Minimum Coverage**: 85%
- **New Code Coverage**: 90%
- **Critical Paths**: 100% (authentication, build triggering, etc.)

## 📚 Documentation

### **Code Documentation**

1. **Docstrings**: Use Google-style docstrings
2. **Type Hints**: Comprehensive type annotations
3. **Comments**: Explain complex logic, not obvious code

### **Documentation Updates**

When making changes, update relevant documentation:

- **README.md**: For new features or installation changes
- **CHANGELOG.md**: For all user-facing changes
- **API Documentation**: For new or changed APIs
- **Code Comments**: For complex implementations

## 🔄 Pull Request Process

### **Before Submitting**

1. **Run the Full Test Suite**
   ```bash
   pytest
   ```

2. **Check Code Quality**
   ```bash
   ruff check .
   ruff format .
   mypy jenkins_mcp_server/
   ```

3. **Update Documentation**
   - Update relevant documentation files
   - Add docstrings for new functions
   - Update CHANGELOG.md

4. **Test Your Changes**
   - Test manually with a real Jenkins instance
   - Ensure all existing functionality still works
   - Add appropriate test cases

### **Pull Request Template**

When creating a Merge Request on GitLab, include:

```markdown
## Description
Brief description of the changes made.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] New tests added for new functionality

## Checklist
- [ ] Code follows CloudThat's style guidelines
- [ ] Self-review of code completed
- [ ] Code is commented, particularly in hard-to-understand areas
- [ ] Corresponding changes to documentation made
- [ ] Changes generate no new warnings
- [ ] New and existing unit tests pass locally
- [ ] Contributor License Agreement acknowledged
```

### **Review Process**

1. **Automated Checks**: All CI checks must pass
2. **Code Review**: CloudThat maintainer review required
3. **Testing**: Manual testing for significant changes
4. **Documentation**: Documentation updates reviewed
5. **Approval**: CloudThat maintainer approval required for merge

## 🐛 Issue Guidelines

### **Bug Reports**

Use the bug report template and include:

- **Environment**: OS, Python version, Jenkins version
- **Steps to Reproduce**: Clear, numbered steps
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Logs**: Relevant error messages or logs
- **Screenshots**: If applicable

### **Feature Requests**

Use the feature request template and include:

- **Problem Statement**: What problem does this solve?
- **Proposed Solution**: How should it work?
- **Alternatives**: Other solutions considered
- **Additional Context**: Any other relevant information

### **Issue Labels**

- `bug`: Something isn't working
- `enhancement`: New feature or request
- `documentation`: Improvements or additions to documentation
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention is needed
- `priority/high`: High priority issue
- `priority/low`: Low priority issue

## 📜 Intellectual Property

### **Contribution License Agreement**

By contributing to this project, you acknowledge and agree that:

1. **Ownership**: All contributions become the intellectual property of CloudThat Technologies Pvt. Ltd.

2. **Rights Grant**: You grant CloudThat perpetual, worldwide, non-exclusive, royalty-free rights to:
   - Use, modify, and distribute your contributions
   - Relicense contributions under different terms
   - Incorporate contributions into proprietary or commercial projects

3. **Original Work**: You confirm that your contributions are your original work or you have the right to submit them

4. **No Conflicting Obligations**: Your contributions do not violate any agreements with employers or other parties

### **CloudThat's Commitment**

CloudThat commits to:

- **Open Source**: Maintaining this project as open source for community benefit
- **Attribution**: Recognizing significant contributors in project documentation
- **Transparency**: Clear communication about project direction and decisions
- **Community**: Fostering a welcoming and inclusive contributor community

## 🆘 Getting Help

### **Communication Channels**

- **GitLab Issues**: For bugs and feature requests
- **GitLab Merge Requests**: For technical discussions about specific changes
- **Email**: For direct communication with maintainers

### **Maintainer Contact**

For urgent issues or questions about contributing:

- **Primary Maintainer**: Saurabh Kumar Jain (skj@cloudthat.com)
- **CloudThat Support**: info@cloudthat.com
- **Repository**: https://gitlab.cloudthat.com/cloudthat-oss/jenkins_mcp.git

## 🎉 Recognition

Contributors are recognized in:

- **CHANGELOG.md**: For significant contributions
- **README.md**: In the acknowledgements section
- **GitLab Contributors**: Automatic recognition
- **Release Notes**: For major contributions

### **Contributor Benefits**

- **Professional Recognition**: Contributions to a CloudThat project
- **Learning Opportunities**: Work with enterprise-grade DevOps and cloud technologies
- **Community Impact**: Contribute to tools used by the Jenkins and AI communities
- **Technical Growth**: Gain experience with modern Python, MCP protocol, and CI/CD

---

## 🏢 About CloudThat

**CloudThat** is a seasoned cloud consulting company and AWS Premier Tier Services Partner, established in 2012. We specialize in cloud strategy, migration, modernization, DevOps, security, data analytics, AI/ML, and managed services.

This Jenkins MCP Server project represents our commitment to innovation and community contribution in the DevOps and cloud-native ecosystem.

**Website**: [https://cloudthat.com](https://cloudthat.com)  
**Contact**: info@cloudthat.com

---

Thank you for contributing to Jenkins MCP Server! Your contributions help make this CloudThat project better for the entire Jenkins and AI community. 🚀
