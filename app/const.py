"""
Const
"""

import os
import secrets
from pathlib import Path

VERSION = "0.2.1"
NAME = "glados"

# Security
# generating a new secret_key on every application start ensures that all users
# are logged out automatically when the app restarts.
# if this is not wanted you have to add the secret key to the config.yml file
# at position security/secret_key.
# leave the value from the config-file empty if you want to use the secret_key from this module.
SECRET_KEY = secrets.token_urlsafe(32)
SYSTEM_USER = "system"

# API
API_WEB_V1 = "/api/web/v1"
API_PAT_V1 = "/api/pat/v1"

# Paths
ROOT = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG = Path(ROOT, "config.yml")
TEMP = Path(ROOT, "temp")
DB_DEVELOPMENT = Path(ROOT, "database/dev.db")
DB_PRODUCTION = Path(ROOT, "database/glados.db")
LOGS = Path(ROOT, "logs")
UPLOADS = Path(ROOT, "uploads")
TEMPLATES = Path(ROOT, "templates")
