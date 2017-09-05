#!python3
#encoding:utf-8
import os.path
import configparser
import argparse
from database.src.Database import Database
import pyotp
import pyperclip
import web.log.Log
class GitHubOtpCreator:
    def __init__(self):
        self.__path_dir_this = os.path.abspath(os.path.dirname(__file__))
        self.__db = Database(self.__path_dir_this)
#        self.__db = Database()
        self.__db.Initialize()
    
    def Create(self):
        self.__totp = pyotp.TOTP(self.__GetUserSecret())
#        print("otp = {0}".format(self.__totp.now()))
        web.log.Log.Log().Logger.info("otp = {0}".format(self.__totp.now()))
        pyperclip.copy(self.__totp.now())
    
    def __GetUserSecret(self):
        parser = argparse.ArgumentParser(
            description='GitHub Repository Uploader.',
        )
        parser.add_argument('-u', '--username', '--user')
        args = parser.parse_args()
        
        username = args.username
        if None is username:
            config = configparser.ConfigParser()
            config.read('./config.ini')
            if not('GitHub' in config):
                raise Exception('ユーザ名が必要です。しかし起動引数にもconfig.iniにも存在しません。起動引数なら第一引数にユーザ名を渡してください。iniならGitHubセクションUserキーにユーザ名を指定してください。')
            if not('User' in config['GitHub']):
                raise Exception('ユーザ名が必要です。しかし起動引数にもconfig.iniにも存在しません。起動引数なら第一引数にユーザ名を渡してください。iniならGitHubセクションUserキーにユーザ名を指定してください。')
            username = config['GitHub']['User']
#        print("username = {0}".format(username))
        web.log.Log.Log().Logger.info("username = {0}".format(username))
        account = self.__db.Accounts['Accounts'].find_one(Username=username)
        if None is account:
            raise Exception('ユーザ {0} はDBのAccountsテーブルに存在しません。登録してから再度実行してください。'.format(username))
        twofactor = self.__db.Accounts['TwoFactors'].find_one(AccountId=account['Id'])
        if None is twofactor:
            raise Exception('ユーザ {0} はDBのTwoFactorsテーブルに存在しません。登録してから再度実行してください。'.format(username))
        return twofactor['Secret']


if __name__ == '__main__':
    c = GitHubOtpCreator()
    c.Create()
