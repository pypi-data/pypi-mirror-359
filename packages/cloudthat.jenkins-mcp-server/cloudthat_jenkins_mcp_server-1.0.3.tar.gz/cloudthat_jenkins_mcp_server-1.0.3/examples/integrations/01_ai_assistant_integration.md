# AI Assistant Integration Examples

This document provides examples of how to integrate the Jenkins MCP server with various AI assistants.

## Installation Methods

The examples below use `uvx` (recommended) for easy installation and execution. Alternative methods:

- **uvx (Recommended)**: `uvx jenkins-mcp-server` - Automatically manages dependencies
- **From Source**: `python -m jenkins_mcp_server` - Requires manual dependency installation
- **Docker**: Use the CloudThat Docker image for containerized deployments

## Amazon Q Developer Integration

### Configuration
```json
{
  "mcpServers": {
    "jenkins": {
      "command": "uvx",
      "args": ["jenkins-mcp-server"],
      "env": {
        "JENKINS_URL": "https://jenkins.company.com",
        "JENKINS_USERNAME": "automation-user",
        "JENKINS_TOKEN": "your-api-token"
      }
    }
  }
}
```

### Example Conversations
```
User: "Show me the status of our production deployment pipeline"
Q: I'll check the status of your production deployment pipeline for you.

User: "The build is failing - can you help me debug it?"
Q: Let me analyze the build logs and system status to help identify the issue.

User: "Set up a new pipeline for our React application"
Q: I'll create a new pipeline with appropriate stages for a React application including build, test, and deployment.
```

## Claude Desktop Integration

### Configuration (claude_desktop_config.json)
```json
{
  "mcpServers": {
    "jenkins": {
      "command": "uvx",
      "args": ["jenkins-mcp-server"],
      "env": {
        "JENKINS_URL": "http://localhost:8080",
        "JENKINS_USERNAME": "admin",
        "JENKINS_TOKEN": "your-token"
      }
    }
  }
}
```

### Example Interactions
```
User: "Analyze our Jenkins performance and suggest optimizations"
Claude: I'll analyze your Jenkins system performance, including build times, resource utilization, and queue patterns, then provide specific optimization recommendations.

User: "Create a secure deployment pipeline for our banking application"
Claude: I'll set up a comprehensive pipeline with security scanning, compliance checks, and proper approval workflows suitable for banking applications.
```

## Cursor IDE Integration

### Setup
1. Install the Jenkins MCP server
2. Configure in Cursor's MCP settings
3. Use natural language to interact with Jenkins

### Example Usage
```
User: "Check if our latest commit broke any builds"
Cursor: Let me check the build status for recent commits and identify any failures.

User: "Deploy the hotfix to staging environment"
Cursor: I'll trigger the deployment pipeline for the hotfix to the staging environment and monitor its progress.
```

## VS Code Integration

### Extension Configuration
```json
{
  "mcp.servers": {
    "jenkins": {
      "command": "uvx",
      "args": ["jenkins-mcp-server"],
      "env": {
        "JENKINS_URL": "${env:JENKINS_URL}",
        "JENKINS_USERNAME": "${env:JENKINS_USERNAME}",
        "JENKINS_TOKEN": "${env:JENKINS_TOKEN}"
      }
    }
  }
}
```

### Workflow Examples
```
User: "Show me which tests are failing in the current branch"
VS Code: I'll check the test results from the latest build for your current branch.

User: "Create a pipeline for this new microservice"
VS Code: I'll generate a pipeline configuration based on your project structure and requirements.
```

## Slack Bot Integration

### Bot Setup
```python
# Slack bot that uses Jenkins MCP server
import slack_sdk
from jenkins_mcp_client import JenkinsMCPClient

@app.command("/jenkins-status")
def jenkins_status(ack, say, command):
    ack()
    # Use MCP client to get Jenkins status
    status = jenkins_client.get_server_info()
    say(f"Jenkins Status: {status}")
```

### Example Commands
```
/jenkins-status - Get overall Jenkins health
/jenkins-build my-app - Trigger build for my-app
/jenkins-logs my-app 42 - Get logs for build #42
/jenkins-queue - Show current build queue
```

## Microsoft Teams Integration

### Bot Configuration
```yaml
# Teams bot configuration
name: Jenkins Assistant
description: AI-powered Jenkins management
commands:
  - name: status
    description: Get Jenkins system status
  - name: build
    description: Trigger a build
  - name: logs
    description: Get build logs
```

### Usage Examples
```
@JenkinsBot status
@JenkinsBot build production-deploy with version=1.2.3
@JenkinsBot analyze performance issues
@JenkinsBot create pipeline for new-service
```

## Custom AI Assistant Integration

### Python Client Example
```python
import asyncio
from mcp.client import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

class JenkinsAIAssistant:
    def __init__(self):
        self.session = None
    
    async def connect(self):
        params = StdioServerParameters(
            command="uvx",
            args=["jenkins-mcp-server"],
            env={
                "JENKINS_URL": "http://localhost:8080",
                "JENKINS_USERNAME": "admin",
                "JENKINS_TOKEN": "your-token"
            }
        )
        
        self.streams = await stdio_client(params).__aenter__()
        self.session = await ClientSession(
            self.streams[0], 
            self.streams[1]
        ).__aenter__()
        await self.session.initialize()
    
    async def process_query(self, query: str):
        # Use AI model to interpret query and call appropriate tools
        if "status" in query.lower():
            return await self.session.call_tool("get_jenkins_server_info")
        elif "build" in query.lower():
            # Extract job name and parameters from query
            return await self.session.call_tool("trigger_jenkins_build", {
                "job_name": "extracted-job-name"
            })
        # Add more query processing logic
```

## Web Interface Integration

### React Component Example
```jsx
import React, { useState } from 'react';
import { JenkinsMCPClient } from './jenkins-mcp-client';

function JenkinsAssistant() {
    const [query, setQuery] = useState('');
    const [response, setResponse] = useState('');
    
    const handleQuery = async () => {
        const client = new JenkinsMCPClient();
        const result = await client.processQuery(query);
        setResponse(result);
    };
    
    return (
        <div>
            <input 
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask about Jenkins..."
            />
            <button onClick={handleQuery}>Ask</button>
            <div>{response}</div>
        </div>
    );
}
```

## Mobile App Integration

### Flutter Example
```dart
class JenkinsAssistant {
  final JenkinsMCPClient _client = JenkinsMCPClient();
  
  Future<String> processVoiceCommand(String command) async {
    // Convert voice to text, then process with MCP
    final result = await _client.processQuery(command);
    return result;
  }
  
  Future<void> sendNotification(String message) async {
    // Send push notification about Jenkins events
  }
}
```

## API Gateway Integration

### REST API Wrapper
```python
from fastapi import FastAPI
from jenkins_mcp_client import JenkinsMCPClient

app = FastAPI()
jenkins_client = JenkinsMCPClient()

@app.post("/jenkins/query")
async def jenkins_query(query: str):
    result = await jenkins_client.process_natural_language_query(query)
    return {"response": result}

@app.get("/jenkins/status")
async def jenkins_status():
    return await jenkins_client.get_server_info()
```

## Monitoring Integration

### Prometheus Metrics
```python
from prometheus_client import Counter, Histogram
from jenkins_mcp_client import JenkinsMCPClient

# Metrics
jenkins_queries = Counter('jenkins_mcp_queries_total', 'Total Jenkins MCP queries')
jenkins_response_time = Histogram('jenkins_mcp_response_seconds', 'Jenkins MCP response time')

class MonitoredJenkinsClient(JenkinsMCPClient):
    async def process_query(self, query):
        jenkins_queries.inc()
        with jenkins_response_time.time():
            return await super().process_query(query)
```

## Security Considerations

### Secure Configuration
```yaml
# Secure environment configuration
jenkins_mcp:
  security:
    encryption: true
    token_rotation: 24h
    audit_logging: true
    rate_limiting: 100/hour
  access_control:
    allowed_users: ["admin", "devops-team"]
    restricted_operations: ["delete", "disable"]
```

### Best Practices
- Use API tokens instead of passwords
- Implement proper access controls
- Enable audit logging
- Use encrypted connections
- Rotate credentials regularly
- Monitor for unusual activity
