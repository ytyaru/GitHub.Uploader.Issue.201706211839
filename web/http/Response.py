#!python3
#encoding:utf-8
import time
from PIL import Image
from io import BytesIO
#from bs4 import BeautifulSoup
from web.http.contenttype.ContentType import ContentType
class Response(object):
    def __init__(self):
        self.__headers = None
    @property
    def Headers(self):
        return self.__headers
    
    def Get(self, r, sleep_time=2, is_show=True):
        if is_show:
            print('Response.start---------------------')
            print("HTTP Status Code: {0} {1}".format(r.status_code, r.reason))
            print(r.text)
            print('Response.end---------------------')
        time.sleep(sleep_time)
        r.raise_for_status()
        
        self.__headers = Response.__Headers(r)        
        if None is self.Headers.ContentType:
            return None
        if None is self.Headers.ContentType.MimeType.String:
            return None
        elif 'application/json' == self.Headers.ContentType.MimeType.String:
            return r.json()
        elif ('image/gif' == self.Headers.ContentType.MimeType.String or
            'image/jpeg' == self.Headers.ContentType.MimeType.String or
            'image/png' == self.Headers.ContentType.MimeType.String
        ):
            return Image.open(BytesIO(r.content))
#        elif r.request.stream:
#            return r.raw
        else:
            return r.text
        """
        # HTML,XML(Webスクレイピング)
        elif ('text/html' == self.Headers.ContentType.MimeType.String or
            'application/xhtml+xml' == self.Headers.ContentType.MimeType.String or
            'text/xml' == self.Headers.ContentType.MimeType.String or
            'application/rss+xml' == self.Headers.ContentType.MimeType.String or
            'application/xml' == self.Headers.ContentType.MimeType.String or
            'application/xhtml+xml' == self.Headers.ContentType.MimeType.String or
            'xml' == self.Headers.ContentType.MimeType.SubType.String or
            (None is not self.Headers.ContentType.MimeType.SubType.Suffix and 'xml' == self.Headers.ContentType.MimeType.SubType.Suffix)
        ):
            return BeautifulSoup(res.text, 'lxml')
        """
            
    class __Headers:
        def __init__(self, r):
#            self.__content_type = self._Headers__ContentType(r.headers['Content-Type'])
            if 'Content-Type' in r.headers:
                self.__content_type = ContentType(r.headers['Content-Type'])
            else:
                self.__content_type = None
        @property
        def ContentType(self):
            return self.__content_type
