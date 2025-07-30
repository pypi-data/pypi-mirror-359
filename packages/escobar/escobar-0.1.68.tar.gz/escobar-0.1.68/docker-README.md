# Escobar Docker Setup

This directory contains Docker configuration for running the Escobar JupyterLab extension in a containerized environment.

## Prerequisites

- Docker installed on your system
- Make utility (available by default on most Unix-based systems) or Docker Compose

## Quick Start

### Using Make

1. Build the Docker image:

   ```
   make build
   ```

2. Run the Docker container:

   ```
   make run
   ```

3. View the container logs (includes the JupyterLab URL with token):

   ```
   make logs
   ```

4. Access JupyterLab in your browser using the URL from the logs (typically http://localhost:8888)

5. Stop the container when done:
   ```
   make stop
   ```

### Using Docker Compose

1. Run the Docker container:

   ```
   docker-compose up -d
   ```

2. View the container logs:

   ```
   docker-compose logs -f
   ```

3. Stop the container when done:

   ```
   docker-compose down
   ```

## Configuration

The Docker setup uses environment variables from the `.env` file. Both the Makefile and Docker Compose automatically create a Docker-specific `.env` file in the `docker-config` directory with the following settings:

- `DEBUG=1` - Enables debug mode
- `SERVER_URL=ws://<host-ip>:8777/ws` - WebSocket server URL (automatically set to your host machine's IP)
- `DEMO_USERS=roman,gregory,yc` - List of demo users

## Makefile Targets

- `make build` - Build the Docker image
- `make run` - Run the Docker container
- `make stop` - Stop the running container
- `make logs` - View container logs
- `make clean` - Remove the container and image
- `make help` - Show help message

## Ports

- `8888` - JupyterLab web interface
- `8777` - WebSocket server for the Escobar extension

## Customization

To customize the configuration:

1. Edit the Makefile or docker-compose.yml to change port mappings or container names
2. Modify the Dockerfile to adjust the base image or dependencies
3. Update the environment variables in the Makefile's `run` target or in the docker-compose.yml file

## Troubleshooting

- If you encounter connection issues with the WebSocket server:

  - For Make: Ensure that the host IP is correctly detected in the Makefile. You may need to manually set the `HOST_IP` variable.
  - For Docker Compose: The container tries to use `host.docker.internal` or falls back to `172.17.0.1`. You may need to modify the command in docker-compose.yml to use your specific host IP.

- If JupyterLab fails to start:

  - For Make: Check the container logs with `make logs` for error messages.
  - For Docker Compose: Check the logs with `docker-compose logs -f` for error messages.

- If the extension doesn't appear in JupyterLab:
  - For Make: Try rebuilding the Docker image with `make clean build run`.
  - For Docker Compose: Try rebuilding with `docker-compose down && docker-compose build --no-cache && docker-compose up -d`.
