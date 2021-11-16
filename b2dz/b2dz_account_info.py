# -*- coding: utf-8 -*-
"""
"""
import json
import os
from functools import wraps
from json import JSONDecodeError

import dropzone as dz
from b2sdk.account_info.exception import MissingAccountData
from b2sdk.v2 import UrlPoolAccountInfo


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
    DOWNLOAD_URL_KEY = "B2DZ_DOWNLOAD_URL"
    MIN_PART_SIZE_KEY = "B2DZ_MIN_PART_SIZE"
    REALM_KEY = "B2DZ_REALM_KEY"
    RECOMMENDED_PART_SIZE_KEY = "B2DZ_RECOMMENDED_PART_SIZE"
    S3_API_URL_KEY = "B2DZ_S3_API_URL"
    SECRET_KEY_KEY = "B2DZ_APPLICATION_KEY"
    BUCKET_NAME_KEY = "B2DZ_BUCKET_NAME"
    PREFIX_KEY = "B2DZ_PREFIX_PATH"

    def __init__(self, application_key_id=None, application_key=None,
                 bucket_name=None, prefix=None, **kwargs):
        super(DropzoneB2AccountInfo, self).__init__()
        if application_key_id is not None:
            self.application_key_id = application_key_id
        if application_key is not None:
            self.application_key = application_key
        if bucket_name is not None:
            self.bucket_name = bucket_name
        if prefix is not None:
            self.prefix = prefix

    @staticmethod
    def _load_value(key):
        value = os.environ.get(key)
        try:
            value = value.replace("\\:", ":").replace('\\"', '"')
        except AttributeError:
            pass
        return value

    @staticmethod
    def _save_value(key, value):
        if value is None or value == "":
            dz.remove_value(key)
        else:
            value = str(value)
            value = value.replace(":", "\\:").replace('"', '\\"')
            dz.save_value(key, value)
            os.environ[key] = value

    @property
    def account_id(self):
        return self._load_value(self.ACCOUNT_ID_KEY)

    @account_id.setter
    def account_id(self, value):
        self._save_value(self.ACCOUNT_ID_KEY, value)

    @property
    def auth_token(self):
        return self._load_value(self.AUTH_TOKEN_KEY)

    @auth_token.setter
    def auth_token(self, value):
        self._save_value(self.AUTH_TOKEN_KEY, value)

    @property
    def api_url(self):
        return self._load_value(self.API_URL_KEY)

    @api_url.setter
    def api_url(self, value):
        self._save_value(self.API_URL_KEY, value)

    @property
    def bucket_name(self):
        return self._load_value(self.BUCKET_NAME_KEY)

    @bucket_name.setter
    def bucket_name(self, value):
        self._save_value(self.BUCKET_NAME_KEY, value)

    @property
    def buckets(self):
        """
        Returns a dictionary of buckets accessible to the account. The key is
        the bucket's name and the value is its ID.

        :rtype: dict[str, str]
        """
        buckets = self._load_value(self.BUCKETS_KEY)
        if buckets is None:
            return {}
        return json.loads(buckets)

    @buckets.setter
    def buckets(self, value):
        """
        :type value: dict[str, str]
        """
        if value is not None:
            value = json.dumps(value)
        self._save_value(self.BUCKETS_KEY, value)

    @property
    def download_url(self):
        return self._load_value(self.DOWNLOAD_URL_KEY)

    @download_url.setter
    def download_url(self, value):
        self._save_value(self.DOWNLOAD_URL_KEY, value)

    @property
    def recommended_part_size(self):
        return self._load_value(self.RECOMMENDED_PART_SIZE_KEY)

    @recommended_part_size.setter
    def recommended_part_size(self, value):
        self._save_value(self.RECOMMENDED_PART_SIZE_KEY, value)

    @property
    def absolute_minimum_part_size(self):
        return self._load_value(self.MIN_PART_SIZE_KEY)

    @absolute_minimum_part_size.setter
    def absolute_minimum_part_size(self, value):
        self._save_value(self.MIN_PART_SIZE_KEY, value)

    @property
    def application_key(self):
        return self._load_value(self.SECRET_KEY_KEY)

    @application_key.setter
    def application_key(self, value):
        self._save_value(self.SECRET_KEY_KEY, value)

    @property
    def prefix(self):
        return self._load_value(self.PREFIX_KEY)

    @prefix.setter
    def prefix(self, value):
        if not value:
            value = "/"
        self._save_value(self.PREFIX_KEY, value)

    @property
    def realm(self):
        return self._load_value(self.REALM_KEY)

    @realm.setter
    def realm(self, value):
        self._save_value(self.REALM_KEY, value)

    @property
    def s3_api_url(self):
        return self._load_value(self.S3_API_URL_KEY)

    @s3_api_url.setter
    def s3_api_url(self, value):
        self._save_value(self.S3_API_URL_KEY, value)

    @property
    def allowed(self):
        """
        :rtype: dict
        """
        value = self._load_value(self.ALLOWED_KEY)
        if value is None:
            return None
        try:
            return json.loads(value)
        except JSONDecodeError as ex:
            print(value)
            raise ex

    @allowed.setter
    def allowed(self, value):
        if value is not None:
            value = json.dumps(value, separators=(",", ":"))
        self._save_value(self.ALLOWED_KEY, value)

    @property
    def application_key_id(self):
        return self._load_value(self.ACCESS_KEY_KEY)

    @application_key_id.setter
    def application_key_id(self, value):
        self._save_value(self.ACCESS_KEY_KEY, value)

    def clear(self):
        self.clear_cache()
        self._clear()
        return super(DropzoneB2AccountInfo, self).clear()

    def clear_cache(self):
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
        return bool(self.application_key_id and self.application_key and
                    self.prefix)

    def refresh_entire_bucket_name_cache(self, name_id_iterable):
        self.buckets = dict(name_id_iterable)

    def remove_bucket_name(self, bucket_name):
        self.buckets = {name: _id for name, _id in self.buckets.items()
                        if name != bucket_name}

    def save_bucket(self, bucket):
        """
        :type bucket: b2sdk.bucket.Bucket
        """
        buckets = self.buckets
        buckets[bucket.name] = bucket.id_
        self.buckets = buckets

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
