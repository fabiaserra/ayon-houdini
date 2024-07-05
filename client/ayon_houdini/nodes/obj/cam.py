import os

from ayon_houdini.nodes.base_node import BaseNode


class Cam(BaseNode):

    def on_created(self):
        self.node.parm("resx").setExpression("$RESX")
        self.node.parm("resy").setExpression("$RESY")
        self.node.parm("aspect").setExpression("$PIX_AR")

        aperture = os.getenv("CAM_APT")
        if aperture:
            self.node.parm("aperture").setExpression("$CAM_APT")