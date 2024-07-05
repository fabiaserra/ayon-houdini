import hou

from ayon_houdini.api import publish


NODE_DESCRIPTION = "AX Render Publisher"


def submit_to_publish(render_publish_node, silent=False):
    """Iterates over all the publisher nodes under AX Render Publisher and submits to publish them"""
    success = True
    response = ""
    for ax_publisher_node in render_publish_node.node("ax_publishers").children():
        response_, success_ = publish.submit_to_publish(
            ax_publisher_node,
            product_group=render_publish_node.parm("base_product_name").evalAsString(),
            silent=True
        )
        if not success_:
            success = False
        response += response_
    
    if success:
        if not silent:
            hou.ui.displayMessage(
                response,
                title="Submission successful",
                severity=hou.severityType.Message, 
            )
        return response, True
    
    if not silent:
        hou.ui.displayMessage(
            response,
            title="Submission error",
            severity=hou.severityType.Error
        )
    return response, False


def input_changed_callback(render_publish_node):
    """Callback when input node on AX Render Publisher changes"""

    # Always clear the child nodes from inside the node on an input change
    for child_node in render_publish_node.node("ax_publishers").children():
        child_node.destroy()

    for out_id in ["beauty", "util"]:
        render_publish_node.parm(f"publish_{out_id}").hide(True)

    input_nodes = render_publish_node.inputs()
    if not input_nodes:
        # If no inputs, return early
        return
    
    # Find a list of all the output files that the node is generating
    output_parms = {}

    input_node = input_nodes[0]
    input_node_type = input_node.type().description()
    if input_node_type == "Arnold":
        output_parms["beauty"] = input_node.parm("ar_picture")
        num_aovs = input_node.parm("ar_aovs").eval()
        for aov_idx in range(1, num_aovs):
            is_enabled = input_node.parm(f"ar_enable_aov{aov_idx}").eval()
            if not is_enabled:
                continue
            
            is_separate_file = input_node.parm(f"ar_aov_separate{aov_idx}").eval()
            if is_separate_file:
                output_parms["util"] = input_node.parm(f"ar_aov_separate_file{aov_idx}")

    elif input_node_type == "Mantra":
        output_parms["beauty"] = input_node.parm("vm_picture")
    elif input_node_type == "Arnold Denoiser":
        output_parms["beauty"] = input_node.parm("output")
    else:
        hou.ui.displayMessage(
            f"Node type {input_node_type} not supported on AX Render Publisher"
        )
        return

    for out_id, output_parm in output_parms.items():
        ax_publisher_node = render_publish_node.node("ax_publishers").createNode(
            "ax::ax_publisher::1.0",
            node_name=out_id
        )
        # Break Hscript expression
        ax_publisher_node.parm("product_name").deleteAllKeyframes()

        ax_publisher_node.setParms(
            {
                "folder_path": render_publish_node.parm("folder_path"),
                "product_name": f'`chs("../../base_product_name")`_{out_id}',
                "task": render_publish_node.parm("task"),
                "product_type": "render",
                "comment": render_publish_node.parm("comment"),
                "use_hip_version": render_publish_node.parm("use_hip_version"),
                "override_version": render_publish_node.parm("override_version"),
                "version": render_publish_node.parm("version"),
                "representations": 1,
                "name1": "exr",
                "path1": output_parm,
            }
        )

        # Activate toggles to show that output exists
        render_publish_node.parm(f"publish_{out_id}").hide(False)
        render_publish_node.parm(f"publish_{out_id}").set(True)
