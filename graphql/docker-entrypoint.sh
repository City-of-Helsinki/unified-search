#!/bin/bash

set -e

export NODE_OPTIONS="--max-http-header-size=16384"
# Start server
if [[ ! -z "$@" ]]; then
    "$@"
elif [[ "$DEV_SERVER" = "1" ]]; then
    npm start
else
    npm run serve
fi
