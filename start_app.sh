#!/bin/bash

# Setting environment variables for database server config
export DB_HOST=$2
export DB_USER="root"
export DB_PASS="root"
# start the application server
python3 server.py $1
