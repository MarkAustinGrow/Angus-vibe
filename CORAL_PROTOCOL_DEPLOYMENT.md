# Deploying the Coral Protocol Integration to Linode Server

This document provides instructions for deploying the Agent Angus Coral Protocol integration to the Linode server.

## Prerequisites

- SSH access to the Linode server
- Git access to the repository
- Docker and Docker Compose installed on the server

## Deployment Steps

### 1. SSH into the Linode Server

```bash
ssh root@angs.club
```

### 2. Navigate to the Angus Directory

```bash
cd /opt/angus
```

### 3. Upload the Deployment Script

You can upload the deployment script using SCP:

```bash
# From your local machine
scp deploy_coral_protocol.sh root@angs.club:/opt/angus/
```

### 4. Make the Deployment Script Executable

```bash
# On the Linode server
chmod +x deploy_coral_protocol.sh
```

### 5. Run the Deployment Script

```bash
# On the Linode server
./deploy_coral_protocol.sh
```

The deployment script will:
- Pull the latest changes from the Coral_protocol branch
- Rebuild the Docker images
- Restart the Docker containers
- Display the status of the containers
- Show the logs of the Coral Protocol adapter

### 6. Verify the Deployment

After the deployment script completes, you can verify that the Coral Protocol integration is running:

```bash
# Check the status of the containers
docker ps

# Check the logs of the Coral Protocol adapter
docker logs angus_coral_1
```

## Troubleshooting

### Container Fails to Start

If the Coral Protocol adapter container fails to start, check the logs:

```bash
docker logs angus_coral_1
```

Common issues include:
- Missing dependencies
- Configuration errors
- Connection issues with the Coral Protocol server

### Git Checkout Issues

If the deployment script fails to checkout the Coral_protocol branch, make sure:
- The branch exists in the remote repository
- You have the necessary permissions
- The local repository is not in a dirty state

You can manually checkout the branch:

```bash
git fetch
git checkout Coral_protocol
```

### Docker Build Issues

If the Docker build fails, check the build logs:

```bash
docker-compose build --no-cache
```

This will rebuild the images without using the cache, which can help identify issues.

## Monitoring and Maintenance

### Checking Logs

You can check the logs of the Coral Protocol adapter at any time:

```bash
docker logs angus_coral_1
```

To follow the logs in real-time:

```bash
docker logs -f angus_coral_1
```

### Restarting the Container

If you need to restart the Coral Protocol adapter:

```bash
docker-compose restart coral
```

### Updating the Integration

To update the integration with the latest changes:

```bash
# Pull the latest changes
git fetch
git checkout Coral_protocol
git pull

# Rebuild and restart the containers
docker-compose build coral
docker-compose up -d
```

## Conclusion

The Coral Protocol integration should now be running on your Linode server. You can interact with it through the Coral Protocol server by mentioning Agent Angus in a thread.
