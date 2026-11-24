#!/bin/sh
set -e
# Apply DB migrations, then start the API server
# (MODEL_TYPE=none: migrations don't need TensorFlow or the model loaded)
MODEL_TYPE=none flask --app wsgi db upgrade
exec gunicorn --workers "${GUNICORN_WORKERS:-2}" --threads 4 --bind 0.0.0.0:5000 \
    --timeout 120 --access-logfile - wsgi:app
