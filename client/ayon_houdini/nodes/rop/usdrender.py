from ayon_houdini.api import publish
from ayon_houdini.nodes.publish_node import PublishNode


class Usdrender(PublishNode):
    
    product_types = (publish.RENDER_TYPE,)

    default_parms = {
        "outputimage": "$HIP/renders/$HIPNAME/$OS/$OS.$F4.exr",
        "lopoutput": "$HIP/ifd/$HIPNAME/render.$F4.usd",
        "savetodirectory_directory": "$HIP/ifd/$HIPNAME/",
        "runcommand": False
    }
