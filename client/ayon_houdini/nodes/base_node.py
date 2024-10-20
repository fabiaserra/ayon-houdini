class BaseNode(object):
    default_parms = {}

    def on_created(self):
        """Callback when node gets called"""
        ptg = self.parmTemplateGroup()

        # Replace a bunch of parm defaults to make it easier for
        # artists to know what has been changed
        ptg = self.replace_parm_defaults(ptg)
        self.setParmTemplateGroup(ptg)

        # We go over all the default parms again and set them as
        # the parm defaults doesn't work for some parms for
        # some reason (i.e. "ar_export_referenced_materials")
        for parm_name, parm_value in self.default_parms.items():
            parm = self.parm(parm_name)
            if not parm:
                continue
            self.parm(parm_name).set(parm_value)

    def on_loaded(self):
        """Callback when node gets loaded"""
        pass

    def replace_parm_defaults(self, ptg):
        """Util function to replace parm template group parm defaults with given dict"""
        # Set values as defaults on node parm template group
        for parm_name, parm_value in self.default_parms.items():
            p = ptg.find(parm_name)
            default_value = p.defaultValue()
            if isinstance(default_value, tuple):
                if isinstance(default_value[0], type(parm_value)):
                    p.setDefaultValue((parm_value,))
                elif isinstance(parm_value, tuple):
                    p.setDefaultExpression(parm_value)
                else:
                    p.setDefaultExpression((parm_value,))
            elif isinstance(default_value, type(parm_value)):
                p.setDefaultValue(parm_value)
            else:
                p.setDefaultExpression(parm_value)
            ptg.replace(ptg.find(parm_name), p)

        return ptg