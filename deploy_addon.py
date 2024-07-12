import os
import ayon_api

# Retrieve env vars
version = os.environ.get("VERSION")
addon_name = os.environ.get("ADDON_NAME")

# Initialize the service and upload the addon zip
ayon_api.init_service()
ayon_api.upload_addon_zip(f"./package/{addon_name}-{version}.zip")