"""File reading/writing utilities."""

# Standard imports
import json
import os


def save_to_json(obj, json_path):
    """Save a structure to a nicely-formatted JSON file."""
    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    with open(json_path, 'w') as f:
        json.dump(obj, f, sort_keys=True, indent=2)


def load_from_json(json_path):
    """Load a structure from a JSON file."""
    with open(json_path, 'r') as f:
        return json.load(f)
