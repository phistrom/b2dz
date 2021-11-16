# -*- coding: utf-8 -*-
"""
"""

import os

import dropzone as dz


class B2DZConfig(object):
    ACCESS_KEY_KEY = "B2DZ_APPLICATION_KEY_ID"
    SECRET_KEY_KEY = "B2DZ_APPLICATION_KEY"
    BUCKET_NAME_KEY = "B2DZ_BUCKET_NAME"
    PREFIX_KEY = "B2DZ_PREFIX_PATH"

    def __init__(self, access_key=None, secret_key=None, bucket_name=None,
                 prefix=None, **kwargs):
        print(access_key)
        if access_key is None:
            access_key = os.environ.get(self.ACCESS_KEY_KEY)
        self.access_key = access_key
        print(self.access_key)

        if secret_key is None:
            secret_key = os.environ.get(self.SECRET_KEY_KEY)
        self.secret_key = secret_key

        if bucket_name is None:
            bucket_name = os.environ.get(self.BUCKET_NAME_KEY)
        self.bucket_name = bucket_name

        if prefix is None:
            prefix = os.environ.get(self.PREFIX_KEY)
        self.prefix = prefix

    @property
    def bucket_name(self):
        return self._bucket_name

    @bucket_name.setter
    def bucket_name(self, value):
        self._bucket_name = value

    @property
    def prefix(self):
        return self._prefix

    @prefix.setter
    def prefix(self, value):
        if not value:
            value = "/"
        self._prefix = value

    @staticmethod
    def keys():
        return (
            "access_key",
            "secret_key",
            "bucket_name",
            "prefix",
        )

    def save(self):
        dz.save_value(self.ACCESS_KEY_KEY, self.access_key)
        dz.save_value(self.SECRET_KEY_KEY, self.secret_key)
        if self.bucket_name:
            dz.save_value(self.BUCKET_NAME_KEY, self.bucket_name)
        else:
            dz.remove_value(self.BUCKET_NAME_KEY)
        dz.save_value(self.PREFIX_KEY, self.prefix)

    @property
    def is_valid(self):
        return bool(self.access_key and self.secret_key and self.prefix)

    def __getitem__(self, item):
        if item not in self.keys():
            raise KeyError()
        value = getattr(self, item)
        print(item, value)
        if value is None:
            return ""
        return value

    def __str__(self):
        items = ["%s=%s" % (k, self[k]) for k in self.keys()]
        items_str = ", ".join(items)
        return "{%s}" % items_str

    def __repr__(self):
        # items = [(k, self[k]) for k in self.keys()]
        # return "B2DZConfig(**%s)" % str(self)
        return str(self)
