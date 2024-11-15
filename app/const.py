"""
Const
"""

import os
import secrets
from pathlib import Path

VERSION = "0.9.2"
NAME = "glados"

# Security
# generating a new secret_key on every application start ensures that all users
# are logged out automatically when the app restarts.
# if this is not wanted you have to add the secret key to the config.yml file
# at position security/secret_key.
# leave the value from the config-file empty if you want to use the secret_key from this module.
SECRET_KEY = secrets.token_urlsafe(32)
SYSTEM_USER = "system"

# DB
ALEMBIC_VERSION = "824d657001b8"

# API
API_WEB_V1 = "/api/web/v1"
API_PAT_V1 = "/api/pat/v1"

# Paths
ROOT = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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
