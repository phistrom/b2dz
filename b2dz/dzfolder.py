# -*- coding: utf-8 -*-
"""
A virtual source folder that holds the files (not folders!) that were dropped
on our action script's icon.
"""

import os.path

from b2sdk.sync.exception import UnSyncableFilename
from b2sdk.sync.folder import AbstractFolder
from b2sdk.sync.path import LocalSyncPath
from b2sdk.sync.scan_policies import DEFAULT_SCAN_MANAGER
from b2sdk.utils import get_file_mtime


class DropzoneFolder(AbstractFolder):
    """
    A b2sdk "Folder" object that represents loose files dragged onto our
    action script's icon. Synchronizer() operates on a source folder and a
    destination folder.
    """

    def __init__(self, file_list):
        file_map = {os.path.basename(f): f for f in file_list
                    if not os.path.isdir(f)}
        if len(file_map) != len(file_list):
            dupes = [k for k, v in file_map.items() if v not in file_list]
            raise ValueError("These file names would be duplicated: %s" %
                             ", ".join(dupes))

        self._file_map = file_map

    def all_files(self, reporter, policies_manager=DEFAULT_SCAN_MANAGER):
        for filename, filepath in self._file_map.items():
            syncpath = LocalSyncPath(
                absolute_path=filepath,
                relative_path=filename,
                mod_time=get_file_mtime(filepath),
                size=os.path.getsize(filepath)
            )
            yield syncpath

    def ensure_non_empty(self):
        pass  # shouldn't even be possible

    def folder_type(self):
        return "local"

    def make_full_path(self, file_name):
        try:
            return self._file_map[file_name]
        except KeyError as ex:
            raise UnSyncableFilename from ex
