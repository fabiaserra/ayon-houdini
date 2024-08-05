# -*- coding: utf-8 -*-
"""AYON startup script."""
from ayon_core.pipeline import install_host
from ayon_houdini.api import HoudiniHost
from ayon_houdini.nodes import decorator


def main():
    print("Installing AYON ...")
    install_host(HoudiniHost())
    decorator.init()


main()