#!/bin/bash

# Set environment variables
export FLASK_APP=app
export FLASK_ENV=production

# Start the Flask app
flask run --host=0.0.0.0 --port=${PORT}

