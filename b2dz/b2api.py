# -*- coding: utf-8 -*-
"""
"""
import os
import sys

from b2sdk.v2 import B2Api

import dropzone as dz
# from .config import B2DZConfig
from .b2dz_account_info import DropzoneB2AccountInfo


class B2Dropzone(object):
    _config_dialog = """
    *.title = Backblaze B2 Options
    application_key_id.type = textfield
    application_key_id.label = Application Key ID:
    application_key_id.mandatory = 1
    application_key_id.default = %(application_key_id)s
    application_key.type = password
    application_key.label = Application Key:
    application_key.default = %(application_key)s
    application_key.mandatory = 1
    bucket_name.type = textfield
    bucket_name.label = Bucket Name
    bucket_name.default = %(bucket_name)s
    prefix.type = textfield
    prefix.label = Path Prefix
    prefix.default = %(prefix)s
    
    saved.type = defaultbutton
    saved.label = Save
    cancelled.type = cancelbutton
    clear_cache.type = button
    clear_cache.label = Clear Cache
    """

    def __init__(self):
        print(os.environ)
        print(self.key_modifier)
        self.config = DropzoneB2AccountInfo()
        print(self.config)
        if not self.config.is_valid or self.clicked:
            self.show_config()
        self.api = B2Api(self.config)
        if not self.config.allowed or not self.config.auth_token:
            print("Need to reauthorize!")
            self.api.authorize_account("production",
                                       self.config.application_key_id,
                                       self.config.application_key)
        else:
            print("Not reauthorizing. '%s' and '%s'" % (self.config.allowed, self.config.auth_token))

        if self.config.bucket_name is None:
            bucket = self.show_bucket_select()
            if bucket is None:
                dz.fail("No bucket was selected.")
                return
            self.config.bucket_name = bucket.name

    @property
    def action_invoked(self):
        return sys.argv[1]

    @property
    def clicked(self):
        """
        True if this action was triggered by the user clicking the action's
        icon.

        :rtype: bool
        """
        return self.action_invoked == "clicked"

    @property
    def dragged(self):
        """
        True if this action was triggered by drag and drop.

        :rtype: bool
        """
        return self.action_invoked == "dragged"

    @property
    def key_modifier(self):
        return os.environ.get("KEY_MODIFIERS")

    def show_bucket_select(self):
        """
        Prompt user to select a bucket from their account.

        :return: a Bucket object representing the user's selection or None if
                 the user hit Cancel
        :rtype: b2sdk.bucket.Bucket|None
        """

        buckets = self.api.list_buckets()
        bucket_map = {b.name: b for b in buckets}
        popup_options = ["b.option = %s" % b.name for b in buckets]
        dialog_config = """
        *.title = Bucket Select (Backblaze B2)
        cancelled.type = cancelbutton
        b.type = popup
        b.label = Bucket to Use
        %s
        """ % "\n ".join(popup_options)
        result = dz.pashua(dialog_config)
        print(result)
        if result["cancelled"] == "1":
            return None
        bucket_name = result["b"]
        return bucket_map[bucket_name]

    def show_config(self):
        """
        Prompts the user to modify the configuration.
        """
        config = self.config
        print(config)
        config_dict = {
            "application_key_id": config.application_key_id,
            "application_key": config.application_key,
            "bucket_name": config.bucket_name,
            "prefix": config.prefix,
        }
        # replace None values with empty strings
        config_dict = {k: "" if v is None else v for k, v in config_dict.items()}
        dialog_box = self._config_dialog % config_dict
        while True:
            results = dz.pashua(dialog_box)
            print(results)
            if results.get("clear_cache") == "1":
                config.clear_cache()
                continue
            else:
                break

        if results["cancelled"] == "1" or results["saved"] != "1":
            print("Cancelled!")
            return

        config = DropzoneB2AccountInfo(**results)
        self.config = config

