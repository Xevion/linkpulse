#!/usr/bin/env bash

# Check whether CWD is 'frontend'
if [ "$(basename "$(pwd)")" != "frontend" ]; then
    echo "error: This script must be run from the 'frontend' directory."
    exit 1
fi

export VITE_BACKEND_TARGET=${VITE_BACKEND_TARGET:-localhost:8000}
pnpm run dev