# -*- coding: utf-8 -*-
"""
A b2sdk SyncReport implementation that adds Dropzone error notifications and
progress percentage.
"""
import sys
import time

import dropzone as dz
from b2sdk.sync.report import SyncReport


class DropzoneSyncReport(SyncReport):
    UPDATE_INTERVAL = 1
    """Minimum time between progress updates"""

    def __init__(self, stdout=sys.stdout, no_progress=False):
        self._determinate = False
        super(DropzoneSyncReport, self).__init__(stdout, no_progress)

    def close(self):
        super(DropzoneSyncReport, self).close()
        if self.warnings:
            dz.alert("Transferred with Warnings:", "\n".join(self.warnings))

    def error(self, message):
        super(DropzoneSyncReport, self).error(message)
        dz.alert("Upload Error", message)

    def _update_progress(self):
        if self.closed or self.no_progress:
            return

        # don't bother updating more frequently than UPDATE_INTERVAL
        now = time.time()
        interval = now - self._last_update_time

        if self.UPDATE_INTERVAL > interval:
            return

        super(DropzoneSyncReport, self)._update_progress()

        try:
            if not self.total_done:
                if self._determinate:
                    self._determinate = False
                    dz.determinate(False)
            elif not self.compare_done:
                if not self._determinate:
                    dz.determinate(True)
                    self._determinate = True
                percent = (self.compare_count / self.total_count) * 100
                dz.percent(percent)
            else:
                if not self._determinate:
                    dz.determinate(True)
                    self._determinate = True
                percent = (self.transfer_bytes / self.total_transfer_bytes) * 100
                dz.percent(percent)
        except ZeroDivisionError:
            pass
