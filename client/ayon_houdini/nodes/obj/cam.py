import os

from ayon_houdini.nodes.base_node import BaseNode


class Cam(BaseNode):

    def on_created(self):
        self.parm("resx").setExpression("$RESX")
        self.parm("resy").setExpression("$RESY")
        self.parm("aspect").setExpression("$PIX_AR")

        aperture = os.getenv("CAM_APT")
        if aperture:
            self.parm("aperture").setExpression("$CAM_APT")