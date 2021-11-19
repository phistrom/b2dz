# -*- coding: utf-8 -*-
"""
Entry functions for Dropzone's two supported function calls:
clicked and dragged.
"""
import traceback

import dropzone as dz
from .b2api import B2Dropzone


def clicked():
    """
    When a user clicks our action script icon, launch configuration menu.
    """
    try:
        B2Dropzone()
    except Exception as ex:
        print(traceback.format_exc())
        dz.fail(" ".join(ex.args))
    else:
        dz.url(False)


def dragged():
    """
    When a user drags files onto our action script icon, transfer the files to
    Backblaze B2.
    """
    try:
        b2dz = B2Dropzone()
        url = b2dz.upload_files()
        dz.finish("Upload complete")
        dz.url(url)
    except Exception as ex:
        dz.fail(" ".join(ex.args))
        raise ex
