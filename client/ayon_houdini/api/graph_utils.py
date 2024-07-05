def get_switch_node_selected_index(switch_node):
    """
    Function to get the single specific input index from a
    switch node since switch nodes only respect one input and ignore
    the rest.
    
    NOTE: Copied from Deadline submission/Houdini/Main/SubmitDeadlineRop.py

    Switch nodes come in a few flavours with slightly different APIs,
    so we perform an existence check to determine which parm to use.

    :param switch_node: The switch node we want to retrieve the input index from
    :return: An int indicating which input to active
    """
    # ie. Driver/switch nodes
    switch_parm = switch_node.parm("index")
    if switch_parm is None:
        # ie. SOP/switch nodes
        switch_parm = switch_node.parm("input")

    return switch_parm.eval()


def get_input_nodes(current_node):
    """
    Function to get a list of all input nodes for a specified node.

    NOTE: Copied from Deadline submission/Houdini/Main/SubmitDeadlineRop.py

    Respects known flow control nodes in the form of switch and fetch nodes.
    :param current_node: The render node which you want to get the inputs for.
    :return: the list of input nodes.
    """
    is_switch = (current_node.type().name() == "switch")
    
    # inputs returns a tuple we want this to be a list so we can modify it.
    input_nodes = list(current_node.inputs())
    
    if is_switch:
        selected_input = get_switch_node_selected_index(current_node)
        if 0 <= selected_input < len(input_nodes):
            input_nodes = [input_nodes[selected_input]]
        else:
            input_nodes = []
    
    # remove all instances of None from input_nodes
    return filter(None, input_nodes)