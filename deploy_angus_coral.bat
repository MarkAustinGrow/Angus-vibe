@echo off
REM Deployment script for Agent Angus with Coral Protocol integration (Windows)

echo Deploying Agent Angus with Coral Protocol integration...

REM Check if Docker and Docker Compose are installed
where docker >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Docker is not installed. Please install Docker first.
    exit /b 1
)

where docker-compose >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Docker Compose is not installed. Please install Docker Compose first.
    exit /b 1
)

REM Pull the latest changes from the repository
echo Pulling latest changes from the repository...
git pull

REM Build the Docker images
echo Building Docker images...
docker-compose build angus-coral

REM Stop any existing containers
echo Stopping existing containers...
docker-compose stop angus-coral

REM Start the new containers
echo Starting new containers...
docker-compose up -d angus-coral

REM Display the logs
echo Deployment complete. Displaying logs...
docker-compose logs -f angus-coral
