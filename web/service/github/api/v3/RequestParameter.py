#!python3
#encoding:utf-8
from web.service.github.api.v3.authentication.Authentication import Authentication
from web.service.github.api.v3.authentication.NonAuthentication import NonAuthentication
from web.service.github.api.v3.authentication.BasicAuthentication import BasicAuthentication
from web.service.github.api.v3.authentication.TwoFactorAuthentication import TwoFactorAuthentication
from web.service.github.api.v3.authentication.OAuthAuthentication import OAuthAuthentication
from web.service.github.api.v3.authentication.OAuthTokenFromDatabaseAuthentication import OAuthTokenFromDatabaseAuthentication
from web.service.github.api.v3.authentication.OAuthTokenFromDatabaseAndCreateApiAuthentication import OAuthTokenFromDatabaseAndCreateApiAuthentication

class RequestParameter:
    def __init__(self, db, authentications):
        self.__db = db
        self.__authentications = []
        if isinstance(authentications, list):
            for a in authentications:
                if isinstance(a, Authentication):
                    self.__authentications.append(a)

    def Get(self, http_method, endpoint):
        api = self.__db.Apis['Apis'].find_one(HttpMethod=http_method.upper(), Endpoint=endpoint)
        if None is api:
            for a in self.__authentications:
                if hasattr(a, 'SetAccessToken'): # OAuthTokenFromDatabaseAndCreateApiAuthentication, OAuthTokenFromDatabaseAuthentication
                    a.SetAccessToken()
                return a.GetRequestParameters()
            return NonAuthentication().GetRequestParameters()
        grants = api['Grants'].split(",")
        if ("Token" in api['AuthMethods']):
            for a in self.__authentications:
                if isinstance(a, OAuthAuthentication):
                    if hasattr(a, 'SetAccessToken'): # OAuthTokenFromDatabaseAndCreateApiAuthentication, OAuthTokenFromDatabaseAuthentication
                        a.SetAccessToken()
                    return a.GetRequestParameters()
        if ("Basic" in api['AuthMethods']):
            for a in self.__authentications:
                if isinstance(a, TwoFactorAuthentication):
                    return a.GetRequestParameters()
                elif isinstance(a, BasicAuthentication):
                    return a.GetRequestParameters()
        if ("ClientId" in api['AuthMethods']):
            raise Exception('Not implemented clientId authorization.')
        raise Exception('Not found AuthMethods: {0} {1} {2}'.format(api['HttpMethod'], api['Endpoint'], self.__GetClassNames()))
        
    def __GetClassNames(self):
        class_name = ""
        for a in self.__authentications:
            class_name += a.__class__.__name__ + ','
        return class_name[:-1]

