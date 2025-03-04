"""
API package for the metrics collection application.
Contains classes for API authentication and remote control.
"""

from .auth import require_auth, generate_token
from .remote_control import RemoteControl 