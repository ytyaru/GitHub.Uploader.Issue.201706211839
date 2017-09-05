#!python3
#encoding:utf-8
import requests
"""
WebAPIを複数回に渡って実行する。まとめて結果を返す。
HttpHeaderのLinkキーにあるrel属性値nextのurlが存在するかぎり、そのURLをリクエストする。
"""
class Paginator(object):
    def __init__(self, response):
        self.__response = response
    """
    requests.get()をくりかえす。r.links['next']['url']が存在する限り。
    @params {string} urlはGETするURL。
    @params {integer} limitはくりかえすリクエストの上限数。0以下なら上限なし。
    @params {dict} **kwargsはrequests.get()に渡す引数。
    @return {list} HTTPレスポンスの配列。
    """
    def Paginate(self, url, limit=0, **kwargs):
        response = []
        count = 0
        while (None is not url):
            r = requests.get(url, **kwargs)
            response += self.__response.Get(r)
            if 'links' in r or None is r.links or 'next' not in r.links or 'url' not in r.links['next']:
                url = None
            else:
                url = r.links['next']['url']
            count += 1
            if 0 < limit and limit <= count:
                return response
        return response

