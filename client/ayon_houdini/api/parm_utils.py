import subprocess

import hou
from ayon_core.lib import path_tools


def create_parm(parm_data):
    """Util function to create a parm template from a dictionary"""
    parm_data = parm_data.copy()
    parm_type = parm_data.pop("type")
    disable_when = parm_data.pop("disable_when", None)
    hide_when = parm_data.pop("hide_when", None)
    if parm_type == hou.FolderParmTemplate:
        parm_data_list = parm_data.pop("_children")
        parm = parm_type(**parm_data)
        for parm_data in parm_data_list:
            child_parm = create_parm(parm_data)
            parm.addParmTemplate(child_parm)
    else:
        parm = parm_type(**parm_data)
    
    if disable_when:
        parm.setConditional(hou.parmCondType.DisableWhen,  disable_when)
    if hide_when:
        parm.setConditional(hou.parmCondType.HideWhen,  hide_when)

    return parm


def insert_parm_data(orig_parm_data, new_parm_data, insert_index):
    """Util function to insert some extra parms on children of orig parm data"""
    for new_parm in new_parm_data:
        orig_parm_data["_children"].insert(insert_index, new_parm)
        insert_index += 1

    return orig_parm_data


def add_parm_template_to_node(parm_data, node):
    """Util function that adds parm data to Node's template group"""
    ptg = node.parmTemplateGroup()
    
    parm = create_parm(parm_data)

    folder_templates = [
        parm_template for parm_template in ptg.entries()
        if parm_template.type() == hou.parmTemplateType.Folder
    ]
    last_folder_name = None
    if folder_templates:
        last_folder_name = folder_templates[-1].name()

    # If we couldn't find a folder parm, we put all the existing parms
    # within a new folder tab so it's easier to visualize the Publish tab
    if not last_folder_name:
        last_folder_name = "orig_parms"
        new_folder = hou.FolderParmTemplate(last_folder_name, "Main")
        # Iterate through existing parameter templates and add them to the new folder
        for parm_template in ptg.parmTemplates():
            new_folder.addParmTemplate(parm_template)
        # Clear the current parameter templates from the node's parm template group
        ptg.clear()
        # Add the new folder to the parm template group
        ptg.append(new_folder)

    ptg.insertAfter(last_folder_name, parm)
    
    # Set the updated parm template group back to the node
    node.setParmTemplateGroup(ptg)


def open_parm_in_mplay(node, parm_name):
    """Util function to display path in MPlay"""
    image_file_parm = node.parm(parm_name)
    with hou.ScriptEvalContext(image_file_parm):
        path = image_file_parm.evalAsString()
        path = path_tools.replace_frame_number_with_token(path, "*")
        subprocess.call(["mplay", path])