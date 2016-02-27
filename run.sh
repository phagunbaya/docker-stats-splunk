#!/bin/sh

# This bash script will write the output of `docker ps` to `ps.txt`
# and the output of `docker stats` to `stats.txt`. It will then call
# the python script to parse these stats into json format and write
# to standard out. It will repeat this every second for eternity.
#
# TODO this logic should be merged in to the python script, and should
# use the docker remote api, which is more featured than the cli.

while sleep 1; do
  docker ps > ps.txt
  #TODO --no-stream option is only available in docker client version >=1.8
  #In the mean time, using a workaround to kill the stream
  #docker stats --no-stream $(docker ps -q) > stats.txt
  rm -f stats.txt
  docker stats $(docker ps -q) > stats.txt &
  while [ ! -s stats.txt ]; do sleep 0.1; done
  kill $!
  wait $! 2>/dev/null
  python run.py
done
