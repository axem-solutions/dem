#!/bin/bash

echo "Cleanup"

rm -rf env

echo "Create python virtuel env"

python3.10 -m venv env

source env/bin/activate
pip install -r requirements.txt

python3.10 -m dem list --local --env
python3.10 -m pytest tests

deactivate




