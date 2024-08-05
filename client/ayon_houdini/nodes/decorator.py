"""
This decorator enhances Houdini nodes by adding a custom SuperNode class as an
additional superclass. The process works as follows:

1. **Initialization on Houdini Startup**:
   - During Houdini startup (from `pythonrc.py`), the `init()` function is
    called.
   - This function modifies Houdini node classes (e.g., `hou.SopNode`) by
    adding `SuperNode` as a superclass. Example:
	    `class hou.SopNode(hou.Node)` becomes
		`class hou.SopNode(hou.Node, SuperNode)`.

2. **Attribute/Method Access**:
   - When an attribute or method is accessed on a Houdini node,
   `SuperNode.__getattr__` is invoked. This method:
     1. Checks if the node is already known. If it is, it proceeds to step 3.
     2. If the node is not known:
        2.1. Checks if there is a known class for the node type
		    (e.g., `obj/myNode`).
        2.2. If the class is not known, attempts to import it dynamically:
		    `from ayon_houdini.nodes.<category>.myNode import MyNode`.
            Note that we are capitalizing the class name to match the PEP8
            naming convention for classes.
        2.3. Creates a new instance of the custom class, decorated by
		    `WrappedCls`, to handle calls between the custom class and the
			original `hou.Node`.
     3. Retrieves the attribute:
        - This triggers `WrappedCls.__getattr__`, which attempts to:
          - Retrieve the attribute from the original `hou.Node`, or
          - Retrieve it from the custom class.

3. **Additional Handling**:
   - When a new instance of a custom class is created, a callback for deletion
   is added. This ensures that the `self.node` pointer does not become invalid
   if the node is deleted.
"""
import hou

# the index of the actual nodeType name in the tuple returned by
# hou.NodeType.nameComponents()
NODE_TYPE_NAME_INDEX = 2


def decorate(cls):
    class WrappedCls(cls):
        """A wrapper class that adds custom behavior to Houdini nodes."""

        def __init__(self, node):
            """
            Initialize the wrapped class with a reference to the Houdini node.
            """
            self._node = node
            super(WrappedCls, self).__init__()

        def __getattr__(self, name):
            """
            Retrieve an attribute from the Houdini node or the wrapped class.
            """
            # First, check if the Houdini node has the attribute
            if hasattr(self._node, name):
                return getattr(self._node, name)

            # If not, delegate to the superclass
            return super(WrappedCls, self).__getattr__(name)

    return WrappedCls


def import_class(node_category, node_type):
    """
    Dynamically import and return a custom class for a given node category and
    type, wrapped in a decorator.

    Args:
        node_category (str): The category of the Houdini node (e.g., 'obj').
        node_type (str): The specific type of the Houdini node (e.g., 'myNode')

    Returns:
        type: The custom class wrapped by the `decorate` function.

    Raises:
        ImportError: If the custom class cannot be imported.
    """
    try:
        path = "ayon_houdini.nodes.{}.{}".format(node_category, node_type)
        module = __import__(path, fromlist=path.split('.')[:-1])
        custom_class = getattr(module, node_type.capitalize())
        return decorate(custom_class)
    except Exception as e:
        raise ImportError(
            f"Could not import class {node_type} from {path}"
        ) from e


def get_identifier(node):
    """
    Get the identifier for the Houdini node, including the category and type.

    Args:
        node (hou.Node): The Houdini node to identify.

    Returns:
        tuple: A tuple containing the node category and type.
    """
    node_category = node.type().category().typeName().lower()
    node_type = node.type().nameComponents()[NODE_TYPE_NAME_INDEX]
    return node_category, node_type


class SuperNode(object):
    __instances = {}
    __classes = {}

    @classmethod
    def reset(cls):
        """
        Clear internal dictionaries to force a refresh.

        This method is used to reset the state of the SuperNode class,
        typically during development or debugging.

        Usage in Houdini:
            from ayon_houdini.nodes.decorator import SuperNode
            SuperNode.reset()
        """
        cls.__instances = {}
        cls.__classes = {}

    @classmethod
    def BeingDeleted(cls, **kwargs):
        """
        Remove a node from the instances dictionary when it is deleted in
        Houdini.

        Args:
            kwargs (dict): A dictionary containing event-related information.
        """
        node = kwargs.get("node")
        if node and node in cls.__instances:
            cls.__instances.pop(node, None)

    def __getattr__(self, name):
        """
        Retrieve an attribute, handling cases where the node is not yet
        registered.

        Args:
            name (str): The name of the attribute to retrieve.

        Returns:
            Any: The value of the requested attribute.

        Raises:
            AttributeError: If the attribute does not exist in the node or the
                custom class.
        """
        # Step 2: Check if the node is new (not yet in the instances dict)
        if self not in SuperNode.__instances:
            identifier = get_identifier(self)

            # Find or import the custom class
            if identifier not in SuperNode.__classes:
                try:
                    custom_class = import_class(*identifier)
                except ImportError:
                    raise AttributeError(
                        f"Attribute '{name}' not found in node type '{identifier}'"
                    )
                SuperNode.__classes[identifier] = custom_class
            else:
                custom_class = SuperNode.__classes[identifier]

            # Create an instance from the classes dictionary and add it to the
            # instances
            SuperNode.__instances[self] = custom_class(self)

            # Add callbacks (e.g., for node deletion)
            self.addEventCallback(
                (hou.nodeEventType.BeingDeleted,), SuperNode.BeingDeleted
            )

        # Step 3: Try to get the value from the custom class instance
        if hasattr(SuperNode.__instances[self], name):
            return SuperNode.__instances[self].__getattribute__(name)
        else:
            raise AttributeError(
                f"NodeType {self.type().nameWithCategory()} has no attribute '{name}'"
            )


def init():
    """Add the custom SuperNode class to Houdini's node classes.
    
    This should be called during Houdini startup.
    """
    for node_class in [hou.SopNode, hou.ObjNode, hou.RopNode]:
        if SuperNode not in node_class.__bases__:
            node_class.__bases__ = (SuperNode,) + node_class.__bases__
