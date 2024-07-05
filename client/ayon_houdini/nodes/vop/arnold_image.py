from ayon_houdini.api import publish
from ayon_houdini.nodes.publish_node import PublishNode


class Arnold_image(PublishNode):
    product_types = (publish.TEXTURE_TYPE,)

    default_parms = {
        "autotx": False,
    }
