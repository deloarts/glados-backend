"""
    System related functions
"""

import platform


def get_os() -> str:
    """Returns the operating system name, release and version."""
    return f"{platform.system()} {platform.release()} ({platform.version()})"


def get_hostname() -> str:
    """Returns the hostname."""
    return platform.node()
