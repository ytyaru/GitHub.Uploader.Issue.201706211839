#!python3
#encoding:utf-8
from requests.structures import CaseInsensitiveDict
from web.http.contenttype.MimeType import MimeType
#from MimeType import MimeType
"""
ContentType
{MimeType}; {Parameter}
Parameter = Key1=Value1; Key2=Value2; Key3=Value3; ...
"""
class ContentType(object):
    def __init__(self, content_type_string):
        self.__string = None # application/json; charset=utf8
        self.__mime_type = None # application/json
        self.__parameters = None # charset=utf-8
        self.__Load(content_type_string)
    @property
    def String(self):
        return self.__string
    @property
    def MimeType(self):
        return self.__mime_type
    @property
    def Parameters(self):
        return self.__parameters
    def __Load(self, content_type_string):
        self.__string = content_type_string
        if None is self.__string:
            self.__mime_type = None
            self.__parameters = None
        content_types = self.__string.split(';')
        self.__mime_type = MimeType(content_types[0])        
        if 1 < len(content_types):
            parameters = content_types[1:]
            self.__parameters = {}
            for p in parameters:
                p = p.strip()
                if 0 == len(p):
                    continue
                if not('=' in p):
                    continue
                key, value = p.split('=')
                self.__parameters.update({key.strip(): value.strip()})
            self.__parameters = CaseInsensitiveDict(self.__parameters)    

