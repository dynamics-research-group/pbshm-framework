#!/bin/bash

# Import framework file
. $HOME/entrypoint-framework.sh ""

# Display banner
print_banner "Gunicorn"

# Start Gunicorn server
print_pending_task_message "Starting Gunicorn server"
exec gunicorn --workers "${GUNICORN_WORKERS:-4}" \
  --bind "${FRONTEND_BIND:-0.0.0.0}:${FRONTEND_PORT:-5000}" \
  --timeout "${GUNICORN_TIMEOUT:-30}" \
  --worker-class "${GUNICORN_WORKER_CLASS:-sync}" \
  --max-requests "${GUNICORN_MAX_REQUESTS:-0}" \
  --max-requests-jitter "${GUNICORN_MAX_REQUESTS_JITTER:-0}" \
  --access-logfile - \
  --error-logfile - \
  'rosehips:create_app()'
