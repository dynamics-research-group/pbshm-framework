#!/bin/bash

# Import framework file
. ./entrypoint-framework.sh ""

setup_mongodb(){
    # Display banner
    print_banner "MongoDB"

    # Flag file to indicate initialisation has been done already
    INIT_FLAG="$HOME/.pbshm_database_initialised"

    # Check if initialisation has been done already
    if [ ! -f "$INIT_FLAG" ]; then

        # Generate secrets
        # Read in secrets from environment variables or files
        # If these aren't provided then defaults/random values will be used
        print_pending_task_message "Generating secrets"
        file_env "MONGO_INITDB_ROOT_USERNAME" "pbshm-admin-$(openssl rand -hex 8)"
        file_env "MONGO_INITDB_ROOT_PASSWORD" "$(openssl rand -hex 32)"
        print_success_status "DONE"

        # Create MongoDB User
        print_pending_task_message "Creating MongoDB user account"
        mongosh --host localhost --port 27017 \
            --eval "use ${MONGO_AUTH_DB:-admin}" \
            --eval "db.createUser({
                user: '$MONGO_INITDB_ROOT_USERNAME',
                pwd: '$MONGO_INITDB_ROOT_PASSWORD',
                roles: [
                    { role: 'userAdminAnyDatabase', db: '${MONGO_AUTH_DB:-admin}' },
                    { role: 'readWriteAnyDatabase', db: '${MONGO_AUTH_DB:-admin}' }
                ]
                })" \
            --eval "db.adminCommand( { shutdown: 1 } )"
        print_success_status "DONE"

    fi

    # Setup framework
    echo "\n"
    setup_framework

}

if [ $(basename "$0") = "entrypoint-mongodb.sh" ]; then
    setup_framework
fi