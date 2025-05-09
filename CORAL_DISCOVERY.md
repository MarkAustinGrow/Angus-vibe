# Coral Protocol Discovery

This document describes how to use the Coral Protocol discovery scripts to test the integration between Angus and the Coral Protocol.

## Overview

The Coral Protocol discovery scripts allow you to:

1. Discover agents on the Coral Protocol server
2. Retrieve agent capabilities
3. Find specific agents (like Yona)

The scripts are designed to handle dynamic session IDs, which change each time the Docker container is restarted.

## Scripts

### docker_test_discovery.py

This is the main Python script that performs the discovery and capabilities retrieval. It can be run directly, but it's recommended to use one of the wrapper scripts.

```bash
python3 docker_test_discovery.py [options]
```

Options:
- `--server-url`: URL of the Coral Protocol server
- `--session-id`: Session ID for the Coral Protocol server
- `--container-name`: Name of the Docker container running the Coral Protocol server
- `--log-file`: Path to the log file in the container

### run_coral_discovery_docker.sh (Linux/macOS)

This script extracts the session ID from Docker logs and runs the discovery script with the extracted session ID.

```bash
./run_coral_discovery_docker.sh [options]
```

Options:
- `--container-name`: Name of the Docker container running the Coral Protocol server
- `--server-url`: URL of the Coral Protocol server
- `--session-id`: Session ID for the Coral Protocol server (if you want to specify it manually)

### run_coral_discovery_docker.bat (Windows)

This is the Windows version of the wrapper script.

```batch
run_coral_discovery_docker.bat [options]
```

Options are the same as for the Linux/macOS version.

### run_coral_discovery_in_container.sh

This script is designed to be run inside the Docker container. It extracts the session ID from the container's logs and runs the discovery script.

```bash
./run_coral_discovery_in_container.sh [options]
```

Options:
- `--server-url`: URL of the Coral Protocol server
- `--session-id`: Session ID for the Coral Protocol server (if you want to specify it manually)
- `--log-file`: Path to the log file in the container

## Usage Examples

### Running from the Host Machine

To run the discovery script from the host machine:

```bash
# Linux/macOS
./run_coral_discovery_docker.sh

# Windows
run_coral_discovery_docker.bat
```

This will extract the session ID from the Docker logs and run the discovery script.

### Running Inside the Container

To run the discovery script inside the Docker container:

```bash
# Copy the scripts to the container
docker cp docker_test_discovery.py app_angus_coral_1:/app/
docker cp run_coral_discovery_in_container.sh app_angus_coral_1:/app/

# Make the script executable
docker exec app_angus_coral_1 chmod +x /app/run_coral_discovery_in_container.sh

# Run the script
docker exec app_angus_coral_1 /app/run_coral_discovery_in_container.sh
```

### Specifying the Session ID Manually

If you know the session ID, you can specify it manually:

```bash
# Linux/macOS
./run_coral_discovery_docker.sh --session-id 9c7b154f-cd07-43de-914a-639b449f2b8c

# Windows
run_coral_discovery_docker.bat --session-id 9c7b154f-cd07-43de-914a-639b449f2b8c

# Inside the container
./run_coral_discovery_in_container.sh --session-id 9c7b154f-cd07-43de-914a-639b449f2b8c
```

### Using a Different Container Name

If your Docker container has a different name:

```bash
# Linux/macOS
./run_coral_discovery_docker.sh --container-name my_container_name

# Windows
run_coral_discovery_docker.bat --container-name my_container_name
```

### Using a Different Server URL

If you're using a different Coral Protocol server:

```bash
# Linux/macOS
./run_coral_discovery_docker.sh --server-url http://my-server.com/devmode/default-app/default-key/session1/sse

# Windows
run_coral_discovery_docker.bat --server-url http://my-server.com/devmode/default-app/default-key/session1/sse

# Inside the container
./run_coral_discovery_in_container.sh --server-url http://my-server.com/devmode/default-app/default-key/session1/sse
```

## Troubleshooting

### Session ID Not Found

If the script can't find the session ID:

1. Make sure the Docker container is running
2. Check the Docker logs to see if the session ID is being printed
3. Try specifying the session ID manually

```bash
docker logs app_angus_coral_1 | grep "Extracted session ID"
```

### Connection Issues

If the script can't connect to the Coral Protocol server:

1. Make sure the server URL is correct
2. Check if the server is running
3. Check if the Docker container has network access to the server

### Agent Not Found

If the script can't find the Yona agent:

1. Make sure the Yona agent is registered with the Coral Protocol server
2. Check if the Yona agent's name contains "yona" (case-insensitive)
3. Try running the script again after a few seconds (the agent might still be registering)

## Future Improvements

1. Add support for calling functions on discovered agents
2. Add support for registering functions with the Coral Protocol server
3. Add support for handling multiple sessions
4. Add support for discovering agents by capability
5. Add support for discovering agents by DID
