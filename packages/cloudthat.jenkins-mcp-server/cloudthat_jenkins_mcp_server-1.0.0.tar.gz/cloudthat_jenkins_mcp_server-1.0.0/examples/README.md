# Jenkins MCP Server Examples

This directory contains comprehensive examples demonstrating how to use the Jenkins MCP Server with AI assistants for various Jenkins operations and workflows.

## 📁 Directory Structure

```
examples/
├── prompts/                    # Natural language prompt examples
│   ├── 01_supported_operations.md    # Basic supported operations
│   ├── 02_advanced_operations.md     # Advanced Jenkins features
│   ├── 03_intelligent_operations.md  # AI-powered operations
│   └── 04_complex_scenarios.md       # Enterprise-scale scenarios
├── integrations/               # AI assistant integration examples
│   └── 01_ai_assistant_integration.md
└── README.md                   # This file
```

## 🚀 Getting Started

### Prerequisites
- Jenkins MCP Server installed and configured
- AI assistant (Amazon Q, Claude, etc.) with MCP support
- Valid Jenkins credentials and API access

### Basic Setup
1. Configure your AI assistant with the Jenkins MCP server
2. Set environment variables for Jenkins connection
3. Start with basic operations from `01_supported_operations.md`
4. Progress to advanced features as needed

## 📋 Example Categories

### 1. Basic Operations (`01_supported_operations.md`)
Core Jenkins operations that every user should know:
- **Job Management**: Creating, listing, and managing Jenkins jobs
- **Build Operations**: Triggering builds, monitoring status, viewing logs
- **System Information**: Server status, queue management, system analysis
- **Best Practices**: Performance optimization and configuration review

**Example Prompts:**
```
"Show me all Jenkins jobs in the production folder."
"Trigger a build of my-app-pipeline with version 2.1.0."
"What's the current status of the Jenkins server?"
```

### 2. Advanced Operations (`02_advanced_operations.md`)
Enterprise-level Jenkins management capabilities:
- **Plugin Management**: Installing, updating, and analyzing plugins
- **Node Management**: Managing Jenkins agents and executors
- **Credential Management**: Secure credential handling and auditing
- **Security Scanning**: Automated security checks and compliance
- **Multi-Branch Pipelines**: Complex branching strategies

**Example Prompts:**
```
"List all installed plugins with available updates."
"Show me the health status of all Jenkins agents."
"Run a security audit of our Jenkins configuration."
```

### 3. Intelligent Operations (`03_intelligent_operations.md`)
AI-powered Jenkins operations leveraging machine learning:
- **Predictive Analytics**: Forecasting capacity and failure patterns
- **Automated Problem Resolution**: Self-healing pipelines
- **Performance Intelligence**: Bottleneck analysis and optimization
- **Security Intelligence**: Threat detection and recommendations
- **Cost Intelligence**: Resource optimization and cost analysis

**Example Prompts:**
```
"Analyze recent build failures and suggest root causes."
"Predict when we'll need additional build capacity."
"Recommend security improvements based on current threats."
```

### 4. Complex Scenarios (`04_complex_scenarios.md`)
Real-world enterprise scenarios and use cases:
- **Enterprise-Scale Operations**: Multi-team, multi-region setups
- **Complex Pipeline Orchestration**: Microservices coordination
- **Advanced Security**: Zero-trust, compliance automation
- **Performance at Scale**: High-volume processing optimization
- **Disaster Recovery**: Comprehensive backup and failover strategies

**Example Prompts:**
```
"Set up Jenkins for multiple teams with isolated environments."
"Configure zero-trust security model for our Jenkins infrastructure."
"Design auto-scaling Jenkins agents based on build queue depth."
```

### 5. AI Assistant Integration (`01_ai_assistant_integration.md`)
Examples of integrating with various AI assistants and platforms:
- **Amazon Q Developer**: Configuration and usage examples
- **Claude Desktop**: Setup and interaction patterns
- **Custom Integrations**: API wrappers and mobile apps
- **Security Considerations**: Best practices for secure integration

## 🎯 Usage Patterns

### For DevOps Engineers
Start with basic operations, then explore advanced features:
1. Job and build management
2. System monitoring and optimization
3. Security and compliance automation
4. Performance tuning and scaling

### For Platform Engineers
Focus on enterprise-scale operations:
1. Multi-team infrastructure setup
2. Advanced security configurations
3. Disaster recovery planning
4. Cost optimization strategies

### For Developers
Concentrate on development workflow integration:
1. Pipeline creation and management
2. Build troubleshooting
3. Test automation
4. Deployment strategies

### For Security Teams
Emphasize security and compliance features:
1. Security scanning and auditing
2. Credential management
3. Compliance automation
4. Threat detection and response

## 🔧 Configuration Examples

### Environment Variables
```bash
export JENKINS_URL="https://jenkins.company.com"
export JENKINS_USERNAME="automation-user"
export JENKINS_TOKEN="your-api-token"
export JENKINS_TIMEOUT="60"
export JENKINS_LOG_LEVEL="INFO"
```

### AI Assistant Configuration
```json
{
  "mcpServers": {
    "jenkins": {
      "command": "python",
      "args": ["-m", "jenkins_mcp_server"],
      "env": {
        "JENKINS_URL": "https://jenkins.company.com",
        "JENKINS_USERNAME": "automation-user",
        "JENKINS_TOKEN": "your-api-token"
      }
    }
  }
}
```

## 🛡️ Security Best Practices

1. **Use API Tokens**: Never use passwords in configurations
2. **Limit Permissions**: Grant minimal required permissions
3. **Rotate Credentials**: Regularly update API tokens
4. **Enable Audit Logging**: Track all operations
5. **Secure Communications**: Use HTTPS/TLS connections
6. **Monitor Access**: Watch for unusual activity patterns

## 📊 Monitoring and Observability

### Key Metrics to Track
- Build success rates and duration trends
- Resource utilization across agents
- Queue wait times and throughput
- Security scan results and compliance status
- Cost metrics and optimization opportunities

### Alerting Recommendations
- Failed builds in critical pipelines
- High resource utilization
- Security vulnerabilities detected
- Credential access anomalies
- System performance degradation

## 🚨 Troubleshooting

### Common Issues
1. **Connection Problems**: Check Jenkins URL and credentials
2. **Permission Errors**: Verify user permissions in Jenkins
3. **Timeout Issues**: Adjust timeout settings for long operations
4. **Rate Limiting**: Implement proper request throttling

### Debug Mode
Enable debug logging for troubleshooting:
```bash
export JENKINS_LOG_LEVEL="DEBUG"
```

## 🤝 Contributing

To add new examples:
1. Follow the existing format and structure
2. Include clear descriptions and use cases
3. Provide realistic, practical examples
4. Test all prompts with the actual MCP server
5. Update this README with new categories

## 📚 Additional Resources

- [Jenkins MCP Server Documentation](../README.md)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [Jenkins API Documentation](https://www.jenkins.io/doc/book/using/remote-access-api/)
- [CloudThat DevOps Services](https://cloudthat.com/devops-services)

---

**Developed by:** [CloudThat Technologies](https://cloudthat.com) - AWS Premier Tier Services Partner  
**Author:** Saurabh Kumar Jain (skj@cloudthat.com) - CSA - Projects Head, DevOps and Kubernetes
