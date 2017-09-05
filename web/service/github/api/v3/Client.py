#!python3
#encoding:utf-8
import web.http.Response
import web.service.github.api.v3.Response
import web.service.github.api.v3.RequestParameter
from web.service.github.api.v3.miscellaneous.Licenses import Licenses
from web.service.github.api.v3.repositories.Repositories import Repositories
from web.service.github.api.v3.authorizations.Authorizations import Authorizations
from web.service.github.api.v3.issues.Issues import Issues
from web.service.github.api.v3.users.Users import Users
from web.service.github.api.v3.users.SshKeys import SshKeys
from web.service.github.api.v3.users.Emails import Emails
class Client(object):
    def __init__(self, db, authentications, args=None):
        self.__db = db
        self.__reqp = web.service.github.api.v3.RequestParameter.RequestParameter(self.__db, authentications)
        self.__response = web.service.github.api.v3.Response.Response()
        self.__license = Licenses(self.__reqp, self.__response)
        self.__repos = Repositories(self.__reqp, self.__response, args)
        self.__authorization = Authorizations(self.__reqp, self.__response)
        self.__issues = Issues(self.__reqp, self.__response, args)
        self.__user = Users(self.__reqp, self.__response)
        self.__sshkey = SshKeys(self.__reqp, self.__response)
        self.__email = Emails(self.__reqp, self.__response)

    @property
    def Repositories(self): return self.__repos
    @property
    def Licenses(self): return self.__license
    @property
    def Authorizations(self): return self.__authorization
    @property
    def Issues(self): return self.__issues
    @property
    def Users(self): return self.__user
    @property
    def SshKeys(self): return self.__sshkey
    @property
    def Emails(self): return self.__email
