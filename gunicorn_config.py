
# Server Socket
bind = "0.0.0.0:8228"  # Bind to all IP addresses on port 8228

# Worker Processes
workers = 1  # Number of worker processes

# Logging
accesslog = "/srv/cyber_portal/logs/access.log"  # Access log file
errorlog = "/srv/cyber_portal/logs/error.log"    # Error log file
loglevel = "debug"  # Logging level (debug, info, warning, error, critical)

# Daemon mode (Optional if running via systemd)
# daemon = True  # Uncomment if you want to run Gunicorn in daemon mode

# Other settings
timeout = 120  # Request timeout
