#!python3
#encoding:utf-8
import re
from requests.structures import CaseInsensitiveDict
#from tree.SubTypeTree import SubTypeTreeFactory
from web.http.contenttype.tree.SubTypeTree import SubTypeTreeFactory
"""
{Tree}.{MediaType}+{Suffix}
Tree = {Facet}.{Tree1.Tree2...}。ファセットごとに構成が異なる。https://developer.github.com/v3/media/
本当は"vnd.github"固有クラスを作って定義するのが理想だが、細かすぎて実装する必要性を見つけられないので見送る。
"""
class SubType(object):
    def __init__(self, sub_type_string):
        self.__string = None
        self.__tree = None
        self.__facet = None
        self.__media_type = None
        self.__suffix = None
        self.__Load(sub_type_string)
    @property
    def String(self):
        return self.__string
    @property
    def Facet(self):
        return self.__facet
    @property
    def Tree(self):
        return self.__tree
    @property
    def MediaType(self):
        return self.__media_type
    @property
    def Suffix(self):
        return self.__suffix
    def __Load(self, sub_type_string):
        self.__string = sub_type_string
        if '+' in sub_type_string:
            sub_type_string, self.__suffix = self.__string.split('+')
        else:
            self.__suffix = None
        breadcrumbs = sub_type_string.split('.') # パンくずリスト
        if 1 == len(breadcrumbs):
            self.__media_type = breadcrumbs[0]
            self.__facet = None
            self.__tree = SubTypeTreeFactory.Create(self.__facet, None) # StandardTree
        else:
            self.__facet = breadcrumbs[0]
            self.__media_type = breadcrumbs[-1]
            self.__tree = SubTypeTreeFactory.Create(self.__facet, breadcrumbs[1:]) # Tree末尾はMediaTypeだがGitHubVenderTreeではVersionやParameterになりうる
