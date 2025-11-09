#!/usr/bin/env bash
set -e

# Load environment variables
export $(grep -v '^#' .env | xargs)

# Start API
uvicorn apps.api.server:app --host 0.0.0.0 --port 8080
