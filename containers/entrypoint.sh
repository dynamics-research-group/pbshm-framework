#!/bin/bash

set -e # Exit on error
set -u # Exit on unset variables

export FLASK_APP=rosehips \
  FLASK_DEBUG=1

# Flag file to indicate initialisation has been done already
INIT_FLAG="$HOME/.pbshm_framework_initialised"

# Check if initialisation has been done already
if [ ! -f "$INIT_FLAG" ]; then
  echo "Running first time setup..."

  # Initialize configuration
  echo "Initializing configuration..."

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

  # Mark initialisation as done
  touch "$INIT_FLAG"

  echo "Initialization complete."
else
  echo "Initialization already done, skipping setup."
fi

echo "Initialization complete, starting Flask application..."
exec flask run --host=0.0.0.0 --port=5000 --no-reload
