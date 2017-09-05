#!python3
#encoding:utf-8
from abc import ABCMeta, abstractmethod
import re
from requests.structures import CaseInsensitiveDict
"""
{Tree}.{MediaType}+{Suffix}
Tree = {Facet}.{Tree1.Tree2...}。ファセットごとに構成が異なる。https://developer.github.com/v3/media/
本当は"vnd.github"固有クラスを作って定義するのが理想だが、細かすぎて実装する必要性を見つけられないので見送る。
"""
class SubTypeTreeFactory(object):
    @staticmethod
    def Create(facet, tree_list):
        if None is tree_list or 0 == len(tree_list) or None is facet or 0 == len(facet):
            return StandardTree(tree_list)
        if facet == VenderTree.GetFacet():
            return VenderTreeFactory.Create(tree_list)
        types = [ParsonalTree, UnregisteredTree]
        for t in types:
            if t.GetFacet() == facet:
                return t(tree_list)
        
        # 未定義ファセットの場合
        facets = ""
        all_types = [VenderTree] + types
        for t in all_types:
            facets = t.GetFacet() + ','
        facets = facets[:-1]
        raise Exception('未定義のファセットです。ファセットは {facets} のうちのどれかにしてください。入力値: {facet}'.format(facets=facets, facet=facet))
class VenderTreeFactory(object):
    @staticmethod
    def Create(tree_list):
        types = [GitHubVenderTree]
        for t in types:
            if t.GetVenderName() == tree_list[0]:
                return t(tree_list)
        return VenderTree(tree_list)

class SubTypeTree(metaclass=ABCMeta):
    def __init__(self, tree_list):
        self.__tree_list = tree_list
    @property
    def TreeList(self):
        return self.__tree_list
    @staticmethod
    @abstractmethod
    def GetFacet():
        return None
"""
tree = vnd.
"""    
class StandardTree(SubTypeTree):
    def __init__(self, tree_list):
        super().__init__(tree_list)
    """
    @staticmethod
    @property
    def Facet(cls):
        return None
    """
    @staticmethod
    def GetFacet():
        return None
    # Staticなプロパティができない
    # <property object at 0xb6a47694>
#    @staticmethod
#    @property
#    def StaticProperty():
#        return 'StaticProperty'

"""
tree = prs.
"""    
class ParsonalTree(SubTypeTree):
    def __init__(self, tree_list):
        super().__init__(tree_list)
    """
    @staticmethod
    @property
    def Facet(cls):
        return "prs"
    """
    @staticmethod
    def GetFacet():
        return "prs"
"""
tree = x.
"""
class UnregisteredTree(SubTypeTree):
    def __init__(self, tree_list):
        super().__init__(tree_list)
    """
    @staticmethod
    @property
    def Facet(cls):
        return "x"
    """
    @staticmethod
    def GetFacet():
        return "x"
"""
tree = vnd.
"""
class VenderTree(SubTypeTree):
    def __init__(self, tree_list):
        super().__init__(tree_list)
    """
    @staticmethod
    @property
    def Facet(cls):
        return "vnd"
    """
    @staticmethod
    def GetFacet():
        return "vnd"
    # staticmethodの実装を強制することができない
#    @staticmethod
#    @abstractmethod
#    def GetVenderName():
#        return None
    @property
    def VenderName(self):
        return super().TreeList[0]

"""
tree = vnd.github.{version}
* application/json
* application/vnd.github+json
* application/vnd.github.v3+json
* application/vnd.github.v3.raw+json
https://developer.github.com/v3/media/
tree_list = github...
"""
class GitHubVenderTree(VenderTree):
    def __init__(self, tree_list):
        super().__init__(tree_list)
        self.__Load()
    def __Load(self):
        if 1 == len(super().TreeList):
            self.__version = None
            self.__param = None
        elif 2 == len(super().TreeList):
            self.__version = super().TreeList[1]
            self.__param = None
        else:
            self.__version = super().TreeList[1]
            self.__param = super().TreeList[2]
            
    @staticmethod
    def GetVenderName():
        return "github"
    @property
    def Version(self):
         return self.__version
    @property
    def Parameter(self):
        return self.__param

