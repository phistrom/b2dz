# -*- coding: utf-8 -*-
"""
"""

import dropzone as dz
from .b2api import B2Dropzone


def clicked():
    B2Dropzone()
    dz.url(False)


dragged = clicked
