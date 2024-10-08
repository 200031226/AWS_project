import sys
import os
import logging

logging.basicConfig(stream=sys.stderr)

# Add the application's directory to the PYTHONPATH
sys.path.insert(0, '/var/www/html')

# Set the working directory (important for relative paths)
os.chdir('/var/www/html')

from flaskapp import app as application
