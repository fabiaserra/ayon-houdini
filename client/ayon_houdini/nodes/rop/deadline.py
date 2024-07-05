import re

from ayon_houdini.api import constants
from ayon_houdini.nodes.base_node import BaseNode


class Deadline(BaseNode):
    default_parms = {
        "dl_group": constants.DEFAULT_DEADLINE_GROUP,
        "dl_arnold_job": True,
        "dl_arnold_group": constants.DEFAULT_DEADLINE_GROUP,
        "dl_mantra_job": True,
        "dl_mantra_group": constants.DEFAULT_DEADLINE_GROUP,
        "dl_usd_job": True,
        "dl_usd_group": constants.DEFAULT_DEADLINE_GROUP,
        "dl_submit_scene": True,
        "dl_job_name": "$HIPNAME - $OS - $AYON_PROJECT_NAME ($SHOW)",
    }

    # Node parms that have Deadline groups set
    parm_paths = {
        "dl_group",
        "dl_arnold_group",
        "dl_mantra_group",
        "dl_usd_group",
    }

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
                
                existing_items = parm.menuItems()
                try:
                    parm.set(existing_items[existing_items.index(new_group)])
                except ValueError:
                    print(f"WARNING: Group {new_group} not found on {existing_items}, defaulting parm.")
                    parm.revertToDefaults()
