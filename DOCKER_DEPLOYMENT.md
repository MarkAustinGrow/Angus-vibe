# Docker Deployment Guide for Agent Angus

This guide provides instructions for deploying Agent Angus in a Docker container on a Linode server.

## Prerequisites

- A Linode server with SSH access
- Docker and Docker Compose installed on the server
- YouTube API credentials (client ID, client secret, API key, channel ID)
- Supabase credentials (URL, key)
- OpenAI API key

## Deployment Steps

### 1. Local Authentication Setup

Before deploying to Linode, you need to generate a YouTube authentication token locally:

1. Clone the Agent Angus repository to your local machine
2. Create a `.env` file with all required credentials
3. Create a `data` directory in the project root:
   ```bash
   mkdir -p data
   ```
4. Run Agent Angus locally to authenticate with YouTube:
   ```bash
   python angus.py --upload --limit 1
   ```
5. This will prompt you to visit a URL, authorize the application, and enter the authorization code
6. After successful authentication, a `token.pickle` file will be generated (it might be in the project root or in the `data` directory)
7. If you can't find the token.pickle file, check the logs for a message like "Saved credentials to [path]"

### 2. Server Setup

1. SSH into your Linode server:
   ```bash
   ssh user@your-linode-ip
   ```

2. Install Docker and Docker Compose if not already installed:
   ```bash
   sudo apt update
   sudo apt install -y docker.io docker-compose
   sudo systemctl enable docker
   sudo systemctl start docker
   sudo usermod -aG docker $USER
   ```
   
3. Log out and log back in for the group changes to take effect:
   ```bash
   exit
   ssh user@your-linode-ip
   ```

4. Create a directory for Agent Angus:
   ```bash
   mkdir -p ~/angus/data
   cd ~/angus
   ```

### 3. File Transfer

1. From your local machine, copy the Agent Angus files to the Linode server:
   ```bash
   scp -r * user@your-linode-ip:~/angus/
   ```

2. Find and copy the authentication token to the server's data directory:
   ```bash
   # If token.pickle is in the project root
   scp token.pickle user@your-linode-ip:~/angus/data/
   
   # If token.pickle is in the data directory
   scp data/token.pickle user@your-linode-ip:~/angus/data/
   
   # If token.pickle is in a different location (replace [path] with the actual path)
   scp [path]/token.pickle user@your-linode-ip:~/angus/data/
   ```

3. Copy the environment variables file:
   ```bash
   scp .env user@your-linode-ip:~/angus/
   ```

4. Copy any hidden files (like .dockerignore):
   ```bash
   scp .dockerignore user@your-linode-ip:~/angus/
   ```

### 4. Docker Deployment

1. On the Linode server, navigate to the Agent Angus directory:
   ```bash
   cd ~/angus
   ```

2. Build the Docker image:
   ```bash
   docker-compose build
   ```

3. Start the container:
   ```bash
   docker-compose up -d
   ```

4. Check the logs to ensure everything is running correctly:
   ```bash
   docker-compose logs -f
   ```

## Maintenance

### Viewing Logs

```bash
docker-compose logs -f
```

### Restarting the Container

```bash
docker-compose restart
```

### Stopping the Container

```bash
docker-compose down
```

### Updating Agent Angus

1. Pull the latest code or make your changes
2. Rebuild and restart the container:
   ```bash
   docker-compose down
   docker-compose build
   docker-compose up -d
   ```

## Troubleshooting

### Authentication Issues

If you encounter authentication issues:

1. Delete the existing token.pickle file locally:
   ```bash
   rm token.pickle
   rm data/token.pickle  # If it exists in the data directory
   ```

2. Generate a new token.pickle file locally:
   ```bash
   python angus.py --upload --limit 1
   ```
   This will prompt you to visit a URL, authorize the application, and enter the authorization code.

3. If you see an error like "invalid_grant: Bad Request", this means the previous token was invalid or expired. The new authentication flow should have generated a new token.pickle file.

4. Copy the new token.pickle file to the server's data directory:
   ```bash
   scp token.pickle user@your-linode-ip:~/angus/data/
   ```
   or
   ```bash
   scp data/token.pickle user@your-linode-ip:~/angus/data/
   ```
   depending on where the new token was saved.

5. Restart the container:
   ```bash
   docker-compose restart
   ```

### Container Not Starting

Check the logs for errors:
```bash
docker-compose logs
```

### Persistent Storage

All persistent data is stored in the `./data` directory, which is mounted as a volume in the container. This includes:

- YouTube authentication token (`token.pickle`)
- Log files

## Security Considerations

- The `.env` file contains sensitive API keys and credentials. Ensure it has restricted permissions:
  ```bash
  chmod 600 .env
  ```

- The `.env` file is included in `.dockerignore` to prevent sensitive information from being built into the Docker image. Instead, the environment variables are passed to the container at runtime through the `env_file` setting in `docker-compose.yml`.

- Regularly rotate API keys and credentials.

- For production environments, consider using Docker secrets instead of environment variables:
  ```bash
  # Create a secret
  echo "your-api-key" | docker secret create openai_api_key -
  
  # Use the secret in docker-compose.yml
  secrets:
    - openai_api_key
  ```
