import hou

from ayon_houdini.api import parm_utils

from ayon_houdini.api import publish
from ayon_houdini.nodes.publish_node import PublishNode


class Arnold(PublishNode):
    
    product_types = (publish.RENDER_TYPE,)

    default_parms = {
        "trange": 1,
        "ar_export_referenced_materials": True,
        "ar_picture": "$HIP/renders/$HIPNAME/$OS/`$OS`_`chs('ax_template')`.$F4.exr",
        "ar_overscan_enable": True,
        "ar_overscan": ("$RESY * 0.05", "$RESY * 0.05", "$RESX * 0.05", "$RESX * 0.05"),
        # TODO: In the future we'd like to be able to set tiling so we can make use
        # of Append and denoising... but it currently crashes Nuke and RV when trying
        # to review non scanline renders
        "ar_picture_tiling": 0,
        "ar_exr_compression": "zips",
        "ar_exr_color_space": "ACES - ACEScg",
        "ar_exr_half_precision": True,
        "ar_deepexr_beauty_half_precision": True,
        "ar_deepexr_alpha_half_precision": True,
        "ar_exr_multipart": True,
        "ar_ass_export_enable": True,
        "ar_ass_file": "$HIP/ass/$HIPNAME/$OS/ass/$OS_`chs('ax_template')`.$F4.ass",
        "ar_texture_auto_maketx": False,
        "ar_abort_on_license_fail": True,
        "ar_picture_append": False,
        "ar_aov_shaders": "/obj/scn_mats/user_aovs",
    }

    template_items = (
        "Low",
        "Medium",
        "High",
        "Low_Deep",
        "Medium_Deep",
        "High_Deep",
    )

    bty_aovs = {
        "albedo": {},
        "diffuse_direct": {},
        "diffuse_indirect": {},
        "specular": {},
        "coat": {},
        "transmission_direct": {},
        "transmission_indirect": {},
        "sss": {},
        "emission": {},
    }

    util_aovs = {
        "N": {
            "ar_aov_picture_format": "exr",
            "ar_aov_exr_compression": "zips",
            "ar_aov_exr_precision": "float",
        },
        "Z": {
            "ar_aov_picture_format": "exr",
            "ar_aov_type": "float",
            "ar_aov_exr_compression": "zips",
            "ar_aov_exr_precision": "float",
            "ar_aov_pixel_filter": "closest_filter",
        },
        "rest": {
            "ar_aov_exr_enable_layer_name": True,
            "ar_aov_exr_layer_name": "Pref",
            "ar_aov_picture_format": "exr",
            "ar_aov_exr_compression": "zips",
            "ar_aov_exr_precision": "float",
        },
        "P": {
            "ar_aov_picture_format": "exr",
            "ar_aov_exr_compression": "zips",
            "ar_aov_exr_precision": "float",
        },
        "crypto_asset": {
            "ar_aov_picture_format": "exr",
            "ar_aov_exr_compression": "zips",
        },
        "crypto_object": {
            "ar_aov_picture_format": "exr",
            "ar_aov_exr_compression": "zips",
        },
        "crypto_material": {
            "ar_aov_picture_format": "exr",
            "ar_aov_exr_compression": "zips",
        },
    }

    extra_parm_data = [
        {
            "type": hou.ToggleParmTemplate,
            "name": "publish_beauty",
            "label": "Publish Beauty",
            "default_value": True,
            "join_with_next": True,
            "help": "Whether to publish the beauty file from Arnold",
        },
        {
            "type": hou.ToggleParmTemplate,
            "name": "publish_util",
            "label": "Publish Util",
            "default_value": True,
            "help": "Whether to publish the beauty file from Arnold",
        },
    ]

    def get_publish_parm_template(self):
        parm_template = super().get_publish_parm_template()
        # Insert some extra parm template after publish button
        return parm_utils.insert_parm_data(
            parm_template, self.extra_parm_data, 1
        )

    def on_created(self):
        """Callback function to run when creating node."""
        super().on_created()

        ptg = self.node.parmTemplateGroup()

        # Add templates parm menu
        templates_parm = hou.MenuParmTemplate(
            "ax_template",
            "AX Template",
            menu_items=self.template_items,
            default_value=2,
            script_callback="from ayon_houdini.nodes.rop.arnold import template_callback;"
                "template_callback(**kwargs)",
            script_callback_language=hou.scriptLanguage.Python,
        )
        ptg.insertBefore(ptg.findIndices("trange"), templates_parm)
        self.node.setParmTemplateGroup(ptg)

        # Create dictionary of AOV parms to set in node
        aov_parms = {}
        num_aovs = len(self.bty_aovs) + len(self.util_aovs)
        self.node.parm("ar_aovs").set(num_aovs)
        aov_idx = 1
        for aov_label, aov_data in self.bty_aovs.items():
            aov_parms[f"ar_aov_label{aov_idx}"] = aov_label
            for aov_parm, aov_value in aov_data.items():
                aov_parms[f"{aov_parm}{aov_idx}"] = aov_value
            aov_idx += 1

        for aov_label, aov_data in self.util_aovs.items():
            aov_parms[f"ar_aov_label{aov_idx}"] = aov_label
            aov_parms[f"ar_aov_separate{aov_idx}"] = True
            aov_parms[f"ar_aov_separate_file{aov_idx}"] = "$HIP/renders/$HIPNAME/$OS/`$OS`_`chs('ax_template')`_util.$F4.exr"
            for aov_parm, aov_value in aov_data.items():
                aov_parms[f"{aov_parm}{aov_idx}"] = aov_value
            aov_idx += 1
        
        self.node.setParms(aov_parms)

        # Force callback of template parm
        template_callback(
            script_value=self.node.parm("ax_template").evalAsString(),
            node=self.node
        )
    
    def publish_callback(self, silent=False):
        """Callback when publish button gets clicked"""
        success = True
        message = ""
        
        message, success = self.pre_publish_callback(silent=silent)
        if not success:
            return message, False

        # Publish the output node normally
        base_product_name = self.node.parm("product_name").evalAsString()
        if self.node.parm("publish_beauty").eval():
            message_, success_ = publish.submit_to_publish(
                self.node,
                publish_data = {
                    "product_name": f"{base_product_name}_beauty"
                },
                silent=True
            )
            if not success_:
                success = False
            message += f"{message_}\n"

        if self.node.parm("publish_util").eval():
            output_files = set()
            num_aovs = self.node.parm("ar_aovs").eval()
            for aov_idx in range(1, num_aovs):
                is_enabled = self.node.parm(f"ar_enable_aov{aov_idx}").eval()
                if not is_enabled:
                    continue
                
                is_separate_file = self.node.parm(f"ar_aov_separate{aov_idx}").eval()
                if is_separate_file:
                    output_files.add(self.node.parm(f"ar_aov_separate_file{aov_idx}").evalAsString())
            
            if len(output_files) > 1:
                success = False
                message += "More than one separate AOV file, only publishing the last one as Util\n"

            publish_data = {
                "representations": {"exr": output_files.pop()},
                "product_name": f"{base_product_name}_util"
            }
            message_, success_ = publish.submit_to_publish(
                self.node,
                publish_data = publish_data,
                silent=True
            )
            if not success_:
                success = False
            message += f"{message_}\n"
        
        if success:
            if not silent:
                hou.ui.displayMessage(
                    message,
                    title="Submission successful",
                    severity=hou.severityType.Message, 
                )
            return message, True
        
        if not silent:
            hou.ui.displayMessage(
                message,
                title="Submission error",
                severity=hou.severityType.Error
            )
        return message, False


def template_callback(**kwargs):
    """Callback function when AX Template parm changes."""
    template_name = kwargs["script_value"]
    parm_overrides = {
        "ar_AA_samples": 3,
        "ar_mb_xform_enable": True,
        "ar_mb_xform_keys": 2,
        "ar_mb_dform_enable": True,
        "ar_mb_dform_keys": 2,
        "ar_picture_format": "exr",
    }
    if "Medium" in template_name:
        parm_overrides["ar_AA_samples"] = 6
        parm_overrides["ar_mb_xform_keys"] = 3
        parm_overrides["ar_mb_dform_keys"] = 3
    elif "High" in template_name:
        parm_overrides["ar_AA_samples"] = 8
        parm_overrides["ar_mb_xform_keys"] = 5
        parm_overrides["ar_mb_dform_keys"] = 5
    
    if "Deep" in template_name:
        parm_overrides["ar_picture_format"] = "deepexr"
    
    node = kwargs["node"]
    node.setParms(parm_overrides)