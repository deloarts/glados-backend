"""
    Glados Backend Tests
"""

from app.config import cfg

# For the tests to run the app must be in debug mode.
# This way no one can accidentally messes with the live db.
assert cfg.debug
