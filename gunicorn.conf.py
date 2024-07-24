# Bind to all available interfaces
bind = "0.0.0.0:8000"

# Single worker process as we have only one client
workers = 3

# Use eventlet worker class for Socket.IO support
worker_class = 'eventlet'

# Increase timeout for processing large files
timeout = 600  # 10 minutes

# Disable keepalive as we have a single client
keepalive = 0



# # Limit requests before worker restart to prevent memory leaks
max_requests = 100
max_requests_jitter = 10

# # Enable auto-reload for development
reload = True

# # Don't run in daemon mode
daemon = False

# # Set high limits for request size
limit_request_line = 0
limit_request_fields = 32768
limit_request_field_size = 0

# # Configure buffers for large files
# # worker_tmp_dir = '/dev/shm'

# # Socket.IO specific settings
worker_connections = 2000



app = 'app:app'
