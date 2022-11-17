#!/bin/bash
MOUNTFROM=$PWD
MOUNTTO='/home/morpheus/workspace/mount'
IMAGE='rsbyrne/everest'
SOCK='/var/run/docker.sock'
docker run -v $MOUNTFROM:$MOUNTTO -v $SOCK:$SOCK --shm-size 2g -p 9999:9999 $IMAGE \
  jupyter lab --no-browser --allow-root --port=9999 --ip='0.0.0.0'
