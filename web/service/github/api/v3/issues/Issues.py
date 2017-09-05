#!python3
#encoding:utf-8
import requests
import urllib.parse
import json
import datetime
import web.http.Paginator
import web.service.github.api.v3.Response
import web.log.Log
class Issues:
    def __init__(self, reqp, response, args):
        self.__reqp = reqp
        self.__response = response
        self.__args = args

    def create(self, title, body=None, labels=None, milestone=None, assignees=None):
        method_params = {}
        if None is title: title = '{0:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
        method_params = {k:v for k, v in locals().items() if None is not v and 'self' != k and 'method_params' != k}
        print(method_params)
        
        method = 'POST'
        endpoint = 'repos/:owner/:repo/issues'
        endpoint = endpoint.replace(':owner', self.__args.username)
        print(self.__repo)
        endpoint = endpoint.replace(':repo', os.path.basename(self.__args.path_dir_pj))
        print(endpoint)
        params = self.__reqp.Get(method, endpoint)
        if 'data' in params: params['data'].update(json.dumps(method_params))
        else: params['data'] = json.dumps(method_params)
#        print(params)
        web.log.Log.Log().Logger.debug(urllib.parse.urljoin("https://api.github.com", endpoint))
        web.log.Log.Log().Logger.debug(params)
        r = requests.post(urllib.parse.urljoin("https://api.github.com", endpoint), **params)
        return self.__response.Get(r)

    """
    Issueを編集する。
    labels: 全ラベルを削除するには空配列[]を指定する。
    assignees: 全ユーザを削除するには空配列[]を指定する。
    """
    def edit(self, title=None, body=None, state=None, milestone=None, labels=None, assignees=None):
        # PATCH /repos/:owner/:repo/issues/:number 
        pass
    
    """
    指定リポジトリのIssueを取得する。
    milestone: 数値, '*', 'none'
    state: open, closed, all
    assignee: 指定ユーザ名, '*', 'none'
    creator: Issue作成ユーザ名
    mentioned: 言及されているユーザ名
    labels: コンマ区切りのラベル名
    sort: created, updated, comments
    direction: asc, desc
    since: YYYY-MM-DDTHH:MM:SSZ
    per_page: 1〜100
    """
    def GetRepoIssues(self, milestone=None, state='open', assignee='*', creator=None, mentioned=None, labels=None, sort='created', direction='desc', since=None, per_page=30):
        method_params = {}
        if None is title: title = '{0:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
        method_params = {k:v for k, v in locals().items() if None is not v and 'self' != k and 'method_params' != k}
        print(method_params)
        
        method = 'GET'
        endpoint = 'repos/:owner/:repo/issues'
        endpoint = endpoint.replace(':owner', self.__args.username)
        endpoint = endpoint.replace(':repo', os.path.basename(self.__args.path_dir_pj))
        print(endpoint)
        params = self.__reqp.Get(method, endpoint)
        if 'params' in params: params['params'].update(method_params)
        else: params['params'] = method_params
        print(params)

        paginator = web.http.Paginator.Paginator(web.service.github.api.v3.Response.Response())
        url = urllib.parse.urljoin('https://api.github.com', endpoint)
        return paginator.Paginate(url, **params)
    
    """
    指定ユーザのIssueを取得する。
    _filter: assigned, created, mentioned, subscribed, all
    state: open, closed, all
    labels: コンマ区切りのラベル名
    sort: created, updated, comments
    direction: asc, desc
    since: YYYY-MM-DDTHH:MM:SSZ
    per_page: 1〜100
    """
    def GetUserIssues(self, _filter='assigned', state='open', labels=None, sort='created', direction='desc', since=None, per_page=30):
        # GET /user/issues
        pass
        
