import hou

# Houdini version string of MAJOR-MINOR (i.e. 19-5) to be used for
# Deadline groups
_hou_version = hou.applicationVersion()
HOU_VERSION_STR = f"{_hou_version[0]}-{_hou_version[1]}"

# Default Deadline group to use for Houdini jobs
# NOTE: the {} is to set the Houdini version (i.e. "19-5" for Houdini 19.5)
DEFAULT_DEADLINE_GROUP = f"houdini-cpu-{HOU_VERSION_STR}"
