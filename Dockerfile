FROM ubuntu:22.04

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

# Install Python and ZFS utilities
RUN apt-get update && \
    apt-get install -y python3 python3-pip zfsutils-linux curl wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the Python script into the container
COPY zfs_exporter.py /zfs_exporter.py

# Expose the port where Prometheus will scrape metrics
EXPOSE 9134

# Command to run the exporter
CMD ["python3", "/zfs_exporter.py"]