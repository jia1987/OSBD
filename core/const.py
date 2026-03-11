import os, sys


class Path():
    # root
    ROOT = os.getcwd()
    # config dir
    # resource
    CONFIG_DIR = os.path.join(ROOT, 'config')
    RC_DIR = os.path.join(ROOT, '_rc')

    # config
    CONFIG = os.path.join(CONFIG_DIR, 'config.json')
    # ICON
    ICON = os.path.join(RC_DIR, 'icon')

    # OUTPUT
    OUTPUT_DIR = os.path.join(ROOT, 'output')


class Text():
    # title
    APP_NAME = '漆包线缺陷检测工具'


__all__ = ("Path", 'Text')
