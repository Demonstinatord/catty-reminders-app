"""
This module builds shared parts for other modules.
"""

import json
import os
from fastapi.templating import Jinja2Templates

# --------------------------------------------------------------------------------
# Read Configuration 
# --------------------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config_path = os.path.join(BASE_DIR, 'config.json')


if not os.path.exists(config_path):
    config_path = 'config.json'

with open(config_path) as config_json:
    config = json.load(config_json)
    users = config['users']
    db_path = config['db_path']



# --------------------------------------------------------------------------------
# Establish the Secret Key
# --------------------------------------------------------------------------------

secret_key = config['secret_key']

# --------------------------------------------------------------------------------
# Templates
# --------------------------------------------------------------------------------

templates = Jinja2Templates(directory="templates")
DEPLOY_REF = os.getenv("DEPLOY_REF", "NA")
