#!/bin/bash
currentDir=$PWD
cd "$(dirname "$0")"
docker build -t rsbyrne/scibase:latest .
docker push rsbyrne/scibase:latest
cd $currentDir
