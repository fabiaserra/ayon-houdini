from ayon_houdini.nodes import wrap_node

node_obj = wrap_node(kwargs["node"])
if node_obj and hasattr(node_obj, "on_created"):
    node_obj.on_created()
