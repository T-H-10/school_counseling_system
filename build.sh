#!/usr/bin/env bash
# Render build script. Migrations run separately in preDeployCommand.
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --noinput
