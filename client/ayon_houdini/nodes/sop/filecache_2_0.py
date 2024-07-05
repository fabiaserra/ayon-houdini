from ayon_houdini.api import publish
from ayon_houdini.nodes.publish_node import PublishNode


class Filecache_2_0(PublishNode):
    product_types = (publish.GEO_TYPE, publish.CACHE_TYPE)

    default_parms = {
        "topscheduler": "/obj/topnet/deadlinescheduler"
    }
