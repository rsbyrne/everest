#!/bin/bash
PYTHONADD="$1"
for PYTHONNAME in "${PYTHONADD[@]}"; do
    export PYTHONPATH=$PYTHONPATH:$PWD/$PYTHONNAME
done
jupyter lab --no-browser --allow-root --port=9999 --ip='0.0.0.0'