import os

from ayon_core.lib import path_tools
from ayon_houdini.api import lib


NODE_DESCRIPTION = "AX Publisher"


def representation_parms_callback(publish_node, input_index):
    representations_parm = publish_node.parm("representations")
    num_representations = representations_parm.eval()

    input_nodes = publish_node.inputs()
    try:
        input_node = input_nodes[input_index]
    except IndexError:
        representations_parm.set(num_representations - 1)

    num_representations = representations_parm.eval()

    for input_node in input_nodes:
        out_parm = lib.get_output_parameter(input_node)
        out_path = out_parm.evalAsString()
        if out_path:
            rep_index = num_representations + 1
            representations_parm.set(rep_index)
            frame_match = path_tools.RE_FRAME_NUMBER.match(
                os.path.basename(out_path)
            )
            if frame_match:
                rep_extension = frame_match.group("extension")
            else:
                rep_extension = os.path.splitext(out_path)[1][1:]
            publish_node.parm("name{}".format(rep_index)).set(rep_extension)
            publish_node.parm("path{}".format(rep_index)).set(out_parm)
    
