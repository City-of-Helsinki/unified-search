#!/bin/bash

set -e


if [[ "$APPLY_MIGRATIONS" = "1" ]]; then
    echo "Applying database migrations..."
    ./manage.py migrate --noinput
fi


if [[ "$INITIALIZE_DATA" = "1" ]]; then
    echo "TODO: Initializing data..."
    #./manage.py initialize_data
fi

# Start server
if [ ! -z "$@" ]; then
    "$@"
elif [ "$DEV_SERVER" = "1" ]; then
    python ./manage.py runserver 0.0.0.0:5001
else
    uwsgi --ini .prod/uwsgi.ini
fi
