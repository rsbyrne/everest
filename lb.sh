#!/bin/bash
# exit when any command fails
set -e
MOUNTTO='/home/morpheus/workspace'
MOUNTFROM=$PWD
while getopts m:c: flag
do
    case "${flag}" in
        m) MOUNTFROM=${OPTARG};;
        c) CAPTURES+=${OPTARG};;
        p) PYTHONADD+=${OPTARG};;
    esac
done
mkdir -p $MOUNTFROM
chmod o+rw $MOUNTFROM
for CAPTURED in "${CAPTURES[@]}"; do
    CAPTURED=$PWD/$CAPTURED
    chown -R 15215 $CAPTURED
    chgrp -R 17932 $CAPTURED
done
IMAGE='rsbyrne/everest:latest'
SOCK='/var/run/docker.sock'
echo $MOUNTFROM
docker run \
  -v $MOUNTFROM:$MOUNTTO -v $SOCK:$SOCK \
  --shm-size 2g -p 9999:9999 \
  $IMAGE \
  ls workspace
#  workspace/mount/everest/init.sh $PYTHONADD
