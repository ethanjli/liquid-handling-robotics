"""File reading/writing utilities."""

# Standard imports
import json
import os


def decode_int_keys(o):
    """Decode a JSON object while converting string int keys to ints.

    Inspired by: https://stackoverflow.com/a/48401729
    """
    def decode_int(string):
        try:
            return int(string)
        except ValueError:
            return string

    if isinstance(o, dict):
        return {decode_int(k): decode_int_keys(v) for (k, v) in o.items()}
    else:
        return o


def save_to_json(obj, json_path):
    """Save a structure to a nicely-formatted JSON file."""
    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    with open(json_path, 'w') as f:
        json.dump(obj, f, sort_keys=True, indent=2)


def load_from_json(json_path, object_hook=decode_int_keys):
    """Load a structure from a JSON file."""
    with open(json_path, 'r') as f:
        return json.load(f, object_hook=object_hook)
