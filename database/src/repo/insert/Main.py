#!python3
#encoding:utf-8
import os.path
import getpass
import database.src.repo.insert.command.repositories.Inserter
class Main:
    def __init__(self, db, username, client):
        self.__inserter = database.src.repo.insert.command.repositories.Inserter.Inserter(db, username, client)

    def Initialize(self):
        self.__inserter.Insert()

    def Run(self):
        print('GitHubリポジトリ情報を取得します。')
        url = 'start'
        while '' != url:
            print('GitHubリポジトリのURLを入力してください。(未入力+Enterで終了)')
            print('サブコマンド    l:既存リポジトリ')
            url = input()
            if '' == url:
                break
            elif 'l' == url or 'L' == url:
                self.__inserter.Show()
            else:
                username = self.data.get_other_username(url)
                repo_name = self.data.get_other_repo_name(url)
                print("ユーザ名: " + username)
                print("リポジトリ名: " + repo_name)
                # 未登録ならDBへ挿入する（GitHubAPIでリポジトリ情報、言語情報、ライセンス情報を取得して）
                self.__inserter.Insert(username, repo_name)

