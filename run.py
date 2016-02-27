#!/usr/bin/env python

# This python script will read the output of `docker ps` from `ps.txt`
# and the output of `docker stats` from `stats.txt`. It will parse the
# stats output into json format and add docker and kubernetes metadata
# using the ps output. Finally, it will write out the stats json format
# to standard out.
#
# Example
# =======
# {
#   "net_output": "0 B",
#   "mem_percent": "0.59%",
#   "container": "97c0f191078a",
#   "kubernetes": {
#     "namespace_name": "default",
#     "pod_name": "dev-dev-merlin-mbhdi",
#     "container_name": "merlin"
#   },
#   "cpu_percent": "0.00%",
#   "net_input": "0 B",
#   "mem_usage": "153.4 MiB",
#   "mem_limit": "25.57 GiB",
#   "docker": {
#     "container_id": "97c0f191078a",
#     "container_name": "k8s_merlin.2bf98748_dev-dev-merlin-mbhdi_default_f89f3c23-7902-11e5-a5d3-42010af00034_e6ea7368"
#   }
# }

import re, json

# Regex pattern for `docker ps`.
# Example:
#   $ docker ps
#   CONTAINER ID   IMAGE                    COMMAND               CREATED       STATUS       PORTS                    NAMES
#   ac96c2533d8d   google/cadvisor:latest   "/usr/bin/cadvisor"   2 hours ago   Up 2 hours   0.0.0.0:8080->8080/tcp   cadvisor
ps_pattern = '^(\w+) {2,}([^ ]+) {2,}(".*) {2,}([\w\d ]+ago) {2,}(Up [\d\w ]+?) {2,}((?:[\d\.:\->tcp/udp]+(?:, )?)*) {2,}([\d\w\-_\.]+) *$'
ps_matcher = re.compile(ps_pattern)

# Read `docker ps` output from file and parse using regex.
ps = []
with open('ps.txt', 'r') as f:
    for line in f.readlines():
        m = ps_matcher.match(line)
        if m:
            ps.append({
              "container": m.group(1),
              "image": m.group(2),
              "command": m.group(3),
              "created": m.group(4),
              "status": m.group(5),
              "ports": m.group(6),
              "name": m.group(7)
            })

# Regex pattern for `docker stats`.
# Example:
#   $ docker stats --no-stream $(docker ps -q)
#   CONTAINER      CPU %    MEM USAGE/LIMIT   MEM %   NET I/O
#   72866f2f73e4   12.34%   89.54 MB/2.1 GB   4.26%   938.7 kB/6.91 MB
stats_pattern = '^(\w+) {2,}([\d\.]+%) {2,}([\d\.]+ \w*B)/([\d\.]+ \w*B) {2,}([\d\.]+%) {2,}([\d\.]+ \w*B)/([\d\.]+ \w*B)$'
stats_matcher = re.compile(stats_pattern)

# Read `docker stats` output from file and parse using regex.
stats = []
with open('stats.txt', 'r') as f:
    for line in f.readlines():
        m = stats_matcher.match(line)
        if m:
            stats.append({
              "container": m.group(1),
              "cpu_percent": m.group(2),
              "mem_usage": m.group(3),
              "mem_limit": m.group(4),
              "mem_percent": m.group(5),
              "net_input": m.group(6),
              "net_output": m.group(7)
            })

# Create mapping from container id to docker info
id_to_docker = {}
for container in ps:
    id = container['container']
    docker = {
      "container_id": id,
      "container_name": container['name']
    }
    id_to_docker[id] = docker

# Regex pattern for kubernetes metadata in container name
# Example:
#   k8s_spark-worker.aeca32c6_spark-worker-controller-72eu2_default_da92bcde-7415-11e5-a5d3-42010af00034_a95e4f20
name_pattern = 'k8s_(.+)\.[a-z0-9]+_([^\._]+)_([^_]+)_[\w\d\-_]+'
name_matcher = re.compile(name_pattern)

# Create mapping from container id to kubernetes info
id_to_kubernetes = {}
for container in ps:
    id = container['container']
    name = container['name']
    m = name_matcher.match(name)
    #print name
    if m:
        kubernetes = {
            'container_name': m.group(1),
            'pod_name': m.group(2),
            'namespace_name': m.group(3)
        }
    else:
        kubernetes = {}
    id_to_kubernetes[id] = kubernetes

# Add docker and kubernetes info to stats
for stat in stats:
    id = stat['container']
    stat['docker'] = id_to_docker[id]
    stat['kubernetes'] = id_to_kubernetes[id]

# Print stats to standard out in json format
for stat in stats:
    print json.dumps(stat)

