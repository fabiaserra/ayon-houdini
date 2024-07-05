from ayon_houdini.api import publish
from ayon_houdini.nodes.publish_node import PublishNode


class Geometry(PublishNode):
    product_types = (publish.GEO_TYPE, publish.CACHE_TYPE)

    default_parms = {
        "sopoutput": "$HIP/geo/$HIPNAME/$HIPNAME.$OS.$F.bgeo.sc",
    }