# Supported Jenkins MCP Server Operations

This document provides example prompts that are fully supported by the Jenkins MCP server implementation.

## Job Management

### Listing Jobs
```
Show me all Jenkins jobs.
```
```
List all jobs in the "production" folder.
```
```
Show me all jobs, including disabled ones.
```

### Job Details
```
Show me the details of the "my-app-pipeline" job.
```
```
Get information about "deploy-job" including its recent builds.
```
```
What's the configuration of the "nightly-backup" job?
```

### Creating Jobs
```
Create a freestyle job named "build-app" with this description: "Builds the main application".
```
```
Create a new pipeline job called "deploy-pipeline" in the "production" folder.
```
```
Set up a basic pipeline for building and testing a Java application.
```

### Updating Pipelines
```
Update the "my-app-pipeline" script to add a test stage.
```
```
Modify the "deploy-pipeline" to include a new deployment step.
```
```
Update the build configuration of "test-pipeline".
```

## Build Operations

### Triggering Builds
```
Trigger a build of the "my-app-pipeline" job.
```
```
Start a build of "deploy-job" with version parameter set to "1.2.0".
```
```
Run the "integration-tests" job with custom parameters.
```

### Build Status
```
What's the status of the latest build of "my-app-pipeline"?
```
```
Show me the status of build #42 for "deploy-job".
```
```
Is the current build of "test-pipeline" still running?
```

### Build Logs
```
Show me the logs from the latest build of "my-app-pipeline".
```
```
Get the console output from build #42 of "deploy-job".
```
```
Display the error logs from the failed build of "test-pipeline".
```

### Build Analytics
```
Analyze the build performance of "my-app-pipeline".
```
```
Show me the success rate and duration trends for "deploy-job".
```
```
What are the common failure points in our pipeline builds?
```

## System Information

### Server Status
```
What's the current status of the Jenkins server?
```
```
Show me the system information for our Jenkins instance.
```
```
Get detailed information about the Jenkins configuration.
```

### Queue Management
```
What builds are currently in the queue?
```
```
Show me the build queue status.
```
```
Are there any builds waiting to be executed?
```

### System Analysis
```
Analyze the overall health of our Jenkins system.
```
```
Check for any performance bottlenecks in our Jenkins setup.
```
```
Show me resource utilization metrics for Jenkins.
```

## Best Practices

### Performance Optimization
```
How can I optimize the performance of "my-app-pipeline"?
```
```
Analyze the build times of our pipelines and suggest improvements.
```
```
What can we do to reduce build queue waiting times?
```

### Configuration Review
```
Review the configuration of "my-app-pipeline" for best practices.
```
```
Check if our pipeline configurations follow Jenkins best practices.
```
```
Suggest improvements for our build job configurations.
```
