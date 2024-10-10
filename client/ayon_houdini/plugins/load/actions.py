"""A module containing generic loader actions that will display in the Loader.

"""

from ayon_houdini.api import plugin

from ayon_core.lib import get_ffprobe_streams
from ayon_core.pipeline import get_representation_path
from ayon_houdini.plugins.load import load_image


class SetFrameRangeLoader(plugin.HoudiniLoader):
    """Set frame range excluding pre- and post-handles"""

    product_types = {
        "animation",
        "camera",
        "pointcache",
        "vdbcache",
        "usd",
    }
    representations = {"abc", "vdb", "usd"}

    label = "Set frame range"
    order = 11
    icon = "clock-o"
    color = "white"

    def load(self, context, name, namespace, data):

        import hou

        version_attributes = context["version"]["attrib"]

        start = version_attributes.get("frameStart")
        end = version_attributes.get("frameEnd")

        if start is None or end is None:
            print(
                "Skipping setting frame range because start or "
                "end frame data is missing.."
            )
            return

        hou.playbar.setFrameRange(start, end)
        hou.playbar.setPlaybackRange(start, end)


class SetFrameRangeWithHandlesLoader(plugin.HoudiniLoader):
    """Set frame range including pre- and post-handles"""

    product_types = {
        "animation",
        "camera",
        "pointcache",
        "vdbcache",
        "usd",
    }
    representations = {"abc", "vdb", "usd"}

    label = "Set frame range (with handles)"
    order = 12
    icon = "clock-o"
    color = "white"

    def load(self, context, name, namespace, data):

        import hou

        version_attributes = context["version"]["attrib"]

        start = version_attributes.get("frameStart")
        end = version_attributes.get("frameEnd")

        if start is None or end is None:
            print(
                "Skipping setting frame range because start or "
                "end frame data is missing.."
            )
            return

        # Include handles
        start -= version_attributes.get("handleStart", 0)
        end += version_attributes.get("handleEnd", 0)

        hou.playbar.setFrameRange(start, end)
        hou.playbar.setPlaybackRange(start, end)


class LoadCameraPlateLoader(plugin.HoudiniLoader):
    """Load plate into selected cameras"""

    product_types = {
        "render",
        "plate",
    }

    representations = {"exr", "png", "jpg"}

    label = "Load plate into selected cameras"
    order = 13
    icon = "video-camera"
    color = "white"

    def load(self, context, name, namespace, data):

        import hou

        selected_nodes = hou.selectedNodes()
        cam_nodes = []
        for node in selected_nodes:
            if node.type().name() == "cam":
                cam_nodes.append(node)
            elif node.type().name() == "alembicarchive":
                for children in node.allSubChildren():
                    if children.type().name() == "cam":
                        cam_nodes.append(children)
                        break

        if not cam_nodes:
            self.log.error(
                "No camera selected, can't load plate"
            )
            return

        img_loader = load_image.ImageLoader()
        img_node = img_loader.load(context, name, namespace, data)

        # Find the resolution of selected representation
        representation = context["representation"]
        plate_path = get_representation_path(representation)
        plate_streams = get_ffprobe_streams(plate_path, self.log)
        # Try to find first stream with defined 'width' and 'height'
        # - this is to avoid order of streams where audio can be as first
        # - there may be a better way (checking `codec_type`?)+
        plate_width = None
        plate_height = None
        for plate_stream in plate_streams:
            if "width" in plate_stream and "height" in plate_stream:
                plate_width = int(plate_stream["width"])
                plate_height = int(plate_stream["height"])

        for cam_node in cam_nodes:
            cam_node.parm("vm_background").set(img_node.parm("filename1"))
            self.log.info("Updated vm_background with a reference to '%s'", img_node.parm("filename1").path())
            if plate_width and plate_height:
                resx_parm = cam_node.parm("resx")
                resx_parm.deleteAllKeyframes()
                resx_parm.set(plate_width)

                resy_parm = cam_node.parm("resy")
                resy_parm.deleteAllKeyframes()
                resy_parm.set(plate_height)

                self.log.info("Updated resx and resy with '%s'x'%s", plate_width, plate_height)
