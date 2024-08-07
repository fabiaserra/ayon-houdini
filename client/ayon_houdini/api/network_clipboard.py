"""
This module provides functions for saving Houdini nodes as a file to
a shared network location so artists can easily share their networks
by copy/pasting through the network.
"""
import os
import json
import glob
import datetime
import subprocess

import hou
from ayon_api import slugify_string


DEFAULT_ROOT = "/pipe/houdini/tools/all/xcopy"

# Name of sidecar file to store metadata about the copied nodes
METADATA_FILE = "metadata.json"


def get_net_copy_root_folder():
    return os.getenv("NETWORK_COPY_ROOT", DEFAULT_ROOT)


def get_user_folder():
    user = os.getenv("USER")
    return os.path.join(get_net_copy_root_folder(), user)


def get_copy_dir(mkdir=True, suffix=None):
    """
    Get a directory path for copying files, ensuring the path is unique.

    Args:
        mkdir (bool): Whether to create the directory if it doesn't exist.
        suffix (str): Optional suffix to append to the directory name.

    Returns:
        str: The unique directory path.
    """
    date = datetime.datetime.now().strftime("%Y.%m.%d_%H:%M:%S")
    folder_name = "_".join([date, suffix]) if suffix else date
    path = os.path.join(get_user_folder(), folder_name)

    # Increment the folder name until a unique path is found
    counter = 1
    unique_path = path
    while os.path.exists(unique_path):
        unique_path = f"{path}_{counter}"
        counter += 1

    if mkdir:
        os.makedirs(unique_path)

    return unique_path


def network_copy():
    """Save selected nodes to disk along with a JSON sidecar file.

    Args:
        nodes (hou.Node or list(hou.Node)): Nodes to save.

    Returns:
        bool: True if successful, False otherwise.
    """
    nodes = hou.selectedNodes()
    if len(nodes) == 0:
        hou.ui.displayMessage(
            title="No nodes selected",
            text="Copy failed\nPlease select some nodes to be copied",
            buttons=("OK, I'll try again",),
            severity=hou.severityType.Message,
        )
        return False

    category = nodes[0].type().category().name()
    filename = "{0}.hclip".format(category.upper())

    result, description = hou.ui.readInput(
        "Enter the clipboard name",
        buttons=(
            "Copy to clipboard",
            "Cancel",
        ),
        close_choice=1,
        severity=hou.severityType.Message,
        help="Nodes to copy:\n" + "\n".join(n.path() for n in nodes),
        title="Network Copy",
    )

    if result:
        return False

    parent_node = nodes[0].parent()

    description = slugify_string(description)
    copy_root_dir = get_copy_dir(suffix=description)
    copy_filepath = os.path.join(copy_root_dir, filename)
    parent_node.saveItemsToFile(nodes, copy_filepath)

    data = {
        "node_type": category,
        "copy_filepath": copy_filepath,
        "hip_file": hou.hipFile.path(),
        "parent_node": parent_node.path(),
    }

    path_json = os.path.join(copy_root_dir, METADATA_FILE)
    with open(path_json, "w") as f:
        json.dump(data, f, indent=4)

    msg = f"Saved selected nodes to: {copy_filepath}"
    hou.ui.setStatusMessage(msg, hou.severityType.ImportantMessage)

    result = hou.ui.displayMessage(
        title="Network Copy",
        text="Copied selected nodes\n\nFilepath:\n%s" % copy_filepath,
        buttons=(
            "Ok",
            "Open folder",
        ),
    )

    if result:
        args = ["xdg-open", copy_root_dir]
        os.system(subprocess.list2cmdline(args))

    return True


class ClipboardItem():
    """
    Container to hold all network copied files.

    Args:
        path (str): Path to the folder containing the files.
    """

    def __init__(self, path):
        self.path = path
        self.user = self.path.split(os.sep)[-2]
        self.date = self.path.split(os.sep)[-1]
        self.label = "{1} ({0})".format(self.user, self.date)

        with open(os.path.join(self.path, METADATA_FILE)) as f:
            self.nfo = json.load(f)


def network_paste(kwargs=None):
    """
    Show a popup to paste nodes.

    Args:
        kwargs (dict): Additional arguments.
    """
    node = kwargs["pane"].pwd()
    copy_root = get_net_copy_root_folder()

    items = [
        ClipboardItem(p)
        for p in glob.glob(copy_root + "/*/*")
        if os.path.isfile(os.path.join(p, METADATA_FILE))
    ]
    items = sorted(items, key=lambda i: i.date, reverse=True)

    ret = hou.ui.selectFromList(
        [i.label for i in items],
        message="Select something to paste",
        title="Network Paste"
    )

    for item in [items[i] for i in ret]:
        target_type = item.nfo["node_type"]
        current_type = node.childTypeCategory().name()

        if target_type == current_type:
            target_network = node
        else:
            network_types = {
                "Sop": "geo",
                "Object": "objnet",
                "Driver": "ropnet",
            }
            network_type = network_types.get(
                target_type,
                f"{target_type.lower()}net"
            )

            name = "net_paste_{0}_{1}".format(item.user, item.date)
            name = slugify_string(name)

            target_network = node.createNode(
                network_type, name, run_init_scripts=False
            )

        copy_filepath = item.nfo.get("copy_filepath")
        if copy_filepath:
            target_network.loadItemsFromFile(
                copy_filepath, ignore_load_warnings=False
            )
            hou.ui.setStatusMessage(
                f"Loaded nodes from: '{copy_filepath}'",
                hou.severityType.ImportantMessage
            )
