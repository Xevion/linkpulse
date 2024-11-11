#!/usr/bin/env bash

# Check whether CWD is 'backend'
if [ "$(basename "$(pwd)")" != "backend" ]; then
    echo "error: This script must be run from the 'backend' directory."
    exit 1
fi

# Default to development mode if not defined
export ENVIRONMENT=${ENVIRONMENT:-development}
export LOG_JSON_FORMAT=${LOG_JSON_FORMAT:-false}
export LOG_LEVEL=${LOG_LEVEL:-debug}
COMMAND="poetry run python3 -m linkpulse $@"

# If arguments start with 'poetry run pytest' or 'pytest' use args as is
if [[ "$1" == "poetry" && "$2" == "run" && "$3" == "pytest" ]]; then
    COMMAND=$@
elif [[ "$1" == "pytest" ]]; then
    COMMAND=$@
fi

# Check if Railway CLI is available
RAILWAY_AVAILABLE=false
if command -v railway &>/dev/null; then
    RAILWAY_AVAILABLE=true
fi

# Check if .env file exists
ENV_FILE_EXISTS=false
if [ -f .env ]; then
    ENV_FILE_EXISTS=true
fi

# Check if DATABASE_URL is defined
DATABASE_DEFINED=false
if [ -n "$DATABASE_URL" ]; then
    DATABASE_DEFINED=true
else
    if $ENV_FILE_EXISTS; then
        if grep -E '^DATABASE_URL=.+' .env &>/dev/null; then
            DATABASE_DEFINED=true
        fi
    fi
fi

# Check if Railway project is linked
PROJECT_LINKED=false
if $RAILWAY_AVAILABLE; then
    if railway status &>/dev/null; then
        PROJECT_LINKED=true
    fi
fi

if $DATABASE_DEFINED; then
    $COMMAND
else
    if $RAILWAY_AVAILABLE; then
        if $PROJECT_LINKED; then
            DATABASE_URL="$(railway variables --service Postgres --environment development --json | jq .DATABASE_PUBLIC_URL -cMr)" $COMMAND
        else
            echo "error: Railway project not linked."
            echo "Run 'railway link' to link the project."
            exit 1
        fi

    else
        echo "error: Could not find DATABASE_URL environment variable."
        echo "Install the Railway CLI and link the project, or create a .env file with a DATABASE_URL variable."
        exit 1
    fi
fi
