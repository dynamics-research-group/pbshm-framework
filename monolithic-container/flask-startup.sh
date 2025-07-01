#!/bin/bash

set -e # Exit on error
set -u

# Define ANSI colour codes
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'  # No Colour

# Function to print a banner message
print_banner() {
    local message="$1"
    local border=$(printf '%*s' "${#message}" '' | tr ' ' '=')
    echo -e "\n${CYAN}${border}${NC}"
    echo -e "${YELLOW}${message}${NC}"
    echo -e "${CYAN}${border}${NC}\n"
}

print_banner "Starting PBSHM Framework"


# Set Flask environment variables
export FLASK_APP=rosehips

# Flag file to indicate initialisation has been done already
INIT_FLAG="$HOME/.pbshm_framework_initialised"

# Check if initialisation has been done already
if [ ! -f "$INIT_FLAG" ]; then
  echo -e "${GREEN}Running first time setup...\n${NC}"

  # Wait for MongoDB to be ready
  echo -e "${YELLOW}Waiting for MongoDB to be ready...${NC}"
  for i in {1..30}; do
    response=$(mongosh --host localhost --port 27017 --eval "db.runCommand('ping').ok" --quiet 2>/dev/null)
    if [ "$response" ]; then
      echo -e "${GREEN}MongoDB is ready\n${NC}"
      break
    fi
    echo -e "${YELLOW}Waiting for MongoDB... ($i/30)${NC}"
    sleep 2
  done

  # Create MongoDB admin user
  echo -e "${YELLOW}Creating MongoDB admin user...${NC}"

  MONGO_INITDB_ROOT_USERNAME=pbshm-framework-admin
  MONGO_INITDB_ROOT_PASSWORD=$(openssl rand -hex 32)

  mongosh --host localhost --port 27017 \
    --eval "use admin" \
    --eval "db.createUser({
      user: '$MONGO_INITDB_ROOT_USERNAME',
      pwd: '$MONGO_INITDB_ROOT_PASSWORD',
      roles: [
        { role: 'userAdminAnyDatabase', db: 'admin' },
        { role: 'readWriteAnyDatabase', db: 'admin' }
      ]
    })" \
    --eval "db.adminCommand( { shutdown: 1 } )"

  echo -e "${GREEN}MongoDB admin user created successfully\n!${NC}"


  # Initialize configuration
  echo -e "${YELLOW}Initializing configuration...${NC}"
  flask init config --hostname=localhost \
    --port=27017 \
    --authentication-database="$MONGO_AUTH_DB" \
    --database-username="$MONGO_INITDB_ROOT_USERNAME" \
    --database-password="$MONGO_INITDB_ROOT_PASSWORD" \
    --pbshm-database="$MONGO_DATA_DB" \
    --user-collection="$MONGO_USER_COLLECTION" \
    --default-collection="$MONGO_DEFAULT_COLLECTION" \
    --secret-key="${MONGO_SECRET_KEY:-}"
  echo -e "${GREEN}Configuration initialized successfully\n${NC}"

  # Initialize database schema and root user
  echo -e "${YELLOW}Initializing db and root user...${NC}"
  flask init db new-root-user --email-address="$USER_EMAIL" \
    --password="$USER_PASSWORD" \
    --first-name="$USER_FIRST_NAME" \
    --second-name="$USER_SECOND_NAME"
  echo -e "${GREEN}Root user initialized successfully\n${NC}"

  # Mark initialisation as done
  touch "$INIT_FLAG"

  echo -e "${GREEN}Initialization complete.\n${NC}"
else
  echo -e "${GREEN}Initialization already done, skipping setup.\n${NC}"
fi

echo -e "${YELLOW}Starting Flask application using gunicorn...${NC}"

# Set gunicorn defaults
GUNICORN_WORKERS=${GUNICORN_WORKERS:-4}
GUNICORN_PORT=${GUNICORN_PORT:-5000}
GUNICORN_BIND=${GUNICORN_BIND:-127.0.0.1}
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
