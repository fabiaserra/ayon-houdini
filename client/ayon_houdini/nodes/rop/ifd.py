from ayon_houdini.api import publish
from ayon_houdini.nodes.publish_node import PublishNode


class Ifd(PublishNode):
    product_types = (publish.RENDER_TYPE,)

    default_parms = {
        "soho_outputmode": 1,
        "soho_diskfile": "$HIP/ifd/$HIPNAME/$OS/ifd/$OS.$F4.ifd",
        "vm_picture": "$HIP/renders/$HIPNAME/$OS/$OS.$F4.exr",
    }
