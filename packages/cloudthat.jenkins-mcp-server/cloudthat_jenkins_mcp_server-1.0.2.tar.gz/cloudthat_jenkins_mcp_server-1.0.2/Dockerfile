# Jenkins MCP Server - Docker Image
# Author: Saurabh Kumar Jain (skj@cloudthat.com)
# Repository: https://gitlab.cloudthat.com/cloudthat-oss/jenkins_mcp.git

FROM python:3.11-slim

# Set labels for CloudThat branding
LABEL maintainer="Saurabh Kumar Jain <skj@cloudthat.com>" \
      org.opencontainers.image.title="Jenkins MCP Server" \
      org.opencontainers.image.description="CloudThat Jenkins MCP Server for AI-driven DevOps" \
      org.opencontainers.image.authors="Saurabh Kumar Jain <skj@cloudthat.com>" \
      org.opencontainers.image.vendor="CloudThat Technologies Pvt. Ltd." \
      org.opencontainers.image.source="https://gitlab.cloudthat.com/cloudthat-oss/jenkins_mcp.git" \
      org.opencontainers.image.licenses="Proprietary"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd --gid 1000 cloudthat && \
    useradd --uid 1000 --gid cloudthat --shell /bin/bash --create-home cloudthat

# Set working directory
WORKDIR /app

# Upgrade pip first
RUN pip install --no-cache-dir --upgrade pip

# Install Python dependencies directly
RUN pip install --no-cache-dir \
    loguru>=0.7.0 \
    "mcp[cli]>=1.6.0" \
    pydantic>=2.10.6 \
    httpx>=0.27.0 \
    python-jenkins>=1.8.0 \
    jenkinsapi>=0.3.14 \
    cachetools>=5.3.0 \
    tenacity>=8.2.0 \
    python-dotenv>=1.0.1

# Copy application code
COPY jenkins_mcp_server/ ./jenkins_mcp_server/
COPY README.md LICENSE ./

# Create necessary directories and set permissions
RUN mkdir -p logs tmp && \
    chown -R cloudthat:cloudthat /app

# Switch to non-root user
USER cloudthat

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import jenkins_mcp_server; print('✅ OK')" || exit 1

# Default command
ENTRYPOINT ["python", "-m", "jenkins_mcp_server"]
CMD ["--help"]
