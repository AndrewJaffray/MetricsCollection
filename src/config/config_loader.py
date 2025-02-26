import json
from pathlib import Path

def load_config(config_path):
    """Load configuration from JSON file."""
    with open(config_path) as f:
        return json.load(f) 