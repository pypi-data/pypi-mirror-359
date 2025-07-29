# Advanced Jenkins MCP Server Operations

This document provides example prompts for advanced Jenkins operations supported by the MCP server.

## Plugin Management

### Plugin Status and Information
```
List all installed Jenkins plugins with their versions.
```
```
Which plugins have available updates?
```
```
Show me details about the Pipeline plugin configuration.
```

### Plugin Analysis
```
Check if any installed plugins have known security vulnerabilities.
```
```
Analyze plugin dependencies and identify any conflicts.
```
```
Which plugins are currently disabled or having issues?
```

### Plugin Recommendations
```
Suggest plugins that would improve our CI/CD workflow.
```
```
What plugins should we consider for better security scanning?
```
```
Recommend plugins for improving our build performance.
```

## Node Management

### Node Status
```
Show me the status of all Jenkins nodes.
```
```
List all offline agents and why they're disconnected.
```
```
What's the current workload distribution across our nodes?
```

### Node Health
```
Check the health of all Jenkins agents.
```
```
Show me resource utilization (CPU, memory) for each node.
```
```
Which nodes are experiencing performance issues?
```

### Node Configuration
```
What labels and capabilities are configured for each node?
```
```
Show me the executor configuration across all nodes.
```
```
List environment variables set on specific nodes.
```

## Credential Management

### Credential Audit
```
List all credentials stored in Jenkins.
```
```
Which credentials are currently being used by our pipelines?
```
```
Show me when each credential was last accessed.
```

### Security Analysis
```
Analyze credential usage patterns for security risks.
```
```
Check for any exposed credentials in build logs.
```
```
Verify that sensitive credentials are properly secured.
```

### Access Control
```
Show me which users have access to which credentials.
```
```
List credentials that might need rotation.
```
```
Check credential permissions against security best practices.
```

## Advanced Deployment Strategies

### Blue-Green Deployment
```
Set up blue-green deployment for our web application using Jenkins.
```
```
Configure health checks for blue-green deployment validation.
```
```
Show me the current status of our blue-green environments.
```

### Canary Deployments
```
Configure canary deployment with progressive traffic shifting.
```
```
Monitor canary deployment metrics and health.
```
```
Set up automated rollback triggers for canary deployments.
```

### Rolling Updates
```
Configure rolling updates for our microservices deployment.
```
```
Set up staged rollout with validation between stages.
```
```
Monitor rolling deployment progress and health checks.
```

## Security Scanning

### Code Analysis
```
Configure SAST (Static Application Security Testing) in our pipeline.
```
```
Set up dependency vulnerability scanning for all projects.
```
```
Add container image security scanning to our build process.
```

### Compliance Checks
```
Run compliance checks against our Jenkins configuration.
```
```
Verify that our pipelines meet security requirements.
```
```
Check for any security policy violations in our setup.
```

### Security Monitoring
```
Monitor Jenkins audit logs for security events.
```
```
Check for any unauthorized access attempts.
```
```
Analyze build artifacts for security issues.
```

## Multi-Branch Pipeline Operations

### Branch Management
```
Show me all branches being built in our multi-branch pipeline.
```
```
Which branches have failing builds?
```
```
Configure branch-specific build behaviors.
```

### Pull Request Integration
```
Show status of all PR builds in our multi-branch pipeline.
```
```
Configure PR build validation requirements.
```
```
Set up automated PR feedback from build results.
```

### Pipeline Analytics
```
Show build statistics across all branches.
```
```
Compare build performance between different branches.
```
```
Analyze resource usage patterns in multi-branch builds.
```

## System Integration

### Tool Integration
```
Show me all configured tools in Jenkins.
```
```
Verify integration status with our source control system.
```
```
Check configuration of our artifact repository integration.
```

### Notification Systems
```
Configure Slack notifications for build events.
```
```
Set up email notifications for security events.
```
```
Integrate with our incident management system.
```

### External Services
```
Check connectivity to all integrated external services.
```
```
Monitor API rate limits with external services.
```
```
Verify webhook configurations and their status.
```

## Performance Optimization

### Build Performance
```
Analyze build times across all pipelines.
```
```
Identify bottlenecks in our build process.
```
```
Suggest ways to optimize our pipeline performance.
```

### Resource Utilization
```
Show me resource usage patterns across our Jenkins system.
```
```
Identify jobs consuming excessive resources.
```
```
Recommend optimal resource allocation for builds.
```

### Caching Strategy
```
Analyze effectiveness of our build caching.
```
```
Suggest improvements for artifact caching.
```
```
Configure distributed caching for builds.
```

## Backup and Disaster Recovery

### Backup Management
```
Verify status of Jenkins configuration backups.
```
```
Check completeness of our backup coverage.
```
```
Test restore procedures from latest backup.
```

### High Availability
```
Check status of Jenkins high availability setup.
```
```
Verify failover configuration.
```
```
Test disaster recovery procedures.
```

## Custom Metrics and Reporting

### Build Metrics
```
Generate build success rate trends by team.
```
```
Show deployment frequency metrics.
```
```
Calculate mean time to recovery for failed builds.
```

### Quality Metrics
```
Show code quality trends from our builds.
```
```
Generate test coverage reports across projects.
```
```
Analyze build stability metrics.
```

### Compliance Reporting
```
Generate security compliance reports.
```
```
Create audit reports for pipeline changes.
```
```
Show credential usage audit trails.
```
