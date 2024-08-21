#!/bin/bash

# Install dependencies
pip install -r requirements.txt

# Install Gunicorn
pip install gunicorn eventlet

# Create a public directory for static files if it doesn't exist
mkdir -p public

# Copy static files if you have any
cp -r static public/

# Start Gunicorn (this won't actually run on Vercel, but it's here for completeness)
# gunicorn --config gunicorn.conf.py app:app