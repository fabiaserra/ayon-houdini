import os
import re

from ayon_houdini.api import constants
from ayon_houdini.nodes.base_node import BaseNode


is_ayon = bool(os.getenv("AYON_BUNDLE_NAME"))


class Deadlinescheduler(BaseNode):
    default_parms = {
        "usetaskcallbackport": True,
        "taskcallbackport": 54321,
        "usemqrelayport": True,
        "mqrelayport": 54322,
        "mqusage": 0,
        "deadline_mqjobgroup": constants.DEFAULT_DEADLINE_GROUP,
        "deadline_jobgroup": constants.DEFAULT_DEADLINE_GROUP,
        "deadline_hfs": "\$HOUDINI_ROOT",
        "deadline_jobname": "PDG TASKS - $HIPNAME - $AYON_PROJECT_NAME ($SHOW)",
        "deadline_mqjobname": "PDG MQ - $HIPNAME - $AYON_PROJECT_NAME ($SHOW)",
        "deadline_submitjobname": 'PDG->Submit cook of `opname("..")` in $HIPNAME.hip - $AYON_PROJECT_NAME ($SHOW)',
        "deadline_overrideplugin": 1,
        "deadline_plugindirectory": "$AX_HOUDINI_TOOLS/deadline_plugins",
    }

    # Node parms that have Deadline groups set
    parm_paths = {
        "deadline_mqjobgroup",
        "deadline_jobgroup",
    }

    def on_created(self):
        super().on_created()

        # These multiparm parms need to be only set because we can't set them through the parm template group
        parms_to_set = {
            "deadline_envmulti": 6,
            "deadline_envname1": "AYON_RENDER_JOB" if is_ayon else "OPENPYPE_RENDER_JOB",
            "deadline_envvalue1": "1",
            "deadline_envname2": "AYON_BUNDLE_NAME" if is_ayon else "OPENPYPE_PUBLISH_JOB",
            "deadline_envvalue2": "$AYON_BUNDLE_NAME" if is_ayon else "0",
            "deadline_envname3": "AYON_PROJECT_NAME" if is_ayon else "AVALON_PROJECT",
            "deadline_envvalue3": "$AYON_PROJECT_NAME" if is_ayon else "$AVALON_PROJECT",
            "deadline_envname4": "AYON_FOLDER_PATH" if is_ayon else "AVALON_ASSET",
            "deadline_envvalue4": "$AYON_FOLDER_PATH" if is_ayon else "$AVALON_ASSET",
            "deadline_envname5": "AYON_TASK_NAME" if is_ayon else "AVALON_TASK",
            "deadline_envvalue5": "$AYON_TASK_NAME" if is_ayon else "$AVALON_TASK",
            "deadline_envname6": "AYON_APP_NAME" if is_ayon else "AVALON_APP_NAME",
            "deadline_envvalue6": "$AYON_APP_NAME" if is_ayon else "$AVALON_APP_NAME",
        }
        self.node.setParms(parms_to_set)

    def on_loaded(self):
        for parm_path in self.parm_paths:
            parm = self.node.parm(parm_path)
            dl_group = parm.evalAsString()
            if constants.HOU_VERSION_STR not in dl_group:
                new_group, num_subs = re.subn(r"\d+-\d+", constants.HOU_VERSION_STR, dl_group)
                # If there was no replacement, check if the group set is one of the legacy ones
                if not num_subs:
                    if dl_group == "houdini-cpu" or dl_group.endswith(("xeon", "epyc")) or dl_group == "none":
                        new_group = constants.DEFAULT_DEADLINE_GROUP
                        print(
                            f"INFO: Replaced legacy '{dl_group}' group from parm '{parm.path()}' with new group: '{new_group}'."
                        )
                else:
                    print(
                        f"INFO: Updated '{dl_group}' group from parm '{parm.path()}' with new Houdini version: '{new_group}'."
                    )
                
                parm.set(new_group)

        # Make sure HFS root is correct for Deadline
        hfs_root_parm = self.node.parm("deadline_hfs")
        hfs_root_parm.set("\$HOUDINI_ROOT")