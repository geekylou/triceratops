#!/bin/bash
cd "$(dirname "$0")"
. ./django-venv/bin/activate

export LC_ALL="en_GB.UTF-8"

gunicorn --user=louise --group=louise -b 127.0.0.1:18001 rss_test.wsgi
