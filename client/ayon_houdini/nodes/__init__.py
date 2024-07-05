import importlib


def wrap_node(node):
    node_type = node.type()
    node_name = node_type.name().lower().replace("::", "_").replace(".", "_")
    category = node_type.category().typeName().lower()

    try:
        mod = importlib.import_module(
            f"ayon_houdini.nodes.{category}.{node_name}"
        )
    except ImportError:
        return

    node_class = getattr(mod, node_name.capitalize())
    if node_class:
        return node_class(node)

    return None
