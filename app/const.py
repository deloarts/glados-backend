"""
Const
"""

import os
import secrets
import sys
from pathlib import Path

VERSION = "0.12.2"
NAME = "glados"

SYSTEM_USER = "system"

# DB
ALEMBIC_VERSION = "b8e97eca009f"

# API
API_WEB_V1 = "/api/web/v1"
API_PAT_V1 = "/api/pat/v1"
API_KEY_V1 = "/api/key/v1"

# Paths
ROOT = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PERSISTENT_KEY_FILE = Path(ROOT, "persistent.secret")
CONFIG = Path(ROOT, "config.yml")
CONFIG_BOUGHT_ITEMS = Path(ROOT, "config_files/bought_items.json")
TEMP = Path(ROOT, "temp")
DB_DEVELOPMENT = Path(ROOT, "database/dev.db")
DB_PRODUCTION = Path(ROOT, "database/glados.db")
LOGS = Path(ROOT, "logs")
UPLOADS = Path(ROOT, "uploads")
TEMPLATES = Path(ROOT, "templates")

# Tools/Stock Cut 1D
N_MAX_PRECISE = 9  # 10 takes ~30s, 9 only 1.2s
N_MAX = 500  # around 1 million with n^2

# Tool/Stock Cut 2D
SOLVER_TIMEOUT = 10  # seconds

# Security
# generating a new secret_key on every application start ensures that all users
# are logged out automatically when the app restarts.
# if this is not wanted you have to add the secret key to the config.yml file
# at position security/secret_key.
# leave the value from the config-file empty if you want to use the secret_key from this module.
SECRET_KEY_NON_PERSISTENT = secrets.token_urlsafe(32)
SECRET_KEY_PERSISTENT = None

if PERSISTENT_KEY_FILE.exists():
    with open(PERSISTENT_KEY_FILE, "r", encoding="utf-8") as secret_key_file:
        SECRET_KEY_PERSISTENT = secret_key_file.read()
else:
    SECRET_KEY_PERSISTENT = secrets.token_urlsafe(32)
    with open(PERSISTENT_KEY_FILE, "w", encoding="utf-8") as secret_key_file:
        secret_key_file.write(SECRET_KEY_PERSISTENT)


if not SECRET_KEY_PERSISTENT:
    raise ValueError("Persistent secret key error: Key is None")
