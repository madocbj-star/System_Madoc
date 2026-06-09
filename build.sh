#!/usr/bin/env bash
set -o errexit

apt-get update -qq
apt-get install -y -qq libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev libcairo2

pip install -r requirements.txt