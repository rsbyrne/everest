#!/bin/bash
WORKSPACE=$PWD/workspace
OUTPUTFILE=$WORKSPACE/"vm.output"
> $OUTPUTFILE
PYTHONADD="$1"
for PYTHONNAME in "${PYTHONADD[@]}"; do
    export PYTHONPATH=$PYTHONPATH:$PWD/$PYTHONNAME
done
jupyter lab \
  --no-browser --allow-root --port=9999 --ip='0.0.0.0' \
  --preferred-dir=$WORKSPACE \
  &> $OUTPUTFILE
