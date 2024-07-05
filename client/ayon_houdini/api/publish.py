import os

import hou
from ayon_core.lib import path_tools
from ayon_deadline.lib import publish
from ayon_houdini.api import graph_utils

from ayon_houdini.nodes import (
    ax_publisher,
    ax_render_publisher,
)
from ayon_houdini.nodes import wrap_node


# Constant strings for the types of products that can be published
RENDER_TYPE = "render"
GEO_TYPE = "model"
CACHE_TYPE = "pointcache"
CAM_TYPE = "camera"
TEXTURE_TYPE = "textures"


def submit_to_publish(
    publish_node, product_group=None, publish_data=None, silent=False
):
    """Submit node to publish in Deadline."""
    if not publish_data:
        publish_data = {}

    message = ""

    representations = publish_data.get("representations") or {}
    if not representations:    
        num_representations = publish_node.parm("representations").evalAsInt()
        for rep_index in range(1, num_representations + 1):
            rep_name = publish_node.parm("name{}".format(rep_index)).evalAsString()
            rep_path = publish_node.parm("path{}".format(rep_index)).evalAsString()
            files, _, _, = path_tools.convert_to_sequence(
                rep_path
            )
            if not files:
                path = path_tools.replace_frame_number_with_token(rep_path, "*")
                message += "No files found at '{}', can't publish representation '{}'\n".format(
                    path,
                    rep_name
                )
                continue
            if rep_name and rep_path:
                representations[rep_name] = rep_path

    if message:
        if not silent:
            hou.ui.displayMessage(
                message,
                title="Representations don't exist on disk",
                severity=hou.severityType.Error
            )
        return message, False

    if not representations:
        message = "At least one representation needs to be added to publish\n"
        if not silent:
            hou.ui.displayMessage(
                message,
                title="No representations",
                severity=hou.severityType.Error
            )
        return message, False
    
    use_hip_version = publish_node.parm("use_hip_version").eval()
    override_version = publish_node.parm("override_version_enable").eval()
    if override_version:
        publish_data["version"] = publish_node.parm("override_version").evalAsInt()      
    elif use_hip_version:
        publish_data["version"] = int(path_tools.get_version_from_path(hou.hipFile.basename()))
        
    folder_path = publish_node.parm("folder_path").evalAsString()
    task_name = publish_node.parm("task").evalAsString()
    product_type = publish_node.parm("product_type").evalAsString()
    product_name = publish_data.get(
        "product_name", publish_node.parm("product_name").evalAsString()
    )
    publish_data["comment"] = publish_node.parm("comment").evalAsString()

    # Add convert to scanline to instance if it's a render publish
    # so we convert .exr to scanline during publish
    #if product_type == "render":
    #    publish_data["convertToScanline"] = True

    # Collect workfile
    publish_data["source"] = hou.hipFile.path()

    # Add task name suffix to all product name publishes out of Houdini
    product_name = f"{product_name}_{os.getenv('AYON_TASK_NAME')}"
    
    # Add task name suffix to all product name publishes out of Houdini
    product_name = f"{product_name}_{os.getenv('AYON_TASK_NAME')}"
    
    try:
        response, success = publish.publish_version(
            os.getenv("AYON_PROJECT_NAME"),
            folder_path,
            task_name,
            product_type,
            product_name,
            representations,
            publish_data,
            overwrite_version=override_version,
            product_group=product_group
        )
        if success:
            message += f"{response}\n"
            if not silent:
                hou.ui.displayMessage(
                    message,
                    title="Submission successful",
                    severity=hou.severityType.Message, 
                )
            return message, True
        else:
            message += f"{response}\n"
            if not silent:
                hou.ui.displayMessage(
                    message,
                    title="Submission error",
                    severity=hou.severityType.Error, 
                )
            return message, False
    except Exception:
        import traceback
        message = "Error submitting asset to publish\nERROR: {}".format(
            traceback.format_exc()
        )
        if not silent:
            hou.ui.displayMessage(
                message,
                title="Submission error",
                severity=hou.severityType.Error
            )
        return message, False


def submit_inputs_to_publish(submitter_node):
    """Traverses up over all the inputs of AX Render Publisher and publishes the one that can be published"""
    success = True
    response = ""
    for node in graph_utils.get_input_nodes(submitter_node):
        # Ignore bypassed nodes
        if node.isBypassed():
            continue

        if node.type().description() == ax_render_publisher.NODE_DESCRIPTION:
            response_, success_ = ax_render_publisher.submit_to_publish(
                node,
                silent=True
            )
        elif node.type().description() == ax_publisher.NODE_DESCRIPTION:
            response_, success_ = submit_to_publish(
                node,
                silent=True
            )
        else:
            node_obj = wrap_node(node)
            if node_obj and hasattr(node_obj, "publish_callback"):
                response_, success_ = node_obj.publish_callback(silent=True)
            else:
                continue
            
        if not success_:
            success = False
        
        response += f"{node.path()} -> {response_}\n"
    
    if success:
        hou.ui.displayMessage(
            response,
            title="Submission successful",
            severity=hou.severityType.Message, 
        )
    else:
        hou.ui.displayMessage(
            response,
            title="Submission error",
            severity=hou.severityType.Error
        )
