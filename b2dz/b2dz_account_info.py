# -*- coding: utf-8 -*-
"""
A b2sdk AccountInfo object for persisting all the information needed to call
b2sdk API functions using Dropzone's ``save_value`` function.
"""
import base64
import collections
import json
import logging
import os
import zlib
from datetime import datetime
from functools import wraps

try:
    from urlparse import urlparse, urljoin
except ImportError:
    from urllib.parse import urlparse
    from urllib.parse import urljoin

import dropzone as dz
from b2sdk.account_info.exception import MissingAccountData
from b2sdk.v2 import UrlPoolAccountInfo


logger = logging.getLogger(__name__)


ACTION_START = datetime.now()
"""Used for prefix percent placeholder formatting"""
logger.debug("Action Start: %s", ACTION_START)


def _missing_error(function):
    """
    Raise MissingAccountData if function's result is None.
    """

    @wraps(function)
    def inner(*args, **kwargs):
        assert function.__name__.startswith('get_')
        result = function(*args, **kwargs)
        if result is None:
            # assumes that it is a "get_field_name"
            raise MissingAccountData(function.__name__[4:])
        return result

    return inner


class DropzoneB2AccountInfo(UrlPoolAccountInfo):
    """
    B2 Account Info object that persists B2 settings in Dropzone's value store.
    """

    ACCESS_KEY_KEY = "B2DZ_APPLICATION_KEY_ID"
    ACCOUNT_ID_KEY = "B2DZ_ACCOUNT_ID"
    ALLOWED_KEY = "B2DZ_ALLOWED_KEY"
    API_URL_KEY = "B2DZ_API_URL"
    AUTH_TOKEN_KEY = "B2DZ_AUTH_TOKEN"
    BUCKETS_KEY = "B2DZ_BUCKETS"
    BUCKET_NAME_KEY = "B2DZ_BUCKET_NAME"
    CUSTOM_DOWNLOAD_URL_KEY = "B2DZ_CUSTOM_DOWNLOAD_URL"
    DOWNLOAD_URL_KEY = "B2DZ_DOWNLOAD_URL"
    MIN_PART_SIZE_KEY = "B2DZ_MIN_PART_SIZE"
    PREFIX_KEY = "B2DZ_PREFIX_PATH"
    REALM_KEY = "B2DZ_REALM_KEY"
    RECOMMENDED_PART_SIZE_KEY = "B2DZ_RECOMMENDED_PART_SIZE"
    S3_API_URL_KEY = "B2DZ_S3_API_URL"
    SECRET_KEY_KEY = "B2DZ_APPLICATION_KEY"

    def __init__(self, application_key_id=None, application_key=None,
                 bucket_name=None, prefix=None, custom_download_url=None,
                 **kwargs):
        super(DropzoneB2AccountInfo, self).__init__()

        self._absolute_minimum_part_size = None
        self._account_id = None
        self._allowed = None
        self._api_url = None
        self._auth_token = None
        self._auth_token = None
        self._bucket_name = None
        self._buckets = None
        self._download_url = None
        self._realm = None
        self._recommended_part_size = None
        self._s3_api_url = None

        self.application_key_id = application_key_id
        self.application_key = application_key
        self.bucket_name = bucket_name
        self.prefix = prefix
        self.custom_download_url = custom_download_url

    def load_config(self):
        self.absolute_minimum_part_size = self._load_value(self.MIN_PART_SIZE_KEY)
        self.account_id = self._load_value(self.ACCOUNT_ID_KEY)
        self.allowed = self._load_json_value(self.ALLOWED_KEY)
        self.api_url = self._load_value(self.API_URL_KEY)
        self.application_key = self._load_value(self.SECRET_KEY_KEY)
        self.application_key_id = self._load_value(self.ACCESS_KEY_KEY)
        self.auth_token = self._load_value(self.AUTH_TOKEN_KEY)
        self.bucket_name = self._load_value(self.BUCKET_NAME_KEY)
        self.buckets = self._load_json_value(self.BUCKETS_KEY)
        self.custom_download_url = self._load_value(self.CUSTOM_DOWNLOAD_URL_KEY)
        self.download_url = self._load_value(self.DOWNLOAD_URL_KEY)
        self.prefix = self._load_value(self.PREFIX_KEY)
        self.realm = self._load_value(self.REALM_KEY)
        self.recommended_part_size = self._load_value(self.RECOMMENDED_PART_SIZE_KEY)
        self.s3_api_url = self._load_value(self.S3_API_URL_KEY)

    def save_config(self):
        self._save_value(self.MIN_PART_SIZE_KEY, self.absolute_minimum_part_size)
        self._save_value(self.ACCOUNT_ID_KEY, self.account_id)
        self._save_json_value(self.ALLOWED_KEY, self.allowed)
        self._save_value(self.API_URL_KEY, self.api_url)
        self._save_value(self.SECRET_KEY_KEY, self.application_key)
        self._save_value(self.ACCESS_KEY_KEY, self.application_key_id)
        self._save_value(self.AUTH_TOKEN_KEY, self.auth_token)
        self._save_value(self.BUCKET_NAME_KEY, self.bucket_name)
        self._save_json_value(self.BUCKETS_KEY, self.buckets)
        self._save_value(self.CUSTOM_DOWNLOAD_URL_KEY, self.custom_download_url)
        self._save_value(self.DOWNLOAD_URL_KEY, self.download_url)
        self._save_value(self.PREFIX_KEY, self.prefix)
        self._save_value(self.REALM_KEY, self.realm)
        self._save_value(self.RECOMMENDED_PART_SIZE_KEY, self.recommended_part_size)
        self._save_value(self.S3_API_URL_KEY, self.s3_api_url)

    @staticmethod
    def _load_value(key):
        value = os.environ.get(key)
        logger.debug("_load_value: Key '%s' was:\n%s", key, value)
        # try:
        #     value = value.replace("\\:", ":").replace('\\"', '"')
        # except AttributeError:
        #     pass
        return value

    @classmethod
    def _load_json_value(cls, key):
        value = cls._load_value(key)
        if not value:
            return None
        value = base64.b64decode(value)
        value = zlib.decompress(value).decode("utf-8")
        return json.loads(value)

    @staticmethod
    def _save_value(key, value):
        if value is None or value == "":  # We still want to allow False or 0
            dz.remove_value(key)
        else:
            value = str(value)
            # value = value.replace(":", "\\:").replace('"', '\\"')
            dz.save_value(key, value)
            os.environ[key] = value

    @classmethod
    def _save_json_value(cls, key, value):
        if value is not None:
            value = json.dumps(value, separators=(",", ":"))
            value = zlib.compress(value.encode("utf-8"))
            value = base64.b64encode(value).decode("utf-8")
        cls._save_value(key, value)

    @property
    def absolute_minimum_part_size(self):
        return self._absolute_minimum_part_size

    @absolute_minimum_part_size.setter
    def absolute_minimum_part_size(self, value):
        if value is not None:
            value = int(value)
        self._absolute_minimum_part_size = value

    @property
    def account_id(self):
        return self._account_id

    @account_id.setter
    def account_id(self, value):
        self._account_id = value

    @property
    def application_key(self):
        return self._application_key

    @application_key.setter
    def application_key(self, value):
        self._application_key = value

    @property
    def allowed(self):
        """
        :rtype: dict
        """
        return self._allowed

    @allowed.setter
    def allowed(self, value):
        """
        :type value: dict
        """
        self._allowed = value

    @property
    def application_key_id(self):
        return self._application_key_id

    @application_key_id.setter
    def application_key_id(self, value):
        self._application_key_id = value

    @property
    def auth_token(self):
        return self._auth_token

    @auth_token.setter
    def auth_token(self, value):
        self._auth_token = value

    @property
    def api_url(self):
        return self._api_url

    @api_url.setter
    def api_url(self, value):
        self._api_url = value

    @property
    def bucket_name(self):
        # if this application key is limited to only one bucket,
        # then that's the bucket name we should be returning
        if self.restricted_bucket:
            return self.restricted_bucket
        return self._bucket_name

    @bucket_name.setter
    def bucket_name(self, value):
        if self.restricted_bucket:
            if not value:
                value = self.restricted_bucket
            elif self.restricted_bucket != value:
                raise ValueError("This application key is restricted to '%s' "
                                 "and cannot be set to '%s'" %
                                 (self.restricted_bucket, value))

        self._bucket_name = value

    @property
    def buckets(self):
        """
        Returns a dictionary of buckets accessible to the account. The key is
        the bucket's name and the value is its ID.

        :rtype: dict[str, str]
        """
        return {} if self._buckets is None else self._buckets

    @buckets.setter
    def buckets(self, value):
        """
        :type value: dict[str, str]|None
        """
        if value is None:
            value = {}
        if not isinstance(value, collections.Mapping):
            raise ValueError("`buckets` should be a dictionary. Not a '%s'."
                             % type(value).__name__)
        self._buckets = value

    @property
    def custom_download_url(self):
        """
        Custom download URL prefix if the user specified one. Otherwise
        returns the B2 "friendly URL" for files in the configured bucket.

        :return: the start of the URL for downloading a file from B2
        :rtype: str
        """
        return self._custom_download_url

    @custom_download_url.setter
    def custom_download_url(self, value):
        if not value:
            self._custom_download_url = None
            return
        parsed = urlparse(value)
        if not parsed.scheme and not parsed.netloc:
            raise ValueError("Invalid custom URL.")
        value = value.rstrip("/") + "/"
        self._custom_download_url = value

    @property
    def download_url(self):
        """
        A download URL that is set by the ``authorize_account`` API call.
        Usually looks similar to ``https://f001.backblazeb2.com``.

        :rtype: str
        """
        return self._download_url

    @download_url.setter
    def download_url(self, value):
        self._download_url = value

    @property
    def effective_download_url(self):
        """
        The custom URL provided by the user. If the user did not provide a
        custom URL, then we use the one provided by Backblaze B2.
        :rtype: str|None
        """
        if self.custom_download_url:
            return self.custom_download_url
        if not self.download_url:
            return None
        urlparts = (self.download_url, "file", self.bucket_name)
        urlparts = [p.strip("/") for p in urlparts]
        # returns <download_url>/file/<bucket-name>/
        return "/".join(urlparts) + "/"

    @property
    def prefix(self):
        return self._prefix

    @prefix.setter
    def prefix(self, value):
        try:
            value = value.strip("/")
        except AttributeError:
            pass
        if not value:
            value = "/"
        else:
            value = "/" + value + "/"
        self._prefix = value

    @property
    def effective_prefix(self):
        prefix = ACTION_START.strftime(self.prefix)
        return prefix

    @property
    def realm(self):
        return self._realm

    @realm.setter
    def realm(self, value):
        self._realm = value

    @property
    def recommended_part_size(self):
        return self._recommended_part_size

    @recommended_part_size.setter
    def recommended_part_size(self, value):
        if value is not None:
            value = int(value)
        self._recommended_part_size = value

    @property
    def restricted_bucket(self):
        """
        This is the name of the bucket that this application key is restricted
        to. If this application key has permission to access any bucket in the
        account, returns None.

        :return: the name of the bucket this application key is restricted to
                 or None if it can access any bucket
        :rtype: str|None
        """
        try:
            return self.allowed["bucketName"]
        except (KeyError, TypeError):
            # self.allowed was probably None
            return None

    @property
    def s3_api_url(self):
        return self._s3_api_url

    @s3_api_url.setter
    def s3_api_url(self, value):
        self._s3_api_url = value

    def clear(self):
        self.clear_cache()
        self._clear()
        return super(DropzoneB2AccountInfo, self).clear()

    def clear_cache(self):
        """
        Clear just the fields that are set by b2sdk and not usually by the
        user directly.
        """
        self.account_id = None
        self.allowed = None
        self.api_url = None
        self.auth_token = None
        self.buckets = None
        self.download_url = None
        self.recommended_part_size = None
        self.absolute_minimum_part_size = None
        self.realm = None
        self.s3_api_url = None

    def _clear(self):
        self.application_key_id = None
        self.application_key = None

    @property
    def is_valid(self):
        return bool(self.application_key_id and self.application_key)

    def refresh_entire_bucket_name_cache(self, name_id_iterable):
        self.buckets = dict(name_id_iterable)
        self.save_config()

    def remove_bucket_name(self, bucket_name):
        try:
            del self.buckets[bucket_name]
            self.save_config()
        except KeyError:
            pass

    def save_bucket(self, bucket):
        """
        :type bucket: b2sdk.bucket.Bucket
        """
        self.buckets[bucket.name] = bucket.id_
        self.save_config()

    def get_bucket_id_or_none_from_bucket_name(self, bucket_name):
        return self.buckets.get(bucket_name)

    def get_bucket_name_or_none_from_bucket_id(self, bucket_id):
        for name, _id in self.buckets.items():
            if bucket_id == _id:
                return name
        return None

    @_missing_error
    def get_account_id(self):
        return self.account_id

    @_missing_error
    def get_application_key_id(self):
        return self.application_key_id

    @_missing_error
    def get_account_auth_token(self):
        return self.auth_token

    @_missing_error
    def get_api_url(self):
        return self.api_url

    @_missing_error
    def get_application_key(self):
        return self.application_key

    @_missing_error
    def get_download_url(self):
        return self.download_url

    @_missing_error
    def get_realm(self):
        return self.realm

    @_missing_error
    def get_recommended_part_size(self):
        return self.recommended_part_size

    @_missing_error
    def get_absolute_minimum_part_size(self):
        return self.absolute_minimum_part_size

    @_missing_error
    def get_allowed(self):
        return self.allowed

    @_missing_error
    def get_s3_api_url(self):
        return self.s3_api_url

    def _set_auth_data(self, account_id, auth_token, api_url, download_url,
                       recommended_part_size, absolute_minimum_part_size,
                       application_key, realm, s3_api_url, allowed,
                       application_key_id):
        self.account_id = account_id
        self.auth_token = auth_token
        self.api_url = api_url
        self.download_url = download_url
        self.recommended_part_size = recommended_part_size
        self.absolute_minimum_part_size = absolute_minimum_part_size
        self.application_key = application_key
        self.realm = realm
        self.s3_api_url = s3_api_url
        self.allowed = allowed
        self.application_key_id = application_key_id

        self.save_config()
