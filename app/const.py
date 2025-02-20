"""
Const
"""

import os
import secrets
from enum import Enum
from enum import unique
from pathlib import Path

VERSION = "0.13.1"
NAME = "glados"

SYSTEM_USER = "system"

# DB
ALEMBIC_VERSION = "8723510377cf"
SERVER_DEFAULT_LANGUAGE = "enGB"
SERVER_DEFAULT_THEME = "dark"

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
# Non-persistent-key: generating a new secret_key on every application start ensures that all users
# are logged out automatically when the app restarts.
# Persistent-key: the secret_key is stored in a file and is used on every application start. This ensures
# that api-keys and user-api-keys are still valid after a restart.
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


# Themes
@unique
class Themes(str, Enum):
    DARK = "dark"
    LIGHT = "light"
