"""Utilities for containers."""


# Nested Trees

def add_to_tree(tree, key_path, value):
    """Add the value to a nested dict from walking down along the specified keys.

    Args:
        tree: a nested dict.
        key_path: an iterable of the keys to follow. If keys is a string, uses
        keys as a single key.
        value: the value to associate with the key path
    """
    cursor = tree
    if isinstance(key_path, str):
        cursor[key_path] = value
    for key in key_path[:-1]:
        if key not in cursor:
            cursor[key] = {}
        cursor = cursor[key]
    cursor[key_path[-1]] = value


def get_from_tree(tree, key_path):
    """Return the value in a nested dict from walking down along the specified keys.

    Args:
        tree: a nested dict.
        key_path: an iterable of the keys to follow. If keys is a string, uses
        keys as a single key.
    """
    cursor = tree
    if isinstance(key_path, str):
        return cursor[key_path]
    for key in key_path:
        cursor = cursor[key]
    return cursor
