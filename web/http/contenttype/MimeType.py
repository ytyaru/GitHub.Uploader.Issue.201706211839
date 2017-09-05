#!python3
#encoding:utf-8
import re
from requests.structures import CaseInsensitiveDict
#from SubType import SubType
from web.http.contenttype.SubType import SubType
"""
{TopLevelType}/{SubType}
"""
class MimeType(object):
    def __init__(self, mime_type_string):
        self.__string = None
        self.__top_level_type = None
        self.__sub_type = None
        self.__Load(mime_type_string)
    @property
    def String(self):
        return self.__string
    @property
    def TopLevelType(self):
        return self.__top_level_type
    @property
    def SubType(self):
        return self.__sub_type
    def __Load(self, mime_type_string):
        self.__string = mime_type_string.strip()
        if None is self.__string:
            self.__top_level_type = None
            self.__sub_type = None
            self.__suffix = None
        else:
            types = self.__string.split('/')
            if 2 != len(types):
                raise Exception('MimeTypeは {TopLevelType}/{SubType} の書式である必要があります。入力値: ' + self.__string)
            self.__top_level_type = types[0]
#            self.__sub_type = self._MimeType__SubType(types[1])
            self.__sub_type = SubType(types[1])

