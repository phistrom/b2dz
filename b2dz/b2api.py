# -*- coding: utf-8 -*-
import logging
import multiprocessing as mp
import os
import sys
import time
import traceback

import dropzone as dz
from b2sdk.sync.sync import Synchronizer
from b2sdk.v2 import B2Api
from b2sdk.v2 import parse_sync_folder
from .b2dz_account_info import DropzoneB2AccountInfo
from .dzfolder import DropzoneFolder
from .dzprogress import DropzoneSyncReport


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


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
    custom_download_url.type = textfield
    custom_download_url.label = Custom URL (i.e. Cloudflare domain)
    custom_download_url.default = %(custom_download_url)s
    
    saved.type = defaultbutton
    saved.label = Save
    cancelled.type = cancelbutton
    clear_cache.type = button
    clear_cache.label = Clear Cache
    """
    """Definition of the configuration menu using Pashua"""

    def __init__(self):
        logger.debug("Current environ:\n\t%s", os.environ)
        logger.debug("Key modifier: %s", self.key_modifier)
        self.config = DropzoneB2AccountInfo()
        try:
            self.config.load_config()
            print(self.config)
        except Exception as ex:
            logger.error(traceback.format_exc())
            dz.alert("Configuration Corrupt", "%s" % " ".join(ex.args))
            self.config = DropzoneB2AccountInfo()  # fresh new config
            self.config.save_config()
        if not self.config.is_valid or self.clicked:
            accepted = self.show_config()
            if accepted is False:
                dz.fail("Configuration was cancelled.")
                return  # the config screen was cancelled

        self.api = B2Api(self.config)
        if not self.config.allowed or not self.config.auth_token:
            logger.info("Need to reauthorize!")
            self.api.authorize_account("production",
                                       self.config.application_key_id,
                                       self.config.application_key)
        else:
            logger.debug("No need to reauthorize.")

        if self.config.bucket_name is None:
            bucket = self.show_bucket_select()
            if bucket is None:
                dz.fail("No bucket was selected.")
                return
            self.config.bucket_name = bucket.name

    @property
    def b2_dest_path(self):
        """
        The B2 destination URL based on the bucket name and user-desired prefix.

        :return: a b2:// URL to send files to
        :rtype: str
        """
        settings = {
            "bucket_name": self.config.bucket_name,
            "prefix": self.config.prefix,
        }
        b2_path = "b2://%(bucket_name)s%(prefix)s" % settings
        return b2_path

    @property
    def action_invoked(self):
        """
        What action the user performed to launch this script. Can only be
        "clicked" or "dragged"

        :return: the action performed
        :rtype: str
        """
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
    def items(self):
        """
        A list of filepaths that were dragged and dropped onto the action
        script's icon.

        :return: a list of filepaths
        :rtype: list[str]
        """
        return sys.argv[2:]

    @property
    def key_modifier(self):
        """
        What key was held down when files were dragged onto this icon. Despite
        the environment variable being plural, only one modifier can be
        recognized (you cannot hold down shift AND control for example).
        Additionally, no modifier key is recorded when you click the action
        script icon. It is only for dragging files.

        :return: the modifier key name or None if no key was held
        :rtype: str|None
        """
        return os.environ.get("KEY_MODIFIERS")

    def get_url(self, filepath):
        """
        Given a local filepath, return the URL that should be used to download
        the given file from B2.

        :param filepath: a path to a local file you presumably just uploaded
        :type filepath: str
        :return: a URL to download the file back down from B2
        :rtype: str
        """
        filename = os.path.basename(filepath).strip("/")
        prefix = self.config.prefix.strip("/")
        filename = prefix + "/" + filename
        filename = filename.lstrip("/")
        url = self.config.effective_download_url + filename
        return url

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
        logger.debug(result)
        if result["cancelled"] == "1":
            return None
        bucket_name = result["b"]
        return bucket_map[bucket_name]

    def show_config(self):
        """
        Prompts the user to modify the configuration.
        """
        config = self.config
        while True:
            config_dict = {
                "application_key_id": config.application_key_id,
                "application_key": config.application_key,
                "bucket_name": config.bucket_name,
                "prefix": config.prefix,
                "custom_download_url": config.custom_download_url,
            }
            # replace None values with empty strings
            config_dict = {k: "" if v is None else v for k, v in config_dict.items()}
            dialog_box = self._config_dialog % config_dict
            # while True:
            results = dz.pashua(dialog_box)
            logger.debug(results)
            if results.get("clear_cache") == "1":
                config.clear_cache()
                continue
            elif results["cancelled"] == "1" or results["saved"] != "1":
                logger.debug("Cancelled!")
                return False

            config = DropzoneB2AccountInfo(**results)
            if config.is_valid:
                config.save_config()
                self.config = config
                return True
            # if config isn't valid, we show the dialog box again

    def upload_files(self):
        """
        Uploads files found in the ``items`` built-in from Dropzone.
        If only a single file (not a folder!) was dragged onto the icon, this
        function returns the public URL to download the file from B2.

        :return: if only a single file was uploaded, a URL, otherwise False
        :rtype: str|bool
        """
        dz.begin("Uploading files...")
        sync = Synchronizer(max_workers=mp.cpu_count())
        folders = [
            (parse_sync_folder(f, self.api), self._dest_subpath(f))
            for f in self.items if os.path.isdir(f)
        ]
        """:type: list[tuple[b2sdk.sync.folder.AbstractFolder,str]]"""

        # all loose files that were dragged onto us that are not folders
        # are covered by "DropzoneFolder"
        files = [i for i in self.items if not os.path.isdir(i)]
        if files:
            folders.append((DropzoneFolder(files), self.b2_dest_path))
        logger.debug(folders)
        for folder, dest_path in folders:
            logger.debug(folder, dest_path)
            dest_folder = parse_sync_folder(dest_path, self.api)
            with DropzoneSyncReport(sys.stdout, False) as reporter:
                millis = int(round(time.time() * 1000))
                sync.sync_folders(folder, dest_folder, millis, reporter)
        if len(folders) == 1 and len(files) == 1:
            return self.get_url(files[0])
        else:
            return False

    def _dest_subpath(self, filepath):
        """
        Returns an adjusted B2 destination path to include the name of the
        folder that is pointed to by ``filepath``. This is so that when you
        drag a folder called "whatever" onto the script, the subfolders and
        files of "whatever" go under a "whatever" folder too, and not just
        straight into root or user-provided prefix.
        So ``b2://my-bucket/myprefix`` becomes
        ``b2://my-bucket/myprefix/whatever``.

        :param filepath: the path to a local folder
        :type filepath: str
        :return: b2_dest_path + the name of the folder pointed to by filepath
        :rtype: str
        """
        if not os.path.isdir(filepath):
            raise ValueError("%s is not a directory" % filepath)
        parent_dir_name = os.path.basename(filepath)
        return self.b2_dest_path + parent_dir_name
