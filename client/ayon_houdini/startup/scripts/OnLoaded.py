"""
This module gets executed after an instance of a node type is created as Houdini
loads a scene file from disk (not when a user creates a node in the network editor,
see OnCreated.py). This also runs when pasting nodes from the clipboard.

This does not run when loading the node as part of the contents of another asset.
If you need to do something when a node inside an asset loads, you must put that
code in the asset’s load handler.

This runs on each node after all nodes are loaded, so the script will see the
complete scene.

We use this opportunity to invoke our custom update method for all nodes that
have this functionality implemented.

Args:
    kwargs (dict): A dictionary containing values provided by the API, such as
        the current node.
"""
node = kwargs["node"]

if hasattr(node, "on_loaded"):
    node.on_loaded()
