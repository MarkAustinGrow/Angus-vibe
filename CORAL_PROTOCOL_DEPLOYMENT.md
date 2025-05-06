# Deploying Coral Protocol Integration to Production

This document provides instructions for deploying the Coral Protocol integration to a production server.

## Prerequisites

- Access to the production server (e.g., Linode)
- Git installed on the server
- Docker and Docker Compose installed on the server
- Proper permissions to pull from the GitHub repository and manage Docker containers

## Deployment Options

### Option 1: Using the Deployment Script

We've provided a deployment script that automates the process of pulling the latest changes and rebuilding the Docker containers.

1. Copy the `deploy_coral_protocol.sh` script to your server:
   ```bash
   scp deploy_coral_protocol.sh user@your-server:/opt/angus/
   ```

2. Make the script executable:
   ```bash
   ssh user@your-server "chmod +x /opt/angus/deploy_coral_protocol.sh"
   ```

3. Run the script:
   ```bash
   ssh user@your-server "cd /opt/angus && ./deploy_coral_protocol.sh"
   ```

### Option 2: Manual Deployment

If you prefer to deploy manually, follow these steps:

1. SSH into your server:
   ```bash
   ssh user@your-server
   ```

2. Navigate to the Angus directory:
   ```bash
   cd /opt/angus
   ```

3. Fetch the latest changes:
   ```bash
   git fetch origin
   ```

4. Checkout the `coral_protocol_langchain` branch:
   ```bash
   git checkout coral_protocol_langchain
   ```

5. Pull the latest changes:
   ```bash
   git pull origin coral_protocol_langchain
   ```

6. Stop the current Docker containers:
   ```bash
   docker-compose down
   ```

7. Rebuild the Docker containers:
   ```bash
   docker-compose build
   ```

8. Start the containers:
   ```bash
   docker-compose up -d
   ```

9. Check the status of the containers:
   ```bash
   docker ps
   ```

## Verifying the Deployment

After deploying the Coral Protocol integration, you should verify that it's working correctly:

1. Check the logs of the containers:
   ```bash
   docker logs angus_angus_1
   docker logs angus_web_1
   ```

2. Look for messages indicating successful connection to the Coral Protocol server:
   ```
   INFO - Connected to MCP server at http://coral.pushcollective.club/sse
   ```

3. Run the Coral Protocol integration test:
   ```bash
   docker exec -it angus_angus_1 python run_coral_test.py
   ```

## Troubleshooting

### Connection Issues

If you're having trouble connecting to the Coral Protocol server, check the following:

1. Make sure the server is accessible from your production server:
   ```bash
   curl http://coral.pushcollective.club/sse
   ```

2. Check the environment variables in your Docker Compose file:
   ```bash
   grep CORAL_SERVER_URL docker-compose.yml
   ```

3. Check the logs for any error messages:
   ```bash
   docker logs angus_angus_1 | grep "Failed to connect"
   ```

### Docker Issues

If you're having issues with Docker, try the following:

1. Check the Docker service status:
   ```bash
   systemctl status docker
   ```

2. Restart Docker:
   ```bash
   systemctl restart docker
   ```

3. Check Docker Compose version:
   ```bash
   docker-compose --version
   ```

### Git Issues

If you're having issues with Git, try the following:

1. Check your Git configuration:
   ```bash
   git config --list
   ```

2. Make sure you have the correct remote:
   ```bash
   git remote -v
   ```

3. Try fetching with verbose output:
   ```bash
   git fetch -v origin
   ```

## Rolling Back

If you need to roll back to a previous version, you can checkout the previous branch and rebuild the containers:

```bash
git checkout previous_branch
docker-compose down
docker-compose build
docker-compose up -d
```

## Monitoring

After deployment, you should monitor the system to ensure it's working correctly:

1. Check the container logs periodically:
   ```bash
   docker logs -f angus_angus_1
   ```

2. Monitor system resources:
   ```bash
   docker stats
   ```

3. Set up alerts for any critical errors in the logs.

## Conclusion

By following these instructions, you should be able to successfully deploy the Coral Protocol integration to your production server. If you encounter any issues, refer to the troubleshooting section or contact the development team for assistance.
