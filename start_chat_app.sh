#!/bin/bash

# Setting environment variables for database server config
export DB_HOST="127.0.0.1"
export DB_USER="root"
export DB_PASS="root"
# start the application server
python3 chat_server.py
