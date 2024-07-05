from ayon_houdini.api import publish
from ayon_houdini.nodes.publish_node import PublishNode


class Alembic(PublishNode):
    product_types = (publish.GEO_TYPE, publish.CACHE_TYPE)

    default_parms = {
        "filename": "$HIP/geo/$HIPNAME/$HIPNAME.$OS.abc",
    }
