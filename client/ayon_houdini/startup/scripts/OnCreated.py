"""
This module gets executed after the user creates a new instance of a node
type (not when a scene file loads, see OnLoaded.py)

We use this opportunity to invoke our custom create method for all nodes that
have this functionality implemented.

Args:
    kwargs (dict): A dictionary containing values provided by the API, such as
        the current node.
"""
node = kwargs["node"]

if hasattr(node, "on_created"):
    node.on_created()
