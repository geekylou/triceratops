#!/bin/bash
cd "$(dirname "$0")"

. ./django-venv/bin/activate

python get_feed.py >/dev/null
