#!/bin/bash

set -e # Exit on error
set -u # Exit on unset variables

# Define ANSI colour codes
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BOLD='\033[1m' # Bold weight
NC='\033[0m' # Clear weight and font

# Function to print a banner message
print_banner() {
    local message="$1"
    local border=$(printf '%*s' "${#message}" '' | tr ' ' '=')
    echo "\n${CYAN}${border}${NC}"
    echo "${YELLOW}${message}${NC}"
    echo "${CYAN}${border}${NC}"
}

# Print pending task message
# Arg 1: message to display
print_pending_task_message(){
    echo -n "${CYAN}${1}... ${NC}"
}

# Print success status from pending task
# Arg 1: message to display
print_success_status(){
    echo "${GREEN}${BOLD}${1}${NC}"
}

# Print error status from pending task
# Arg 1: message to display
print_error_status(){
    echo "${RED}${BOLD}${1}!${NC}"
}

# Load environment variable from file
# Arg 1: variable name
# Arg 2: default value
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

# Setup framework
setup_framework(){
    # Display banner
    print_banner "PBSHM Framework"

    # Flag for development mode
    DEVELOPMENT_FLAG=false
    if [ $# -eq 1 ] && [ ! -z "$1" ] && [ "$1" = "--development" ]; then
        DEVELOPMENT_FLAG=true
    fi

    # Flask app path
    if [ "$DEVELOPMENT_FLAG" = true ]; then
        export FLASK_APP_PATH="/app/development"
    else
        export FLASK_APP_PATH="rosehips"
    fi

    # Flag file to indicate initialisation has been done already
    INIT_FLAG="$HOME/.pbshm_framework_initialised"

    # Check if initialisation has been done already
    if [ ! -f "$INIT_FLAG" ]; then
        
        # Source credentials from environment file if it exists
        if [ -f "$HOME/.mongo.env" ]; then
            print_pending_task_message "Reading credentials from environment file"
            source "$HOME/.mongo.env"
            print_success_status "DONE"
        fi

        # Generate secrets
        # Read in secrets from environment variables or files
        # If these aren't provided then defaults/random values will be used
        print_pending_task_message "Generating secrets"
        file_env "MONGO_AUTH_USERNAME" "pbshm-admin-$(openssl rand -hex 8)"
        file_env "MONGO_AUTH_PASSWORD" "$(openssl rand -hex 32)"
        file_env "USER_EMAIL" "framework-admin@pbshm.ac.uk"
        file_env "USER_PASSWORD" "secure_password"
        print_success_status "DONE"

        # Initialise configuration
        print_pending_task_message "Initialising configuration"
        flask --app="$FLASK_APP_PATH" init config \
            --hostname="${MONGO_HOSTNAME:-localhost}" \
            --port="${MONGO_PORT:-27017}" \
            --authentication-database="${MONGO_AUTH_DB:-admin}" \
            --database-username="$MONGO_AUTH_USERNAME" \
            --database-password="$MONGO_AUTH_PASSWORD" \
            --pbshm-database="${MONGO_DATA_DB:-pbshm-framework}" \
            --user-collection="${MONGO_USER_COLLECTION:-users}" \
            --default-collection="${MONGO_DEFAULT_COLLECTION:-structures}" \
            --secret-key="${MONGO_SECRET_KEY:-}"
        print_success_status "DONE"

        # Initialise database
        print_pending_task_message "Initialising database"
        flask --app="$FLASK_APP_PATH" init db
        print_success_status "DONE"

        # Initialise new root user
        print_pending_task_message "Initialising root user"
        flask --app="$FLASK_APP_PATH" init new-root-user \
            --email-address="$USER_EMAIL" \
            --password="$USER_PASSWORD" \
            --first-name="${USER_FIRST_NAME:-FirstName}" \
            --second-name="${USER_SECOND_NAME:-LastName}"
        print_success_status "DONE"

        # Remove sensitive environment variables and mark initialised
        print_pending_task_message "Removing secrets"
        unset MONGO_AUTH_USERNAME \
            MONGO_AUTH_PASSWORD \
            USER_EMAIL \
            USER_PASSWORD
        touch "$INIT_FLAG"
        print_success_status "DONE"

    fi

    # Start framework
    if [ "$DEVELOPMENT_FLAG" = true ]; then
        
        # Start development server
        print_pending_task_message "Starting development server"
        exec flask --app="$FLASK_APP_PATH" run --debug --reload \
            --host="${FRONTEND_BIND:-0.0.0.0}" \
            --port="${FRONTEND_PORT:-5000}"
        print_success_status "OK"

    else

        # Start production server
        print_pending_task_message "Starting production server"
        exec "$HOME/entrypoint-wsgi.sh"
        print_success_status "OK"

    fi

}

if [ "$(basename "$0")" = "entrypoint-framework.sh" ]; then
    setup_framework
fi
