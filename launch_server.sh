#!/bin/bash
cd "$(dirname "$0")"
. ./django-venv/bin/activate

gunicorn --user=louise --group=louise -b 127.0.0.1:18001 rss_test.wsgi
