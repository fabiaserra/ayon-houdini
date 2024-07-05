import os

import hou
import assettools
from qtpy import QtWidgets


class CustomVHDASaveDialog(assettools.VHDASaveDialog):
    """Override standard Houdini HDA dialog to streamline the options to our needs."""
    
    def __init__(self, node: hou.Node, method: assettools.Method,
                 parent: QtWidgets.QWidget = None):
        
        # Call parent method to do everything like the default dialog
        super().__init__(node, method, parent)

        # And then hide and modify some of the dialogs after they have been created
        
        # Not allow artist to uncheck things we want enabled
        # always
        # self._submenubox.setEnabled(False)
        self._syncbtn.setEnabled(False)
        self._fullnamebox.setEnabled(False)
        self._authorcheck.setEnabled(False)
        self._versioncheck.setEnabled(False)
        self._locationbox.setEnabled(False)
        self._prefixcatcheck.setEnabled(False)
        self._patternbox.setEnabled(False)
        self._createdirscheck.setEnabled(False)
        self._filepathbox.setEnabled(False)

        # Fill some defaults
        self._submenubox.clear()
        self._submenubox.setCurrentText("Alkemy-X")
        self._authorbox.setCurrentText("ax")
        existing_save_path = self._filepathbox.text()
        filename = os.path.basename(existing_save_path)
        save_dir = f"/proj/{os.getenv('SHOW')}/tools/houdini/all/otls"
        self._filepathbox.setText(f"{save_dir}/{filename}")
        self._locationbox.setCurrentText(save_dir)


def createAssetFromSubnet(node):
    dialog = CustomVHDASaveDialog(
        node, method=assettools.Method.CreateAsset
    )
    dialog.show()


def saveAs(node: hou.Node):
    dialog = CustomVHDASaveDialog(node, method=assettools.Method.SaveAs)
    dialog.show()


def increaseMajorVersion(node: hou.Node):
    dialog = CustomVHDASaveDialog(node, method=assettools.Method.IncreaseMajor)
    dialog.show()


def increaseMinorVersion(node: hou.Node):
    dialog = CustomVHDASaveDialog(node, method=assettools.Method.IncreaseMinor)
    dialog.show()