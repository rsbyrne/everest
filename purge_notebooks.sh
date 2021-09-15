#!/bin/bash
python3 -m nbconvert --clear-output "$(dirname "$0")"/*.ipynb
