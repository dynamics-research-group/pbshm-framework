#!/bin/bash

set -e # Exit on error
set -u # Exit on unset variables

# usage: file_env VAR [DEFAULT]
#    ie: file_env 'XYZ_DB_PASSWORD' 'example'
# (will allow for "$XYZ_DB_PASSWORD_FILE" to fill in the value of
#  "$XYZ_DB_PASSWORD" from a file, especially for Docker's secrets feature)
file_env() {
  local var="$1"
  local fileVar="${var}_FILE"
  local def="${2:-}"
  if [ "${!var:-}" ] && [ "${!fileVar:-}" ]; then
    echo >&2 "error: both $var and $fileVar are set (but are exclusive)"
    exit 1
  fi
  local val="$def"
  if [ "${!var:-}" ]; then
    val="${!var}"
  elif [ "${!fileVar:-}" ]; then
    val="$(<"${!fileVar}")"
  fi
  export "$var"="$val"
  unset "$fileVar"
}

# Set Flask environment variables
export FLASK_APP=rosehips

# Flag file to indicate initialisation has been done already
INIT_FLAG="$HOME/.pbshm_framework_initialised"

# Check if initialisation has been done already
if [ ! -f "$INIT_FLAG" ]; then
  echo "Running first time setup..."

  # Initialize configuration
  echo "Initializing configuration..."

  # Read in secrets from environment variables or files
  # If these aren't provided then defaults/random values will be used
  file_env "MONGO_INITDB_ROOT_USERNAME" "pbshm-admin"
  file_env "MONGO_INITDB_ROOT_PASSWORD" "$(openssl rand -hex 32)"
  file_env "USER_EMAIL" "user@pbshm.ac.uk"
  file_env "USER_PASSWORD" "secure_password"

  # Setup MongoDB root user
  python <<EOF
from pymongo import MongoClient
client = MongoClient(
    host='${MONGO_HOSTNAME:-localhost}',
    port=${MONGO_PORT:-27017},
)
client.${MONGO_AUTH_DB:-admin}.command(
    'createUser',
    '$MONGO_INITDB_ROOT_USERNAME',
    pwd='$MONGO_INITDB_ROOT_PASSWORD',
    roles=[{'role': 'root', 'db': '${MONGO_AUTH_DB:-admin}'}]
)
EOF

  flask init config --hostname="$MONGO_HOSTNAME" \
    --port="$MONGO_PORT" \
    --authentication-database="$MONGO_AUTH_DB" \
    --database-username="$MONGO_INITDB_ROOT_USERNAME" \
    --database-password="$MONGO_INITDB_ROOT_PASSWORD" \
    --pbshm-database="$MONGO_DATA_DB" \
    --user-collection="$MONGO_USER_COLLECTION" \
    --default-collection="$MONGO_DEFAULT_COLLECTION" \
    --secret-key="${MONGO_SECRET_KEY:-}"
  echo "Configuration initialized successfully"

  # Initialize database schema and root user
  echo "Initializing db and root user..."
  flask init db new-root-user --email-address="$USER_EMAIL" \
    --password="$USER_PASSWORD" \
    --first-name="$USER_FIRST_NAME" \
    --second-name="$USER_SECOND_NAME"
  echo "Root user initialized successfully"

  # Remove sensitive environment variables
  unset MONGO_INITDB_ROOT_USERNAME \
    MONGO_INITDB_ROOT_PASSWORD \
    USER_EMAIL \
    USER_PASSWORD

  # Mark initialisation as done
  touch "$INIT_FLAG"

  echo "Initialization complete."
else
  echo "Initialization already done, skipping setup."
fi

echo "Initialization complete, starting Flask application..."

# Set gunicorn defaults
GUNICORN_WORKERS=${GUNICORN_WORKERS:-4}
GUNICORN_PORT=${GUNICORN_PORT:-5000}
GUNICORN_BIND=${GUNICORN_BIND:-0.0.0.0}
GUNICORN_TIMEOUT=${GUNICORN_TIMEOUT:-30}
GUNICORN_WORKER_CLASS=${GUNICORN_WORKER_CLASS:-sync}
GUNICORN_MAX_REQUESTS=${GUNICORN_MAX_REQUESTS:-0}
GUNICORN_MAX_REQUESTS_JITTER=${GUNICORN_MAX_REQUESTS_JITTER:-0}

exec gunicorn -w "$GUNICORN_WORKERS" \
  -b "$GUNICORN_BIND:$GUNICORN_PORT" \
  --timeout "$GUNICORN_TIMEOUT" \
  --worker-class "$GUNICORN_WORKER_CLASS" \
  --max-requests "$GUNICORN_MAX_REQUESTS" \
  --max-requests-jitter "$GUNICORN_MAX_REQUESTS_JITTER" \
  --access-logfile - \
  --error-logfile - \
  'rosehips:create_app()'
