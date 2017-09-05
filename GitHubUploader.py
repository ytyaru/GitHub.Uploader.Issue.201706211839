#!/usr/bin/python3
#!python3
#encoding:utf-8
import sys
import os.path
import subprocess
import configparser
import argparse
import web.service.github.api.v3.AuthenticationsCreator
import web.service.github.api.v3.Client
import database.src.Database
import cui.uploader.Main
import web.log.Log
import database.src.contributions.Main
import setting.Setting

class Main:
    def __init__(self):
        pass

    def Run(self):
        parser = argparse.ArgumentParser(
            description='GitHub Repository Uploader.',
        )
        parser.add_argument('path_dir_pj')
        parser.add_argument('-u', '--username')
        parser.add_argument('-d', '--description')
        parser.add_argument('-l', '--homepage', '--link', '--url')
        parser.add_argument('-m', '--messages', action='append')
        args = parser.parse_args()
#        print(args)
#        print('path_dir_pj: {0}'.format(args.path_dir_pj))
#        print('-u: {0}'.format(args.username))
#        print('-d: {0}'.format(args.description))
#        print('-l: {0}'.format(args.homepage))

        self.__setting = setting.Setting.Setting(os.path.abspath(os.path.dirname(__file__)))
        path_dir_db = self.__setting.DbPath
        web.log.Log.Log().Logger.debug(path_dir_db)
        
        # os.path.basename()で空文字を返されないための対策
        # https://docs.python.jp/3/library/os.path.html#os.path.basename
        if args.path_dir_pj.endswith('/'):
            args.path_dir_pj = args.path_dir_pj[:-1]
        
        if None is args.username:
            print(self.__setting.GithubUsername)
            args.username = self.__setting.GithubUsername        
        self.__db = database.src.Database.Database(os.path.abspath(os.path.dirname(__file__)))
        self.__db.Initialize()
        
        if None is self.__db.Accounts['Accounts'].find_one(Username=args.username):
            web.log.Log.Log().Logger.warning('指定したユーザ {0} はDBに存在しません。GitHubUserRegister.pyで登録してください。'.format(args.username))
            return
        
        # Contributionsバックアップ
        self.__UpdateAllUserContributions(path_dir_db)
        
        # アップローダ起動
        creator = web.service.github.api.v3.AuthenticationsCreator.AuthenticationsCreator(self.__db, args.username)
        authentications = creator.Create()
        client = web.service.github.api.v3.Client.Client(self.__db, authentications, args)
        main = cui.uploader.Main.Main(self.__db, client, args)
        main.Run()

    def __UpdateAllUserContributions(self, path_dir_db, username=None):
        m = database.src.contributions.Main.Main(path_dir_db)
        if None is not username:
            m.Run(username)
        else:
            for a in self.__db.Accounts['Accounts'].find():
                m.Run(a['Username'])


if __name__ == '__main__':
    main = Main()
    main.Run()
