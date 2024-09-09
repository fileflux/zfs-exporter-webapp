
# ZFS Exporter Web Application

## Overview
This is a Python-based web application designed to expose ZFS pool metrics for Prometheus scraping. It gathers ZFS pool information, such as total capacity, available space, and pool status, so that Promethus can scrape this information and display it via Grafana. The app uses `zfsutils-linux` to interact with the ZFS pools and is designed for easy deployment via Docker.

## Features
- Expose ZFS pool metrics via a `/metrics` API endpoint.
- Serve ZFS data in a format compatible with Prometheus for monitoring.
- Dockerized for easy deployment.
- Includes custom readiness and liveness probes for Kubernetes to ensure high availability.
- GitHub Actions CI/CD workflow to build a multi-platform container image and push it to DockerHub.
- Integrated security scanning of the container image using Trivy.

## Prerequisites
To run this application locally or in a container, you need:
- Python 3.x
- ZFS installed on the system (`zfsutils-linux` for Linux distributions)
- Prometheus (for scraping metrics)
- Docker (for containerization)

Install the dependencies locally by running:
```bash
sudo apt-get install zfsutils-linux python3
```

## Repository Structure

```plaintext
fileflux-zfs-exporter-webapp/
├── Dockerfile             
├── README.md               
├── zfs_exporter.py         
├── liveness.sh             
├── readiness.sh           
```

### What Each File Does
- **docker.yaml**: Contains the GitHub Actions workflow for building and pushing the multi-platform container image to DockerHub and scanning it for vulnerabilities using Trivy.

- **zfs_exporter.py**: The core of the web application. It exposes a `/metrics` endpoint that Prometheus can scrape to collect ZFS pool statistics. It gathers information about ZFS pools and serves them in a Prometheus-compatible format.

- **Dockerfile**: Configuration for building the Docker image. It installs the required Python dependencies and ZFS utilities, and then runs the `zfs_exporter.py` script.

- **liveness.sh**: Liveness probe script to verify that the application is running properly. Kubernetes uses this to check the application's health.

- **readiness.sh**: Readiness probe script to ensure that the application is ready to handle traffic. Kubernetes uses this to determine if the app is ready to serve requests.

## Building the Docker Image

To build the Docker image for this web app:

1. Clone the repository:
   ```bash
   git clone https://github.com/fileflux/zfs-exporter-webapp.git
   cd fileflux-zfs-exporter-webapp
   ```

2. Build the Docker image:
   ```bash
   docker build -t zfs-exporter .
   ```

## Probes

This web app includes Kubernetes health probes:

- **Liveness Probe**: Ensures that the container is still running. If this probe fails, Kubernetes will restart the container.
  ```bash
  ./liveness.sh
  ```

- **Readiness Probe**: Ensures that the app is ready to serve traffic. If this probe fails, Kubernetes will stop sending requests to the container.
  ```bash
  ./readiness.sh
  ```

Both scripts are designed to return appropriate status codes to Kubernetes based on the application's health.

## GitHub Workflow (including Trivy)

A GitHub Actions workflow is included to automate the build process. The workflow builds a multi-platform container image for AMD64 and ARM-based systems and pushes the image to DockerHub. This workflow also integrates `Trivy`, a vulnerability scanning tool, to scan the container image and ensure it is secure.

This workflow:
1. Checks the code and accesses DockerHub.
2. Builds and pushes multi-platform Docker images for AMD64 and ARM to DockerHub using the Dockerfile in the repository.
3. Runs a security scan on the Docker image using `Trivy`.
4. Logs out from DockerHub.

## Usage

Once the app is running, Prometheus can send a GET request to the `/metrics` endpoint to collect ZFS pool metrics. Example metrics exposed:

```plaintext
# HELP zfs_pool_capacity Total capacity of the ZFS pool
# TYPE zfs_pool_capacity gauge
zfs_pool_capacity{pool="zpool1"} 500000000000

# HELP zfs_pool_available Available space in the ZFS pool
# TYPE zfs_pool_available gauge
zfs_pool_available{pool="zpool1"} 250000000000
```

## Additional Notes
- Ensure that ZFS is installed and running on the host machine or within the container.
- The liveness and readiness probes are useful when deploying the app in a Kubernetes environment to ensure high availability.
