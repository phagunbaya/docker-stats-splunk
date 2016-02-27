
FROM ubuntu:14.04

# Disable prompts from apt.
ENV DEBIAN_FRONTEND noninteractive

# Install prerequisites.
RUN apt-get update && \
    apt-get install -y -q curl python && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Install Docker client.
ENV DOCKER_VERSION 1.6.2
RUN curl -sSL -O https://get.docker.com/builds/Linux/x86_64/docker-${DOCKER_VERSION} && \
    chmod +x docker-${DOCKER_VERSION} && \
    mv docker-${DOCKER_VERSION} /usr/local/bin/docker

# Copy the monitor scripts.
COPY run.sh /run.sh
COPY run.py /run.py

# Run the monitor script.
ENTRYPOINT ["/run.sh"]
