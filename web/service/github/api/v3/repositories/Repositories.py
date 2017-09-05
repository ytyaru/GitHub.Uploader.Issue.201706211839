#!python3
#encoding:utf-8
import requests
import urllib.parse
import json
import web.http.Paginator
import web.service.github.api.v3.Response
import web.log.Log
class Repositories:
    def __init__(self, reqp, response, args):
        self.__reqp = reqp
        self.__response = response
        self.__args = args

    def create(self, name, description=None, homepage=None):
        method = 'POST'
        endpoint = 'user/repos'
        params = self.__reqp.Get(method, endpoint)
        params['data'] = json.dumps({"name": name, "description": description, "homepage": homepage})
        web.log.Log.Log().Logger.debug(urllib.parse.urljoin("https://api.github.com", endpoint))
        web.log.Log.Log().Logger.debug(params)
        r = requests.post(urllib.parse.urljoin("https://api.github.com", endpoint), **params)
        return self.__response.Get(r)
        
    def gets(self, visibility=None, affiliation=None, type=None, sort='full_name', direction=None, per_page=30):
        if (visibility is None) and (affiliation is None) and (type is None):
            type = 'all'
        self.__raise_param_error(visibility, ['all', 'public', 'private'], 'visibility')
        if not(None is affiliation):
            for a in affiliation.split(','):
                self.__raise_param_error(a, ['owner', 'collaborator', 'organization_member'], 'affiliation')
        self.__raise_param_error(type, ['all', 'owner', 'public', 'private', 'member'], 'type')
        self.__raise_param_error(sort, ['created', 'updated', 'pushed', 'full_name'], 'sort')
        if direction is None:
            if sort == 'full_name':
                direction = 'asc'
            else:
                direction = 'desc'
        else:
            self.__raise_param_error(direction, ['asc', 'desc'], 'direction')

        paginator = web.http.Paginator.Paginator(web.service.github.api.v3.Response.Response())
        url = urllib.parse.urljoin('https://api.github.com', 'user/repos')
        params = self.__GetCreateParameter(visibility, affiliation, type, sort, direction, per_page)
        return paginator.Paginate(url, **params)

    def __GetCreateParameter(self, visibility=None, affiliation=None, type=None, sort='full_name', direction=None, per_page=30):
        method = 'GET'
        endpoint = 'user/repos'
        params = self.__reqp.Get(method, endpoint)
        params['headers'].update({'Accept': 'application/vnd.github.drax-preview+json'})
        params['params'] = {}
        if not(None is visibility):
            params['params']["visibility"] = visibility
        if not(None is affiliation):
            params['params']["affiliation"] = affiliation
        if not(None is type):
            params['params']["type"] = type
        if not(None is sort):
            params['params']["sort"] = sort
        if not(None is direction):
            params['params']["direction"] = direction
        if not(None is per_page):
            params['params']["per_page"] = per_page
        web.log.Log.Log().Logger.debug(params)
        return params

    def __raise_param_error(self, target, check_list, target_name):
        if not(target is None) and not(target in check_list):
            raise Exception("Parameter Error: [{0}] should be one of the following values. : {1}".format(target_name, check_list))

    """
    公開リポジトリの一覧を取得する。
    @param [int] since is repository id on github.
    """
    def list_public_repos(self, since, per_page=30):
        method = 'GET'
        endpoint = 'repositories'
        params = self.__reqp.Get(method, endpoint)
        params['params'] = json.dumps({"since": since, "per_page": per_page})
        print(params)
        web.log.Log.Log().Logger.debug(params)
        r = requests.get(urllib.parse.urljoin("https://api.github.com", endpoint), **params)
        return self.__response.Get(r)

    """
    リポジトリを削除する。
    引数を指定しなければ、デフォルトユーザのカレントディレクトリ名リポジトリを対象とする。
    """
    def delete(self, username=None, repo_name=None):
        if None is username:
            username = self.__args.username
        if None is repo_name:
            repo_name = os.path.basename(self.__args.path_dir_pj)
        endpoint = 'repos/:owner/:repo'
        params = self.__reqp.Get('DELETE', endpoint)
        endpoint = endpoint.replace(':owner', username)
        endpoint = endpoint.replace(':repo', repo_name)
        r = requests.delete(urllib.parse.urljoin("https://api.github.com", endpoint), **params)
        return self.__response.Get(r)

    """
    リポジトリを編集する。
    リポジトリ名、説明文、homepageを変更する。
    指定せずNoneのままなら変更しない。
    """
    def edit(self, name=None, description=None, homepage=None):
        if None is name:
            name = os.path.basename(self.__args.path_dir_pj)
        if None is description:
            description = self.__args.description
        if None is homepage:
            homepage = self.__args.homepage

        endpoint = 'repos/:owner/:repo'
        params = self.__reqp.Get('PATCH', endpoint)
        endpoint = endpoint.replace(':owner', self.__args.username)
        endpoint = endpoint.replace(':repo', os.path.basename(self.__args.path_dir_pj))
        params['data'] = {}
        params['data']['name'] = name
        if not(None is description or '' == description):
            params['data']['description'] = description
        if not(None is homepage or '' == homepage):
            params['data']['homepage'] = homepage
        params['data'] = json.dumps(params['data'])
        url = urllib.parse.urljoin("https://api.github.com", endpoint)
        web.log.Log.Log().Logger.debug(url)
        web.log.Log.Log().Logger.debug(params['headers'])
        web.log.Log.Log().Logger.debug(params['data'])
        r = requests.patch(url, **params)
        return self.__response.Get(r)
        
    """
    リポジトリのプログラミング言語とそのファイルサイズを取得する。
    @param  {string} usernameはユーザ名
    @param  {string} repo_nameは対象リポジトリ名
    @return {dict}   結果(JSON形式)
    """
    def list_languages(self, username=None, repo_name=None):
        if None is username:
            username = self.__args.username
        if None is repo_name:
            repo_name = os.path.basename(self.__args.path_dir_pj)
        endpoint = 'repos/:owner/:repo/languages'
        params = self.__reqp.Get('GET', endpoint)
        endpoint = endpoint.replace(':owner', username)
        endpoint = endpoint.replace(':repo', repo_name)
        web.log.Log.Log().Logger.debug(endpoint)
        r = requests.get(urllib.parse.urljoin("https://api.github.com", endpoint), **params)
        return self.__response.Get(r)

