import os

import hou
from ayon_core.lib import path_tools
from ayon_houdini.api import lib, parm_utils

from ayon_houdini.api import publish
from ayon_houdini.nodes.base_node import BaseNode


class PublishNode(BaseNode):
    """Base class for nodes that publish products to AYON."""

    # Tuple of product types that can be published
    product_types = ()

    def on_created(self):
        """Callback when node gets created."""
        super().on_created()

        # Add folder that allows us to publish the node
        parm_utils.add_parm_template_to_node(
            self.get_publish_parm_template(), self.node
        )

        self.update_representations()

    def update_representations(self):
        """Callback to update representation parms automatically"""
        out_parm = lib.get_output_parameter(self.node)
        representations_parm = self.node.parm("representations")
        if out_parm:
            representations_parm.set(1)
            rep_name_parm = self.node.parm("name1")
            # This needs to be static because Houdini doesn't allow us to
            # save expressions on multiparms
            rep_name_parm.set(self.get_rep_name_from_path(out_parm.evalAsString()))
            rep_path_parm = self.node.parm("path1")
            rep_path_parm.set(f'`chs("./{out_parm.name()}")`')
        else:
            representations_parm.set(0)
    
    def pre_publish_callback(self, silent=False):
        """Callback to run any code before publish"""
        message = ""
        comment = self.node.parm("comment").evalAsString()
        if not comment:
            message = "Comment missing, please add a comment to publish.\n"
            if not silent:
                hou.ui.displayMessage(
                    message,
                    title="Validation error",
                    severity=hou.severityType.Error
                )
            return message, False
        
        return message, True
    
    def publish_callback(self, silent=False):
        """Callback when publish button gets clicked"""
        message, success = self.pre_publish_callback(silent=silent)
        if not success:
            return message, False
        return publish.submit_to_publish(self.node, silent=silent)

    def get_rep_name_from_path(self, out_path):
        """Util function to find our convention for representation names given a file path"""
        frame_match = path_tools.RE_FRAME_NUMBER.match(
            os.path.basename(out_path)
        )
        if frame_match:
            return frame_match.group("extension")
        
        return os.path.splitext(out_path)[1][1:]

    def get_publish_parm_template(self):
        """Return the parameters that allow the user to publish the node."""        
        return {
            "type": hou.FolderParmTemplate,
            "name": "publish_folder",
            "label": "Publish",
            "folder_type": hou.folderType.Tabs,
            "_children": [
                {
                    "type": hou.ButtonParmTemplate,
                    "name": "publish_button",
                    "label": "Submit to Publish",
                    "script_callback": "from ayon_houdini.nodes import wrap_node; "
                        "node_obj = wrap_node(kwargs['node']); node_obj.publish_callback()",
                    "script_callback_language": hou.scriptLanguage.Python,
                },
                {
                    "type": hou.StringParmTemplate,
                    "name": "comment",
                    "label": "Comment",
                    "num_components": 1,
                    "help": "Comment to add to published product."
                },
                {
                    "type": hou.StringParmTemplate,
                    "name": "folder_path",
                    "label": "Folder Path",
                    "num_components": 1,
                    "default_value": ("$AYON_FOLDER_PATH",),
                    "help": "Folder path we want to publish product to (i.e., /001/sh01)."
                },
                {
                    "type": hou.StringParmTemplate,
                    "name": "task",
                    "label": "Task Name",
                    "num_components": 1,
                    "default_value": ("$AYON_TASK_NAME",),
                    "help": "Name of the task we want to publish to."
                },
                {
                    "type": hou.MenuParmTemplate,
                    "name": "product_type",
                    "label": "Product Type",
                    "menu_items": self.product_types,
                    "help": "Type of product we want to publish."
                },
                {
                    "type": hou.StringParmTemplate,
                    "name": "product_name",
                    "label": "Product Name",
                    "num_components": 1,
                    "default_value": ("$OS",),
                    "help": "Name of the product being published."
                },
                {
                    "type": hou.ToggleParmTemplate,
                    "name": "use_hip_version",
                    "label": "Use version from HIP",
                    "default_value": True,
                    "join_with_next": True,
                    "help": "Whether to use as product version the version of the HIP scene.",
                    "disable_when": "{override_version_enable == 1}"
                },
                {
                    "type": hou.ToggleParmTemplate,
                    "name": "override_version_enable",
                    "label": "Override version",
                    "join_with_next": True,
                    "disable_when": "{use_hip_version == 1}",
                    "help": "Whether to override the product version to a specific one. "\
                        "If 'Use version from HIP' and this are disabled, the product version "\
                        "will simply be the next available one."
                },
                {
                    "type": hou.IntParmTemplate,
                    "name": "override_version",
                    "label": "version",
                    "num_components": 1,
                    "min": 1,
                    "min_is_strict": True,
                    "is_label_hidden": True,
                    "disable_when": "{override_version_enable == 0}"
                },
                {
                    "type": hou.SeparatorParmTemplate,
                    "name": "separator1",
                },
                {
                    "type": hou.FolderParmTemplate,
                    "name": "representations",
                    "label": "Representations",
                    "folder_type": hou.folderType.MultiparmBlock,
                    "_children": [
                        {
                            "type": hou.StringParmTemplate,
                            "name": "name",
                            "label": "Name",
                            "num_components": 1,
                            "help": "Name of the representation"
                        },
                        {
                            "type": hou.StringParmTemplate,
                            "name": "path",
                            "label": "Path",
                            "num_components": 1,
                            "help": "Path of the representation"
                        },
                        {
                            "type": hou.ButtonParmTemplate,
                            "name": "show_in_mplay",
                            "label": "Show in MPlay",
                            "help": "Try open path in MPlay",
                            "script_callback": "from ayon_houdini.api parm_utils;"
                                "parm_utils.open_parm_in_mplay(kwargs['node'], 'path{}'.format(kwargs['script_multiparm_index']))",
                            "script_callback_language": hou.scriptLanguage.Python
                        },
                    ]
                },
            ]
        }

    